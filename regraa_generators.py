import random
from regraa_reactive_base import *
from regraa_sound_events import silent_event
import regraa_constants

# store objects by their unique id
regraa_objects = {}

# simple, single event + transition
def just(id, event):
    """ Just a oneshot event. """
    if id in regraa_objects:
        current_object = regraa_objects[id].update(event)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _just(event)
        regraa_objects[id] = new_obj
        return new_obj
    
class _just(schedulable_observable):
    """ Just one repeated event. """
    def __init__(self, event):
        schedulable_observable.__init__(self)
        self.update(event)        
    def update(self, event):        
        self.event = event
        return self
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

# Randomized sequence of events and transitions
def rand(*args):
    """ Randomized events with randomly chosen transition times between them. """
    id = args[0]
    if id in regraa_objects:
        current_object = regraa_objects[id].update(args[1:])
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _rand(args[1:])
        regraa_objects[id] = new_obj
        return new_obj
    
class _rand(schedulable_observable):
    """ Randomized events with randomly chosen transition times between them (inner class). """
    def __init__(self, sequence):
        schedulable_observable.__init__(self)                
        self.update(sequence)        
    def update(self, sequence):
        self.events = []
        self.transitions = []
        for arg in sequence:
            if type(arg) is int:
                self.transitions.append(transition(arg))
            else:
                self.events.append(arg)        
        return self
    def next_transition(self):        
        return random.choice(self.transitions)
    def next_event(self):
        return random.choice(self.events)


# choose event with certain probability    
def chance(*args, default=(silent_event(), 512)):
    """ Choose event with certain probability. """
    id = args[0]
    if id is not None and id in regraa_objects:
        current_object = regraa_objects[id].update(default, args[1:])
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _chance(default, args[1:])
        regraa_objects[id] = new_obj
        return new_obj

class _chance(schedulable_observable):
    def __init__(self, default, event_tuples):
        schedulable_observable.__init__(self)        
        self.step = 0
        self.event_list = []
        self.event = silent_event()
        self.transition = silent_event()
        self.update(default, event_tuples)
    def update(self, default, event_tuples):
        self.event_list = []
        probability_count = 0
        for event_tuple in event_tuples:            
            for i in range(0, event_tuple[0]):
                self.event_list.append((event_tuple[1], event_tuple[2]))
                probability_count += 1
                if probability_count > 100:
                    print("probability overflow !")
                    break
        for i in range(probability_count, 100):
             self.event_list.append(default)
        return self    
    def next_transition(self):
        if hasattr(self.transition, "step"):
            self.transition.step = self.step
        return self.transition
    def next_event(self):
        current_event = random.choice(self.event_list)
        self.event = current_event[0]
        self.transition = transition(current_event[1])
        if hasattr(self.event, "step"):
            self.event.step = self.step
        self.step += 1
        return self.event
    
    
