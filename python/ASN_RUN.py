from ASN_BASE import *

class ASN_RUN(ASN_BASE):

    def __init__(self, filename = "ASN_EXPORT.yaml"):
        # Initialize and load graph
        super(ASN_BASE, self).__init__()
        self.load(filename)

    """
    Update the node values with new events and a dt
    """
    def update(self, events, dt):
        # generate new node values
        new_values = {}
        for event in events:
            for e in [(e[0],e[1]) for e in self.graph.edges() if self.graph.edge[e[0]][e[1]]['trigger'] == event]:
                if e[1] in new_values:
                    new_values[e[1]] += self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'] * dt
                else:
                    new_values[e[1]] = self.graph.node[e[0]]['value'] * self.graph.edge[e[0]][e[1]]['weight'] * dt
        # update node values in graph
        for node in new_values.keys():
            self.graph.node[node]['value'] = new_values[node]
