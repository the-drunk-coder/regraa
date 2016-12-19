"""
In this file, find the functions that actually trigger the sound generators.

reGraa doesn't use it's own sound generation, but different backends, as seen below.

"""
import atexit, os, copy
from pygame import midi
from pygame import time as pg_time 
from regraa_pitch import *
from regraa_reactive_base import *
from regraa_dynamic_parametrization import *
import regraa_supercollider_client as sc_client
import regraa_akita_client as akita_client
from random import randint 
import regraa_osc_tools as osc_tools
from regraa_defaults import regraa_defaults as default 

class sound_event(event):
    def __init__(self, gain=0.5, dur=0):
        #print("init sound_event " + str(gain))
        self.gain = gain
        self.dur = dur
        self.additional_latency = 0
        self.scatter = 0
        self.temp_params = {}
    def play(self):
        raise NotImplementedError
    # method to be called before pushed to subscribers, i.e. to update latency and the like
    def update(self):
        for key in self.__dict__.keys():
            if type(self.__dict__[key]) is dpar:
                if self.__dict__[key].is_fading:
                    self.__dict__[key].process_fade()
    def resolve_params(self):       
        for key in self.__dict__.keys():
            if type(self.__dict__[key]) is dpar:
                if self.__dict__[key].is_fading:
                    temp_res = self.__dict__[key].get_value()
                else:
                    temp_res = self.__dict__[key].resolve()
                self.temp_params[key] = self.__dict__[key]                               
                #print("resolve " + key + " " + str(temp_res))
                #print("temp pre: " + str(self.temp_params[key]))
                #print("orig pre: " + str(self.__dict__[key]))
                self.__dict__[key] = temp_res
    def unresolve_params(self):
        for key in self.temp_params.keys():
            #print("unresolve " + key)
            self.__dict__[key] = self.temp_params[key]
            #print("temp post: " + str(self.temp_params[key]))
            #print("orig post: " + str(self.__dict__[key]))
        self.temp_params = {}
        
class silent_event(event):
    def __init__(self, gain=0.5, dur=0):
        sound_event.__init__(self, gain = gain, dur = dur)
    def play(self):
        pass

class akita_param_event(sound_event):
    def __init__(self, gain=0.5, dur=0):
        sound_event.__init__(self, gain = gain, dur = dur)
    def play(self):
        pass
    
class tuned_sound_event(sound_event):
    def __init__(self, *args, gain=0.5, dur=256):
        sound_event.__init__(self, gain = gain, dur = dur)
        self.pitch = args[0]

class synth_sound_event(sound_event):
    def __init__(self, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        #print("init synth_sound_event " + str(gain))
        sound_event.__init__(self, gain = gain, dur = dur)        
        self.sustain = dur - a - d - r
        self.attack = a
        self.decay = d
        self.release = r
        self.rev = rev
        self.pan = pan
        self.lp_cutoff = lp_cutoff
    def get_sustain(self):
        self.sustain = self.dur - self.attack - self.decay - self.release
        return self.sustain    
    def get_osc_bundle(self):
        if(self.rev > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        if type(self.lp_cutoff) is regraa_pitch:
            co_freq = self.lp_cutoff.pitch.frequency
        else:
            co_freq = self.lp_cutoff
        message = osc_tools.build_message("/s_new", current_synth_name, -1, 0, 1,
                          "gain", max(0.0, min(self.gain,  1.1)),
                          "a", self.attack / 1000,
                          "d", self.decay / 1000,
                          "s", self.get_sustain() / 1000,
                          "r", self.release / 1000,
                          "rev", self.rev,
                          "pan", self.pan,
                          "lp_cutoff", co_freq)
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end synth_sound_event

class akita_(sound_event):
    def __init__(self, instance, start=0.0, dur=256, fade_in=0, fade_out=0, gain=0.2, flippiness=0.0, fuzziness=0.0, rev=0.0,
                 lp_cutoff=20000, lp_q=2, mean_filter_on=0, sample_repeat=1, samplerate_mod=1, pan=0.5,
                 pf_q=1.0, pf_gain=0.0, pf_freq=1000, hp_q = 1.0, hp_cutoff=1 ):        
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
        self.lp_q = lp_q
        self.lp_cutoff = lp_cutoff
        self.sample_repeat = sample_repeat
        self.samplerate_mod = samplerate_mod
        self.pan = pan
        self.pf_q = pf_q
        self.pf_freq = pf_freq
        self.pf_gain = pf_gain
        self.hp_q = hp_q
        self.hp_cutoff = hp_cutoff
    def update(self):
        self.additional_latency = default.akita_latency
        sound_event.update(self)
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
                                          float(self.pf_q),
                                          float(self.pf_freq),
                                          float(self.pf_gain),
                                          float(self.hp_q),
                                          float(self.hp_cutoff))
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_

class akita_param_(akita_param_event):
    def __init__(self, instance, gain=0.2, flippiness=0.0, fuzziness=0.0, rev=0.0, lp_cutoff=20000, lp_q=2,
                 mean_filter_on=0, sample_repeat=1, samplerate_mod=1, pan=0.5,
                 pf_q=1.0, pf_gain=0.0, pf_freq=1000, hp_q = 1.0, hp_cutoff=1):        
        akita_param_event.__init__(self, gain = gain, dur = 0)
        self.additional_latency = default.akita_latency
        self.instance = instance        
        self.flippiness = flippiness
        self.fuzziness = fuzziness
        self.rev = rev
        self.mean_filter_on = mean_filter_on
        self.lp_q = lp_q
        self.lp_cutoff = lp_cutoff
        self.sample_repeat = sample_repeat
        self.samplerate_mod = samplerate_mod
        self.pan = pan
        self.pf_q = pf_q
        self.pf_freq = pf_freq
        self.pf_gain = pf_gain
        self.hp_q = hp_q
        self.hp_cutoff = hp_cutoff
    def update(self):
        self.additional_latency = default.akita_latency
        sound_event.update(self)
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
                                          float(self.pf_q),
                                          float(self.pf_freq),
                                          float(self.pf_gain),
                                          float(self.hp_q),
                                          float(self.hp_cutoff))
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_


class akita_nl_(akita_param_event):
    def __init__(self, instance,
                 kn = 0.9, kp = 0.9, gn = 1.0,
		      gp = 1.0, alpha_mix = 0.5, gain_sc = 1.0,
		      g_pre = 1.0, g_post = 1.0, lp_cutoff = 2000, on=0):        
        akita_param_event.__init__(self, gain = 0, dur = 0)        
        self.additional_latency = default.akita_latency
        self.instance = instance
        self.kn = kn
        self.kp = kp
        self.gn = gn
        self.gp = gp
        self.alpha_mix = alpha_mix
        self.gain_sc = gain_sc
        self.g_pre = g_pre
        self.g_post = g_post
        self.lp_cutoff = lp_cutoff
        self.on = on
    def update(self):
        self.additional_latency = default.akita_latency
        sound_event.update(self)
    def get_osc_bundle(self):            
        message = osc_tools.build_message("/akita/param/nonlin",                                          
                                          float(self.kn),
                                          float(self.kp),                                          
                                          float(self.gn),
                                          float(self.gp),
                                          float(self.alpha_mix),
                                          float(self.gain_sc),                                          
                                          float(self.g_pre),
                                          float(self.g_post),
                                          float(self.lp_cutoff),
                                          int(self.on))                                          
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_nl_param

class akita_lti1_(akita_param_event):
    def __init__(self, instance,
                 hp_cutoff=1, hp_q=1,
                 pf_freq=5000, pf_q=300, pf_gain=0.0,
                 lp_cutoff=20000, lp_q=1):
                 
        akita_param_event.__init__(self, gain = 0, dur = 0)        
        self.additional_latency = default.akita_latency
        self.instance = instance
        self.hp_cutoff = hp_cutoff;
        self.hp_q = hp_q;
        self.pf_freq = pf_freq;
        self.pf_gain = pf_gain;
        self.pf_q = pf_q;        
        self.lp_cutoff = lp_cutoff;
        self.lp_q = lp_q;        
    def update(self):
        self.additional_latency = default.akita_latency
        sound_event.update(self)
    def get_osc_bundle(self):            
        message = osc_tools.build_message("/akita/param/lti/one",                                          
                                          float(self.hp_q),
                                          float(self.hp_cutoff),                                          
                                          float(self.pf_q),
                                          float(self.pf_freqreq),
                                          float(self.pf_gain),
                                          float(self.lp_q),                                          
                                          float(self.lp_cutoff))                                          
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_nl_param

class akita_lti2_(akita_param_event):
    def __init__(self, instance,
                 hp_cutoff=1, hp_q=1,
                 pf_freq=5000, pf_q=300, pf_gain=0.0,
                 lp_cutoff=20000, lp_q=1):
                 
        akita_param_event.__init__(self, gain = 0, dur = 0)        
        self.additional_latency = default.akita_latency
        self.instance = instance
        self.hp_cutoff = hp_cutoff;
        self.hp_q = hp_q;
        self.pf_freq = pf_freq;
        self.pf_gain = pf_gain;
        self.pf_q = pf_q;        
        self.lp_cutoff = lp_cutoff;
        self.lp_q = lp_q;        
    def update(self):
        self.additional_latency = default.akita_latency
        sound_event.update(self)        
    def get_osc_bundle(self):            
        message = osc_tools.build_message("/akita/param/lti/two",                                          
                                          float(self.hp_q),
                                          float(self.hp_cutoff),                                          
                                          float(self.pf_q),
                                          float(self.pf_freq),
                                          float(self.pf_gain),
                                          float(self.lp_q),                                          
                                          float(self.lp_cutoff))                                          
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end akita_nl_param

class sample_sound_event(synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=0, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, lp_cutoff=20000, lp_q=1, hp_cutoff=15, hp_q=1, pf_freq=1000, pf_gain=0, pf_q=1):
        #print("init sample_sound_event " + str(gain))
        synth_sound_event.__init__(self, gain=gain, dur=dur, a=a, d=0, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
        self.folder = str(args[0])
        self.name = str(args[1])        
        self.speed = speed
        #print(self.speed)
        self.start = float(start)        
        self.lp_q = lp_q
        self.hp_cutoff = hp_cutoff
        self.hp_q = hp_q
        self.pf_freq = pf_freq
        self.pf_q = pf_q
        self.pf_gain = pf_gain
        sc_client.register_sample(self.folder, self.name)
    def get_osc_bundle(self):
        if(self.rev > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        if type(self.lp_cutoff) is regraa_pitch:
            co_lp_freq = self.lp_cutoff.pitch.frequency
        else:
            co_lp_freq = self.lp_cutoff
        if type(self.hp_cutoff) is regraa_pitch:
            co_hp_freq = self.hp_cutoff.pitch.frequency
        else:
            co_hp_freq = self.hp_cutoff
        if type(self.pf_freq) is regraa_pitch:
            co_pf_freq = self.pf_freq.pitch.frequency
        else:
            co_pf_freq = self.pf_freq
        #print(co_hp_freq)
        #print(co_lp_freq)
        #print(co_pf_freq)
        #print(float(self.dur) / 1000.0)
        #print(self.gain)
        #print(float(self.dur) / 1000.0)
        #print(float(self.attack) / 1000.0)
        #print(float(self.release) / 1000.0)        
        message = osc_tools.build_message("/s_new", current_synth_name, -1, 0, 1,
                                          "bufnum", sc_client.samples[self.folder + ":" + self.name],
                                          "speed", self.speed,
                                          "rev", self.rev,
                                          "pan", self.pan,
                                          "lp_cutoff", co_lp_freq,
                                          "lp_q", self.lp_q,
                                          "hp_cutoff", co_hp_freq,
                                          "hp_q", self.hp_q,
                                          "pf_freq", co_pf_freq,
                                          "pf_gain", self.pf_gain,
                                          "pf_q", self.pf_q,
                                          "gain", max(0.0, min(self.gain,  1.1)),
                                          "start", self.start,
                                          "length", float(self.dur) / 1000.0,
                                          "a", float(self.attack) / 1000.0,
                                          "r", float(self.release) / 1000.0)
        return osc_tools.build_bundle(self.ntp_timestamp, message)
# end sample_sound_event()

class tuned_synth_sound_event(synth_sound_event, tuned_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        tuned_sound_event.__init__(self, args[0], gain=gain, dur=dur)
        synth_sound_event.__init__(self, gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)        
    def get_osc_bundle(self):
        if(self.rev > 0.0):
            current_synth_name = self.synth_name + "rev"
        else:
            current_synth_name = self.synth_name
        if type(self.lp_cutoff) is regraa_pitch:
            co_freq = self.lp_cutoff.pitch.frequency
        else:
            co_freq = self.lp_cutoff
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
                          "lp_cutoff", co_freq)
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

class bow_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "bow"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end bow_


class beep_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "beep"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end beep_

class sine_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "sine"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end sine_

class sqr_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "sqr"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end sqr_

class buzz_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "buzz"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end buzz_

class subt_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "subt"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end subt_

class risset_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "risset"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end risset_

class pluck_(tuned_synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "pluck"
        tuned_synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)
# end pluck_

class noise_(synth_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, d=5, r=5, rev=0.0, pan=0.0, lp_cutoff=15000):
        self.synth_name = "noise"
        synth_sound_event.__init__(self, args[0], gain=gain, dur=dur, a=a, d=d, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff)        
# end noise_

class sample_(sample_sound_event):
    def __init__(self, *args, gain=0.5, dur=0, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, lp_cutoff=20000, lp_q=1, hp_cutoff=15, hp_q=1, pf_freq=1000, pf_gain=0, pf_q=1):
        if dur > 0.0:
            self.synth_name="grain"
        else:
            self.synth_name="sampl"    
        #print("init sample_ " + str(gain))
        sample_sound_event.__init__(self, args[0], args[1],
                                    speed=speed, gain=gain, dur=dur,
                                    a=a, r=r, rev=rev, pan=pan,
                                    lp_cutoff=lp_cutoff, lp_q=lp_q,
                                    hp_cutoff=hp_cutoff, hp_q=hp_q,
                                    pf_freq=pf_freq, pf_q=pf_q, pf_gain=pf_gain,
                                    start=start)
# end sample_
        
class sample8ch_(sample_sound_event):
    def __init__(self, *args, gain=0.5, dur=256, a=4, speed=1.0, start=0.0, r=5, rev=0.0, pan=0.0, lp_cutoff=20000, lp_q=1, hp_cutoff=15, hp_q=1, pf_freq=1000, pf_gain=0, pf_q=1):
        if dur > 0.0:
            self.synth_name="grain8"
        else:
            self.synth_name="sampl8"    
        sample_sound_event.__init__(self, args[0], args[1], speed=speed, gain=gain, dur=dur, a=a, r=r, rev=rev, pan=pan, lp_cutoff=lp_cutoff, start=start)
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

