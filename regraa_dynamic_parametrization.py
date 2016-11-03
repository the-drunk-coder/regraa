from math import *

class dpar:
    """ parameter to be modified at runtime """
    def __init__(self, default_value):
        self.value = default_value
        self.fade_step_curr = 0
        self.fade_steps = 0
        self.sin_inc = 0
        self.diff = 0
        self.temp_val = 0
        self.is_fading = False
    def set(self, new_value):
        self.value = new_value
    def fade(self, new_value, fade_step):
        # if already fading, actualize value
        if fade_step < 2:
            # do nothing
            return
        if self.fade_steps != 0:
            self.value = self.value - (self.diff * sin(self.sin_inc * self.fade_step_curr))
        self.sin_inc = (pi / 2) / fade_step 
        self.fade_steps = fade_step - 1
        self.fade_step_curr = 0
        self.diff = self.value - new_value
        self.is_fading = True
    def process_fade(self):
        if self.fade_step_curr < self.fade_steps:
            #print("still_fading " + str(self.fade_step_curr))
            self.temp_val = self.value - (self.diff * sin(self.sin_inc * self.fade_step_curr))
            self.fade_step_curr = self.fade_step_curr + 1
        elif self.fade_step_curr >= self.fade_steps:
            # reset
            self.fade_step_curr = 0;
            self.fade_steps = 0;
            self.sin_inc = 0;
            self.value = self.value - self.diff
            self.diff = 0
            self.is_fading = False
    # what the hack ...
    def get_value(self):         
        if self.is_fading:
            return self.temp_val
        else:
            return self.value
    def resolve(self):
        self.process_fade()
        return self.get_value()
