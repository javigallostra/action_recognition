import random as rn

class SequenceGenerator:

    def __init__(self):
        self.step_list = []
        self.distribution_list = []
        self.combinations = 0
        self.past_events = []

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
        self.past_events = []
        dt = 0
        for step in self.step_list:
            # shuffle and add/remove state
            rn.shuffle(step)
            for event, tmin, tmax in step:
                # add duration (dt)
                dt = rn.random() * (tmax - tmin) + tmin
                self.past_events.append(event)
                sequence.append([event, dt, list(self.past_events)])

        # return
        return sequence
