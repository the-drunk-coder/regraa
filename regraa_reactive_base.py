import copy, uuid
import regraa_scheduler as scheduler

class event:
    def __init__(self, additional_latency = 0):
        self.ntp_timestamp = 0
        self.additional_latency = additional_latency
        #self.scatter = 0
        self.content = None

class transition:
    def __init__(self, dur):
        self.dur = dur
        self.scatter = 0
        
class chord(event):
    def __init__(self, *args, additional_latency = 0):
        event.__init__(self, additional_latency=additional_latency)
        self.content = args
    
# handles subscriptions for just about anything ...
class subscribeable:
    def __init__(self):
        self.subscribers = []            
    def subscribe(self, subscriber):
        try:
            # subscribers are unique ... 
            self.subscribers.index(subscriber)
        except ValueError:
            try:
                # in case the subscriber had another parent before,
                if subscriber.parent is not self:
                    subscriber.parent.unsubscribe(subscriber)
                    subscriber.parent = self
            except AttributeError:
                # in this case, the subscriber had no parent ..
                subscriber.parent = self
            self.subscribers.append(subscriber)
            if subscriber.is_activator():
                # triggers activation backtracking that should reach basic
                # event source soon ... 
                subscriber.activate()
        return subscriber
    def unsubscribe(self, subscriber):
        try:
            # subscribers are unique ... 
            self.subscribers.remove(subscriber) 
        except ValueError:
            pass
        return self
    def clear_subscribers(self):
        self.subscribers = []    
    def push_event(self, event):
        # generate next event or transition in sequence
        for subscriber in self.subscribers:
            subscriber.handle_event(event)
    def pull_transition(self, transition):
        # here, the behaviour might get chaotic and unpredictable quite quickly ...
        for subscriber in self.subscribers:
            transition = subscriber.handle_transition(transition)
        return transition
    def __rshift__(self, other):
        # for now, only chains without diversions possible
        self.subscribers = []
        return self.subscribe(other)
    #def __lshift__(self, other):
    #    other.subscribe(self)
    def __or__(self, other):
        return self.unsubscribe(other)
    # each subscribable can be given the power to activate its parent object
    def is_activator(self):
        return False
    def activate(self):
        if hasattr(self, "parent"):
            self.parent.activate()
    
# class that generates a sequence of events, manually triggered
class abstract_observable(subscribeable):
    def __init__(self):
        subscribeable.__init__(self)       
    def next(self):
        # generate and push event to subscribers
        self.push_event(self.next_event())
        # get raw transition and pull eventual changes from subscribers
        self.pull_transition(self.next_transition())        
    def next_transition(self):
        # generate next transition in sequence
        raise NotImplementedError()
    def next_event(self):
        # generate next event in sequence
        raise NotImplementedError()    

def is_chord(event):
        try:
            type(event).mro().index(chord)
        except ValueError:           
            return False
        return True

# class that generates a sequence of events, triggered by scheduler    
class schedulable_observable(abstract_observable):
    def __init__(self):
        subscribeable.__init__(self)
        self.shift_time = 0
        self.shift_difference = 0        
        self.active = False
        # needed for clean deactivation of objects,
        # as all future events scheduled for this event
        # need to be removed from scheduler 
        self._uuid = uuid.uuid4().hex        
        self.syncables = []
    def sync(self, other):
        other.deactivate()
        self.syncables.append(other)
    def deactivate(self):
        self.active = False
        scheduler.clean(self._uuid)
    def stop(self):
        self.deactivate()        
    def shift(self, new_shift_time):
        print("setting shift time to " + str(new_shift_time))
        self.shift_difference = new_shift_time - self.shift_time                            
        self.shift_time = new_shift_time
    def reset(self):
        pass
    def sync_at(self, *args):
        pass
    def activate(self):
        if not self.active:
            self.active = True
            self.next(scheduler.now, scheduler.now)        
    def next(self, logical_time, actual_time):
        if not self.active:
            return
        
        # synchronize another object to this object
        if len(self.syncables) != 0:
            for syncable in self.syncables:
                syncable.activate()
            self.syncables = []
            
        # generate and push event to subscribers
        # before, update things like additional latencies and shift time
        current_event = self.next_event()
        current_event.update()
                      
        # equip event with ntp timestamp in case we want to use it with osc ...
        current_event.ntp_timestamp = scheduler.get_timestamp(logical_time, current_event.additional_latency)
        if is_chord(current_event):
            for sub_event in current_event.content:
                sub_event.ntp_timestamp = current_event.ntp_timestamp
        
        # push event to subscriber line !
        self.push_event(current_event)

        # get raw transition and pull eventual changes from subscribers
        try:
            current_transition = self.pull_transition(self.next_transition())
        except NotImplementedError:
            print("seems as if object has finished ...")
            self.deactivate()
            return

        # apply shift        
        logical_time = logical_time + self.shift_difference
        self.shift_difference = 0

        # apply scatter        
        scatter = current_transition.scatter
        current_transition.scatter = 0
                
        self.schedule_next_step(logical_time, current_transition.dur + scatter)           
    def schedule_next_step(self, current_logical_time, time):
        scheduler.schedule_function(self._uuid, self.next, current_logical_time + time)    
    
        
# class that generates a sequence of events
class abstract_observer(subscribeable):
    def __init__(self):
        subscribeable.__init__(self)
    def handle_event(self, event):                
        self.push_event(self.on_event(event))
    def handle_transition(self, transition):        
        return self.pull_transition(self.on_transition(transition))
    def on_event(self, event):
        return event
    def on_transition(self, transition):        
        return transition    
    
