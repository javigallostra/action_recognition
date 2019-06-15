from A2SN_BUILD import *
from A2SN_RUN import *
from kitchen_objects import *
from sequence_generator import *
import random as rn
import time
import matplotlib.pyplot as plt
import threading
import time


class PlotPoolA2SN:
    def __init__(self, pool, tick):
        self.pool = pool
        self.tick = tick
        self.nfigs = 0
        self.stop_loop = False

    def __plot_init(self):
        plt.ion()
        self.nfigs = 0
        for A2SN in self.pool.values():
            self.nfigs += 1
            A2SN.plot(self.nfigs)

    def __plot_end(self):
        plt.ioff()
        plt.show()
        plt.close('all')

    def __plot_update(self):
        for A2SN in self.pool.values():
            A2SN.plot()
        plt.show()
        plt.pause(0.0001)

    def plot_loop(self):
        self.stop_loop = False
        self.__plot_init()
        t0 = time.time()
        while not self.stop_loop:
            self.__plot_update()
            dt = time.time() - t0
            if (self.tick - dt) > 0:
                time.sleep(self.tick - dt)
            else:
                print("WARNING - plot loop slower than desired rate: " + str(dt))
            t0 = time.time()
        self.__plot_end()

    """
    Stop the plot loop and remove all figures
    """
    def stop(self):
        self.stop_loop = True

class RunPoolA2SN:
    def __init__(self, pool, tick):
        self.pool = pool
        self.tick = tick
        self.detected = False
        self.stop_update = False
        self.update_thread = 0
        self.thread_lock = threading.Lock()
        self.ti = 0

    def __update_loop(self):
        while not self.__check_stop():
            # update graph values
            for A2SN in self.pool.values():
                A2SN.update()
            # check action recognition
            self.__check_detection()
            dt = time.time() - self.ti
            # check that dt < clock tick and wait/continue
            if (self.tick - dt) > 0:
                time.sleep(self.tick - dt)
            else:
                print("WARNING - update loop slower than desired rate: " + str(dt))
            # time it
            self.ti = time.time()

    def __check_stop(self):
        # thread safe loop ending check
        self.thread_lock.acquire()
        check = self.stop_update
        self.thread_lock.release()
        return check

    def __check_detection(self):
        if not self.detected:
            maxvals = [(A2SN.graph.node[0]['action'], A2SN.max_value) for A2SN in self.pool.values()]
            relvals =[(maxvals[i][0], [(maxvals[i][1] - maxvals[j][1]) >  maxvals[j][1] for j in range(len(maxvals)) if j != i]) for i in range(len(maxvals))]
            th = 10
            for i in range(len(maxvals)):
                if maxvals[i][1] > th:
                    superior = True
                    for j in relvals[i][0]:
                        if not j:
                            superior = False
                    if superior:
                        val = maxvals[i][1]
                        mval = max([maxvals[k][1] for k in range(len(maxvals)) if k != i])
                        self.detected = True
                        print("DETECTED :" + maxvals[i][0] + " at t = " + str(0) + " conf: " + str(val/mval))
                        break

    def stop_update_loop(self):
        self.thread_lock.acquire()
        self.stop_update = True
        self.thread_lock.release()
        self.update_thread.join()

    def start_update_loop(self):
        self.detected = False
        for A2SN in self.pool.values():
            A2SN.reset()
        self.update_thread = threading.Thread(target=self.__update_loop,daemon=True)
        self.ti = time.time()
        self.update_thread.start()

    def restart_update_loop(self):
        self.stop_update_loop()
        self.start_update_loop()


o = KitchenObjects()

#######################################
# Generate master sequences for actions
gen = SequenceGenerator()
MasterSequences = {}
milk_options = ["pascual"]#,"lletnostra"]
coffee_options = ["nescafe"]
cacao_options = ["nesquik"]
sugar_options = ["sugar"]
cereal_options = ["acorsugar"]#, "marcillacafe"]
yogurt_options = ["yogurt"]
chocolate_options = ["colacao"]
mug_options = ["mug"]
# 1 - coffee
MasterSequences["coffee"] = []
for coffee in coffee_options:
    for milk in milk_options:
        for sugar in sugar_options:
            for mug in mug_options:
                gen.add_step([(o[coffee].PRESENT,1.5,2), (o[milk].PRESENT,1.5,2), (o[mug].PRESENT,1.5,2), (o[sugar].PRESENT,1.5,2)])
                gen.add_step([(o[coffee].MOVING,1.5,2), (o[milk].MOVING,1.5,2), (o[sugar].MOVING,1.5,2)])
                MasterSequences["coffee"].append(gen.copy())
                gen.empty()
# 2 - cacao
MasterSequences["cacao"] = []
for milk in milk_options:
    for cacao in cacao_options:
        for mug in mug_options:
            gen.add_step([(o[cacao].PRESENT,1.5,2), (o[milk].PRESENT,1.5,2), (o[mug].PRESENT,1.5,2)])
            gen.add_step([(o[cacao].MOVING,1.5,2), (o[milk].MOVING,1.5,2)])
            MasterSequences["cacao"].append(gen.copy())
            gen.empty()

# 3 - cereals
MasterSequences["cereals"] = []
for milk in milk_options:
    for cacao in cacao_options:
        for cereals in cereal_options:
            for mug in mug_options:
                gen.add_step([(o[cereals].PRESENT,1.5,2), (o[milk].PRESENT,1.5,2), (o[mug].PRESENT,1.5,2)])
                gen.add_step([(o[cereals].MOVING,1.5,2), (o[milk].MOVING,1.5,2)])
                MasterSequences["cereals"].append(gen.copy())
                gen.empty()


#######################################
# Generate A2SN_BASE for each action
# (repeat each master sequence n times)
# then save the generated A2SN
A2SN_pool = {}
n = 1
for action in MasterSequences.keys():
    A2SN_pool[action] = A2SN_BUILD(action)
    for master_sequence in MasterSequences[action]:
        for i in range(n):
            sequence = master_sequence.generate()
            A2SN = A2SN_BUILD()
            for new_event, all_events, dt, te in sequence:
                A2SN.add_node_by_event(new_event)
            A2SN.end()
            A2SN_pool[action] += A2SN
    A2SN_pool[action].export(action + ".yaml")

#####################################################
# Load the prevously saved A2SN into A2SN_RUN objects
A2SN_pool = {}
for action in MasterSequences.keys():
    A2SN_pool[action]  = A2SN_RUN()
    A2SN_pool[action].load(action + ".yaml")

##################
# Test the program
plotter = PlotPoolA2SN(A2SN_pool,0.5)
updater = RunPoolA2SN(A2SN_pool, 0.2)
#sequenceSim = SequenceSimulator(A2SN_pool, MasterSequences)

updater.start_update_loop()
for A2SN in A2SN_pool.values():
    A2SN.update_events([11])
plotter.plot_loop()

"""
for i in range(1):
    # 1 - generate sequence
    action = rn.choice(list(MasterSequences.keys()))
    sequence_generator = rn.choice(MasterSequences[action])
    seq = sequence_generator.generate()
    # 2 - run sequence
    print(action)
    ti = time.time()
    for new_event, all_events, dt, te in seq:
        print("******************************** " + str(new_event))
        for A2SN in A2SN_pool.values():
            A2SN.update_events(all_events)
        timeel = time.time() - ti
        if (dt - timeel) > 0:
            time.sleep(dt - timeel)
        ti = time.time()
"""
