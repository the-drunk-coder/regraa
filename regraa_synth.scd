o = Server.local.options;
o.memSize.postln;
o.memSize = 8192;

SynthDef.new(\buzz, { | freq, gain, a, d, s, r, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env.new([lim_freq, lim_cutoff, lim_cutoff * 0.5, lim_cutoff * 0.5, 0], [a, d, s, r]);
	var ampenv = Env.new([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFSaw.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\sqr, { | freq, gain, a, d, s, r, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([freq, lim_cutoff, lim_cutoff * 0.5, lim_cutoff * 0.5, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFPulse.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\sine, { | freq, gain, a, d, s, r, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = SinOsc.ar(freq) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\noise, { | gain, a, d, s, r, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = WhiteNoise.ar() * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\subt, { | freq, gain, a, d, s, r, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = Resonz.ar(Resonz.ar(BPF.ar(WhiteNoise.ar(), freq, 0.1, 3),freq, 0.1, 3), freq, 0.1, 3) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\subtrev, { | freq, gain, a, d, s, r, pan, rev |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = Resonz.ar(Resonz.ar(BPF.ar(WhiteNoise.ar(), freq, 0.1, 3),freq, 0.1, 3), freq, 0.1, 3) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\noiserev, { | gain, a, d, s, r, rev, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = WhiteNoise.ar() * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\sinerev, { | freq, gain, a, d, s, r, rev, pan |
	var lim_gain = min(gain, 1.1);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = SinOsc.ar(freq) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\buzzrev, { | freq, gain, a, d, s, r, rev, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFSaw.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\sqrrev, { | freq, gain, a, d, s, r, rev, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(LFPulse.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef(\sampl, {| bufnum, gain, start, rev, pan, lp_cutoff, lp_q, hp_cutoff, hp_q, pf_freq, pf_q, pf_gain, speed |
	//var lim_cutoff = min(cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var length = BufDur.ir(bufnum);
	var sample = PlayBuf.ar(1, bufnum, speed, 1, length * 44100 * start, doneAction:2);
	var sample_hp = BHiPass.ar(sample, hp_cutoff, hp_q);
	var sample_peak = BPeakEQ.ar(sample_hp, pf_freq, pf_q, pf_gain);
	var sample_lp = BLowPass.ar(sample_peak, lp_cutoff, lp_q);
	//var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, length * 44100 * start,  doneAction:2), cutoff) * gain;
	Out.ar(0, Pan2.ar(sample_lp * lim_gain, pan));
	}
).store;

SynthDef(\samplrev, {| bufnum, gain, start, rev, pan, lp_cutoff, lp_q, hp_cutoff, hp_q, pf_freq, pf_q, pf_gain, speed |
	//var lim_cutoff = min(cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var length =  BufDur.ir(bufnum);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sample = PlayBuf.ar(1, bufnum, speed, 1, length * 44100 * start, doneAction:2);
	var sample_hp = BHiPass.ar(sample, hp_cutoff, hp_q);
	var sample_peak = BPeakEQ.ar(sample_hp, pf_freq, pf_q, pf_gain);
	var sample_lp = BLowPass.ar(sample_peak, lp_cutoff, lp_q);
	var revsampl = FreeVerb.ar(sample_lp * lim_gain, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, Pan2.ar(revsampl, pan));
	}
).store;

// initial envelope on sample, the cleanest one with only one limiter, just getting rid of the clicks ...
SynthDef(\grain, {| bufnum, gain, start, length, a, r, rev, pan, lp_cutoff, lp_q, hp_cutoff, hp_q, pf_freq, pf_q, pf_gain, speed |
	var lim_gain = min(gain, 1.0);
	//var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length - a - r, r], curve:'wel');
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length - a - r, r]);
	var sample = PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start);
	var sample_hp = BHiPass.ar(sample, hp_cutoff, hp_q);
	var sample_peak = BPeakEQ.ar(sample_hp, pf_freq, pf_q, pf_gain);
	var sample_lp = BLowPass.ar(sample_peak, lp_cutoff, lp_q);
	var sample_env = Limiter.ar(sample_lp, level:1.0, dur:0.006);
	Out.ar(0, Pan2.ar(sample_env * EnvGen.ar(cutenv, doneAction:2), pan));
	}
).store;

SynthDef(\grainrev, {| bufnum, gain, start, length, a, r, rev, pan, lp_cutoff, lp_q, hp_cutoff, hp_q, pf_freq, pf_q, pf_gain, speed |
	var lim_gain = min(gain, 1.0);
	//var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length - a - r, r], curve:'wel');
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length - a - r, r]);
	var sample = PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start);
	var sample_hp = BHiPass.ar(sample, hp_cutoff, hp_q);
	var sample_peak = BPeakEQ.ar(sample_hp, pf_freq, pf_q, pf_gain);
	var sample_lp = BLowPass.ar(sample_peak, lp_cutoff, lp_q);
	var sample_env = Limiter.ar(sample_lp * EnvGen.ar(cutenv), level:1.0, dur:0.006);
	var revsampl = FreeVerb.ar(sample_env, mix:rev, room:0.6) + (sample_env * (1 - rev));
	//DetectSilence.ar(revsampl, doneAction:2);
    var revenv = Env.new([0, 1.0, 1.0, 0], [0, length + a + r + 1.4, 0.6]);
	Out.ar(0, Pan2.ar(revsampl  * EnvGen.ar(revenv, doneAction:2), pan));
	}
).store;

// 8-Channel versions of sampl and grain ... channels ('pan' argument) reach from 0 to 7
SynthDef(\sampl8, {| bufnum, gain, start, rev, pan, lp_cutoff, speed |
	var lim_cutoff = min(lp_cutoff, 20000);
	var lim_gain = min(gain, 1.1);
	var length = BufDur.ir(bufnum);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, length * 44100 * start,  doneAction:2), lp_cutoff) * gain;
	Out.ar(0, PanAz.ar(8, sampl, pan * 0.25, orientation:0));
	}
).store;

SynthDef(\sampl8rev, {| bufnum, gain, start, rev, pan, lp_cutoff, speed |
	//var lim_cutoff = min(lp_cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var length =  BufDur.ir(bufnum);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed), lp_cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, PanAz.ar(8, revsampl, pan * 0.25, orientation:0));
	}
).store;

SynthDef(\grain8, {| bufnum, gain, start, length, rev, pan, lp_cutoff, speed |
	var lim_gain = min(gain, 1.0);
	//var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length - a - r, r], curve:'wel');
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [a, length - a - r, r]);
	var sample = PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start);
	var sample_hp = BHiPass.ar(sample, hp_cutoff, hp_q);
	var sample_peak = BPeakEQ.ar(sample_hp, pf_freq, pf_q, pf_gain);
	var sample_lp = BLowPass.ar(sample_peak, lp_cutoff, lp_q);
	var sample_env = Limiter.ar(sample_lp, level:1.0, dur:0.006);
	Out.ar(0, PanAz.ar(8, sample_env * EnvGen.ar(cutenv, doneAction:2), pan * 0.25, orientation:0));
	}
).store;

SynthDef(\grain8rev, {| bufnum, gain, start, length, rev, pan, lp_cutoff, speed |
	//var lim_cutoff = min(lp_cutoff,20000);
	var lim_gain = min(gain, 1.1);
	var cutenv = Env.new([0, lim_gain, lim_gain, 0], [0.004, length - 0.008, 0.004]);
	var sampl = LPF.ar(PlayBuf.ar(1, bufnum, speed, 1, startPos: BufDur.ir(bufnum) * 44100 * start), lp_cutoff) * EnvGen.ar(cutenv);
	var revsampl = FreeVerb.ar(sampl, mix:rev, room:0.6);
	DetectSilence.ar(revsampl, doneAction:2);
	Out.ar(0, PanAz.ar(8, revsampl, pan * 0.25, orientation:0));
	}
).store;

// Based on the risset port by Frederik Oloffson
SynthDef(\risset, {|freq, gain, a, d, s, r, pan, lp_cutoff|
	var length = a + d + s + r;
	var amps= #[1, 0.67, 1, 1.8, 2.67, 1.67, 1.46, 1.33, 1.33, 1, 1.33];
	var durs= #[1, 0.9, 0.65, 0.55, 0.325, 0.35, 0.25, 0.2, 0.15, 0.1, 0.075];
	var frqs= #[0.56, 0.56, 0.92, 0.92, 1.19, 1.7, 2, 2.74, 3, 3.76, 4.07];
	var dets= #[0, 1, 0, 1.7, 0, 0, 0, 0, 0, 0, 0];
	var src= LPF.ar(Mix.fill(11, {|i|
		var env= EnvGen.ar(Env.perc(0.005, length*durs[i], amps[i], -4.5), 1);
		SinOsc.ar(freq*frqs[i]+dets[i], 0, gain*env);
	}), lp_cutoff);
	Out.ar(0, Pan2.ar(src, pan));
}).store;

// Based on the risset port by Frederik Oloffson
SynthDef(\rissetrev, {|freq, gain, a, d, s, r, pan, rev, lp_cutoff|
	var length = a + d + s + r;
	var amps= #[1, 0.67, 1, 1.8, 2.67, 1.67, 1.46, 1.33, 1.33, 1, 1.33];
	var durs= #[1, 0.9, 0.65, 0.55, 0.325, 0.35, 0.25, 0.2, 0.15, 0.1, 0.075];
	var frqs= #[0.56, 0.56, 0.92, 0.92, 1.19, 1.7, 2, 2.74, 3, 3.76, 4.07];
	var dets= #[0, 1, 0, 1.7, 0, 0, 0, 0, 0, 0, 0];
	var src= LPF.ar(Mix.fill(11, {|i|
		var env= EnvGen.ar(Env.perc(0.005, length*durs[i], amps[i], -4.5), 1);
		SinOsc.ar(freq*frqs[i]+dets[i], 0, gain*env);
	}), lp_cutoff);
	var revsrc = FreeVerb.ar(src, mix:rev, room:0.6);
	DetectSilence.ar(revsrc, doneAction:2);
	Out.ar(0, Pan2.ar(revsrc, pan));
}).store;

SynthDef(\pluck, {|out=0, freq=440, pan=0, length=0.5, gain=0.3, lp_cutoff=12000 |
	var lim_cutoff = min(lp_cutoff,20000);
	var lim_freq = min(freq, 15000);
	var pluck, period, string, snd, filterenv;
	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	period = freq.reciprocal;
	string = CombL.ar(pluck, period, period, length*6);
	string = LeakDC.ar(LPF.ar(Pan2.ar(string, pan), lp_cutoff));
	filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [3, 60, 100, 100]);
	snd = BLowPass4.ar(string, EnvGen.ar(filterenv)) * gain;
	DetectSilence.ar(snd, doneAction:2);
	Out.ar(0, string)
}).store;

SynthDef(\pluckrev, {|out=0, freq=440, pan=0, length=0.5, gain=0.3, lp_cutoff=12000, rev=0.1|
	var lim_cutoff = min(lp_cutoff,20000);
	var lim_freq = min(freq, 15000);
	var pluck, period, string, snd, revsnd, filterenv;
	pluck = PinkNoise.ar(Decay.kr(Impulse.kr(0.005), 0.05));
	period = freq.reciprocal;
	string = CombL.ar(pluck, period, period, length*6);
	string = LeakDC.ar(LPF.ar(Pan2.ar(string, pan), lp_cutoff));
	filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [3, 60, 100, 100]);
	snd = BLowPass4.ar(string, EnvGen.ar(filterenv)) * gain;
	revsnd = FreeVerb.ar(snd, mix:rev, room:0.2);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, revsnd)
}).store;

SynthDef.new(\beep, { | freq, gain, a, d, s, r, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env.new([lim_freq, lim_cutoff, lim_cutoff * 0.5, lim_cutoff * 0.5, 0], [a, d, s, r]);
	var ampenv = Env.new([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(Beep.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\beeprev, { | freq, gain, a, d, s, r, rev, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(Beep.ar(freq), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;

SynthDef.new(\bow, { | freq, gain, a, d, s, r, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env.new([lim_freq, lim_cutoff, lim_cutoff * 0.5, lim_cutoff * 0.5, 0], [a, d, s, r]);
	var ampenv = Env.new([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(StkInst.ar(Stk.at("Bowed"),freq, 1, gain, 0.5,[2,64, 4,17,11,52,1,0,23,128,128]), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv, doneAction: 2);
	Out.ar(0, Pan2.ar(snd, pan))
	}
).store;

SynthDef.new(\bowrev, { | freq, gain, a, d, s, r, rev, lp_cutoff, pan |
	var lim_cutoff = min(lp_cutoff,15000);
	var lim_freq = min(freq, 15000);
	var lim_gain = min(gain, 1.1);
	var filterenv = Env([lim_freq, lim_cutoff, lim_cutoff * 0.8, lim_cutoff * 0.8, 0], [a, d, s, r]);
	var ampenv = Env([0, lim_gain, lim_gain*0.7, lim_gain*0.7, 0], [a, d, s, r]);
	var snd = BLowPass4.ar(StkInst.ar(Stk.at("Bowed"), freq, 1, gain, 0.5,[2,64, 4,17,11,52,1,0,23,128,128]), EnvGen.ar(filterenv)) * EnvGen.ar(ampenv);
	var revsnd = FreeVerb.ar(snd, mix:rev, room:0.6);
	DetectSilence.ar(revsnd, doneAction:2);
	Out.ar(0, Pan2.ar(revsnd, pan))
	}
).store;
