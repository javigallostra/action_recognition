import networkx as nx
import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb
from math import sqrt
from state import *
from random import random


from time import sleep

"""
Class representing an ASN with full functionality.
"""
class ASN_BASE(object):
    """
    Create a directed graph, add the first node,
    and initialize ASN variables.
    """
    def __init__(self):
        # create graph with start nodes
        self.graph = nx.DiGraph()
        self.graph.add_node(0, state=State([]), end=False, color=[1,0,0], value=1) # start
        # keep track of node count
        self.node_count = 1
        # keep track of end node
        self.end_node = 0
        # keep track of current state
        self.latest_state = State([])
        # figure to plot to
        self.figure = 1

    """
    End building the graph, setting the
    latest node to be the end node
    """
    def end(self):
        self.end_node = self.node_count - 1
        self.graph.node[self.end_node]['end'] = True
        self._relabel_nodes()

    """
    Plot the graph using matplotlib
    """
    def plot(self, fig = 0):
        # change figure if needed
        if fig:
            self.figure = fig
        # switch to interactive and clear figure
        plt.ion()
        plt.figure(self.figure)
        plt.clf()
        # draw graph
        nx.draw(self.graph, labels=self._node_label_map(), font_color='k', pos=self._node_position(), node_color=self._node_color_map(), node_size=self._node_size_map(), edge_color=self._edge_color_map(), with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos=self._node_position(), edge_labels=self._edge_labels())
        # show
        plt.pause(0.0001)
        plt.show()


    """
    Compute a color map of the graph edges
    based on their weight.
    """
    def _edge_color_map(self):
        # 1. find the edge with highest weight
        # 2. colorize all edges with saturation = weight/max_weight
        max_w = max([self.graph.edge[e0][e1]['weight'] for (e0,e1) in self.graph.edges()])
        for ni, nf, weight in self.graph.edges(data='weight'):
            if weight > max_w:
                max_w = weight
            for ni, nf, weight in self.graph.edges(data='weight'):
                c = 1 - weight/max_w
                rgb = (c, c, c)
                self.graph.edge[ni][nf]['color'] = rgb
        cmap = [self.graph.edge[edge[0]][edge[1]]['color'] for edge in self.graph.edges()]
        return cmap

    def _node_label_map(self):
        labels = {}
        for n in self.graph.nodes():
            labels[n] = "{:.2f}".format(self.graph.node[n]['value'])
        return labels

    """
    Compute a color map of the graph nodes based on
    their index.
    """
    def _node_color_map(self):
        # colorize the graph nodes
        # 1. start at pure green
        # 2. equally traverse all the (hue/value) until (0/1)
        for n in range(1,self.node_count):
            h = (1/3) + 0.5*(1 - n/(self.node_count-2))
            s = 1
            v = sqrt(sqrt(n/(self.node_count-2)))
            rgb = hsv_to_rgb(h,s,v)
            self.graph.node[n]['color'] = rgb
        # generate a color map for plotting
        cmap = [self.graph.node[i]['color'] for i in self.graph.nodes()]
        cmap[self.node_count - 1] = self.graph.node[0]['color']
        return cmap


    def _node_size_map(self):
        max_value = max([self.graph.node[n]['value'] for n in self.graph.nodes()])
        sizes = []
        for n in range(self.node_count):
            perc = self.graph.node[n]['value']/max_value
            sizes.append(10 + 290*(perc/(0.001 + perc)))
        return sizes


    def _node_position(self):
        mapping = self._node_depth_map()
        # generate a position map based on node depth
        nodes_pos = {}
        for depth in range(len(mapping)):
            depth_elems = mapping[depth]
            total_width = len(depth_elems)
            for width in range(total_width):
                elem = depth_elems[width]
                nodes_pos[elem] = (width-total_width/2, depth)
        return nodes_pos

    """
    Generate the labels of the graph edges
    representing the event that triggers the edge
    """
    def _edge_labels(self):
        labels = {}
        for edge in self.graph.edges():
            labels[edge] = self.graph.edge[edge[0]][edge[1]]['trigger']
        return labels

    """
    Merge the current graph with a different one
    """
    def __iadd__(self, ASN2):
        new_states = [ASN2.graph.node[n]['state'] for n in range(1,ASN2.end_node)]
        parent_state = State([])
        # merge all nodes (except for first and last node)
        for new_state in new_states:
            self.add_node_by_state(new_state, parent_state)
            parent_state = new_state.copy()
        # merge last node
        new_state = ASN2.graph.node[ASN2.end_node]['state']
        if self.end_node == 0:
            # case of empty left-hand graph
            self.add_node_by_state(new_state, parent_state)
            self.end()
        else:
            # normal case: check edge and add if necessary
            event = new_state - parent_state
            current_states_hash = [self.graph.node[n]['state'].hash() for n in range(self.node_count)]
            parent_node = current_states_hash.index(parent_state.hash())
            edge = (parent_node, self.end_node)
            if edge not in self.graph.edges():
                self.graph.add_edge(edge[0], edge[1], weight=1, factor = 1, trigger=event)
        # relabel the nodes to match the new structure
        self._relabel_nodes()
        return self

    """
    Used for building the graph
    with a new event, adding a new
    node and edge from a parent state
    if needed
    """
    def add_node_by_event(self, event, parent_state = 0):
        # if parent_state is not given, take our latest state
        # (for when the graph is being created, not merged)
        if not isinstance(parent_state, State):
            parent_state = self.latest_state
        # generate new state
        new_state = parent_state.copy() + event
        # go to add node by state
        self.add_node_by_state(new_state, parent_state, event)

    """
    Used for building the graph
    with a new state, adding a new
    node and edge from a parent state
    if needed
    """
    def add_node_by_state(self, new_state, parent_state = 0, event = 0):
        # if parent_state is not given, take our latest state
        # (for when the graph is being created, not merged)
        if not isinstance(parent_state, State):
            parent_state = self.latest_state
        # get event that occurred
        if event == 0:
            event = new_state - parent_state
        # get current hashed states
        current_states_hash = [self.graph.node[n]['state'].hash() for n in range(self.node_count)]
        # add node if needed, else do nothing
        if new_state.hash() not in current_states_hash:
            self.graph.add_node(self.node_count, state=new_state.copy(), end=False, color=[0,0,0], value=0.0)
            current_states_hash.append(new_state.hash())
            self.node_count += 1
        # add edge if needed, else do nothing
        parent_node = current_states_hash.index(parent_state.hash())
        new_node = current_states_hash.index(new_state.hash())
        edge = (parent_node, new_node)
        if edge not in self.graph.edges():
                self.graph.add_edge(edge[0], edge[1], weight=1, factor=1, trigger=event)
        # update latest_state
        self.latest_state = new_state.copy()

    """
    Generate a dictionary containing pairs
    'depth:[nodes in depth]''
    """
    def _node_depth_map(self):
        node_depth_map = {0:[0]}
        for path in nx.all_simple_paths(self.graph,0,self.end_node):
            for depth in range(len(path)):
                if depth not in node_depth_map:
                    node_depth_map[depth] = []
                if path[depth] not in node_depth_map[depth]:
                    node_depth_map[depth].append(path[depth])
        return node_depth_map

    """
    Rename the graph nodes ordered by
    their 'depth level', useful after
    merging two graphs
    """
    def _relabel_nodes(self):
        # generate a relabel map based on node depth
        count = 0
        node_remap = {}
        mapping = self._node_depth_map()
        for depth in range(len(mapping)):
            depth_elems = mapping[depth]
            for node in depth_elems:
                node_remap[node] = count
                count += 1
        # relabel nodes
        self.graph = nx.relabel_nodes(self.graph, node_remap)
        # update end node id
        self.end_node = self.node_count - 1
        # set edge weights
        self._set_edge_weights()

    """
    Set the edge weights based on their number
    of parent nodes
    """
    def _set_edge_weights(self):
        for n in range(self.end_node,0,-1):
            pred = self.graph.predecessors(n)
            n_pred = len(pred)
            for p in pred:
                self.graph.edge[p][n]['factor'] = 1/n_pred


    """
    Export the ASN data to a .yaml file that
    can be loaded again.
    """
    def export(self, filename = "ASN_EXPORT.yaml"):
        nx.write_yaml(self.graph,"./exports/" + filename)

    """
    Load a previously exported YAML file.
    """
    def load(self, filename=""):
        # Read graph
        self.graph = nx.read_yaml("./exports/" + filename)
        # Set node node_count
        self.node_count = len(list(self.graph.nodes()))
        # Set end node id
        self.end_node = self.node_count - 1
        # update latest_state
        self.latest_state = self.graph.node[self.end_node]['state'].copy()
