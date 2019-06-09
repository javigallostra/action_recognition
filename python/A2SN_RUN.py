from A2SN_BASE import *

"""
Class representing an A2SN with added functionalities:
update the node values with occurred events
"""
class A2SN_RUN(A2SN_BASE):

    """
    Call A2SN_BASE init function, load graph data from file
    (only if specified), and set variables needed for running
    """
    def __init__(self, filename = ""):
        # Initialize
        super(A2SN_RUN, self).__init__()
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
        self.past_events = []


    """
    Update the node values with a new event during a dt
    """
    def update(self, new_event = 0, dt = 0):
        # compute elapsed ticks
        ticks = int(dt/self.tick)
        # add event to past_events list
        if new_event and (new_event not in self.past_events):
            self.past_events = [new_event] + self.past_events
        # for each tick
        for t in range(ticks):
            # update time, empty node dict to update
            self.et += self.tick
            messages = {}
            # for each active event
            for event in self.past_events:
                # check triggered edges -> add node input messages
                for e in [(e[0],e[1]) for e in self.graph.edges() if self.graph.edge[e[0]][e[1]]['trigger'] == event]:
                    if e[1] in messages:
                        messages[e[1]].append(self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'] * self.graph.edge[e[0]][e[1]]['factor'])
                    else:
                        messages[e[1]] = [self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'] * self.graph.edge[e[0]][e[1]]['factor']]
                # update node values in graph (input messages, then decay)
                for node in range(self.node_count):
                    if node in messages.keys():
                        self.graph.node[node]['value'] += sum(messages[node])
                        #################
                        # SUM OR MAX???
                        #################
                    self.graph.node[node]['value'] *= self.decay_factor
            # plot at each tick
            self.plot()
        # add remaining elapsed time
        self.et += dt%self.tick
