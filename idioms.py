I, I6, I64 = 1_530, 1_630, 1_640
II, II6 = 2_530, 2_630
IV = 4_530
V, V6  = 5_530, 5_630
V7, V65, V43, V42 = 5_753, 5_653, 5_643, 5_642
VII6 = 7_630

modes = {
	"aeolian": (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24), 
	"ionian": (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24)
}
major_scales = {"C":"#", "G":"#", "D":"#", "A":"#", "E":"#", "B":"#", 
	"F#":"#", "Db":"b", "Ab":"b", "Eb":"b", "Bb":"b", "F":"b"
}
minor_scales = {"A":"#", "E":"#", "B":"#", "F#":"#", "C#":"#", "G#":"#", 
	"D#":"#", "Bb":"b", "F":"b", "C":"b", "G":"b", "D":"b"
}

"""Do you need pedantic accidental designations based on key signature such as Cb or E#
if so use all_notes instead of tonics variable, 
the latter of which has dependencies"""

all_notes = (
	"A", ("A#","Bb"), "B", "C", ("C#", "Db"), "D",
	"E", ("F"), ("F#", "Gb"), "G", ("G#", "Ab")
)
tonics = {
	"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
	"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
}
"""tuple with one item needs comma. Negative chords denote descent
You can create fake passing chords by combining accents"""

# Converting pitch to scale degree
major_scale_degrees = { 0:0, 2:1, 4:2, 5:3, 7:4, 9:5, 11:6 }
minor_scale_degrees = { 0:0, 2:1, 3:2, 5:3, 7:4, 8:5, 10:6, 11:6 }

expand_tonic1 = {
	I: ((-V6, I), (VII6, I6), (VII6, -I), (-V65, I6), (V43, I6), 
		(V42, -I6), (-V65, I), (V43, -I)), 
	I6: ((-V6, I), (-VII6, I6), (-VII6, -I), (-V65, I), (-V43, -I), 
		(V42, -I6), (-V43, I6))
}

expand_tonic2 = {
	I: ((-V6, V43, -I), (V43, -V65, I), (-V65, V43, -I), (-V6, VII6, -I), 
		(-V65, VII6, -I)),
}
accent_tonic = {
	I: (I6,), I6: (-I,)
}
tonic_to_subdom = {
	I: (II, II6, IV), I6: (II6, IV)
}
accent_subdom = {
	II: (II6,), II6: (-II,), IV: (-II, II6)
}
"""Custom IV key for following dict"""
expand_subdom = {
	II: ((I6, II6),), II6: ((-I6, -II),), IV: ((II6, II),(II, II6))
}
subdom_to_dom = {
	II: (V, V7, -V65), II6: (V, V7, V42), IV: (V, V7, V42)
}
accent_dom = {
	V: (V6, V65), V6: (-V,), I64: (V, V7, V42)
}
bass_notes = {
	I:0, II: 1, V43: 1, VII6: 1, I6: 2, IV: 3, II6: 3, V42: 3, V: 4, V7: 4, 
	I64: 4, V6: 6, V65: 6
}
dom_to_tonic = {
	V: (-I,), V7: (-I,), V6: (I,), V65: (I,),  V43:(-I,), V42: (-I,)
}
# Flat is better than nested
chord_tones = {
	I: (0, 2, 4), I6: (0, 2, 4), I64: (0, 2, 4), II: (1, 3, 5),  II6: (1, 3, 5), 
	IV: (3, 5, 0), V: (1, 4, 6), V6: (1, 4, 6), VII6: (1, 3, 6), 
	V7: (1, 3, 4, 6), V65: (1, 3, 4, 6), V43: (1, 3, 4, 6), V42: (1, 3, 4, 6)
}
"""A and P for accent and passing chords. Both are based on preceding chords
An accent chord sequence is a single chord added to a sequence. Addendum of 1 (e.g., I6)
Passing chord: I VII6 I. Addendum of 2. First chord from prior sequence.
A to P is an accent chord that become a passing chord: I6 I VII6 I Addendum of 3
First chord from prior sequence. I is the accent here. """
antecedent = {
	("P","A"):(2,2,2,2), ("A","P","A"): (2,1,1,2,2), ("A","A","P"):(2,2,1,1,2),
	("A","P","P"):(2,1,1,1,1,2), ("P","P","A"): (1,1,1,1,2,2), 
	("P","A","P"): (1,1,2,1,1,2), ("A","A","P","A"): (1,1,1,1,2,2),
	("A","A","DP"): (2,2,1,1,1,1), ("DP", "A", "A"): (1,1,1,1,2,2,)
}
"""F denotes the final chord, dominant or tonic depending on half/authentic cadence. 
Final dominant can be V7 or V. Some chord combos may have multiple possible note combos
This is designated with numbers. S for subdominant C for I64"""
consequent1 = {
	("AS","AS","FD"): (2,2,4), ("AS","AS","AS","FD"): (2,2,2,2), 
	("AS","PS","FD"): (1,1,2,4), ("AS","PS","PS","FD"):(1,1,1,1,2,2),
	("AS1","PS","FD"): (2,2,2,2), ("AS","AS","CD","FD"): (2,2,2,2),
	("AS","CD","FD"): (2,2,4), ("AS","PS","CD","FD"): (1,1,2,2,2),
}

"""FT: Final tonic"""
consequent2 = {
	("AS","AS","AD","FT"): (2,2,2,2), ("AS","AD","FT"): (2,2,4),
	("AS","AS1","AD","FT"): (2,1,1,4), ("AS","CD","AD","FT"): (2,2,2,2),
	("AS","CD","AD", "FT"): (2,1,1,4)
}
names = {
	"1":"I", "2":"II", "3":"III", "4":"IV", "5":"V", "6":"VI", "7":"VII",
	"530":"", "753":"7", "630":"6", "653": "65", "640":"64", 
	"643": "43", "642":"42"   
}

interval_names = {
	(0,0): "P8", (0,1): "d2", (1,0): "A1", (1,1): "m2", (2,1): "M2", (2,2): "d3",
	(3,1): "A2", (3,2): "m3", (4,2): "M3", (4,3): "d4", (5,2): "A3", (5,3): "P4",
	(6,3): "A4", (6,4): "d5", (7,4): "P5", (7,5): "d6", (8,4): "A5", (8,5): "m6",
	(9,5): "M6", (9,6): "d7", (10,5): "A6", (10,6): "m7", (11,6): "M7", 
	(11,7): "d8", (0,6): "A7"
}

harmonic_dissonance = ("d2", "A1", "m2", "M2", "d3", "A2", "d4", "A3", "P4", 
	"A4", "d5", "d6", "A5", "d7", "A6", "m7", "M7", "d8")