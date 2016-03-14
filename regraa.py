import os, sys
from regraa_pitch import *
from regraa_sound_events import *
from regraa_generators import *
from regraa_observers import *
from regraa_transformers import *
#from regraa_test import *

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
        
os.system('clear')
sys.ps1 = "reGraa> "




