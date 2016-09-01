class dpar:
    """ parameter to be modified at runtime """
    def __init__(self, default_value):
        self.value = default_value
        self.fade_step_curr = 0;
        self.fade_steps = 0;
        self.fade_inc = 0;
    def set(self, new_value):
        self.value = new_value
    def fade(self, new_value, fade_step):
        self.fade_inc = (float((self.value - new_value)) / fade_step) * -1
        self.fade_steps = fade_step
    def resolve(self):
        if self.fade_step_curr < self.fade_steps:
            self.value = self.value + self.fade_inc
            self.fade_step_curr = self.fade_step_curr + 1
        elif self.fade_step_curr >= self.fade_steps:
            self.fade_step_curr = 0;
            self.fade_steps = 0;
            self.fade_inc = 0;
        return self.value
