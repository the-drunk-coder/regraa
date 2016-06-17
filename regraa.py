import os, sys
from infix import or_infix
from regraa_pitch import *
from regraa_sound_events import *
from regraa_generators import *
from regraa_observers import *
from regraa_transformers import *
import regraa_akita_client as akita_client

def akita_set_latency(lat):
    akita_client.akita_add_latency = lat
    
def akita_quit ():
    akita_client.quit_akita_instances()

def akita_load(*args, **kwargs):
    akita_client.load(*args, **kwargs)

def midi_set_latency(latency):
    global midi_latency
    midi_latency = latency
    
@or_infix
def sync(one, two):
    one.sync(two)
        
os.system('clear')
sys.ps1 = "reGraa> "




