from A2SN_BASE import *
import threading
import time

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
        self.ti = 0
        self.active_events = []
        self.update_thread = 0
        self.stop_thread = False
        self.thread_lock = threading.Lock()

    """
    Update the active events with a new world input
    """
    def update_events(self, events = []):
        self.update_events_thread = threading.Thread(target=self.__update_events,args=(events,),daemon=True)
        self.update_events_thread.start()

    """
    Update events thread
    """
    def __update_events(self, events = []):
        self.thread_lock.acquire()
        self.active_events = list(events)
        self.thread_lock.release()

    """
    Start the updating loop at each clock tick
    """
    def start(self):
        self.update_thread = threading.Thread(target=self.__update_loop,daemon=True)
        self.ti = time.time()
        self.update_thread.start()

    """
    Stop the updating thread
    """
    def stop(self):
        self.stop_thread = True

    """
    Thread function that updates the node values
    at each clock tick
    """
    def __update_loop(self):
        # While not stop
        while(not self.stop_thread):
            # update graph values and time it
            ti = time.time()
            self.thread_lock.acquire()
            self.__update()
            self.thread_lock.release()
            dt = time.time() - ti
            # check that dt < clock tick and wait/continue
            if (dt > self.tick):
                continue
            else:
                time.sleep(self.tick - dt)
                continue
    """
    Update the node values
    """
    def __update(self):
        messages = {}
        # for each active event
        for event in self.active_events:
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
