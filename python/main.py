from ASN_BASE import *
from ASN_RUN import *
from kitchen_objects import *
from sequence_generator import *
import matplotlib.pyplot as plt
import random as rn

o = KitchenObjects()

#######################################
# Generate master sequences for actions
gen = SequenceGenerator()
MasterSequences = {}
milk_options = ["pascual","lletnostra"]
coffee_options = ["nescafe", "marcillacafe"]
cacao_options = ["nesquik", "colacao"]
sugar_options = ["acorsugar", "sugar"]
# 1 - coffee
MasterSequences["coffee"] = []
for coffee in coffee_options:
    for milk in milk_options:
        for sugar in sugar_options:
            gen.add_step([(o[coffee].PRESENT,1.5,2), (o[milk].PRESENT,1.5,2), (o["mug"].PRESENT,1.5,2), (o[sugar].PRESENT,1.5,2)])
            gen.add_step([(o[coffee].MOVING,1.5,2), (o[milk].MOVING,1.5,2), (o[sugar].MOVING,1.5,2)])
            MasterSequences["coffee"].append(gen.copy())
            gen.empty()
# 2 - cacao
MasterSequences["cacao"] = []
for milk in milk_options:
    for cacao in cacao_options:
        gen.add_step([(o[cacao].PRESENT,1.5,2), (o[milk].PRESENT,1.5,2), (o["mug"].PRESENT,1.5,2)])
        gen.add_step([(o[cacao].MOVING,1.5,2), (o[milk].MOVING,1.5,2)])
        MasterSequences["cacao"].append(gen.copy())
        gen.empty()


#######################################
# Generate A2SN_BASE for each action
# (repeat each master sequence n times)
# then convert to A2SN_RUN
n = 5
A2SN_pool = {}
for action in MasterSequences.keys():
    A2SN_pool[action] = ASN_BASE()
    for master_sequence in MasterSequences[action]:
        for i in range(n):
            sequence = master_sequence.generate()
            A2SN = ASN_BASE()
            for event, dt, past_events in sequence:
                A2SN.add_node_by_event(event)
            A2SN.end()
            A2SN_pool[action] += A2SN
    run_a2sn = ASN_RUN()
    run_a2sn.inherit(A2SN_pool[action])
    A2SN_pool[action] = run_a2sn

# Plot for visualization and for linking to figure
fig = 1
for action in A2SN_pool.keys():
    A2SN_pool[action].plot(fig)
    fig += 1

# Test the program
action = rn.choice(list(MasterSequences.keys()))
sequence_generator = rn.choice(MasterSequences[action])
seq = sequence_generator.generate()
print(action)
for event, dt, past_events in seq:
    print(event)
    for A2SN in A2SN_pool.values():
        A2SN.update(past_events, dt)
    plt.pause(0.1)

plt.ioff()
plt.show()

"""
while len(list(nx.all_simple_paths(G.graph,0,G.end_node))) < MakeCoffee.variations():
    seq = MakeCoffee.generate()
    G2 = ASN()
    for state, dt in seq:
        G2.update(state, dt)
    G2.finish_action()
    G.merge_with(G2)
"""
"""
G = ASN_BASE()
i = 0
while i<5:
    seq1 = MakeCoffee1.generate()
    seq2 = MakeCoffee2.generate()
    G2 = ASN_BASE()
    G3 = ASN_BASE()
    for event, dt, all_events in seq1:
        G2.add_node_by_event(event)
    for event, dt, all_events in seq2:
        G3.add_node_by_event(event)
    G2.end()
    G3.end()
    G += G2
    G += G3
    i+=1

G2.plot()
plt.ioff()
plt.show()
G2 += G2
G2.plot()
plt.ioff()
plt.show()



G.plot()
plt.ioff()
plt.show()

G.export()

G2 = ASN_RUN()

plt.ion()
plt.figure(1)
G2.plot(1)

seq = MakeCoffee1.generate()
for event, dt, past_events in seq:
    print(event)
    G2.update(past_events, dt)
    plt.pause(0.1)


plt.ioff()
plt.show()
"""
