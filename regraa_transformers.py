from regraa_reactive_base import *
import regraa_constants
import random

class add(abstract_event_modifier):
    def __init__(self, param, increment, destructive=False):
        abstract_event_modifier.__init__(self, destructive=destructive)
        self.increment = increment
        self.param = param
    def modify_event(self, event):
        # special case: pitch/freq duality ...
        if self.param is "pitch":
            if hasattr(event, "pitch"):
                event.set_pitch(event.pitch + self.increment)
            elif hasattr(event, "freq"):
                event.freq = event.freq + self.increment
        else:
            if hasattr(event, self.param):
                setattr(event, self.param, getattr(event, self.param) + self.increment)             
        return event

class brownian(abstract_event_modifier):
    def __init__(self, param, increment, destructive=False):
        abstract_event_modifier.__init__(self, destructive=destructive)        
        self.increment = increment
        self.param = param
        self.value = None
    def modify_event(self, event):
        # in case of first arriving event or destructive modification
        if (self.value is None and not self.destructive) or self.destructive :
            self.value = getattr(event, self.param)        
        # special case: pitch/freq duality ...
        self.value =  self.value + random.choice([self.increment, -self.increment])        
        if self.param is "pitch":
            if hasattr(event, "pitch"):
                event.set_pitch(self.value)
            elif hasattr(event, "freq"):
                event.freq = self.value
        else:
            if hasattr(event, self.param):
                setattr(event, self.param, self.value)             
        return event
    
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
        
def just_map(event_modifier, transition_modifier=None, id=None):
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
        self.update(event_modifier, transition_modifier)
    def update(self, event_modifier, transition_modifier):
        self.event_modifier = event_modifier
        self.transition_modifier = transition_modifier
        return self
    def on_event(self, event):
        return self.event_modifier.apply_to(event)
    def on_transition(self, transition):
        if self.transition_modifier is not None:
            return self.transition_modifier.apply_to(transition)
        else:
            return transition
        
"""        
class parameter_modifier(abstract_event_modifier):
    def __init__(self, *args, **kwargs):
        abstract_event_modifier.__init__(self, destructive=kwargs.get("destructive", False))
    def modify_event(self, event):



parammod(pitch=add(0.5))
"""


    
