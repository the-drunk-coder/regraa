import random
from regraa_reactive_base import *
from regraa_sound_events import silent_event
from regraa_defaults import regraa_defaults as default

def is_generator(gen):
        try:
            type(schedulable_observable).mro().index(gen)
        except ValueError:           
            return False
        return True

    
class just(schedulable_observable):
    """ Just one repeated event. """
    def __init__(self):
        schedulable_observable.__init__(self)
        #self.update(event)        
    def update(self, event):        
        self.event = event
        return self
    def next_event(self):        
        return self.event

class loop(schedulable_observable):
    """ Loop of events with transition times between them. """
    def __init__(self):
        schedulable_observable.__init__(self)        
        self.index = 0
        self.index_syncables = {}
    def reset(self):
        self.index = 0
    def sync_at(self, index, syncable):
        syncable.deactivate()
        syncable.reset()
        try:
            self.index_syncables[index]
        except KeyError:
            self.index_syncables[index] = []        
        self.index_syncables[index].append(syncable)
    def update(self, *sequence):
        self.events = []
        self.transitions = []
        for arg in sequence:                        
            self.events.append(arg[0])
            self.transitions.append(transition(arg[1]))                    
        return self
    def next_transition(self):
        trans = self.transitions[self.index]
        self.index = (self.index + 1) % len(self.events)
        return trans
    def next_event(self):
        try:
            current_syncables = self.index_syncables[self.index]
        except:
            current_syncables = []
        if len(current_syncables) > 0:
            for syncable in current_syncables:
                syncable.activate()
                self.index_syncables[self.index] = []
        return self.events[self.index]
    def insert(self, pos, event_tuple):
        self.events.insert(pos, event_tuple[0])
        self.transitions.insert(pos, event_tuple[1])
    def push_back(self, event_tuple):
        self.events.append(event_tuple[0])
        self.transitions.append(transition(event_tuple[1]))
    def replace(self, pos, event_tuple):
        self.events.pop(pos)
        self.transitions.pop(pos)
        self.events.insert(pos, event_tuple[0])
        self.transitions.insert(pos, transition(event_tuple[1]))

class rand(schedulable_observable):
    """ Randomized events with randomly chosen transition times between them. """
    def __init__(self):
        schedulable_observable.__init__(self)        
    def update(self, *sequence):
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

class chance(schedulable_observable):
    def __init__(self):
        schedulable_observable.__init__(self)        
        self.step = 0
        self.event_list = []
        self.event = silent_event()
        self.transition = silent_event()
        #self.update(default, event_tuples)
    def update(self, *event_tuples, default=(silent_event(),silent_event())):
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
    
    
