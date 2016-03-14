from regraa_reactive_base import *
import regraa_constants

# store objects by their unique id
regraa_objects = {}

# simple, single event + transition
def just(id, event, transition_time):
    """ Just one repeated event. """
    if id in regraa_objects:
        current_object = regraa_objects[id].update(event, transition_time)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _just(event, transition_time)
        regraa_objects[id] = new_obj
        return new_obj
    
class _just(schedulable_observable):
    """ Just one repeated event. """
    def __init__(self, event, transition_time):
        schedulable_observable.__init__(self)
        self.update(event, transition_time)        
    def update(self, event, transition_time):
        self.transition = transition(transition_time)
        self.event = event
        return self
    def next_transition(self):
        return self.transition
    def next_event(self):        
        return self.event

# looped sequence of events and 
def loop(*args):
    """ Looped of events with transition times between them. """
    id = args[0]
    if id in regraa_objects:
        current_object = regraa_objects[id].update(args[1:])
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _loop(args[1:])
        regraa_objects[id] = new_obj
        return new_obj
    
class _loop(schedulable_observable):
    """ Looped of events with transition times between them (inner class). """
    def __init__(self, sequence):
        schedulable_observable.__init__(self)        
        self.index = 0
        self.update(sequence)        
    def update(self, sequence):
        self.events = []
        self.transitions = []
        for arg in sequence:
            if type(arg) is int:
                self.transitions.append(transition(arg))
            else:
                self.events.append(arg)
        if len(self.events) is not len(self.transitions):
            raise Exception("invalid loop, not enough transitions")
        return self
    def next_transition(self):
        trans = self.transitions[self.index]
        self.index = (self.index + 1) % len(self.events)
        return trans
    def next_event(self):
        #print(self.index)
        return self.events[self.index]
