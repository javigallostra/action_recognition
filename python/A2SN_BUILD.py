from A2SN_BASE import *

"""
Class representing an A2SN with added functionalities:
functions to build the graph from scracth by adding events
"""
class A2SN_BUILD(A2SN_BASE):

    """
    Call A2SN_BASE init function
    """
    def __init__(self):
        # Initialize
        super(A2SN_BUILD, self).__init__()

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
            self.graph.add_node(self.node_count, state=new_state.copy(), end=False, color=(0,0,0), value=0.0)
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
