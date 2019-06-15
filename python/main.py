from A2SN_BUILD import *
from A2SN_RUN import *
from kitchen_objects import *
from sequence_generator import *
import matplotlib.pyplot as plt
import random as rn
import time

import threading
import time


class PlotPoolA2SN:
    def __init__(self, pool, dt):
        self.pool = pool
        self.dt = dt
        self.nfigs = 0
        self.stop_thread = False
        self.thread_lock = threading.Lock()
        self.plot_thread = threading.Thread(target=self.__plot_loop,daemon=True)
        self.plot_thread.start()

    def __plot_init(self):
        self.nfigs = 0
        for A2SN in self.pool.values():
            self.nfigs += 1
            A2SN.plot(self.nfigs)

    def __plot_loop(self):
        plt.ion()
        self.__plot_init()
        stop = False
        t0 = time.time()
        while not stop:
            for A2SN in self.pool.values():
                A2SN.plot()
            plt.show()
            plt.pause(0.0001)
            dt = time.time() - t0
            if (self.dt - dt) > 0:
                time.sleep(self.dt - dt)
            self.thread_lock.acquire()
            if self.stop_thread:
                stop = True
            self.thread_lock.release()
            t0 = time.time()
        plt.ioff()
        plt.show()
        plt.close('all')

    """
    Stop the plot thread and remove all figures
    """
    def stop(self):
        self.thread_lock.acquire()
        self.stop_thread = True
        self.thread_lock.release()
        self.plot_thread.join()

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
plotter = PlotPoolA2SN(A2SN_pool,0.1)
for i in range(10):
    # 1 - generate sequence
    action = rn.choice(list(MasterSequences.keys()))
    sequence_generator = rn.choice(MasterSequences[action])
    seq = sequence_generator.generate()
    # 2 - start A2SNs
    for A2SN in A2SN_pool.values():
        if i == 0:
            A2SN.start()
        else:
            A2SN.restart()
    # 3 - run sequence
    print(action)
    ti = time.time()
    found = False
    timefound = 0
    tottime = 0
    for new_event, all_events, dt, te in seq:
        print("******************************** " + str(new_event))
        for A2SN in A2SN_pool.values():
            A2SN.update_events(all_events)

        maxvals = [(A2SN.graph.node[0]['action'], A2SN.max_value) for A2SN in A2SN_pool.values()]
        relvals =[(maxvals[i][0], [(maxvals[i][1] - maxvals[j][1]) >  maxvals[j][1] for j in range(len(maxvals)) if j != i]) for i in range(len(maxvals))]
        th = 10
        tottime += dt
        if not found:
            for i in range(len(maxvals)):
                if maxvals[i][1] > th:
                    superior = True
                    for j in relvals[i][0]:
                        if not j:
                            superior = False
                    if superior:
                        found = True
                        timefound = te
                        val = maxvals[i][1]
                        mval = max([maxvals[k][1] for k in range(len(maxvals)) if k != i])
                        print("DETECTED :" + maxvals[i][0] + " at t = " + str(timefound) + " conf: " + str(val/mval))
                        print(val)
                        print(mval)
                        print(maxvals)
                        break

        timeel = time.time() - ti
        if (dt - timeel) > 0:
            time.sleep(dt - timeel)

        ti = time.time()

    print("EDT: " + str(timefound/tottime))

#plt.ioff()
#plt.show()

for A2SN in A2SN_pool.values():
    A2SN.stop()

while True:
    pass
