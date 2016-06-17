from regraa_reactive_base import *
import regraa_constants
import random
import math

class regraa_universal_modifier():
    def __init__(self, param="", destructive=False):                
        self.param = param        
        self.destructive = destructive
    def apply_to(self, entity):
        if self.destructive:
            #print("DESTROY!!!")
            return self.modify_entity(entity)                    
        else:
            return self.modify_entity(copy.deepcopy(entity))
    def modify_entity(self, entity):                
        if hasattr(entity, self.param):
            setattr(entity, self.param, self.calculate_value(getattr(entity, self.param)))
        return entity
    def calculate_value(self, current_value):
        raise NotImplementedError    
    
# dummy modifier
class none(regraa_universal_modifier):
    def __init__(self):
        regraa_universal_modifier.__init__(self, param="none", destructive=False)
    def apply_to(self, entity):        
        return entity

class mute(regraa_universal_modifier):
    def __init__(self, destructive=False):
        regraa_universal_modifier.__init__(self, param="gain", destructive=destructive)
    def calculate_value(self, current_value):
        return 0.0
    
"""
Simple arithmetics
"""    
class add(regraa_universal_modifier):
    def __init__(self, param, increment, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment        
    def calculate_value(self, current_value):        
        return current_value + self.increment

class sub(regraa_universal_modifier):
    def __init__(self, param, decrement, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.decrement = decrement        
    def calculate_value(self, current_value):        
        return current_value - self.decrement

class div(regraa_universal_modifier):
    def __init__(self, param, divisor, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.divisor = divisor        
    def calculate_value(self, current_value):        
        return current_value / self.divisor

class mul(regraa_universal_modifier):
    def __init__(self, param, factor, destructive=False):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.factor = factor        
    def calculate_value(self, current_value):        
        return current_value * self.factor
    

""" 

stateful transformers

need to be destructive for now ... 
somewhat clearer that way ... 

"""

class fade_in(regraa_universal_modifier):
    def __init__(self, param, increment, goal, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment
        self.goal = goal
    def calculate_value(self, current_value):                
        tmp = current_value + self.increment
        if tmp > self.goal:
            return self.goal
        else:
            return current_value + self.increment

class fade_out(regraa_universal_modifier):
    def __init__(self, param, decrement, goal, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.decrement = decrement
        self.goal = goal
    def calculate_value(self, current_value):
        tmp = current_value - self.decrement
        if tmp < self.goal:
            return self.goal
        else:
            return current_value - self.decrement
           
class brownian(regraa_universal_modifier):
    def __init__(self, param, increment, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.increment = increment        
    def calculate_value(self, current_value):                
        return current_value + random.choice([self.increment, -self.increment])

class sinestretch(regraa_universal_modifier):
    def __init__(self, param, cyclicity, min_bound, max_bound, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.cyclicity = cyclicity
        self.min_bound = min_bound
        self.max_bound = max_bound
        self.step = 0
        self.degree_increment = 360 / self.cyclicity
    def calculate_value(self, current_value):
        degree = ((self.step % self.cyclicity) * self.degree_increment) % 360
        abs_sin = abs(math.sin(math.radians(degree)))
        stretch_range = self.max_bound - self.min_bound
        return (abs_sin * stretch_range) + self.min_bound        
    
class wrap(regraa_universal_modifier):
    def __init__(self, param, lower, upper, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.lower = lower
        self.upper = upper
    def calculate_value(self, current_value):
        if current_value < self.lower:            
            return self.upper
        elif current_value > self.upper:            
            return self.lower
        else:
            return current_value

class bounds(regraa_universal_modifier):
    def __init__(self, param, lower, upper, destructive=True):
        regraa_universal_modifier.__init__(self, param=param, destructive=destructive)
        self.lower = lower
        self.upper = upper
    def calculate_value(self, current_value):
        if current_value < self.lower:
            return self.lower
        elif current_value > self.upper:
            return self.upper
        else:
            return current_value

# modifier applicators
class map(abstract_observer):
    def __init__(self, event_modifier, transition_modifier):
        abstract_observer.__init__(self)
        self.step = 0
        self.update(event_modifier, transition_modifier)
    def update(self, event_modifier, transition_modifier):
        self.event_modifier = event_modifier
        self.transition_modifier = transition_modifier
        return self
    def on_event(self, event):
        #print("EVENT MOOOD!")
        if hasattr(self.event_modifier, "step"):
            self.event_modifier.step = self.step
        self.step += 1        
        return self.event_modifier.apply_to(event)
    def on_transition(self, transition):
        #print("TRANS MOOOD!")
        if self.transition_modifier is not None:
            if hasattr(self.transition_modifier, "step"):
                self.transition_modifier.step = self.step
            return self.transition_modifier.apply_to(transition)
        else:
            return transition    
    
class chance_map(abstract_observer):
    def __init__(self, *modifier_tuples, default=(none(), none())):
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



    
