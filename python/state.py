class State:
    def __init__(self, event_list):
        self.state_dict = {}
        for event in event_list:
            if event in self.state_dict.keys():
                self.state_dict[event] += 1
            else:
                self.state_dict[event] = 1

    def __eq__(self, eq_state):
        # check if object is of different type
        if (type(eq_state) != "<class 'state.State'>"):
            return False
        # compare states
        for event in eq_state.state_dict.keys():
            if event not in self.state_dict.keys():
                return False
            elif eq_state.state_dict[event] != self.state_dict[event]:
                return False
            else:
                continue
        return True

    def __iadd__(self, event):
        if event in self.state_dict.keys():
            self.state_dict[event] += 1
        else:
            self.state_dict[event] = 1
        return self

    def __add__(self, event):
        return self.__iadd__(event)

    def __sub__(self, subs_state):
        curr_keys = list(self.state_dict.keys())
        # if not substract zero, substract normally
        if len(subs_state.state_dict.keys()) != 0:
            diff = 0
            for event in list(subs_state.state_dict.keys()):
                if event not in list(self.state_dict.keys()):
                    print("Event " + str(event) + "is not in the left hand operator of the substraction.")
                    return -1
                elif subs_state.state_dict[event] > self.state_dict[event]:
                    print("Event " + str(event) + "occurs more times in the right hand operator of the substraction.")
                    return -1
                else:
                    diff = self.state_dict[event] - subs_state.state_dict[event]
                    if diff == 0:
                        del curr_keys[curr_keys.index(event)]
                        continue
                    elif diff == 1:
                        continue
                    else:
                        print("Event " + str(event) + "occurs at least two times more in the left hand operator.")
                        return -1
        # check that only one event is left
        if len(curr_keys) != 1:
            print("Substraction returned more than one element.")
            return -1
        else:
            return curr_keys[0]

    def __contains__(self, event):
        return (event in self.state_dict.keys())

    def copy(self):
        events = []
        for event in self.state_dict.keys():
            for n in range(self.state_dict[event]):
                events.append(event)
        return State(events)

    """
    Generate a the hash state as an ordered
    list of 4 digit numbers where the first
    two digits represent the event occured
    and the latter represent its number of occurrences
    """
    def hash(self):
        hashed_state = [self.state_dict[i] + int(str(i) + '00') for i in self.state_dict.keys()]
        hashed_state.sort()
        hashed_state = "x".join([str(i) for i in hashed_state])
        return hashed_state
