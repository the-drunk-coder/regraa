from regraa import *
from regraa_scheduler import *

class string_event(event):
    def __init__(self, some_string):
        event.__init__(self)
        self.content = some_string

class string_sequence_generator(abstract_observable):
    def __init__(self, *args):
        abstract_observable.__init__(self)
        self.default_transition = transition(512)
        self.event_sequence = args
        self.sequence_length = len(args)
        self.sequence_index = 0
    def next_transition(self):
        return self.default_transition
    def next_event(self):
        current_event = self.event_sequence[self.sequence_index]
        self.sequence_index = (self.sequence_index + 1) % self.sequence_length
        return current_event
    def schedule_next_step(self, transition):
        print("Next step scheduled in: " + str(transition.duration))

class scheduled_string_sequence_generator(schedulable_observable):
    def __init__(self, *args, scheduler = None):
        schedulable_observable.__init__(self, scheduler)
        self.default_transition = transition(1024)
        self.event_sequence = args
        self.sequence_length = len(args)
        self.sequence_index = 0
    def next_transition(self):
        return self.default_transition
    def next_event(self):
        current_event = self.event_sequence[self.sequence_index]
        self.sequence_index = (self.sequence_index + 1) % self.sequence_length
        return current_event

class print_observer(abstract_observer):
    def __init__(self):
        abstract_observer.__init__(self)
    def on_event(self, event):
        print("Event: " + str(event.content))
        try:
            print("Event timestamp: " + str(event.ntp_timestamp))
        except AttributeError:
            pass
        return event
    def on_transition(self, transition):
        print("Transition (ms): " + str(transition.duration))
        return transition

class uppercase(abstract_event_modifier):
    def __init__(self, destructive = False):
        abstract_event_modifier.__init__(self, destructive)
    def modify_event(self, event):
        event.content = event.content.upper()
        return event

class halftime(abstract_transition_modifier):
    def __init__(self, destructive = False):
        abstract_transition_modifier.__init__(self, destructive)
    def modify_transition(self, transition):
        transition.duration = transition.duration / 2
        return transition

class to_uppercase_transformer(abstract_observer):
    def __init__(self):
        abstract_observer.__init__(self)
        self.event_modifier = uppercase(destructive = False)
    def on_event(self, event):
        return self.event_modifier.apply_to(event)    

class halftime_transformer(abstract_observer):
    def __init__(self):
        abstract_observer.__init__(self)
        self.transition_modifier = halftime(destructive = False)
    def on_transition(self, transition):
        return self.transition_modifier.apply_to(transition)    

sched = timestamp_dictionary_scheduler()

gen = string_sequence_generator(
    string_event("hi, "),
    string_event("how "),
    string_event("are "),
    string_event("you "),
    string_event("?"),
    )

scgen = scheduled_string_sequence_generator(
    string_event("1_hi, "),
    string_event("2_how "),
    string_event("3_are "),
    string_event("4_you "),
    string_event("5_?"),
    scheduler = sched
    )

mod = to_uppercase_transformer()

half = halftime_transformer()

obs = print_observer()



