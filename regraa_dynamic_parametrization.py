class dpar:
    """ parameter to be modified at runtime """
    def __init__(self, default_value):
        self.value = default_value
    def set(self, new_value):
        self.value = new_value
    def resolve(self):
        return self.value
