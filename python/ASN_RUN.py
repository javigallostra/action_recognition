from ASN_BASE import *

class ASN_RUN(ASN_BASE):

    def __init__(self, filename = ""):
        # Initialize
        super(ASN_BASE, self).__init__()
        # Load if specified
        if filename != "":
            self.load(filename)
        else:
            print("WARNING: creating RUN A2SN without a filename to load.")
            print("         Call load(filename), inherit(A2SN) or create the A2SN from scratch.")
        # properties
        self.decay_factor = 0.95
        self.tick = 0.1
        self.et = 0

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


    """
    Update the node values with active events during a dt
    """
    def update(self, active_events, dt):
        # compute elapsed ticks
        ticks = int(dt/self.tick)
        # for each tick
        for t in range(ticks):
            # update time, empty node dict to update
            self.et += self.tick
            messages = {}
            # for each active event
            for event in active_events:
                # check triggered edges -> add node input messages
                for e in [(e[0],e[1]) for e in self.graph.edges() if self.graph.edge[e[0]][e[1]]['trigger'] == event]:
                    if e[1] in messages:
                        messages[e[1]].append(self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'] * self.graph.edge[e[0]][e[1]]['factor'])
                    else:
                        messages[e[1]] = [self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'] * self.graph.edge[e[0]][e[1]]['factor']]
                # update node values in graph (first decay, then input messages)
                for node in range(self.node_count):
                    self.graph.node[node]['value'] *= self.decay_factor
                    if node in messages.keys():
                        self.graph.node[node]['value'] += sum(messages[node])
                        #################
                        # SUM OR MAX???
                        #################
            # plot at each tick
            self.plot()
        # add remaining elapsed time
        self.et += dt%self.tick
