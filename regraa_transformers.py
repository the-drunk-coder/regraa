from regraa_reactive_base import *
import regraa_constants
import random
import math

class regraa_universal_modifier(abstract_modifier):
    def __init__(self, modifier=None, param="", destructive=False):
        abstract_modifier.__init__(self, modifier=modifier, destructive=destructive)        
        self.value = None
        self.param = param    
    def modify_entity(self, entity):
        # in case of first arriving entity or destructive modification
        if (self.value is None and not self.destructive) or self.destructive :
            self.value = getattr(entity, self.param)        
        # special case: pitch/freq duality ...
        if self.param is "pitch":
            if hasattr(entity, "pitch"):
                entity.set_pitch(self.calculate_value())
            elif hasattr(entity, "freq"):
                entity.freq = self.calculate_value()
        else:
            if hasattr(entity, self.param):
                setattr(entity, self.param, self.calculate_value())
        return entity
    def calculate_value(self):
        raise NotImplementedError

class non(abstract_modifier):
    def apply_to(self, entity):
        return entity
    
class add(regraa_universal_modifier):
    def __init__(self, param, increment, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment        
    def calculate_value(self):        
        return self.value + self.increment

class brownian(regraa_universal_modifier):
    def __init__(self, param, increment, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment        
    def calculate_value(self):
        self.value = self.value + random.choice([self.increment, -self.increment])        
        return self.value

class sinestretch(regraa_universal_modifier):
    def __init__(self, param, cyclicity, min_bound, max_bound, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.cyclicity = cyclicity
        self.min_bound = min_bound
        self.max_bound = max_bound
        self.step = 0
        self.degree_increment = 360 / self.cyclicity
    def calculate_value(self):
        degree = ((self.step % self.cyclicity) * self.degree_increment) % 360
        abs_sin = abs(math.sin(math.radians(degree)))
        stretch_range = self.max_bound - self.min_bound
        self.value = (abs_sin * stretch_range) + self.min_bound        
        return self.value
    
class wrap(regraa_universal_modifier):
    def __init__(self, modifier, lower, upper, destructive=False):
        regraa_universal_modifier.__init__(self,param=modifier.param, modifier=modifier, destructive=destructive)
        self.lower = lower
        self.upper = upper
    def calculate_value(self):
        print(self.value)
        if self.value < self.lower:
            return self.upper
        elif self.value > self.upper:
            return self.lower
        else:
            return self.value
        

regraa_transformers = {}
        
def just_map(event_modifier, transition_modifier, id=None):
    """ Map single event modifier to stream. """
    if id is not None and id in regraa_transformers:
        current_object = regraa_transformers[id].update(event_modifier, transition_modifier)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _just_map(event_modifier, transition_modifier)
        regraa_transformers[id] = new_obj
        return new_obj

        
class _just_map(abstract_observer):
    def __init__(self, event_modifier, transition_modifier):
        abstract_observer.__init__(self)
        self.step = 0
        self.update(event_modifier, transition_modifier)
    def update(self, event_modifier, transition_modifier):
        self.event_modifier = event_modifier
        self.transition_modifier = transition_modifier
        return self
    def on_event(self, event):
        if hasattr(self.event_modifier, "step"):
            self.event_modifier.step = self.step
        self.step += 1
        return self.event_modifier.apply_to(event)
    def on_transition(self, transition):
        if self.transition_modifier is not None:
            if hasattr(self.transition_modifier, "step"):
                self.transition_modifier.step = self.step
            return self.transition_modifier.apply_to(transition)
        else:
            return transition
        

    
