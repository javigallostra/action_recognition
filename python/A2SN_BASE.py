import networkx as nx
import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb
from math import sqrt
from state import *
from random import random

"""
Class representing an A2SN with the basic functionalities:
initialize, plot, reorder graph.
"""
class A2SN_BASE(object):

    """
    Create a directed graph, add the first node,
    and initialize A2SN basic variables.
    """
    def __init__(self, action_name=""):
        # create graph with start nodes
        self.graph = nx.DiGraph()
        self.graph.add_node(0, state=State([]), end=False, color=(1,0,0), value=1, depth=1, action=action_name) # start
        # keep track of node count
        self.node_count = 1
        # keep track of end node
        self.end_node = 0
        # keep track of current state
        self.latest_state = State([])
        # figure to plot to and title
        self.figure = 1
        self.fig_title = action_name

    ################
    # PLOT METHODS #
    ################

    """
    Compute a color map of the graph edges
    based on their weight.
    """
    def __edge_color_map(self):
        # 1. find the edge with highest weight
        # 2. colorize all edges with saturation = weight/max_weight
        max_w = max([self.graph.edge[e0][e1]['weight']*self.graph.edge[e0][e1]['factor'] for (e0,e1) in self.graph.edges()])
        for ni, nf, weight in self.graph.edges(data='weight'):
            if weight > max_w:
                max_w = weight
            for ni, nf, weight in self.graph.edges(data='weight'):
                """
                c = 1 - weight/max_w
                """
                c = 0.2
                rgb = (c, c, c)
                self.graph.edge[ni][nf]['color'] = rgb
        cmap = [self.graph.edge[edge[0]][edge[1]]['color'] for edge in self.graph.edges()]
        return cmap

    """
    Compute a color map of the graph nodes based on
    their index.
    """
    def __node_color_map(self):
        # colorize the graph nodes
        # 1. start at pure green
        # 2. equally traverse all the (hue/value) until (0/1)
        for n in range(1,self.end_node + 1):
            h = (1/3) + (2/3)*(1 - n/(self.end_node))
            s = 1
            v = sqrt(sqrt(n/(self.end_node)))
            rgb = hsv_to_rgb(h,s,v)
            self.graph.node[n]['color'] = rgb
        # generate a color map for plotting
        cmap = [self.graph.node[i]['color'] for i in self.graph.nodes()]
        cmap[self.node_count - 1] = self.graph.node[0]['color']
        return cmap

    """
    Compute a map of node labels with the desired formatting,
    being the label the value of the node
    """
    def __node_label_map(self):
        labels = {}
        for n in self.graph.nodes():
            labels[n] = "{:.2f}".format(self.graph.node[n]['value']/self.graph.node[n]['depth'])
        return labels

    """
    Generate the labels of the graph edges
    representing the event that triggers the edge
    """
    def __edge_labels(self):
        labels = {}
        for edge in self.graph.edges():
            labels[edge] = self.graph.edge[edge[0]][edge[1]]['trigger']
        return labels

    """
    Generate a map of node sizes according to their value
    """
    def __node_size_map(self):
        values = [self.graph.node[n]['value']/self.graph.node[n]['depth'] for n in self.graph.nodes()]
        max_value = max(values)
        sizes = []
        for value in values:
            perc = value/max_value
            sizes.append(10 + 290*(perc/(0.001 + perc)))
        return sizes

    """
    Compute the position of the nodes according to
    their depth for better visualization
    """
    def __node_position(self):
        mapping = self.__node_depth_map()
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
    Plot the graph using matplotlib
    """
    def _plot(self, fig = 0, title = ""):
        # change figure and title if needed
        if fig:
            self.figure = fig
        if title != "":
            self.fig_title = title
        # switch to interactive and clear figure
        plt.figure(self.figure)
        plt.clf()
        plt.title(self.fig_title)
        # draw graph
        nx.draw(self.graph, labels=self.__node_label_map(), font_color=(0,0,0), pos=self.__node_position(), node_color=self.__node_color_map(), node_size=self.__node_size_map(), edge_color=self.__edge_color_map(), with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos=self.__node_position(), edge_labels=self.__edge_labels())

    #########################
    # OTHER UTILITY METHODS #
    #########################

    """
    Generate a dictionary containing pairs
    'depth:[nodes in depth]''
    """
    def __node_depth_map(self):
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
    def relabel_nodes(self):
        # generate a relabel map based on node depth
        # and udpate their depth value
        count = 0
        node_remap = {}
        mapping = self.__node_depth_map()
        for depth in range(len(mapping)):
            depth_elems = mapping[depth]
            for node in depth_elems:
                node_remap[node] = count
                self.graph.node[node]['depth'] = depth
                count += 1
        # Fix depth of node 0
        self.graph.node[0]['depth'] = 1
        # relabel nodes
        self.graph = nx.relabel_nodes(self.graph, node_remap)
        # update end node id
        self.end_node = self.node_count - 1
        # set edge weights
        self.__set_edge_factors()

    """
    Set the edge factors based on their number
    of parent nodes
    """
    def __set_edge_factors(self):
        for n in range(self.end_node,0,-1):
            pred = self.graph.predecessors(n)
            n_pred = len(list(pred))
            for p in pred:
                self.graph.edge[p][n]['factor'] = 1/n_pred

    ###################
    # LOAD AND EXPORT #
    ###################

    """
    Export the A2SN data to a .yaml file that
    can be loaded again.
    """
    def export(self, filename = "A2SN_EXPORT.yaml"):
        nx.write_yaml(self.graph,"./exports/" + filename)

    """
    Load a previously exported YAML file.
    """
    def load(self, filename="A2SN_EXPORT.yaml"):
        # Read graph
        self.graph = nx.read_yaml("./exports/" + filename)
        # Set node node_count
        self.node_count = len(list(self.graph.nodes()))
        # Set end node id
        self.end_node = self.node_count - 1
        # update latest_state
        self.latest_state = self.graph.node[self.end_node]['state'].copy()
        # set figure title to be the action name
        self.fig_title = self.graph.node[0]['action']
        # Fix any errors
        self.relabel_nodes()

    """
    Inherit graph and data from an existing A2SN.
    """
    def inherit(self, A2SN):
        # Read graph
        self.graph = A2SN.graph
        # Set node node_count
        self.node_count = len(list(self.graph.nodes()))
        # Set end node id
        self.end_node = self.node_count - 1
        # update latest_state
        self.latest_state = self.graph.node[self.end_node]['state'].copy()
        # set figure title to be the action name
        self.fig_title = self.graph.node[0]['action']
        # Fix any errors
        self.relabel_nodes()
