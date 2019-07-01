from A2SN_BUILD import *
from A2SN_RUN import *
from kitchen_objects import *
from sequence_generator import *
import random as rn
import time
import matplotlib.pyplot as plt
import threading
import time
import math

from numpy import arange

# disable warnings
import sys
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

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
                if self.verbose: print("WARNING - plot loop slower than desired rate: " + str(dt))
                pass
            t0 = time.time()
        self.__plot_end()

    """
    Stop the plot loop and remove all figures
    """
    def stop(self):
        self.stop_loop = True

class RunPoolA2SN:
    def __init__(self, pool, tick, verbose = False):
        self.pool = pool
        self.tick = tick
        self.verbose = verbose
        self.detected = False
        self.stop_update = False
        self.update_thread = 0
        self.thread_lock = threading.Lock()
        self.ti = 0

    def __update_loop(self):
        self.ti = time.time()
        t0 = time.time()
        while not self.__check_stop():
            # update graph values
            for A2SN in self.pool.values():
                A2SN.update()
            # check action recognition
            self.__check_detection()
            dt = time.time() - t0
            # check that dt < clock tick and wait/continue
            if (self.tick - dt) > 0:
                time.sleep(self.tick - dt)
            else:
                if self.verbose: print("WARNING - update loop slower than desired rate: " + str(dt))
                pass
            # time it
            t0 = time.time()

    def __check_detection(self):
        te = time.time()-self.ti
        maxvals = [(A2SN.graph.node[0]['action'], A2SN.max_value) for A2SN in self.pool.values()]
        th0 = 3
        if self.verbose: print(str(te)+','+','.join([','.join([info[0],str(info[1])]) for info in maxvals]))
        if not self.detected:
            relvals =[(maxvals[i][0], [(maxvals[i][1] - maxvals[j][1]) >  maxvals[j][1]*th0 for j in range(len(maxvals)) if j != i]) for i in range(len(maxvals))]
            th = 10
            for i in range(len(maxvals)):
                if maxvals[i][1] > th:
                    superior = True
                    for j in relvals[i][1]:
                        if not j:
                            superior = False
                    if superior:
                        val = maxvals[i][1]
                        mval = max([maxvals[k][1] for k in range(len(maxvals)) if k != i])
                        self.detected = True
                        if self.verbose: print("DETECTED :" + maxvals[i][0] + " at t = " + str(te) + " conf: " + str(val/mval))
                        break

    def stop_update_loop(self):
        self.thread_lock.acquire()
        self.stop_update = True
        self.thread_lock.release()
        self.update_thread.join()

    def __check_stop(self):
        # thread safe loop ending check
        self.thread_lock.acquire()
        check = self.stop_update
        self.thread_lock.release()
        return check

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



class SequenceSimulator:
    def __init__(self, master_sequences, pool, verbose = False):
        self.master_sequences = master_sequences
        self.pool = pool
        self.verbose = verbose
        self.sequence = 0
        self.run_thread = 0
        self.t0 = 0
        self.stop_run = False
        self.thread_lock = threading.Lock()

    def run_random_sequence(self):
        action = rn.choice(list(MasterSequences.keys()))
        generator = rn.choice(MasterSequences[action])
        self.sequence = generator.generate()
        self.stop_run = False
        self.run_thread = threading.Thread(target=self.__run_sequence,daemon=True)
        self.t0 = time.time()
        if self.verbose: print("Start simulation of action: " + str(action).upper())
        self.run_thread.start()

    def __run_sequence(self):
        ti = time.time()
        for new_event, all_events, dt, te in self.sequence:
            if self.verbose: print("NEW EVENT " + str(new_event))
            for A2SN in self.pool.values():
                A2SN.update_events(all_events)
            tel = time.time() - ti
            if (dt - tel) > 0:
                time.sleep(dt - tel)
            ti = time.time()
            if self.__check_stop():
                return
        if self.verbose: print("Sequence finished.")

    def stop_run(self):
        self.thread_lock.acquire()
        self.stop_run = True
        self.thread_lock.release()
        self.run_thread.join()

    def __check_stop(self):
        # thread safe loop ending check
        self.thread_lock.acquire()
        check = self.stop_run
        self.thread_lock.release()
        return check



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
                gen.add_step([(o[coffee].PRESENT,0,0), (o[milk].PRESENT,5,7), (o[mug].PRESENT,5,7), (o[sugar].PRESENT,5,7)])
                gen.add_step([(o[coffee].MOVING,10,15), (o[milk].MOVING,10,15), (o[sugar].MOVING,10,15)])
                MasterSequences["coffee"].append(gen.copy())
                gen.empty()
# 2 - cacao
MasterSequences["cacao"] = []
for milk in milk_options:
    for cacao in cacao_options:
        for mug in mug_options:
            gen.add_step([(o[cacao].PRESENT,0,0), (o[milk].PRESENT,5,7), (o[mug].PRESENT,7,7)])
            gen.add_step([(o[cacao].MOVING,10,15), (o[milk].MOVING,10,15)])
            MasterSequences["cacao"].append(gen.copy())
            gen.empty()

# 3 - cereals
MasterSequences["cereals"] = []
for milk in milk_options:
    for cacao in cacao_options:
        for cereals in cereal_options:
            for mug in mug_options:
                gen.add_step([(o[cereals].PRESENT,0,0), (o[milk].PRESENT,5,7), (o[mug].PRESENT,5,7)])
                gen.add_step([(o[cereals].MOVING,10,15), (o[milk].MOVING,10,15)])
                MasterSequences["cereals"].append(gen.copy())
                gen.empty()


#######################################
# Generate A2SN_BASE for each action
# (repeat each master sequence n times)
# then save the generated A2SN
A2SN_pool = {}
n = 5
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

########################
# Test the program in RT

# plotter = PlotPoolA2SN(A2SN_pool,1.0)
# updater = RunPoolA2SN(A2SN_pool, 0.5, True)
# sequenceSim = SequenceSimulator(MasterSequences, A2SN_pool)
#
# updater.start_update_loop()
# sequenceSim.run_random_sequence()
# plotter.plot_loop()


#######################
# Test the program fast

def check_detection(a2sn_pool, alpha, beta):
    maxvals = [(A2SN.graph.node[0]['action'], A2SN.max_value) for A2SN in a2sn_pool.values()]
    relvals =[(maxvals[i][0], [(maxvals[i][1] - maxvals[j][1])/maxvals[j][1] > alfa if ((j != i) and (maxvals[j][1] > 0)) else False for j in range(len(maxvals))]) if (maxvals[i][1] > 0) else (0,False) for i in range(len(maxvals))]
    for i in range(len(maxvals)):
        if maxvals[i][1] > beta:
            superior = True
            for j in relvals[i][0]:
                if not j:
                    superior = False
            if superior:
                val = maxvals[i][1]
                mval = max([maxvals[k][1] for k in range(len(maxvals)) if k != i])
                return ([maxvals[i][0], val/mval])
    return 0

unrecog_perc = 5
alfa = 5
beta = 10
i = 0
while i < 1:
    i += 1
    #generate confmat
    cmat = {}
    occurr = {}
    for action in list(A2SN_pool.keys()):
        cmat[action] = {}
        occurr[action] = 0
        for action2 in list(A2SN_pool.keys()):
            cmat[action][action2] = 0
    tests = 50
    update_tick = 0.35
    tot_corr = 0
    corr_edt = 0
    corr_conf = 0
    undet = 0
    for i in range(tests):
        action = rn.choice(list(MasterSequences.keys()))
        #print("ACTION: " + action)
        m_seq = rn.choice(MasterSequences[action])
        seq = m_seq.generate()
        dt = 0
        step = 0
        tot_t = seq[-1][-1]
        det = 0
        for A2SN in A2SN_pool.values():
            A2SN.reset()
        while dt < tot_t:
            dt += update_tick
            if dt >= seq[step][-1]:
                for A2SN in A2SN_pool.values():
                    A2SN.update_events(seq[step][1])
                step += 1
            for A2SN in A2SN_pool.values():
                A2SN.update()
            det = check_detection(A2SN_pool, alfa, beta)
            if det != 0:
                print("DETECTED :" + det[0] + " at t = " + str(dt) + " conf: " + str(det[1]) + " edt: " + str(100*dt/tot_t))
                cmat[action][det[0]] += 1
                occurr[action] += 1
                if (action == det[0]):
                    tot_corr += 1
                    corr_edt += dt/tot_t
                    corr_conf += det[1]
                break
        if det == 0:
            undet += 1

    for action in list(A2SN_pool.keys()):
        for action2 in list(cmat[action].keys()):
            cmat[action][action2] /= occurr[action]

    print(sum([A2SN.node_count for A2SN in A2SN_pool.values()]))

    print("CMAT")
    print(cmat)

    print("AVG UNDET")
    print(100*undet/tests)

    print("AVG CORR")
    print(100*tot_corr/tests)

    print("AVG FALSE")
    print(100*(tests - tot_corr - undet)/tests)

    print("AVG EDT")
    print(100*corr_edt/tot_corr)

    print("AVG CONF")
    print(corr_conf/tot_corr)

    print("ALPHA")
    print(alfa)

    print("BETA")
    print(beta)

    #if (100*undet/tests) > unrecog_perc:
    #    beta *= 0.95
    #    alfa *= 0.95
    #else:
    #    alfa *= math.exp(corr_conf/tot_corr)



############
# ROC
#for alfa in [x/10 for x in range(10,201)]:
#    for beta in [x/10 for x in range(10,201)]:
"""
for alfa in [x for x in arange(0,100,1)]:
    for beta in [x for x in arange(0,100,1)]:
        # generate confmat
        cmat = {}
        occurr = {}
        for action in list(A2SN_pool.keys()):
            cmat[action] = {}
            occurr[action] = 0
            for action2 in list(A2SN_pool.keys()):
                cmat[action][action2] = 0
        tests = 100
        update_tick = 0.35
        tot_corr = 0
        corr_edt = 0
        corr_conf = 0
        undet = 0
        for i in range(tests):
            action = rn.choice(list(MasterSequences.keys()))
            #print("ACTION: " + action)
            m_seq = rn.choice(MasterSequences[action])
            seq = m_seq.generate()
            dt = 0
            step = 0
            tot_t = seq[-1][-1]
            det = 0
            for A2SN in A2SN_pool.values():
                A2SN.reset()
            while dt < tot_t:
                dt += update_tick
                if dt >= seq[step][-1]:
                    for A2SN in A2SN_pool.values():
                        A2SN.update_events(seq[step][1])
                    step += 1
                for A2SN in A2SN_pool.values():
                    A2SN.update()
                det = check_detection(A2SN_pool, alfa, beta)
                if det != 0:
                    #print("DETECTED :" + det[0] + " at t = " + str(dt) + " conf: " + str(det[1]) + " edt: " + str(100*dt/tot_t))
                    cmat[action][det[0]] += 1
                    occurr[action] += 1
                    if (action == det[0]):
                        tot_corr += 1
                        corr_edt += dt/tot_t
                        corr_conf += det[1]
                    break
            if det == 0:
                undet += 1

        #for action in list(A2SN_pool.keys()):
        #    for action2 in list(cmat[action].keys()):
        #        cmat[action][action2] /= occurr[action]
        doable = True
        stat_data = []
        for action in list(cmat.keys()):
            TP = 0
            FN = 0
            FP = 0
            TN = 0
            for act1 in list(cmat.keys()):
                for act2 in list(cmat[act1].keys()):
                    if (act1 == action):
                        if (act1 == act2):
                            TP += cmat[act1][act2]
                        else:
                            FN += cmat[act1][act2]
                    elif (act2 == action):
                        FP += cmat[act1][act2]
                    else:
                        TN += cmat[act1][act2]
            #if undet < 10: print (action, TP, FP, P,N, undet, P+N+undet)
            if (TP+FN == 0 or FP+TN == 0):
                doable = False
            else:
                stat_data.append([TP,FN,FP,TN])
        if doable:
            elements = []
            for data in stat_data:
                elements.append(data[2]/(data[2]+data[3]))
                elements.append(data[0]/(data[0]+data[1]))
            print(' '.join([str(i) for i in elements]))
            totP = sum([data[0]+data[1] for data in stat_data])
            totN = sum([data[2]+data[3] for data in stat_data])
            if (totP!=0 and totN!=0):
                microTPR = sum([data[0] for data in stat_data])/totP
                macroTPR = sum([data[0]/(data[0]+data[1]) for data in stat_data])/len(stat_data)
                microFPR = sum([data[2] for data in stat_data])/totN
                macroFPR = sum([data[2]/(data[2]+data[3]) for data in stat_data])/len(stat_data)
                #print(microFPR,microTPR,macroFPR,macroTPR)

print (cmat)
"""
