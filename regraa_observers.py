import threading
from regraa_reactive_base import *
from regraa_sound_events import *
import regraa_supercollider_client as sc_client

class sound_out(abstract_observer):
    def __init__(self):
        abstract_observer.__init__(self)
    def on_event(self, event):        
        if self.is_synth_sound_event(event):                        
            try:
                sc_client.send(event.get_osc_bundle())
            except Exception as e:
                print(e)
                print("Couldn't process synth sound event for some reason")    
        else:
            async = threading.Thread(target=event.play)
            async.start()
        return event
    def is_synth_sound_event(self, event):
        try:
            type(sine_(c4)).mro().index(synth_sound_event)
        except ValueError:           
            return False
        return True
    def is_activator(self):
        return True
    
snd1 = sound_out()
snd2 = sound_out()
snd3 = sound_out()
snd4 = sound_out()
snd5 = sound_out()
snd6 = sound_out()
snd7 = sound_out()
snd8 = sound_out()
snd9 = sound_out()
snd10 = sound_out()
