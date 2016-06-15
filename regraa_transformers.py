from regraa_reactive_base import *
import regraa_constants
import random
import math

class regraa_universal_modifier():
    def __init__(self, param="", destructive=False):        
        self.value = None
        self.param = param        
        self.destructive = destructive
    def apply_to(self, entity):
        if not self.destructive:
            return self.modify_entity(copy.deepcopy(entity))        
        else:
            return self.modify_entity(entity)                    
    def modify_entity(self, entity):                
        self.value = getattr(entity, self.param)                
        if hasattr(entity, self.param):
            setattr(entity, self.param, self.calculate_value())
        return entity
    def calculate_value(self):
        raise NotImplementedError

# dummy modifier
class none():
    def apply_to(self, entity):
        return entity

class mute(regraa_universal_modifier):
    def __init__(self, destructive=False):
        regraa_universal_modifier.__init__(self, param="gain", destructive=destructive)
    def calculate_value(self):
        return 0.0
    
"""
Simple arithmetics
"""    
class add(regraa_universal_modifier):
    def __init__(self, param, increment, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment        
    def calculate_value(self):        
        return self.value + self.increment

class sub(regraa_universal_modifier):
    def __init__(self, param, decrement, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.decrement = decrement        
    def calculate_value(self):        
        return self.value - self.decrement

class div(regraa_universal_modifier):
    def __init__(self, param, divisor, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.divisor = divisor        
    def calculate_value(self):        
        return self.value / self.divisor

class mul(regraa_universal_modifier):
    def __init__(self, param, factor, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.factor = factor        
    def calculate_value(self):        
        return self.value * self.factor
    

""" 

stateful transformers

need to be destructive for now ... 
somewhat clearer that way ... 

"""
class brownian(regraa_universal_modifier):
    def __init__(self, param, increment, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment        
    def calculate_value(self):                
        return self.value + random.choice([self.increment, -self.increment])

class sinestretch(regraa_universal_modifier):
    def __init__(self, param, cyclicity, min_bound, max_bound, destructive=True):
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
        return (abs_sin * stretch_range) + self.min_bound        
    
class wrap(regraa_universal_modifier):
    def __init__(self, param, lower, upper, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.lower = lower
        self.upper = upper
    def calculate_value(self):
        if self.value < self.lower:            
            return self.upper
        elif self.value > self.upper:            
            return self.lower
        else:
            return self.value

class bounds(regraa_universal_modifier):
    def __init__(self, param, lower, upper, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.lower = lower
        self.upper = upper
    def calculate_value(self):
        if self.value < self.lower:
            return self.lower
        elif self.value > self.upper:
            return self.upper
        else:
            return self.value
        
regraa_transformers = {}
        
def map(event_modifier, transition_modifier, id=None):
    """ Map single event modifier to stream. """
    if id is not None and id in regraa_transformers:
        current_object = regraa_transformers[id].update(event_modifier, transition_modifier)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _map(event_modifier, transition_modifier)
        regraa_transformers[id] = new_obj
        return new_obj

        
class _map(abstract_observer):
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


def chance_map(*args, default=(none(), none()), id=None):
    """ Map single event modifier to stream. """
    if id is not None and id in regraa_transformers:
        current_object = regraa_transformers[id].update(default, args)
        if regraa_constants.rebuild_chain:
            current_object.clear_subscribers()
        return current_object
    else:
        new_obj = _chance_map(default, args)
        regraa_transformers[id] = new_obj
        return new_obj

        
class _chance_map(abstract_observer):
    def __init__(self, default, modifier_tuples):
        abstract_observer.__init__(self)
        self.step = 0
        self.modifier_list = []
        self.event_modifier = none()
        self.transition_modifier = none()
        self.update(default, modifier_tuples)
    def update(self, default, modifier_tuples):
        self.modifier_list = []
        probability_count = 0
        for modifier_tuple in modifier_tuples:
            for i in range(0, modifier_tuple[0]):
                self.modifier_list.append((modifier_tuple[1], modifier_tuple[2]))
                probability_count += 1
                if probability_count > 100:
                    print("probability overflow !")
                    break
        for i in range(probability_count, 100):
             self.modifier_list.append(default)
        return self
    def on_event(self, event):
        current_modifiers = random.choice(self.modifier_list)
        self.event_modifier = current_modifiers[0]
        self.transition_modifier = current_modifiers[1]
        if hasattr(self.event_modifier, "step"):
            self.event_modifier.step = self.step
        self.step += 1
        return self.event_modifier.apply_to(event)
    def on_transition(self, transition):
        if hasattr(self.transition_modifier, "step"):
            self.transition_modifier.step = self.step
        return self.transition_modifier.apply_to(transition)



    
