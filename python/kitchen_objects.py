

class KitchenObject:

    id_dict = {}

    def __init__(self, object_name, object_id):
        # default values
        self.id = 0
        self.name = ""
        # add object to dict if possible
        if object_id % 10 > 0:
            print("Invalid object id %d: must be a multiple of 10." % (object_id))
        elif object_id in KitchenObject.id_dict.keys():
            print("""Unable to create object '%s' with id %d.\n
                    Object '%s' the same id already exists"""
                  % (object_name, object_id, KitchenObject.id_dict[object_id]))
        else:
            KitchenObject.id_dict[object_id] = object_name
            self.id = object_id
            self.name = object_name
            self.PRESENT = self.id + 1
            self.MOVING = self.id + 2
            self.AWAY = self.id

class Objects:

    def __init__(self):
        # Name list and dictionary
        self.object_names = ["colacao","marcillacafe","sugar","nescafe","acorsugar","pascual","nesquik","yogurt","mug","lletnostra"] # TOO read from file?
        self.objects = {}
        # Fill dictionary
        self.object_id = 0
        for name in self.object_names:
            self.object_id += 10
            self.objects[name] = KitchenObject(name, self.object_id)

    def __getitem__(self, name):
        return self.objects[name]

    def __setitem__(self, object_name):
        if object_name in self.objects.keys():
            print("Object %s already exists." % (object_name))
        else:
            self.object_id += 10
            self.objects[name] = KitchenObject(object_name, self.object_id)
