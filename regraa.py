import os, sys
from infix import or_infix
from regraa_pitch import *
from regraa_sound_events import *
from regraa_generators import *
from regraa_observers import *
from regraa_transformers import *
import regraa_akita_client as akita_client
#from regraa_test import *

def akita_set_latency(lat):
    akita_client.akita_add_latency = lat
    
def akita_quit ():
    akita_client.quit_akita_instances()

def akita_load(*args, **kwargs):
    akita_client.load(*args, **kwargs)

def midi_set_latency(latency):
    global midi_latency
    midi_latency = latency
    
def get_by_id(id):    
    if id in regraa_objects:
        return regraa_objects[id]
    elif id in regraa_transformers:
        return regraa_transformers[id]
    else:
        return none

def silence():
    for id in regraa_objects:
        regraa_objects[id].deactivate()
    for id in regraa_transformers:
        regraa_transformers[id].active = False

@or_infix
def sync(one, two):
    get_by_id(one).sync(get_by_id(two))
        
os.system('clear')
sys.ps1 = "reGraa> "




