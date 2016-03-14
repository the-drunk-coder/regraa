from regraa_reactive_base import *
import regraa_constants

class pitch_mod(abstract_event_modifier):
    def __init__(self, increment, destructive=False):
        abstract_event_modifier.__init__(self, destructive=destructive)
        self.increment = increment
    def modify_event(self, event):
        if hasattr(event, "pitch"):
            event.set_pitch(event.pitch + self.increment)
        elif hasattr(event, "freq"):
            event.freq = event.freq + self.increment           
        return event

regraa_transformers = {}
        
def smap(id=None, event_modifier, transition_modifier=None):
    """ Map single event modifier to stream. """
    if id is not None and id in regraa_transformers:
        current_object = regraa_transformers[id].update(event_modifier, transition_modifier)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _smap(event_modifier, transition_modifier)
        regraa_transformers[id] = new_obj
        return new_obj

        
class _smap(abstract_observer):
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


    
