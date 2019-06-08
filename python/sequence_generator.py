import random as rn

class SequenceGenerator:

    def __init__(self):
        self.step_list = []
        self.past_events = []

    def add_step(self, step):
        self.step_list.append(step)

    def variations(self):
        variations = 1
        for step in self.step_list:
            if type(step).__name__ == 'list':
                variations *= len(step)
        return variations

    def generate(self):
        sequence = []
        self.past_event = 0
        dt = 0
        for step in self.step_list:
            # shuffle and add/remove state
            rn.shuffle(step)
            for event, tmin, tmax in step:
                # add duration (dt)
                dt = rn.random() * (tmax - tmin) + tmin
                sequence.append([event, dt, self.past_event])
                if event % 10 == 0:
                    self.past_event = 0
                else:
                    self.past_event = event

        # return
        return sequence
