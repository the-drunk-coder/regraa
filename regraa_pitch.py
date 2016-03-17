from music21 import pitch, duration
import copy

# ensure certain pitch behaviour
class regraa_pitch():    
    def __init__(self, pitch_string):
        self.pitch = pitch.Pitch(pitch_string)                   
    def __add__(self, other):
        new_pitch = copy.deepcopy(self)
        if type(other) is int:
            new_pitch.pitch.midi = self.pitch.midi + other
        if type(other) is float:
            # calculate semitones and microtones
            semitones = int(other)
            micro_ratio = other - semitones
            microtones = int(100 * micro_ratio)
            if semitones > 0:
                new_pitch.pitch.midi += semitones                        
            if microtones > 0:
                old_cents = new_pitch.pitch.microtone.cents
                new_cents = old_cents + microtones
                if new_cents >= 100:
                    new_pitch.pitch.microtone = 0
                    new_pitch.pitch.midi += 1
                    new_cents -= 100
                new_pitch.pitch.microtone = new_cents            
        return new_pitch
    def __sub__(self, other):
        new_pitch = copy.deepcopy(self)
        if type(other) is int:
            new_pitch.pitch.midi -= other
        if type(other) is float:
            # calculate semitones and microtones
            semitones = int(other)
            micro_ratio = other - semitones
            microtones = int(100 * micro_ratio)
            if semitones > 0:
                new_pitch.pitch.midi -= semitones
            if microtones > 0:
                old_cents = new_pitch.pitch.microtone.cents                
                new_cents = old_cents - microtones
                if new_cents <= -100:
                    new_pitch.pitch.microtone = 0
                    new_pitch.pitch.midi -= 1
                    new_cents += 100
                new_pitch.pitch.microtone = new_cents                                                          
        return new_pitch
    def __hash__(self):
        return str(self).__hash__()
    def __lt__(self, other):
        if type(other) is int:
            return self.pitch.midi < other
        else:
            return self.pitch.frequency < other.pitch.frequency       
    def __le__(self, other):
        if type(other) is int:
            return self.pitch.midi <= other
        else:
            return self.pitch.frequency <= other.pitch.frequency
    def __ge__(self, other):        
        if type(other) is int:
            return self.pitch.midi >= other
        else:
            return self.pitch.frequency >= other.pitch.frequency
    def __eq__(self, other):
        if type(other) is int:
            return self.pitch.midi == other
        else:
            return self.pitch.frequency == other.pitch.frequency


# pitch constants
c0 = regraa_pitch("C0")
cis0 = regraa_pitch("C#0")
des0 = regraa_pitch("D-0")
d0 = regraa_pitch("D0")
dis0 = regraa_pitch("D#0")
es0 = regraa_pitch("E-0")
e0 = regraa_pitch("E0")
f0 = regraa_pitch("F0")
fis0 = regraa_pitch("F#0")
ges0 = regraa_pitch("G-0")
g0 = regraa_pitch("G0")
gis0 = regraa_pitch("G#0")
as0 = regraa_pitch("A-0")
a0 = regraa_pitch("A0")
ais0 = regraa_pitch("A#0")
bes0 = regraa_pitch("B-0")
b0 = regraa_pitch("B0")

c1 = regraa_pitch("C1")
cis1 = regraa_pitch("C#1")
des1 = regraa_pitch("D-1")
d1 = regraa_pitch("D1")
dis1 = regraa_pitch("D#1")
es1 = regraa_pitch("E-1")
e1 = regraa_pitch("E1")
f1 = regraa_pitch("F1")
fis1 = regraa_pitch("F#1")
ges1 = regraa_pitch("G-1")
g1 = regraa_pitch("G1")
gis1 = regraa_pitch("G#1")
as1 = regraa_pitch("A-1")
a1 = regraa_pitch("A1")
ais1 = regraa_pitch("A#1")
bes1 = regraa_pitch("B-1")
b1 = regraa_pitch("B1")

c2 = regraa_pitch("C2")
cis2 = regraa_pitch("C#2")
des2 = regraa_pitch("D-2")
d2 = regraa_pitch("D2")
dis2 = regraa_pitch("D#2")
es2 = regraa_pitch("E-2")
e2 = regraa_pitch("E2")
f2 = regraa_pitch("F2")
fis2 = regraa_pitch("F#2")
ges2 = regraa_pitch("G-2")
g2 = regraa_pitch("G2")
gis2 = regraa_pitch("G#2")
as2 = regraa_pitch("A-2")
a2 = regraa_pitch("A2")
ais2 = regraa_pitch("A#2")
bes2 = regraa_pitch("B-2")
b2 = regraa_pitch("B2")

c3 = regraa_pitch("C3")
cis3 = regraa_pitch("C#3")
des3 = regraa_pitch("D-3")
d3 = regraa_pitch("D3")
dis3 = regraa_pitch("D#3")
es3 = regraa_pitch("E-3")
e3 = regraa_pitch("E3")
f3 = regraa_pitch("F3")
fis3 = regraa_pitch("F#3")
ges3 = regraa_pitch("G-3")
g3 = regraa_pitch("G3")
gis3 = regraa_pitch("G#3")
as3 = regraa_pitch("A-3")
a3 = regraa_pitch("A3")
ais3 = regraa_pitch("A#3")
bes3 = regraa_pitch("B-3")
b3 = regraa_pitch("B3")

c4 = regraa_pitch("C4")
cis4 = regraa_pitch("C#4")
des4 = regraa_pitch("D-4")
d4 = regraa_pitch("D4")
dis4 = regraa_pitch("D#4")
es4 = regraa_pitch("E-4")
e4 = regraa_pitch("E4")
f4 = regraa_pitch("F4")
fis4 = regraa_pitch("F#4")
ges4 = regraa_pitch("G-4")
g4 = regraa_pitch("G4")
gis4 = regraa_pitch("G#4")
as4 = regraa_pitch("A-4")
a4 = regraa_pitch("A4")
ais4 = regraa_pitch("A#4")
bes4 = regraa_pitch("B-4")
b4 = regraa_pitch("B4")

c5 = regraa_pitch("C5")
cis5 = regraa_pitch("C#5")
des5 = regraa_pitch("D-5")
d5 = regraa_pitch("D5")
dis5 = regraa_pitch("D#5")
es5 = regraa_pitch("E-5")
e5 = regraa_pitch("E5")
f5 = regraa_pitch("F5")
fis5 = regraa_pitch("F#5")
ges5 = regraa_pitch("G-5")
g5 = regraa_pitch("G5")
gis5 = regraa_pitch("G#5")
as5 = regraa_pitch("A-5")
a5 = regraa_pitch("A5")
ais5 = regraa_pitch("A#5")
bes5 = regraa_pitch("B-5")
b5 = regraa_pitch("B5")

c6 = regraa_pitch("C6")
cis6 = regraa_pitch("C#6")
des6 = regraa_pitch("D-6")
d6 = regraa_pitch("D6")
dis6 = regraa_pitch("D#6")
es6 = regraa_pitch("E-6")
e6 = regraa_pitch("E6")
f6 = regraa_pitch("F6")
fis6 = regraa_pitch("F#6")
ges6 = regraa_pitch("G-6")
g6 = regraa_pitch("G6")
gis6 = regraa_pitch("G#6")
as6 = regraa_pitch("A-6")
a6 = regraa_pitch("A6")
ais6 = regraa_pitch("A#6")
bes6 = regraa_pitch("B-6")
b6 = regraa_pitch("B6")

c7 = regraa_pitch("C7")
cis7 = regraa_pitch("C#7")
des7 = regraa_pitch("D-7")
d7 = regraa_pitch("D7")
dis7 = regraa_pitch("D#7")
es7 = regraa_pitch("E-7")
e7 = regraa_pitch("E7")
f7 = regraa_pitch("F7")
fis7 = regraa_pitch("F#7")
ges7 = regraa_pitch("G-7")
g7 = regraa_pitch("G7")
gis7 = regraa_pitch("G#7")
as7 = regraa_pitch("A-7")
a7 = regraa_pitch("A7")
ais7 = regraa_pitch("A#7")
bes7 = regraa_pitch("B-7")
b7 = regraa_pitch("B7")

c8 = regraa_pitch("C8")
cis8 = regraa_pitch("C#8")
des8 = regraa_pitch("D-8")
d8 = regraa_pitch("D8")
dis8 = regraa_pitch("D#8")
es8 = regraa_pitch("E-8")
e8 = regraa_pitch("E8")
f8 = regraa_pitch("F8")
fis8 = regraa_pitch("F#8")
ges8 = regraa_pitch("G-8")
g8 = regraa_pitch("G8")
gis8 = regraa_pitch("G#8")
as8 = regraa_pitch("A-8")
a8 = regraa_pitch("A8")
ais8 = regraa_pitch("A#8")
bes8 = regraa_pitch("B-8")
b8 = regraa_pitch("B8")

c9 = regraa_pitch("C9")
cis9 = regraa_pitch("C#9")
des9 = regraa_pitch("D-9")
d9 = regraa_pitch("D9")
dis9 = regraa_pitch("D#9")
es9 = regraa_pitch("E-9")
e9 = regraa_pitch("E9")
f9 = regraa_pitch("F9")
fis9 = regraa_pitch("F#9")
ges9 = regraa_pitch("G-9")
g9 = regraa_pitch("G9")
gis9 = regraa_pitch("G#9")
as9 = regraa_pitch("A-9")
a9 = regraa_pitch("A9")
ais9 = regraa_pitch("A#9")
bes9 = regraa_pitch("B-9")
b9 = regraa_pitch("B9")






        
