from ASN_BASE import *
from ASN_RUN import *
from kitchen_objects import *
from sequence_generator import *
import matplotlib.pyplot as plt
o = Objects()

MakeCoffee1 = SequenceGenerator()
MakeCoffee1.add_step([(o["marcillacafe"].PRESENT,1.5,2), (o["lletnostra"].PRESENT,1.5,2), (o["mug"].PRESENT,1.5,2), (o["acorsugar"].PRESENT,1.5,2)])
MakeCoffee1.add_step([(o["marcillacafe"].MOVING,1.5,2), (o["lletnostra"].MOVING,1.5,2), (o["acorsugar"].MOVING,1.5,2)])

MakeCoffee2 = SequenceGenerator()
MakeCoffee2.add_step([(o["nescafe"].PRESENT,1.5,2), (o["lletnostra"].PRESENT,1.5,2), (o["mug"].PRESENT,1.5,2), (o["acorsugar"].PRESENT,1.5,2)])
MakeCoffee2.add_step([(o["nescafe"].MOVING,1.5,2), (o["lletnostra"].MOVING,1.5,2), (o["acorsugar"].MOVING,1.5,2)])

"""
while len(list(nx.all_simple_paths(G.graph,0,G.end_node))) < MakeCoffee.variations():
    seq = MakeCoffee.generate()
    G2 = ASN()
    for state, dt in seq:
        G2.update(state, dt)
    G2.finish_action()
    G.merge_with(G2)
"""
G = ASN_BASE()
i = 0
while i<50:
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
