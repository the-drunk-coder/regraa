import os, sys
from infix import shift_infix as infix
from regraa_pitch import *
from regraa_sound_events import *
from regraa_control_events import *
from regraa_generators import *
from regraa_observers import *
from regraa_transformers import *
from regraa_dynamic_parametrization import *
import regraa_akita_client as akita_client
from regraa_defaults import regraa_defaults as defaults

def akita_set_latency(lat):
    defaults.akita_latency = lat
    
def akita_quit ():
    akita_client.quit_akita_instances()

def akita_load(*args, **kwargs):
    akita_client.load(*args, **kwargs)

def midi_set_latency(latency):
    defaults.midi_latency = latency

@infix
def shift(obj, time):
    #print("shift!!!!" + str(time))    
    obj.shift(time)
    
@infix
def sync_to(one, two):
    print("sync")
    two.sync(one)

@infix
def sync_at(one, two):
    print("sync at")
    two[0].sync_at(two[1], one)

    

os.system('clear')
sys.ps1 = "reGraa> "




