import random as rn
from math import factorial

"""
Class used to build master sequences and then
generate sample sequences from them
"""
class SequenceGenerator:

    """
    Initialize the masters sequence step list
    """
    def __init__(self, steps=[]):
        self.step_list = list(steps)

    """
    Add a step to the master sequence
    """
    def add_step(self, step):
        self.step_list.append(step)

    """
    Return the number of possible variations
    of the master sequence
    """
    def variations(self):
        variations = 1
        for step in self.step_list:
            if type(step).__name__ == 'list':
                variations *= factorial(len(step))
        return variations

    """
    Generate a sample sequence from
    the master sequence steps
    """
    def generate(self):
        sequence = []
        active_events = []
        te = 0
        for step in self.step_list:
            # shuffle and add/remove state
            rn.shuffle(step)
            for event, tmin, tmax in step:
                # remove concurrent steps
                for active_event in active_events:
                    if active_event - event < 10:
                        del active_event
                # update active events
                if event%10 == 0:
                    event = 0
                elif event not in active_events:
                    active_events.append(event)
                # add duration (dt)
                dt = rn.random() * (tmax - tmin) + tmin
                te += dt
                sequence.append([event, list(active_events), dt, te])
        # return
        return sequence

    """
    Empty the step list of the master sequence
    """
    def empty(self):
        self.__init__()

    """
    Return a deep copy of the SequenceGenerator object
    """
    def copy(self):
        return SequenceGenerator(self.step_list)
