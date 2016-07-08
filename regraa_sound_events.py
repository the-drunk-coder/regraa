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
import regraa_akita_client as akita_client
from random import randint 
import regraa_osc_tools as osc_tools
from regraa_defaults import regraa_defaults as default 

class sound_event(event):
    def __init__(self, gain=0.5, dur=0):
        self.gain = gain
        self.dur = dur
        self.additional_latency = 0
        self.scatter = 0
    def play(self):
        raise NotImplementedError
    # method to be called before playing, i.e. to update latency and the like
    def update(self):
        pass

class silent_event(event):
    def __init__(self, gain=0.5, dur=0):
        sound_event.__init__(self, gain = gain, dur = dur)
    def play(self):
        pass
    
class tuned_sound_event(sound_event):
    def __init__(self, *args, gain=0.5, dur=256):
        sound_event.__init__(self, gain = gain, dur = dur)
        self.pitch = args[0]

class synth_sound_event(sound_event):
    def __init__(self, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        sound_event.__init__(self, gain = gain, dur = dur)        
        self.sustain = dur - a - d - r
        self.attack = a
        self.decay = d
        self.release = r
        self.rev = rev
        self.pan = pan
        self.cutoff = cutoff
    def get_sustain(self):
        self.sustain = self.dur - self.attack - self.decay - self.release
        return self.sustain    
    def get_osc_bundle(self):
        if(self.rev > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        if type(self.cutoff) is regraa_pitch:
            co_freq = self.cutoff.pitch.frequency
        else:
            co_freq = self.cutoff
        message = osc_tools.build_message("/s_new", current_synth_name, -1, 0, 1,
                          "gain", max(0.0, min(self.gain,  1.1)),
                          "a", self.attack / 1000,
                          "d", self.decay / 1000,
                          "s", self.get_sustain() / 1000,
                          "r", self.release / 1000,
                          "rev", self.rev,
                          "pan", self.pan,
                          "cutoff", co_freq)
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end synth_sound_event

class akita_(sound_event):
    def __init__(self, instance, start=0.0, dur=256, fade_in=0, fade_out=0, gain=0.2, flippiness=0.0, fuzziness=0.0, rev=0.0,
                 cutoff=20000, q=2, mean_filter_on=0, sample_repeat=1, samplerate_mod=1, pan=0.5,
                 peak_q=1.0, peak_gain=0.0, peak_f=1000, hp_q = 1.0, hp_freq=1 ):        
        sound_event.__init__(self, gain = gain, dur = dur)
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.additional_latency = default.akita_latency
        self.instance = instance
        self.start = start
        self.flippiness = flippiness
        self.fuzziness = fuzziness
        self.rev = rev
        self.mean_filter_on = mean_filter_on
        self.lp_q = q
        self.lp_cutoff = cutoff
        self.sample_repeat = sample_repeat
        self.samplerate_mod = samplerate_mod
        self.pan = pan
        self.peak_q = peak_q
        self.peak_f = peak_f
        self.peak_gain = peak_gain
        self.hp_q = hp_q
        self.hp_freq = hp_freq
    def update(self):
        self.additional_latency = default.akita_latency
    def get_osc_bundle(self):            
        message = osc_tools.build_message("/akita/play",
                                          float(self.start),
                                          int(self.dur),
                                          int(self.fade_in),
                                          int(self.fade_out),
                                          float(self.gain),
                                          float(self.rev),
                                          self.mean_filter_on,
                                          float(self.lp_q),
                                          float(self.lp_cutoff),
                                          float(self.flippiness),
                                          float(self.fuzziness),
                                          int(self.sample_repeat),
                                          float(self.pan),
                                          float(self.samplerate_mod),
                                          float(self.peak_q),
                                          float(self.peak_f),
                                          float(self.peak_gain),
                                          float(self.hp_q),
                                          float(self.hp_freq))
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_

class akita_param_(sound_event):
    def __init__(self, instance, gain=0.2, flippiness=0.0, fuzziness=0.0, rev=0.0, cutoff=20000, q=2,
                 mean_filter_on=0, sample_repeat=1, samplerate_mod=1, pan=0.5,
                 peak_q=1.0, peak_gain=0.0, peak_f=1000, hp_q = 1.0, hp_freq=1):        
        sound_event.__init__(self, gain = gain, dur = 0)
        self.additional_latency = default.akita_latency
        self.instance = instance        
        self.flippiness = flippiness
        self.fuzziness = fuzziness
        self.rev = rev
        self.mean_filter_on = mean_filter_on
        self.lp_q = q
        self.lp_cutoff = cutoff
        self.sample_repeat = sample_repeat
        self.samplerate_mod = samplerate_mod
        self.pan = pan
        self.peak_q = peak_q
        self.peak_f = peak_f
        self.peak_gain = peak_gain
        self.hp_q = hp_q
        self.hp_freq = hp_freq
    def update(self):
        self.additional_latency = default.akita_latency
    def get_osc_bundle(self):            
        message = osc_tools.build_message("/akita/param",                                          
                                          float(self.gain),
                                          float(self.rev),
                                          self.mean_filter_on,
                                          float(self.lp_q),
                                          float(self.lp_cutoff),
                                          float(self.flippiness),
                                          float(self.fuzziness),
                                          int(self.sample_repeat),
                                          float(self.pan),
                                          float(self.samplerate_mod),
                                          float(self.peak_q),
                                          float(self.peak_f),
                                          float(self.peak_gain),
                                          float(self.hp_q),
                                          float(self.hp_freq))
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_

class sample_sound_event(synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=0, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, cutoff=20000):
        synth_sound_event.__init__(self, gain=gain, dur=dur, a=a, d=0, r=r, rev=rev, pan=pan, cutoff=cutoff)
        self.folder = str(args[0])
        self.name = str(args[1])        
        self.speed = speed
        #print(self.speed)
        self.start = start
        sc_client.register_sample(self.folder, self.name)
    def get_osc_bundle(self):
        if(self.rev > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        if type(self.cutoff) is regraa_pitch:
            co_freq = self.cutoff.pitch.frequency
        else:
            co_freq = self.cutoff
        message = osc_tools.build_message("/s_new", current_synth_name, -1, 0, 1,
                                           "bufnum", sc_client.samples[self.folder + ":" + self.name],
                                           "speed", self.speed,
                                           "rev", self.rev,
                                           "pan", self.pan,
                                           "cutoff", co_freq,
                                           "gain", max(0.0, min(self.gain,  1.1)),
                                           "start", self.start,
                                           "dur", self.dur,
                                           "a", self.attack / 1000,
                                           "d", self.release / 1000)
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end sample_sound_event()

class tuned_synth_sound_event(synth_sound_event, tuned_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, cutoff=15000):
        tuned_sound_event.__init__(self, args[0], gain=gain, dur=dur)
        synth_sound_event.__init__(self, gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, cutoff=cutoff)        
    def get_osc_bundle(self):
        if(self.rev > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        if type(self.cutoff) is regraa_pitch:
            co_freq = self.cutoff.pitch.frequency
        else:
            co_freq = self.cutoff
        if type(self.pitch) is regraa_pitch:
            p_freq = self.pitch.pitch.frequency
        else:
            p_freq = self.pitch        
        message = osc_tools.build_message("/s_new", current_synth_name, -1, 0, 1,
                          "freq", p_freq,
                          "gain", max(0.0, min(self.gain,  1.1)),
                          "a", self.attack / 1000,
                          "d", self.decay / 1000,
                          "s", self.get_sustain() / 1000,
                          "r", self.release / 1000,
                          "rev", self.rev,
                          "pan", self.pan,
                          "cutoff", co_freq)
        return osc_tools.build_bundle(self.ntp_timestamp, message)
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
    def __init__(self, *args, gain=0.5, dur=256, portamento=False):
        tuned_sound_event.__init__(self, args[0], gain=gain, dur=dur)
        self.additional_latency = default.midi_latency
        self.portamento = portamento
    def update(self):
        self.additional_latency = default.midi_latency
    def play(self, *args, **kwargs):        
        current_pitch = self.pitch.pitch.midi
        pg_time.wait(self.additional_latency)
        if current_pitch not in notes_on:            
            notes_on[current_pitch] = True
            velocity = int(127.0 * self.gain)
            midi_out.note_on(current_pitch, velocity)
            pg_time.wait(int(self.dur))
            if not self.portamento:
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
    def play(self):
        pg_time.wait(self.additional_latency)
        amp = 100 * self.gain
        command = "espeak -s{} -a{} --stdout \"{}\" | aplay -q" .format(int(self.speed), int(amp), self.text)
        os.system(command)
# end say_    

