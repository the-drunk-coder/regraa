import threading, time, struct
from pygame import time as pgtime
from pythonosc.parsing import ntp
"""

A somewhat naive function scheduler ...

"""
    
start_time = time.time()
now = 0

# server latency for scsynth (in ms)
latency = 100

active = False
timestamp_dictionary = {}
stack = []

def get_timestamp(logical_time, additional_latency):
    timestamp = start_time + ((logical_time + latency + additional_latency) / 1000)    
    return timestamp
    
def start(timestamp_dictionary, stack):
    global active
    active = True
    scheduler_loop(timestamp_dictionary, stack)

def scheduler_loop(timestamp_dictionary, stack):
    global now
    while active:        
        now = pgtime.get_ticks()
        # now schedule pending events ... thus we're having a fixed point of time ('now')
        while len(stack) > 0:
            delayed_event = stack.pop()
            # correct future time if wait was not precise
            future_time = delayed_event[1]                               
            if future_time not in timestamp_dictionary:
                timestamp_dictionary[future_time] = {}
            # get objects uuid
            key = delayed_event[0]
            # store function to be scheduled under the object uuid (necessary for cleaning) 
            timestamp_dictionary[future_time][key] = delayed_event[2]
        # after everything has been said and done, check if there's any garbage left ...
        time_points = timestamp_dictionary.keys()
        past_time_points = [x for x in time_points if x < now]
        for time_point in past_time_points:                    
            #print(str(len(timestamp_dictionary[past])) + " EVENTS at " + str(past))
            for past_event in timestamp_dictionary[time_point]:                
                try:                    
                    async = threading.Thread(target=timestamp_dictionary[time_point][past_event], args=(time_point, now))
                    async.start()
                except Exception as e:
                    print(e) 
                    raise e
            del timestamp_dictionary[time_point]            
            # wait one microsecond              
        pgtime.wait(1) 

# schedule a function to a later point of time
def schedule_function(key, func, timestamp):        
    stack.append([key, timestamp, func])

# needed for clean deactivation of objects     
def clean(key):
    for time_point in timestamp_dictionary.keys():
        if key in timestamp_dictionary[time_point]:
            del timestamp_dictionary[time_point][key]
            
    
scheduler_thread = threading.Thread(target=start, args=(timestamp_dictionary,stack))
scheduler_thread.start()

