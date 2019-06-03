# Chords expressed as numbers to allow negative numbers 
# that represent descending motion.
# Add secondary diminished inversions 6/5 moves by half step
I, I6, I64 = 10_530_1, 10_630_1, 10_640_1
I_LYDIAN, I_MAJOR, I_MIXO = 21_530_1, 22_530_1, 23_530_1
I_DORIAN, I_MINOR, I_PHRYG = 24_530_1, 25_530_1, 26_530_1
V7_OF_IV, V65_OF_IV, V43_OF_IV = 50_753_4, 50_653_4, 50_643_4
VII7_OF_II, VII65_OF_II = 70_753_2, 70_653_2
DIM7_DOWN_OF_I = 11_753_1 

II, II6 = 20_530_1, 20_630_1, 
II7, II65, II43, II42 = 20_753_1, 20_653_1, 20_643_1, 20_642_1
II_LYDIAN, II_MAJOR, II_MIXO = 21_530_2, 22_530_2, 23_530_2
II_DORIAN, II_MINOR, II_PHRYG = 24_530_2, 25_530_2, 26_530_2
V7_OF_V, V65_OF_V, V43_OF_V = 50_753_5, 50_653_5, 50_643_5
VII7_OF_III, VII65_OF_III = 70_753_3, 70_653_3
DIM7_DOWN_OF_II = 11_753_2

III = 30_530_1
III_LYDIAN, III_MAJOR, III_MIXO = 21_530_3, 22_530_3, 23_530_3
III_DORIAN, III_MINOR, III_PHRYG = 24_530_3, 25_530_3, 26_530_3
V65_OF_VI, V43_OF_VI = 50_653_6, 50_643_6 
VII7_OF_IV, VII65_OF_IV = 70_753_4, 70_653_4
DIM7_DOWN_OF_III = 11_753_3

IV, IV6, IV7 = 40_530_1, 40_630_1, 40_753_1
IV_LYDIAN, IV_MAJOR, IV_MIXO = 21_530_4, 22_530_4, 23_530_4
IV_DORIAN, IV_MINOR, IV_PHRYG = 24_530_4, 25_530_4, 26_530_4
VII7_OF_V, VII65_OF_V = 11_753_5, 70_653_5
DIM7_DOWN_OF_IV = 11_753_4

V, V6  = 50_530_1, 50_630_1
V_LYDIAN, V_MAJOR, V_MIXO = 21_530_5, 22_530_5, 23_530_5
V_DORIAN, V_MINOR, V_PHRYG = 24_530_5, 25_530_5, 26_530_5
V7, V65, V43, V42 = 50_753_1, 50_653_1, 50_643_1, 50_642_1
VII7_OF_VI, VII65_OF_VI = 70_753_6, 70_653_6
DIM7_DOWN_OF_V = 11_753_5

VI = 60_530_1
VI_LYDIAN, VI_MAJOR, VI_MIXO = 21_530_6, 22_530_6, 23_530_6
VI_DORIAN, VI_MINOR, VI_PHRYG = 24_530_6, 25_530_6, 26_530_6
V7_OF_II, V65_OF_II, V43_OF_II = 50_753_2, 50_653_2, 50_643_2
DIM7_DOWN_OF_VI = 11_753_6

VII6, VII7, VII65 = 70_630_1, 70_753_1, 70_653_1
VII_LYDIAN, VII_MAJOR, VII_MIXO = 21_530_7, 22_530_7, 23_530_7
VII_DORIAN, VII_MINOR, VII_PHRYG = 24_530_7, 25_530_7, 26_530_7
V65_OF_III, V43_OF_III = 50_653_3, 50_643_3

modes = {
	"lydian": (0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24),
	"ionian": (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24),
	"mixo": (0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24),
	"dorian": (0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19, 21, 22, 24),
	"aeolian": (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24),
	"phryg": (0, 1, 3, 5, 7, 8, 10, 12, 13, 15, 17, 19, 20, 22, 24) 
}
major_accidentals = {"C":"#", "G":"#", "D":"#", "A":"#", "E":"#", "B":"#", 
	"F#":"#", "Db":"b", "Ab":"b", "Eb":"b", "Bb":"b", "F":"b"
}
minor_accidentals = {"A":"#", "E":"#", "B":"#", "F#":"#", "C#":"#", "G#":"#", 
	"D#":"#", "Bb":"b", "F":"b", "C":"b", "G":"b", "D":"b"
}
"""Do you need pedantic accidental designations based on key signature 
such as Cb or E#. If so, use all_notes instead of tonics variable, 
the latter of which has dependencies"""
all_notes = (
	"A", ("A#","Bb"), ("B","Cb"), ("B#","C"), ("C#", "Db"), "D",
	("E","Fb"), ("E#","F"), ("F#", "Gb"), "G", ("G#", "Ab")
)
tonics = {
	"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
	"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
}
# Converting pitch to scale degree
major_scale_degrees = { 0:0, 2:1, 4:2, 5:3, 7:4, 9:5, 11:6}
minor_scale_degrees = { 0:0, 2:1, 3:2, 5:3, 7:4, 8:5, 10:6, 11:6}

# These are short chord progression sequences for different scenarios
# Fix DIM7 going down to VI octave drop
expand_tonic1 = {
	I: ((-V6, I), (VII6, I6), (VII6, -I), (-V65, I6), (V43, I6), (V42, -I6), 
		(-V65, I), (V43, -I), (-IV6, -I6), (-VI, -I6),
		(-V43_OF_VI, -VI), (-DIM7_DOWN_OF_VI, -VI), (-VII7_OF_VI, VI)), 
	I6: ((-V6, I), (-VII6, I6), (-VII6, -I), (-V65, I), (-V43, -I), 
		(V42, -I6), (-V43, I6)),
	III: ((-V6, I), (-VII6, I6), (-VII6, -I), (-V65, I), (-V43, -I), 
		(V42, -I6), (-V43, I6)),
}
expand_tonic2 = {
	I: ((-V6, V43, -I), (V43, -V65, I), (-V65, V43, -I), (-V6, VII6, -I), 
		(-V65, VII6, -I)),
}
expand_tonic3 = {
	I: ((-V6, I), (VII6, -I), (-V65, I), (V43, -I), (-VII7, I), 
		(DIM7_DOWN_OF_I, -I))
}
accent_tonic = {
	I: (I6, -VI), I6: (-I,), VI: (-III, -I6)
}
# you can't repeat chord from weak to strong beat
restart_tonic = {
	I: (I6,), I6: (-I,), V: (VI, -I6),
	VI: (I,), V7: (VI, -I6), V65: (I,), V43: (-I, I6), 
	V42: (-I6,),
}
# check for melodic augmented second
tonic_to_subdom1 = {
	I: (II, II6, IV), I6: (II6, IV, -II, -II7, II65), 
	III: (II6, IV, -II, -II7, II65),
	VI: (-IV, -IV7, -II7, -II6, -II65), 
	IV6: (-IV, -IV7, -II6), V7_OF_II: (-II,), V65_OF_II: (II,), V43_OF_II: (-II,), 
	V65_OF_IV: (IV,), V43_OF_IV: (-IV,), V7_OF_IV: (IV,), 
	VII7_OF_II: (II,), DIM7_DOWN_OF_II: (-II,), VII7_OF_IV: (IV,), 
	DIM7_DOWN_OF_IV: (-IV,)
}
tonic_to_subdom2 = {
	I: (V65_OF_II, V43_OF_II, V65_OF_IV, V7_OF_IV, VII7_OF_II, 
		DIM7_DOWN_OF_II, VII7_OF_IV, DIM7_DOWN_OF_IV), 
	I6: (-V65_OF_II, V43_OF_II, V65_OF_IV, V43_OF_IV, -DIM7_DOWN_OF_II, 
		-VII7_OF_II, VII7_OF_IV, DIM7_DOWN_OF_IV),
	VI:(V7_OF_II, -V43_OF_II, -V43_OF_IV, -DIM7_DOWN_OF_II, -VII7_OF_II, 
		-VII7_OF_IV, -DIM7_DOWN_OF_IV)
}
tonic_to_subdom3 = {
	I: ((V65_OF_II, II), (V43_OF_II, -II), (V65_OF_IV, IV), (VII7_OF_II, II), 
		(DIM7_DOWN_OF_II, -II), (VII7_OF_IV, IV), (DIM7_DOWN_OF_IV, -IV)),
	I6: ((-V65_OF_II, II), (V43_OF_II, -II), (V65_OF_IV, IV), (V43_OF_IV, -IV), 
		(-DIM7_DOWN_OF_II, -II), (-VII7_OF_II, II), (VII7_OF_IV, IV), 
		(DIM7_DOWN_OF_IV, -IV)),
	VI: ((V7_OF_II, -II), (-V43_OF_II, -II), (-V43_OF_IV, -IV), 
		(-DIM7_DOWN_OF_II, -II), (-VII7_OF_II, II), (-DIM7_DOWN_OF_IV, -IV), (-VII7_OF_IV, IV))
}
accent_subdom1 = {
	II: (II6,), II6: (-II, -II7), II7: (II65,), II65: (-II7, II43), 
	II43: (-II65,), IV: (-II, II6), IV7: (II65,)
}
expand_subdom1 = {
	II: ((I6, II6), (I6, II65)), II6: ((-I6, -II), (V65_OF_IV, IV)), 
	II7: ((I6, II65),), II65: ((-I6, -II7),), IV: ((II6, -II), (-II, II6), 
		(-V43_OF_II, -II))
}
subdom_to_dom1 = {
	I: (V, -V65, V43), II: (V, -V65), II6: (V, V42), II65: (V,), II43: (-V,), 
	II7: (V,), IV: (V, V42), IV7: (V, V42), I64: (V,)
}
subdom_to_dom2 = {
	II: ((I6, V), (V65_OF_V, V)), II7: ((V7_OF_V, V), (V65_OF_V, V)),
	II6: ((V65_OF_V, V), (V43_OF_V, -V)), II65:((V65_OF_V, V), (V43_OF_V, -V)), 
	II43: (-V43_OF_V, -V), IV: ((V65_OF_V, V), (V43_OF_V, -V)), 
	IV7: ((V65_OF_V,V), (V43_OF_V,-V))
}
subdom_to_dom3 = {
	I: (-V65, V43), I6: (-V43, V42), II: (V43, V42, -V6, -V65), II7: (V43, V42, -V6, -V65), 
	II6: (-V43, V42), II65: (-V43, V42), IV: (-V43, V42), IV7: (-V43, V42)
}
subdom_to_tonic1 = {
	I: ((V43, I6),), I6: ((-V43, I6), (V42, -I6),), II: ((V43, I6), (V42, I6)), 
	II7: ((V43, I6), (V42, I6)), II6: ((-V43, I6), (V42, -I6)), 
	II65: ((-V43, I6), (V42, -I6)), IV: ((-V43, I6), (V42, -I6))
}
accent_dom = {
	V: (V6, V65, V7, -V42), V6: (-V,), I64: (V, V7)
}
dom_to_tonic1 = {
	V: (-I,), V7: (-I,), V6: (I,), V65: (I,),  V43:(-I,), V42: (-I6,)
}
half_cadence = {
	I: (V,), I6: (V,), III: (V,), VI: (-V,), IV6: (-V,), II: (V,), 
	II6: (V,), II7: (V,), II65: (V,), II43: (V,), IV: (V,), IV7: (V)
}
auth_cadence = {
	I: (V, V7), I6: (V, V7), I64: (V, V7) ,III: (V, V7), VI: (-V, -V7), IV6: (-V, -V7), 
	II: (V, V7), II6: (V, V7), II7: (V, V7), II65: (V, V7), II43: (V, V7), 
	IV: (V, V7), IV7: (V, V7)
}

chord_tones = { 
	I: (0,2,4), I6: (0,2,4), I64: (0,2,4), I_MAJOR: (0,2,4), V7_OF_IV:(0,2,4,6), 
	V65_OF_IV: (0,2,4,6), V43_OF_IV: (0,2,4,6), II: (1,3,5),  II6: (1,3,5), 
	II7: (1,3,5,0), II65: (1,3,5,0), II43: (1,3,5,0), II42: (1,3,5,0), 
	V7_OF_V: (1,3,5,0), V65_OF_V: (1,3,5,0), V43_OF_V: (1,3,5,0), III: (2,4,6), 
	V65_OF_VI: (2,4,6,1), V43_OF_VI: (2,4,6,1), IV: (3,5,0), IV6: (3,5,0), 
	IV7: (3,5,0,2), V: (4,6,1), V6: (4,6,1), V7: (4,6,1,3), V65: (4,6,1,3), 
	V43: (4,6,1,3), V42: (4,6,1,3), VI: (5,0,2), V7_OF_II: (5,0,2,4), 
	V65_OF_II: (5,0,2,4), V43_OF_II: (5,0,2,4), VII6: (6,1,3), 
	V65_OF_III: (6,1,3,5), V43_OF_III: (6,1,3,5), VII7: (6,1,3,5), 
	DIM7_DOWN_OF_I:(0,2,4,6),
	VII7_OF_II: (0,2,4,6), DIM7_DOWN_OF_II: (1,3,5,0),
	VII7_OF_III: (1,3,5,0), DIM7_DOWN_OF_III: (2,4,6,1),
	VII7_OF_IV: (2,4,6,1), DIM7_DOWN_OF_IV: (3,5,0,2),
	VII7_OF_V: (3,5,0,2), DIM7_DOWN_OF_V: (4,6,1,3), 
	VII7_OF_VI: (4,6,1,3), DIM7_DOWN_OF_VI: (5,0,2,4)
}

bass_notes = {}
for chord, degrees in chord_tones.items():
	inversion = chord // 10 % 1000
	if inversion in (530, 753):
		bass_notes[chord] = degrees[0]
	elif inversion in (630, 653):
		bass_notes[chord] = degrees[1]
	elif inversion in (640, 643):
		bass_notes[chord] = degrees[2]
	elif inversion == 642:
		bass_notes[chord] = degrees[3]

assert(len(bass_notes.keys()) == len(chord_tones.keys()))

"""Accent chord sequence = attach one chord to progression
Passing chord sequence = attach two chords to progression
Double passing chord sequence = attach three chords to progression
TA = Tonic accent chord. TP = Tonic passing chords. 
0TP = tonic passing chord that returns to itself
TDP = tonic double passing chord
TPS-C = Tonic passing to subdominant (complete)
TPS-I = Tonic passing chord to subdominant with last chord missing (incomplete). 
	Allows overlap with secondary dominants: the end becomes the beginning.
TAS = transition from tonic to subdominant with accent chord
SPD-C = subdominant passing chord to dominant (complete).
	Allows secondary dominants
SA = Subdominant accent chord. SP = sudominant passing chord
SAU = ultimate subdominant accent chord before dominant at cadence
	Allows I64 chord
SAP = penultimate accent chord before dominant at cadence
	Allows Neapolitan + I64 chord
DAU = ultimate dominant accent chord +/- cadence
(I/P)DA = imperfect/perfect dominant accent chord
(I/P)TA = imperfect/perfect tonic accent chord
	Allows imperfect/perfect authentic cadence
BI = Basic idea. CI = Contrasting idea"""
# Explicitly add second chord
# Passing chords, IAC, Extend w/ tonic accent(remove?)
# SAU DAU means PDA ITA etc.  TA only for 4 consecutive 1s
ci1_from_tonic_with_rest = {
	(2,2,2,2):(("TAS","DAU"),),
	(2,1,1,2,2):(("TAS","SAU","DAU"), ("TAS","PDA","ITA"), ("TAS","IDA","PTA"), 
		("TAS","IDAITA"), ("TAS","SPD-C"), ("TPS-C","DAU"), ("TAS","SPD-C"), 
		("TA","TAS","DAU")),
	# (1,1,1,1,2,2):(("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), ("TPS-C","IDA","PTA"), 
	# 	("TPS-C","IDAITA"), ("TPS-C","SPD-C"), ("TAS","SA","SPD-C"), 
	# 	("TAS","SP","DAU"), ("TAS","SAP","SAU","DAU"), ("TAS","SA","PDA","ITA"),
	# 	("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"), ("TA","TPS-C","DAU"),
	# 	("TA","TAS","SPD-C"), ("TA","TAS","SAU","DAU"), ("TA","TAS","PDA","ITA"),
	# 	("TA","TAS","IDA","PTA"), ("TA","TAS","IDAITA")),
	(2,1,2,1):(("TAS","DAU"),), 
	# (1,1,1,2,1): (("TPS-C","DAU"), ("TAS","SPD-C"), ("TAS","SAU","DAU"), 
	# 	("TAS","PDA","ITA"), ("TAS","IDA","PTA"), ("TAS","IDAITA")),
	(4,2,2): (("DAU",),),
	(2,2,4): (("TAS", "DAU"), ("SPD-C",), ("PDA", "ITA"), ("IDA", "PTA"), 
		("IDAITA",)),
	(3,2,1): (("DAU",),),
	(2,1,3): (("TAS", "DAU"), ("SPD-C",), ("PDA", "ITA"), ("IDA", "PTA"), 
		("IDAITA",)),
}
ci2_from_tonic_with_rest = {
	(2,2,2,2):(("PDAX","TAU"),), (2,1,1,2,2):(("TAS","PDAX","TAU"),), 
	# (1,1,1,1,2,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"),
	# 	("TAS","SPD-C","TAU")),
	(2,1,2,1):(("PDAX","TAU"),), 
	# (1,1,1,2,1):(("TAS","PDAX","TAU"),),
	(4,2,2): (("TAU",),),
	(2,2,4): (("PDAX", "TAU"),),
	(3,2,1): (("TAU",),),
	(2,1,3): (("PDAX", "TAU"),)
}
ci1_from_tonic_no_rest = {
	(2,2,2,2):(("TAS","SAU","DAU"), ("TAS","PDA","ITA"), ("TAS","IDA","PTA"), 
		("TPS-C","DAU"), ("TA","TAS","DAU")),
	(2,1,1,2,2):(("TAS","SP","DAU"), ("TAS","SAP","SAU","DAU"), ("TAS","SP","DAU"),
		("TAS","SAU","PDA","ITA"), ("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"), 
		("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), ("TPS-C","IDA","PTA"), 
		("TPS-C", "IDAITA"), ("TA","TPS-C","DAU"), ("TA","TAS","SAU","DAU")),
	# (1,1,1,1,2,2): (("TPS-C","SP","DAU"), ("TPS-C","SAP","SAU","DAU"), 
	# 	("TPS-C","SA","PDA","ITA"), ("TPS-C","SA","IDA","PTA"), 
	# 	("TPS-C","SA","IDAITA"), ("TAS","SP","SAU","DAU"), ("TAS","SP","PDA","ITA"),
	# 	("TAS","SP","IDA","PTA"), ("TAS","SP","IDAITA"), ("TA","TPS-C","SAU","DAU"),
	# 	("TA","TPS-C","PDA","ITA"), ("TA","TPS-C","IDA","PTA"), 
	# 	("TA","TPS-C","IDAITA")),
	(2,1,2,1):(("TPS-C","DAU"), ("TAS","SAU","DAU"), ("TAS","PDA","ITA"), 
		("TAS","IDA","PTA"), ("TAS","IDAITA")),
	# (1,1,1,2,1):(("TPS-C","SAU","DAU"), ("TAS","SAP","SAU","DAU",), 
	# 	("TAS","SA","PDA","ITA"), ("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA")),
	(4,2,2): (("TAS", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
	(2,2,4): (("TAS", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
	(3,2,1): (("TAS", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
	(2,1,3): (("TAS", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
}
ci2_from_tonic_no_rest = {
	(2,2,2,2):(("TAS","PDAX","TAU"),), 
	(2,1,1,2,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"), 
		("TAS","SPD-C","TAU")), 
	# (1,1,1,1,2,2):(("TAS","SAP","SAU","PDAX","TAU"), ("TPS-C","SAU","PDAX","TAU"),
	# 	("TAS","SP","PDAX","TAU"), ("TAS","SA","SPD-C","TAU")), 
	(2,1,2,1):(("TAS","PDAX","TAU"),), 
	# (1,1,1,2,1):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"), 
	# 	("TAS","SPD-C","TAU")),
	(4,2,2): (("PDAX", "TAU"),),
	(2,2,4): (("PDAX", "TAU"),),
	(3,2,1): (("PDAX", "TAU"),),
	(2,1,3): (("PDAX", "TAU"),),
}
ci1_from_subdom_with_rest = {
	(2,2,2,2):(("SAU","DAU"), ("SPD-C",), ("PDA","ITA"), ("IDA","PTA"), 
		("IDAITA",),),
	(2,1,1,2,2):(("SAP","SAU","DAU"), ("SP","DAU"), ("SA","SPD-C"), 
		("SA","PDA","ITA"), ("SA","IDA","PTA"), ("SA","IDAITA")),
	# (1,1,1,1,2,2):(("SP","SPD-C"), ("SP","SAU","DAU"), ("SP","PDA","ITA"), 
	# 	("SP","IDA","PTA"), ("SP","IDAITA"), ("SA","SP","DAU"), 
	# 	("SA","SA","SPD-C")),
	(2,1,2,1):(("SPD-C",), ("SAU","DAU"), ("PDA","ITA"), ("IDA","PTA"), ("IDAITA",)),
	# (1,1,1,2,1):(("SP","DAU"), ("SA","SPD-C")),
	(4,2,2): (("DAU",),),
	(2,2,4): (("SPD-C",), ("SAU", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), 
		("IDAITA",)),
	(3,2,1): (("DAU",),),
	(2,1,3): (("SPD-C",), ("SAU", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), 
		("IDAITA",)),
}
ci2_from_subdom_with_rest = {
	(2,2,2,2):(("PDAX","TAU"),),
	(2,1,1,2,2):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	# (1,1,1,1,2,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"),
	# 	("SA","SPD-C","TAU")),
	(2,1,2,1):(("PDAX","TAU"),), 
	# (1,1,1,2,1):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	(4,2,2): (("TAU",),), # illegal. allow for authentic cadence mandatory no rest
	(2,2,4): (("PDAX", "TAU"),),
	(3,2,1): (("TAU",),),
	(2,1,3): (("PDAX", "TAU"),)
}
ci1_from_subdom_no_rest = {
	(2,2,2,2):(("SAP","SAU","DAU"), ("SP","DAU"), ("SAU","PDA","ITA"), 
		("SA","IDA","PTA"), ("SA","IDAITA")),
	(2,1,1,2,2):(("SA","SP","DAU"), ("SP","SAU","DAU"), ("SP","PDA","ITA"), 
		("SP","IDA","PTA"), ("SP","IDAITA")),
	# (1,1,1,1,2,2): (("SP","SP","DAU"), ("SP","SAP","SAU","DAU"), 
	# 	("SP","SA","PDA","ITA"), ("SP","SA","IDA","PTA"), ("SP","SA","IDAITA")),
	(2,1,2,1):(("SP","DAU"), ("SAP","SAU","DAU"), ("SA","PDA","ITA"), 
		("SA","IDA","PTA"), ("SA","IDAITA")),
	# (1,1,1,2,1):(("SP","SAU","DAU"), ("SP","PDA","ITA"), ("SP","IDA","PTA"), 
	# 	("SP","IDAITA")),
	(4,2,2): (("SAU", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
	(2,2,4): (("SAU", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
	(3,2,1): (("SAU", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
	(2,1,3): (("SAU", "DAU"), ("PDA", "ITA"), ("IDA", "PTA"), ("IDAITA",)),
}
ci2_from_subdom_no_rest = {
	(2,2,2,2):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	(2,1,1,2,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"), 
		("SA","SPD-C","TAU")),
	# (1,1,1,1,2,2):(("SA","SP","PDAX","TAU"), ("SP","SAU","PDAX","TAU"),
	# 	("SP","SPD-C","TAU")),
	(2,1,2,1):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	# (1,1,1,2,1):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"), 
	# 	("SA","SPD-C","TAU")),
	(4,2,2): (("PDAX", "TAU"),),
	(2,2,4): (("PDAX", "TAU"),),
	(3,2,1): (("PDAX", "TAU"),),
	(2,1,3): (("PDAX", "TAU"),),
}

""" Some BI sequences use subdominant chords: subsidiary progression
Numbers in sequences to allow duplicate progressions with different rhythms
Attempting to find all the sweet rhythms (manually)
	Don't use passing chord on strong part of beat!!!!
	Accent chords (e.g., I64) should be on strong part of beat
	Consecutive tonic accent chords are boring. 
Arranged by rhythm: prolongation(s) -> TPS-I(s) -> TPS-C(s) -> subsidiary(s)"""

bi1_rhythms_of_3 = {
	("TP","TA"):(2,1,2,1), ("TP","TPS-I"):(2,1,2,1), 
	("TA","TAS","DAU"):(2,1,2,1), ("TPS-C","DAU"): (2,1,2,1), 
	("TAS","SA","DAU"):(2,1,2,1), 
	# ("TA","TP","TA"):(1,1,1,2,1), ("TA","TP","TPS-I"):(1,1,1,2,1),
	# ("TA","TPS-C","DAU"):(1,1,1,2,1),
	("TA","TPS-I"):(3,2,1), ("TAS", "DAU"): (3,2,1),
	("TAS", "DAU"): (2,1,3),
}
bi1_rhythms_of_4 = {
	("TP","TA"): (2,2,2,2), ("TP","TPS-I"):(2,2,2,2), 
	("TPS-C","DAU"): (2,2,2,2), ("TAS","SA","DAU"):(2,2,2,2), 
	("TA","TAS","DAU"):(2,2,2,2), ("0TP","VI"):(2,2,2,2),
	("TA","TP","TA"):(2,1,1,2,2), ("TA","TP","TPS-I"):(2,1,1,2,2), 
	("TP","TA","TPS-I"):(2,1,1,2,2), ("TPS-C","SA","DAU"):(2,1,1,2,2),
	("TA","TPS-C","DAU"):(2,1,1,2,2), ("TP","TAS","DAU"):(2,1,1,2,2), 
	# ("TP","TP","TA"):(1,1,1,1,2,2), ("TP","TP","TPS-I"):(1,1,1,1,2,2),
	# ("TP","TPS-C","DAU"):(1,1,1,1,2,2), ("TP","TAS","SA","DAU2"):(1,1,1,1,2,2),
	# ("TDP","TA","TPS-I"):(1,1,1,1,2,2), ("TDP","TAS","DAU"):(1,1,1,1,2,2),
	# ("TDP","VI","TA"):(1,1,1,1,2,2),
	("TA", "TPS-I"):(4,2,2), ("TAS", "DAU"): (4,2,2),
	("TAS", "DAU"): (2,2,4),
	# (3,1,3,1)
	# (4,3,1):
}

# Nested dicts to prevent excessive if statements
chord_sequences = {
	"TA": accent_tonic, "TP": expand_tonic1, "TDP": expand_tonic2, 
	"0TP": expand_tonic3, "TPS-I": tonic_to_subdom2, "TPS-C": tonic_to_subdom3, 
	"TAS": tonic_to_subdom1, "SA": accent_subdom1, "SP": expand_subdom1, 
	"DAU": subdom_to_dom1, "SPD-C": subdom_to_dom2, "SAP": accent_subdom1, 
	"SAU": accent_subdom1, "PDA": half_cadence, "PDAX": auth_cadence, 
	"PTA": dom_to_tonic1, "IDA": subdom_to_dom3, "IDAITA": subdom_to_tonic1
}
# 3/4, 4/4, 9/8, 12/8
time_sigs = ((3,2), (4,2), (3,3), (4,3))

chord_names = {
	"10":"I", "20":"II", "30":"III", "40":"IV", "50":'V', "60":"VI", "70":"VII",
	"1":"I", "2":"II", "3":"III", "4":"IV", "5":'V', "6":"VI", "7":"VII",
	"11":"Falling DIM", "21":"Lydian", "22":"Major", "23":"Mixo", "24":"Dorian",
	"25":"Minor", "26":"Phryg", "530":"", "753":'7', "630":'6', "653": "65", 
	"640":"64", "643": "43", "642":"42"   
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
# I haven't learned the proper way to resolve these intervals, 
# if such a technique exists
unresolved_dissonance = ("d2", "A1", "m2", "M2", "d3", "d4", "A3", "P4", 
	"d6", "A5", "A6", "m7", "M7", "d8")

# Use root notes of chords
sec_doms_in_major = {
	0: (0,0,0,-1), 1: (0,1,0,0), 2: (0,1,0,0), 5: (0,1,0,0), 6: (0,1,1,0)
}
sec_doms_in_minor = {
	0: (0,1,0,0), 1: (0,1,1,0), 2: (0,0,0,-1), 5: (1,1,1,0), 6: (0,0,0,0) 
}
sec_dim_up_in_major = {
	0:(1,0,0,-1), 1:(1,1,0,0), 2:(0,0,-1,-1), 3:(1,0,0,-1), 4: (1,0,0,0), 
	6:(0,0,0,-1)
}
sec_dim_down_in_major = {
	0:(1,0,0,-1), 1:(1,1,0,0), 2:(1,1,0,0), 3:(1,0,0,-1), 4: (1,0,0,0),
	5:(1,1,0,0)
}
sec_dim_up_in_minor = {
	0: (1,1,0,0), 1: (0,0,0,-1), 2: (1,0,0,-1), 3: (1,1,0,0), 4: (0,0,-1,-1), 
	6:(1,0,0,0)
}
sec_dim_down_in_minor = {
	0: (1,1,0,0), 1:(1,1,1,0), 2:(1,0,0,-1), 3: (1,1,0,0), 4: (1,1,0,0), 
	5:(1,0,0,-1)
}
sec_dims = {
	("up", "ionian"): sec_dim_up_in_major,
	("up", "aeolian"): sec_dim_up_in_minor,
	("down", "ionian"): sec_dim_down_in_major,
	("down", "aeolian"): sec_dim_down_in_minor
}

# Check for duplicate overriding keys in dicts 
THIRD = 0.3333
