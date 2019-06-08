import random as rn

class SequenceGenerator:

    def __init__(self, steps=[]):
        self.step_list = list(steps)

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
        past_events = []
        dt = 0
        for step in self.step_list:
            # shuffle and add/remove state
            rn.shuffle(step)
            for event, tmin, tmax in step:
                # add duration (dt)
                dt = rn.random() * (tmax - tmin) + tmin
                sequence.append([event, dt, list(past_events)])
                if event % 10 == 0:
                    for i in reange(len(past_events)):
                        if past_events[i] - event <= 10:
                            del past_events[i]
                if event not in past_events:
                    past_events.append(event)
        # return
        return sequence

    def empty(self):
        self.__init__()

    def copy(self):
        return SequenceGenerator(self.step_list)
