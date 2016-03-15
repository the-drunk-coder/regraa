"""
In this file, find the functions that actually trigger the sound generators.

reGraa doesn't use it's own sound generation, but different backends, as seen below.

"""
import atexit, os, copy
from pygame import midi
from pygame import time as pg_time 
from regraa_pitch import *
from regraa_reactive_base import *
import regraa_supercollider_client as sc_client

class sound_event(event):
    def __init__(self, gain=0.5, dur=0):
        self.gain = gain
        self.dur = dur
    def play():
        raise NotImplementedError

class tuned_sound_event(sound_event):
    def __init__(self, *args, gain=0.5, dur=256):
        sound_event.__init__(self, gain = gain, dur = dur)
        if type(args[0]) is regraa_pitch:
            self.set_pitch(args[0])                             
        else:
            self.freq = float(args[0])
    def set_pitch(self, new_pitch):
        self.pitch = copy.deepcopy(new_pitch)
        self.freq = float(self.pitch.pitch.frequency)

class synth_sound_event(sound_event):
    def __init__(self, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        sound_event.__init__(self, gain = gain, dur = dur)        
        self.sustain = dur - a - d - r
        self.attack = a
        self.decay = d
        self.release = r
        self.reverb = rev
        self.pan = pan
        if type(cutoff) is regraa_pitch:
            self.cutoff = cutoff.pitch.frequency
        else:
            self.cutoff = cutoff        
    def get_osc_bundle(self):
        if(self.reverb > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        message = sc_client.build_message("/s_new", current_synth_name, -1, 0, 1,
                          "gain", max(0.0, min(self.gain,  1.1)),
                          "a", self.attack / 1000,
                          "d", self.decay / 1000,
                          "s", self.sustain / 1000,
                          "r", self.release / 1000,
                          "rev", self.reverb,
                          "pan", self.pan,
                          "cutoff", self.cutoff)
        return sc_client.build_bundle(self.ntp_timestamp, message)
# end synth_sound_event

class sample_sound_event(synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=0, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, cutoff=20000):
        synth_sound_event.__init__(self, gain=gain, dur=dur, a=a, d=0, r=r, rev=rev, pan=pan, cutoff=cutoff)
        self.folder = str(args[0])
        self.name = str(args[1])        
        self.speed = speed
        print(self.speed)
        self.start = start
        sc_client.register_sample(self.folder, self.name)
    def get_osc_bundle(self):
        if(self.reverb > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        message = sc_client.build_message("/s_new", current_synth_name, -1, 0, 1,
                                           "bufnum", sc_client.samples[self.folder + ":" + self.name],
                                           "speed", self.speed,
                                           "rev", self.reverb,
                                           "pan", self.pan,
                                           "cutoff", self.cutoff,
                                           "gain", max(0.0, min(self.gain,  1.1)),
                                           "start", self.start,
                                           "dur", self.dur,
                                           "a", self.attack / 1000,
                                           "d", self.release / 1000)
        return sc_client.build_bundle(self.ntp_timestamp, message)
# end sample_sound_event()

class tuned_synth_sound_event(synth_sound_event, tuned_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        tuned_sound_event.__init__(self, args[0], gain = gain, dur = dur)
        synth_sound_event.__init__(self, gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)        
    def get_osc_bundle(self):
        if(self.reverb > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        message = sc_client.build_message("/s_new", current_synth_name, -1, 0, 1,
                          "freq", self.freq,
                          "gain", max(0.0, min(self.gain,  1.1)),
                          "a", self.attack / 1000,
                          "d", self.decay / 1000,
                          "s", self.sustain / 1000,
                          "r", self.release / 1000,
                          "rev", self.reverb,
                          "pan", self.pan,
                          "cutoff", self.cutoff)
        return sc_client.build_bundle(self.ntp_timestamp, message)
# end tuned_synth_sound_event
            

midi.init()

midi_out = midi.Output(0,0)
midi_out.set_instrument(0)

def del_out():
    midi.quit()
    del midi_out

# make sure midi out is removed on program exit, to avoid pointer exception
atexit.register(del_out)

# naive note mutex
notes_on = {}

class midi_(tuned_sound_event):
    def __init__(self, *args, gain=0.5, dur=256):
        tuned_sound_event.__init__(self, args[0], gain=gain, dur=dur)
        self.latency = 0
    def set_latency(self, latency):
        self.latency = latency
    def play(*args, **kwargs):        
        current_pitch = self.pitch.pitch.midi
        if current_pitch not in notes_on:
            pg_time.wait(self.latency)
            notes_on[current_pitch] = True
            velocity = int(127 * self.gain)
            midi_out.note_on(current_pitch, velocity)
            pg_time.wait(int(self.dur))
            midi_out.note_off(current_pitch, velocity)
            del notes_on[current_pitch]        

""" Synthetic sounds, created with the SC3 backend ... """

class sine_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "sine"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end sine_

class sqr_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "sqr"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end sqr_

class buzz_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "buzz"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end buzz_

class subt_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "subt"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end subt_

class risset_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "risset"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end risset_

class pluck_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "pluck"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end pluck_

class noise_(synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        self.synth_name = "noise"
        synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)        
# end noise_

class sample_(sample_sound_event):
    def __init__(self, *args, gain=0.5, dur=0, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, cutoff=20000):
        if dur > 0.0:
            self.synth_name="grain"
        else:
            self.synth_name="sampl"    
        sample_sound_event.__init__(self, args[0], args[1], speed=speed, gain=gain, dur=dur, a=a, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end sample_
        
class sample8ch_(sample_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, cutoff=20000):
        if dur > 0.0:
            self.synth_name="grain8"
        else:
            self.synth_name="sampl8"    
        sample_sound_event.__init__(self, args[0], args[1], speed=speed, gain=gain, dur=dur, a=a, r=r, rev=rev, pan=pan, cutoff=cutoff)
# end sample_
    
class say_(sound_event):
    def __init__(self, *args, gain=0.6, speed=140):
        sound_event.__init__(self, gain=gain, dur = 0)
        self.text = args[0]
        self.speed = speed
        self.latency = 0
    def set_latency(self, latency):
        self.latency = latency
    def play():
        pg_time.wait(self.latency)
        amp = 100 * self.gain
        command = "espeak -s{} -a{} --stdout \"{}\" | aplay -q" .format(int(speed), int(amp), text)
        os.system(command)
# end say_    

