import networkx as nx
import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb
from math import sqrt
from state import *

"""
Class representing an ASN with full functionality.
"""
class ASN_BASE:
    """
    Create a directed graph, add the first node,
    and initialize ASN variables.
    """
    def __init__(self):
        # create graph with start nodes
        self.graph = nx.DiGraph()
        self.graph.add_node(0, state=State([]), end=False, color=[1,0,0], value=0.0) # start
        # keep track of node count
        self.node_count = 1
        # keep track of end node
        self.end_node = 0
        # keep track of current state
        self.latest_state = State([])
        # positions of the nodes for drawing
        self.nodes_pos = {}

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
    def plot(self):
        plt.plot()
        #graph_pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos=self.nodes_pos, node_color=self._node_color_map(), edge_color=self._edge_color_map(), font_color=[1,1,1], with_labels=True, font_weight='bold')
        #nx.draw(self.graph, pos=graph_pos,font_color=[1,1,1], with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos=self.nodes_pos, edge_labels=self._edge_labels())
        plt.show()

    """
    Compute a color map of the graph edges
    based on their weight.
    """
    def _edge_color_map(self):
        # 1. find the edge with highest weight
        # 2. colorize all edges with saturation = weight/max_weight
        max_w = 0
        for ni, nf, weight in self.graph.edges(data='weight'):
            if weight > max_w:
                max_w = weight
            for ni, nf, weight in self.graph.edges(data='weight'):
                c = 0#1- weight/max_w
                rgb = (c, c, c)
                self.graph.edge[ni][nf]['color'] = rgb
        cmap = [self.graph.edge[edge[0]][edge[1]]['color'] for edge in self.graph.edges()]
        return cmap

    """
    Compute a color map of the graph nodes based on
    their index.
    """
    def _node_color_map(self):
        # colorize the graph nodes
        # 1. start at pure green
        # 2. equally traverse all the (hue/value) until (green',0)
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
            event = new_state - parent_state
            current_states_hash = [self.graph.node[n]['state'].hash() for n in range(self.node_count)]
            parent_node = current_states_hash.index(parent_state.hash())
            edge = (parent_node, self.end_node)
            if edge not in self.graph.edges():
                self.graph.add_edge(edge[0], edge[1], weight=1, trigger=event)
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
            self.graph.add_node(self.node_count, state=new_state.copy(), end=False, color=[0,0,0], value=0)
            current_states_hash.append(new_state.hash())
            self.node_count += 1
        # add edge if needed, else do nothing
        parent_node = current_states_hash.index(parent_state.hash())
        new_node = current_states_hash.index(new_state.hash())
        edge = (parent_node, new_node)
        if edge not in self.graph.edges():
                self.graph.add_edge(edge[0], edge[1], weight=1, trigger=event)
        # update latest_state
        self.latest_state = new_state.copy()

    """
    Rename the graph nodes ordered by
    their 'depth level', useful after
    merging two graphs
    """
    def _relabel_nodes(self):
        node_depth = {0:[0]}
        for path in nx.all_simple_paths(self.graph,0,self.end_node):
            for depth in range(len(path)):
                if depth not in node_depth:
                    node_depth[depth] = []
                if path[depth] not in node_depth[depth]:
                    node_depth[depth].append(path[depth])
        node_count = -1
        node_remap = {}
        for depth in range(len(node_depth)):
            depth_elems = node_depth[depth]
            total_width = len(depth_elems)
            for width in range(total_width):
                elem = depth_elems[width]
                node_count += 1
                node_remap[elem] = node_count
                self.nodes_pos[node_count] = (width-total_width/2, depth)
        self.graph = nx.relabel_nodes(self.graph, node_remap)
        self.end_node = self.node_count - 1
