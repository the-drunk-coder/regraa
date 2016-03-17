from regraa_reactive_base import *
import regraa_constants
import random
import math

class regraa_universal_modifier(abstract_event_modifier, abstract_transition_modifier):
    def __init__(self, param="", destructive=False):
        abstract_event_modifier.__init__(self, destructive=destructive)
        abstract_transition_modifier.__init__(self, destructive=destructive)
        self.value = None
        self.param = param
    def modify_event(self, event):
        return self.inner_modify(event)
    def modify_transition(self, transition):
        return self.inner_modify(transition)
    def inner_modify(self, entity):
        # in case of first arriving entity or destructive modification
        #if (self.value is None and not self.destructive) or self.destructive :
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
    
class wrap(abstract_event_modifier):
    def __init__(self, modifier, lower, upper, destructive=False):
        abstract_event_modifier.__init__(self, modifier=modifier, destructive=destructive)
        self.param = modifier.param
        self.lower = lower
        self.upper = upper
    def modify_event(self, event):
        if hasattr(event, self.param):
            current_value = getattr(event, self.param)
            if current_value > self.upper:
                print("case larger")
                current_value = self.lower
            elif current_value < self.lower:
                print("case smaller")
                current_value = self.upper
            if self.param is "pitch":
                event.set_pitch(current_value)
            else:
                setattr(event, self.param, current_value)        
        return event


regraa_transformers = {}
        
def just_map(event_modifier, tmod=None, id=None):
    """ Map single event modifier to stream. """
    if id is not None and id in regraa_transformers:
        current_object = regraa_transformers[id].update(event_modifier, tmod)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _just_map(event_modifier, tmod)
        regraa_transformers[id] = new_obj
        return new_obj

        
class _just_map(abstract_observer):
    def __init__(self, event_modifier, tmod):
        abstract_observer.__init__(self)
        self.step = 0
        self.update(event_modifier, tmod)
    def update(self, event_modifier, tmod):
        self.event_modifier = event_modifier
        self.tmod = tmod
        return self
    def on_event(self, event):
        if hasattr(self.event_modifier, "step"):
            self.event_modifier.step = self.step
        self.step += 1
        return self.event_modifier.apply_to(event)
    def on_transition(self, transition):
        if self.tmod is not None:
            if hasattr(self.tmod, "step"):
                self.tmod.step = self.step
            return self.tmod.apply_to(transition)
        else:
            return transition
        

    
