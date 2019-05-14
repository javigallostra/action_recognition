import networkx as nx
import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb
from math import sqrt
from kitchen_objects import *
from sequence_generator import *

class ASN:
    def __init__(self):
        # create graph with start and end nodes
        self.graph = nx.DiGraph()
        self.graph.add_node(0, state={}, end=False, color=[1,0,0], value=1) # start
        # keep track of latest node and node count
        self.node_count = 0
        self.end_node = -1
        # keep track of object states
        self.object_states = []

    def _add_event(self, event, parent=-1):
        if parent == -1:
            parent = self.node_count
        # generate node state by adding the event
        new_state = self.graph.node[parent]['state'].copy()
        if event in new_state:
            new_state[event] += 1
        else:
            new_state[event] = 1
        # add node to graph
        self.node_count += 1
        self.graph.add_node(self.node_count, state=new_state, end=False, value=0)
        # add edge to graph
        self.graph.add_edge(parent, self.node_count, weight=1, trigger=event, activation_value=0.5)

    def _remove_event(self, event):
        state_index = self.object_states.index(event + 1)
        if state_index >= 0:
            del self.object_states[state_index]
        else:
            print("WARNING: Trying to remove a non existing state.")

    def finish_action(self):
        self.graph.node[self.node_count]['end'] = True
        self.end_node = self.node_count

    def plot(self):
        plt.plot()
        graph_pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos=graph_pos, node_color=self._node_color_map(), edge_color=self._edge_color_map(), font_color=[1,1,1], with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, graph_pos, edge_labels=self._edge_labels())
        plt.show()

    def _edge_color_map(self):
        # colorize the graph edges
        # 1. find the edge with highest weight
        # 2. colorize all edges with saturation = weight/max_weight
        max_w = 0
        for ni, nf, weight in self.graph.edges(data='weight'):
            if weight > max_w:
                max_w = weight
        for ni, nf, weight in self.graph.edges(data='weight'):
            c = 1- weight/max_w
            rgb = (c, c, c)
            self.graph.edge[ni][nf]['color'] = rgb
        cmap = [self.graph.edge[edge[0]][edge[1]]['color'] for edge in self.graph.edges()]
        return cmap

    def _node_color_map(self):
        # colorize the graph nodes
        # 1. start at pure green
        # 2. equally traverse all the (hue/value) until (green',0)
        for n in range(1, self.node_count + 1):
            h = (1/3) + 0.5*(1 - n/self.node_count)
            s = 1
            v = sqrt(sqrt(n/self.node_count))
            rgb = hsv_to_rgb(h,s,v)
            self.graph.node[n]['color'] = rgb
        # generate a color map for plotting
        cmap = [self.graph.node[i]['color'] for i in self.graph.nodes()]
        cmap[self.end_node] = self.graph.node[0]['color']
        return cmap

    def _edge_labels(self):
        labels = {}
        for edge in self.graph.edges():
            labels[edge] = self.graph.edge[edge[0]][edge[1]]['trigger']
        return labels

    def merge_with(self, ASN2):
        my_states = [self.graph.node[n]['state'] for n in range(self.node_count + 1)]
        my_hashed_states = [self._state_hash(i) for i in my_states]
        latest_node = 0
        # merge all nodes except last one
        for n in range(1, ASN2.node_count + 1):
            node_state = ASN2.graph.node[n]['state']
            if self._state_hash(node_state) in my_hashed_states:
                node_asn1 = my_states.index(node_state)
                edge = (latest_node, node_asn1)
                if edge in self.graph.edges():
                    self.graph.edge[edge[0]][edge[1]]['weight'] += 1
                else:
                    event = ASN2.graph.edge[n-1][n]['trigger']
                    self.graph.add_edge(latest_node, node_asn1, weight=1, trigger=event, activation_value=0.5)
                latest_node = node_asn1
            else:
                event = ASN2.graph.edge[n-1][n]['trigger']
                # check for latest node
                if n == ASN2.node_count:
                    self.graph.add_edge(latest_node, self.end_node, weight=1, trigger=event, activation_value=0.5)
                else:
                    self._add_event(event, latest_node)
                    latest_node = self.node_count

    def _state_hash(self, state):
        hashed_state = [state[i] + int(str(i) + '00') for i in state.keys()]
        hashed_state.sort()
        return hashed_state

    def update(self, world_state, dt):
        add_values = {}
        curr_edges = list(self.graph.edges(data='trigger'))
        for ni, nf, t in curr_edges:
            # update activation values and shit
            edge = (ni, nf)
            if edge in curr_edges:
                alpha = self.graph.edge[edge[0]][edge[1]]['activation_value']
                w = self.graph.edge[edge[0]][edge[1]]['weight']
                if t in self.object_states and self.graph.node[ni]['value'] >= alpha:
                    add_values[nf] = self.graph.node[ni]['value'] * w * dt
        for node in add_values.keys():
            self.graph.node[node]['value'] += add_values[node]
                
        previous_states = self.object_states.copy()
        # update states: add new states (and new nodes)
        # supposedly only one new state can be added per change
        for object_state in world_state:
            if object_state not in previous_states:
                self._add_event(object_state)
                self.object_states.append(object_state)
            else:
                del previous_states[previous_states.index(object_state)]
        # the remaining previous states are no longer valid
        for old_state in previous_states:
            del self.object_states[self.object_states.index(old_state)]

    def reorder(self):
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
            for elem in depth_elems:
                node_count += 1
                node_remap[elem] = node_count
        print(node_remap)
        self.graph = nx.relabel_nodes(self.graph, node_remap)
        self.end_node = node_count
        
        
            

o = Objects()

MakeCoffee = SequenceGenerator()
MakeCoffee.add_step([(o["LECHE"].PRESENT,0.5,1), (o["CAFE"].PRESENT,0.5,1), (o["TAZA"].PRESENT,0.5,1)])
MakeCoffee.add_step([(o["LECHE"].MOVING,0.5,1), (o["CAFE"].MOVING,0.5,1)])
MakeCoffee.add_step([(o["LECHE"].AWAY,1.5,2), (o["CAFE"].AWAY,1.5,2)])
MakeCoffee.add_step((o["TAZA"].MOVING,3.5,4))

G = ASN()
G.plot()
seq = MakeCoffee.generate()
for state, dt in seq:
    G.update(state, dt)
G.finish_action()
G.plot()

"""
while len(list(nx.all_simple_paths(G.graph,0,G.end_node))) < MakeCoffee.variations():
    seq = MakeCoffee.generate()
    G2 = ASN()
    for state, dt in seq:
        G2.update(state, dt)
    G2.finish_action()
    G.merge_with(G2)
"""
i = 0
while i<100:
    seq = MakeCoffee.generate()
    G2 = ASN()
    for state, dt in seq:
        G2.update(state, dt)
    G2.finish_action()
    G.merge_with(G2)
    i+=1
G.plot()

G.reorder()

G.plot()

