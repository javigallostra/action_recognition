import random as rn

class SequenceGenerator:

    def __init__(self):
        self.step_list = []
        self.distribution_list = []
        self.combinations = 0

    def add_step(self, step):#, distr):
        self.step_list.append(step)
        #self.distribution_list.append(distr)

    def variations(self):
        variations = 1
        for step in self.step_list:
            if type(step).__name__ == 'list':
                variations *= len(step)
        return variations

    def generate(self):
        sequence = []
        dt = 0
        for step in self.step_list:
            # check for lists: events that can swap order
            if type(step).__name__ == 'list':
                # shuffle and add/remove state
                rn.shuffle(step)
                for event, tmin, tmax in step:
                    # add duration (dt)
                    dt = rn.random() * (tmax - tmin) + tmin
                    sequence.append([event, dt])
            else:
                event, tmin, tmax = step
                dt = rn.random() * (tmax - tmin) + tmin
                sequence.append([event, dt])

        # return
        return sequence
