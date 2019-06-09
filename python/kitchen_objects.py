"""
Class to represent an object and assign a unique id to it
"""
class KitchenObject:

    id_dict = {}
    last_id = 0

    """
    Assign unique ids to the object if
    the name is not already taken
    """
    def __init__(self, object_name):
        # If object_name is already exists
        if object_name in KitchenObject.id_dict.values():
            print("""Unable to create object '%s'.\n
                    Object '%s' already exists."""
                  % (object_name, object_name))
        # If object_name_does not exist
        else:
            # Update last_id
            KitchenObject.last_id += 10
            # Add object and id to dictionary
            KitchenObject.id_dict[KitchenObject.last_id] = object_name
            # Set object values
            self.id = KitchenObject.last_id
            self.name = object_name
            self.PRESENT = self.id + 1
            self.MOVING = self.id + 2

"""
Placeholder list for the objects considered in the project
"""
class KitchenObjects:
    """
    Generate a dictionary of 'object_name':KitchenObject pairs
    """
    def __init__(self, object_names=[]):
        # Object dictionary
        self.objects = {}
        # Name list
        if len(object_names) < 1:
            object_names = ["colacao","marcillacafe","sugar",
                                "nescafe","acorsugar","pascual","nesquik",
                                "yogurt","mug","lletnostra"] # TODO:  read from file?
        # Fill dictionary
        for name in object_names:
            self.objects[name] = KitchenObject(name)

    """
    Get the KitchenObject instance corresponding to the name given
    """
    def __getitem__(self, name):
        return self.objects[name]
