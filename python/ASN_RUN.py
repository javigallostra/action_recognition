from ASN_BASE import *

class ASN_RUN(ASN_BASE):

    def __init__(self, filename = "ASN_EXPORT.yaml"):
        # Initialize and load graph
        super(ASN_BASE, self).__init__()
        self.load(filename)
        # properties
        self.decay_factor = 0.95
        self.tick = 0.1

    """
    Update the node values with new events and a dt
    """
    def update(self, event, dt):
        # generate new node values
        add_values = {}
        ticks = int(dt/self.tick)
        for t in range(ticks):
            for e in [(e[0],e[1]) for e in self.graph.edges() if self.graph.edge[e[0]][e[1]]['trigger'] == event]:
                if e[1] in add_values:
                    add_values[e[1]].append(self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'])
                else:
                    add_values[e[1]] = [self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight']]
            # update node values in graph (first decay, then input values)
            for node in range(self.node_count):
                self.graph.node[node]['value'] *= self.decay_factor
                if node in add_values.keys():
                    self.graph.node[node]['value'] += max(add_values[node])
            self.plot()
