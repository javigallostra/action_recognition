from A2SN_BASE import *

"""
Class representing an A2SN with added functionalities:
functions to build the graph from scracth by adding events
"""
class A2SN_BUILD(A2SN_BASE):

    """
    Call A2SN_BASE init function
    """
    def __init__(self, action_name = ""):
        # Initialize
        super(A2SN_BUILD, self).__init__(action_name)


    """
    Merge the current graph with a different one
    (currently only works if adding a single-path graph)
    """
    def __iadd__(self, A2SN2):
        new_states = [A2SN2.graph.node[n]['state'] for n in range(1,A2SN2.end_node)]
        parent_state = State([])
        # merge all nodes (except for first and last node)
        for new_state in new_states:
            self.add_node_by_state(new_state, parent_state)
            parent_state = new_state.copy()
        # merge last node
        new_state = A2SN2.graph.node[A2SN2.end_node]['state']
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
                self.graph.add_edge(edge[0], edge[1], weight=1, factor=1, trigger=event)
        # relabel the nodes to match the new structure
        self.relabel_nodes()
        return self

    """
    Used for building the graph
    with a new event, adding a new
    node and edge from a parent state
    if needed
    """
    def add_node_by_event(self, event = 0, parent_state = 0):
        if event:
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
            self.graph.add_node(self.node_count, state=new_state.copy(), end=False, color=(0,0,0), value=0.0, depth=0)
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
    End building the graph, setting the
    latest node to be the end node
    """
    def end(self):
        self.end_node = self.node_count - 1
        self.graph.node[self.end_node]['end'] = True
        self.relabel_nodes()
