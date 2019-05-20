from ASN import *
from kitchen_objects import *
from sequence_generator import *

o = Objects()

MakeCoffee = SequenceGenerator()
MakeCoffee.add_step([(o["LECHE"].PRESENT,0.5,1), (o["CAFE"].PRESENT,0.5,1), (o["TAZA"].PRESENT,0.5,1)])
#MakeCoffee.add_step((o["TAZA"].MOVING,3.5,4))
MakeCoffee.add_step([(o["LECHE"].MOVING,0.5,1), (o["CAFE"].MOVING,0.5,1)])
#MakeCoffee.add_step((o["TAZA"].MOVING,3.5,4))
MakeCoffee.add_step([(o["LECHE"].AWAY,1.5,2), (o["CAFE"].AWAY,1.5,2)])
#MakeCoffee.add_step((o["TAZA"].MOVING,3.5,4))
MakeCoffee.add_step((o["TAZA"].PRESENT,3.5,4))

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
while i<100:
    seq = MakeCoffee.generate()
    G2 = ASN_BASE()
    for event, dt in seq:
        G2.add_node_by_event(event)
    G2.end()
    G += G2
    i+=1
G.plot()
