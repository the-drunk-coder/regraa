import threading
from regraa_reactive_base import *
from regraa_sound_events import *
import regraa_supercollider_client as sc_client
import regraa_akita_client as akita_client

class sound_out(abstract_observer):
    def __init__(self):
        abstract_observer.__init__(self)
    def on_event(self, event):
        if is_chord(event):
            for sub_event in event.content:
                #sub_event.ntp_timestamp = event.ntp_timestamp
                self.on_event(sub_event)
        elif self.is_synth_sound_event(event):                        
            try:
                sc_client.send(event.get_osc_bundle())
            except Exception as e:
                print(e)
                print("Couldn't process synth sound event for some reason")
                #raise(e)
        elif self.is_akita_event(event):            
            try:
                akita_client.send(event.instance, event.get_osc_bundle())
            except Exception as e:
                print(e)
                print("Couldn't  process akita event for some reason")
                #raise(e)
        else:
            async = threading.Thread(target=event.play)
            async.start()
        return event
    def is_synth_sound_event(self, event):
        try:
            type(event).mro().index(synth_sound_event)
        except ValueError:           
            return False
        return True
    def is_akita_event(self, event):
        akita = True
        akita_param = True
        try:
            type(event).mro().index(akita_)
        except ValueError:           
            akita = False
        try:
            type(event).mro().index(akita_param_event)
        except ValueError:           
            akita_param = False        
        return akita or akita_param
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

