# Chords expressed as numbers to allow negative numbers 
# that represent descending motion.
# Underscores to denote secondary dominants
# First number is 1 because values affect visual, not audio output
I, I6, I64 = 1_530_1, 1_630_1, 1_640_1
V65_IV, V43_IV = 5_653_4, 5_643_4

II, II6 = 2_530_1, 2_630_1, 
II7, II65, II43, II42 = 2_753_1, 2_653_1, 2_643_1, 2_642_1
V7_V, V65_V, V43_V = 5_753_5, 5_653_5, 5_643_5

III = 3_530_1
V65_VI, V43_VI = 5_653_6, 5_643_6 

IV, IV6, IV7 = 4_530_1, 4_630_1, 4_753_1
V, V6  = 5_530_1, 5_630_1
V7, V65, V43, V42 = 5_753_1, 5_653_1, 5_643_1, 5_642_1

VI = 6_530_1 
V65_II, V43_II = 5_653_2, 5_643_2

VII6 = 7_630_1
V65_III, V43_III = 5_653_3, 5_643_3

modes = {
	"aeolian": (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24), 
	"ionian": (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24)
}
# decide accidentals for diatonic notes based on key sig. Reduces symbol clutter.
major_accidentals = {"C":"#", "G":"#", "D":"#", "A":"#", "E":"#", "B":"#", 
	"F#":"#", "Db":"b", "Ab":"b", "Eb":"b", "Bb":"b", "F":"b"
}
minor_accidentals = {"A":"#", "E":"#", "B":"#", "F#":"#", "C#":"#", "G#":"#", 
	"D#":"#", "Bb":"b", "F":"b", "C":"b", "G":"b", "D":"b"
}
"""Do you need pedantic accidental designations based on key signature 
such as Cb or E#. If so use all_notes instead of tonics variable, 
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

# tuple with one item needs comma.
# These are short chord progression sequences for different scenarios
expand_tonic1 = {
	I: ((-V6, I), (VII6, I6), (VII6, -I), (-V65, I6), (V43, I6), (V42, -I6), 
		(-V65, I), (V43, -I), (-IV6, -I6), (-VI, -I6), (V65_III, III), 
		(-V43_VI,-VI), (V65_III, III)), 
	I6: ((-V6, I), (-VII6, I6), (-VII6, -I), (-V65, I), (-V43, -I), 
		(V42, -I6), (-V43, I6), (-V65_III, III), (V43_III, -III)),
	III: ((-V6, I), (-VII6, I6), (-VII6, -I), (-V65, I), (-V43, -I), 
		(V42, -I6), (-V43, I6)),
	VI: ((-V43_III, -III),)
}
expand_tonic2 = {
	I: ((-V6, V43, -I), (V43, -V65, I), (-V65, V43, -I), (-V6, VII6, -I), 
		(-V65, VII6, -I)),
}
expand_tonic3 = {
	I: ((-V6, I), (VII6, -I), (-V65, I), (V43, -I))
}
accent_tonic = {
	I: (I6,), I6: (-I,), III: (-I, I6), VI: (-III, -I6)
}
# you can't repeat chord from weak to strong beat
restart_tonic = {
	I: (I6, III), I6: (-I, III), III: (-I, I6), V: (VI, -I6, -III),
	VI: (I,), V7: (VI, -I6, -III), V65: (I,), V43: (-I, I6, III), 
	V42: (-I6, -III), V65_II:(II), V43_II:(-II,-IV), V65_IV:(IV,),
}
tonic_to_subdom1 = {
	I: (II, II6, IV), I6: (II6, IV, II, II7, II65), 
	III: (II6, IV, II, II7, II65), VI: (-IV, -IV7, -II7, -II6, -II65), 
	IV6: (-IV, -IV7, -II6), V65_II: (II,), V43_II: (II6,-II), V65_IV: (IV,),
	V43_IV: (-IV,)
}
tonic_to_subdom2 = {
	I: (V65_II, V43_II, V65_IV), I6: (-V65_II, V43_II, V65_IV, V43_IV),
	III: (-V65_II, V43_II, V65_IV, V43_IV), VI:(-V43_II, -V43_IV)
}
tonic_to_subdom3 = {
	I: ((V65_II, II), (V43_II, -II), (V65_IV, IV)),
	I6:((-V65_II, II), (V43_II, -II), (V65_IV, IV), (V43_IV, -IV)),
	III:((-V65_II, II), (V43_II, -II), (V65_IV, IV), (V43_IV, -IV)),
	VI: ((-V43_II, -II), (-V43_IV, -IV))
}
accent_subdom1 = {
	II: (II6,), II6: (-II, -II7), II7: (II65,), II65: (-II7, II43), 
	II43: (-II65,), IV: (-II, II6), IV7: (II65,)
}
expand_subdom1 = {
	II: ((I6, II6), (I6, II65)), II6: ((-I6, -II), (V65_IV, IV)), 
	II7: ((I6, II65),), II65: ((-I6, -II7),), IV: ((II6, -II), (-II, II6), 
		(-V43_II, -II))
}
subdom_to_dom1 = {
	II: (V, -V65), II6: (V, V42), II65: (V,), II43: (-V,), 
	II7: (V,), IV: (V, V42), IV7: (V, V42), I64: (V,)
}
subdom_to_dom2 = {
	II: ((I6, V), (V65_V, V)), II7: ((V7_V,V), (V65_V,V)),
	II6: ((V65_V, V), (V43_V, -V)), II65:((V65_V, V), (V43_V, -V)), 
	II43: (-V43_V, -V), IV: ((V65_V, V), (V43_V, -V)), IV7: ((V65_V,V), (V43_V,-V))
}
subdom_to_dom3 = {
	II: (V43, V42, -V6, -V65), II7: (V43, V42, -V6, -V65), II6: (-V43, V42), II65: (-V43, V42),
	IV: (-V43, V42), IV7: (-V43, V42)
}
subdom_to_tonic1 = {
	II: ((V43, I6), (V42, I6)), II7: ((V43, I6), (V42, I6)), 
	II6: ((-V43, I6), (V42, -I6)), II65: ((-V43, I6), (V42, -I6)), 
	IV: ((-V43, I6), (V42, -I6))
}
accent_dom = {
	V: (V6, V65, V7, -V42), V6: (-V,), I64: (V, V7)
}
dom_to_tonic1 = {
	V: (-I,), V7: (-I,), V6: (I,), V65: (I,),  V43:(-I,), V42: (-I6,)
}
bass_notes = {
	I:0, II42: 0, V65_II: 0, II: 1, II7: 1, V43: 1, VII6: 1, V65_III: 1, V7_V: 1, III: 2, 
	I6: 2, V65_IV: 2, V43_II: 2, II6: 3, II65: 3, V65_V: 3, IV: 3, IV7: 3, 
	V42: 3, V43_III: 3, V: 4, V7: 4, I64: 4, V65_VI: 4, V43_IV: 4, II43: 5, 
	V43_V: 5, IV6: 5, VI: 5, V6: 6, V65: 6, V43_VI: 6
}
chord_tones = { 
	I: (0,2,4), I6: (0,2,4), I64: (0,2,4), V65_IV: (0,2,4,6), V43_IV: (0,2,4,6), 
	II: (1,3,5),  II6: (1,3,5), II7: (1,3,5,0), II65: (1,3,5,0), 
	II43: (1,3,5,0), II42: (1,3,5,0), V7_V: (1,3,5,0), V65_V: (1,3,5,0), V43_V: (1,3,5,0),
	III: (2,4,6), V65_VI: (2,4,6,1), V43_VI: (2,4,6,1), IV: (3,5,0), IV6: (3,5,0), 
	IV7: (3,5,0,2), V: (4,6,1), V6: (4,6,1), V7: (4,6,1,3), V65: (4,6,1,3), 
	V43: (4,6,1,3), V42: (4,6,1,3), VI: (5,0,2), V65_II: (5,0,2,4), 
	V43_II: (5,0,2,4), VII6: (6,1,3), V65_III: (6,1,3,5), V43_III: (6,1,3,5)
}

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
	# (2,2,1,1,2):(("TAS","SAU","DAU"), ("TAS","PDA","ITA"), ("TAS","IDA","PTA"), 
	# 	("TAS","IDAITA"),("TPS-C","DAU"), ("TA","TAS","DAU")),
	# (2,1,1,1,1,2):(("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), ("TPS-C","IDA","PTA"), 
	# 	("TPS-C","IDAITA"), ("TAS","SP","DAU"), ("TAS","SA","PDA","ITA"), 
	# 	("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"), ("TA", "TPS-C","DAU")),
	(1,1,1,1,2,2):(("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), ("TPS-C","IDA","PTA"), 
		("TPS-C","IDAITA"), ("TPS-C","SPD-C"), ("TAS","SA","SPD-C"), 
		("TAS","SP","DAU"), ("TAS","SAP","SAU","DAU"), ("TAS","SA","PDA","ITA"),
		("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"), ("TA","TPS-C","DAU"),
		("TA","TAS","SPD-C"), ("TA","TAS","SAU","DAU"), ("TA","TAS","PDA","ITA"),
		("TA","TAS","IDA","PTA"), ("TA","TAS","IDAITA")),
	# (1,1,2,1,1,2): (("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), 
	# 	("TPS-C","IDA","PTA"), ("TPS-C","IDAITA"), ("TAS","SP","DAU"), 
	# 	("TAS","SAP","SAU","DAU"),("TAS","SA","PDA","ITA"), ("TAS","SA","IDA","PTA"),
	# 	("TAS","SA","IDAITA")),
	# (2,2,1,1,1,1):(("TPS-C","DAU"), ("TAS","SAU","DAU"), ("TAS","PDA","ITA"), 
	# 	("TAS","IDA","PTA"), ("TAS","IDAITA")),
	(2,1,2,1):(("TAS","DAU"),), (2,1,1,2): (("TAS","DAU"),),
	# (2,1,1,1,1):(("TAS","DAU"),), 
	(1,1,1,2,1): (("TPS-C","DAU"), ("TAS","SPD-C"), ("TAS","SAU","DAU"), 
		("TAS","PDA","ITA"), ("TAS","IDA","PTA"), ("TAS","IDAITA")),
}
ci2_from_tonic_with_rest = {
	(2,2,2,2):(("PDAX","TAU"),), (2,1,1,2,2):(("TAS","PDAX","TAU"),), 
	# (2,2,1,1,2):(("TAS","PDAX","TAU"),), 
	# (2,1,1,1,1,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"), 
	# 	("TAS","SPD-C","TAU")),
	(1,1,1,1,2,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"),
		("TAS","SPD-C","TAU")),
	# (1,1,2,1,1,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"),
	# 	("TAS","SPD-C","TAU")), (2,2,1,1,1,1):(("TAS","PDAX","TAU"),), 
	(2,1,2,1):(("PDAX","TAU"),),
	(2,1,1,2):(("PDA","TAU"),),
	# (2,1,1,1,1):(("PDAX","TAU"),), 
	(1,1,1,2,1):(("TAS","PDAX","TAU"),)
}
ci1_from_tonic_no_rest = {
	(2,2,2,2):(("TAS","SAU","DAU"), ("TAS","PDA","ITA"), ("TAS","IDA","PTA"), 
		("TPS-C","DAU"), ("TA","TAS","DAU")),
	(2,1,1,2,2):(("TAS","SP","DAU"), ("TAS","SAP","SAU","DAU"), ("TAS","SP","DAU"),
		("TAS","SAU","PDA","ITA"), ("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"), 
		("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), ("TPS-C","IDA","PTA"), 
		("TPS-C", "IDAITA"), ("TA","TPS-C","DAU"), ("TA","TAS","SAU","DAU")),
	# (2,2,1,1,2):(("TAS","SA","SPD-C"), ("TAS","SAP","SAU","DAU"), ("TAS","SP","DAU"), 
	# 	("TAS","SAU","PDA","ITA"), ("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"), 
	# 	("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"), ("TPS-C","IDA","PTA"), 
	# 	("TPS-C", "IDAITA"), ("TA","TAS","SPD-C")),
	# (2,1,1,1,1,2):(("TPS-C","SA","SPD-C"), ("TPS-C","SAP","SAU","DAU"), 
	# 	("TPS-C","SA","PDA","ITA"), ("TPS-C","SA","IDA","PDA"), 
	# 	("TPS-C","SA","IDAITA"), ("TA","TPS-C","SAU","DAU"), 
	# 	("TA","TPS-C","PDA","ITA"), ("TA","TPS-C","IDA","PTA"), 
	# 	("TA","TPS-C","IDAITA"), ("TA","TAS","SAP","SAU","DAU"), 
	# 	("TA","TAS","SA","PDA","ITA"), ("TA","TAS","SA","IDA","PTA"), 
	# 	("TA","TAS","SA","IDAITA")),
	(1,1,1,1,2,2): (("TPS-C","SP","DAU"), ("TPS-C","SAP","SAU","DAU"), 
		("TPS-C","SA","PDA","ITA"), ("TPS-C","SA","IDA","PTA"), 
		("TPS-C","SA","IDAITA"), ("TAS","SP","SAU","DAU"), ("TAS","SP","PDA","ITA"),
		("TAS","SP","IDA","PTA"), ("TAS","SP","IDAITA"), ("TA","TPS-C","SAU","DAU"),
		("TA","TPS-C","PDA","ITA"), ("TA","TPS-C","IDA","PTA"), 
		("TA","TPS-C","IDAITA")),
	# (1,1,2,1,1,2):(("TPS-C","SA","SPD-C"), ("TPS-C","SAP","SAU","DAU"), 
	# 	("TPS-C","SA","PDA","ITA"), ("TPS-C","SA","IDA","PTA"), 
	# 	("TPS-C","SA","IDAITA"), ("TAS","SP","SAU","DAU"), ("TAS","SP","SPD-C"), 
	# 	("TAS","SP","PDA","ITA"), ("TAS","SP","IDA","PTA"), ("TAS","SP","IDAITA")),
	# (2,2,1,1,1,1):(("TPS-C","SP","DAU"), ("TPS-C","SAP","SAU","DAU"), 
	# 	("TPS-C","SA","PDA","ITA"), ("TPS-C","SA","IDA","PTA"), 
	# 	("TPS-C","SA","IDAITA"), ("TAS","SA","SP","DAU")),
	(2,1,2,1):(("TPS-C","DAU"), ("TAS","SAU","DAU"), ("TAS","PDA","ITA"), 
		("TAS","IDA","PTA"), ("TAS","IDAITA")),
	(2,1,1,2):(("TPS-C","DAU"), ("TAS","SAU","DAU"), ("TAS","PDA","ITA"), 
		("TAS","IDA","PTA"), ("TAS", "IDAITA")),
	# (2,1,1,1,1):(("TPS-C","SPD-C"), ("TPS-C","SAU","DAU"), ("TPS-C","PDA","ITA"),
	# 	("TPS-C","IDA","PTA"), ("TPS-C","IDAITA"), ("TAS","SA","SPD-C")),
	(1,1,1,2,1):(("TPS-C","SAU","DAU"), ("TAS","SAP","SAU","DAU",), 
		("TAS","SA","PDA","ITA"), ("TAS","SA","IDA","PTA"), ("TAS","SA","IDAITA"))
}
ci2_from_tonic_no_rest = {
	(2,2,2,2):(("TAS","PDAX","TAU"),), 
	(2,1,1,2,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"), 
		("TAS","SPD-C","TAU")), 
	# (2,2,1,1,2):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU")), 
	# (2,1,1,1,1,2):(("TAS","SAP","SAU","PDAX","TAU"), ("TPS-C","SAU","PDAX","TAU"), 
	# 	("TAS","SP","PDAX","TAU")),
	(1,1,1,1,2,2):(("TAS","SAP","SAU","PDAX","TAU"), ("TPS-C","SAU","PDAX","TAU"),
		("TAS","SP","PDAX","TAU"), ("TAS","SA","SPD-C","DAU")),
	# (1,1,2,1,1,2):(("TAS","SAP","SAU","PDAX","TAU"), ("TPS-C","SAU","PDAX","TAU"),
	# 	("TAS","SP","PDAX","TAU")),
	# (2,2,1,1,1,1):(("TAS","SAP","SAU","PDAX","TAU"), ("TPS-C","SAU","PDAX","TAU"),
	# 	("TAS","SA","SPD-C","PDAX")), 
	(2,1,2,1):(("TAS","PDAX","TAU"),), (2,1,1,2):(("TAS","PDAX","TAU"),),
	# (2,1,1,1,1):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU")), 
	(1,1,1,2,1):(("TAS","SAU","PDAX","TAU"), ("TPS-C","PDAX","TAU"), 
		("TAS","SPD-C","TAU"))
}
ci1_from_subdom_with_rest = {
	(2,2,2,2):(("SAU","DAU"), ("SPD-C",), ("PDA","ITA"), ("IDA","PTA"), 
		("IDAITA",),),
	(2,1,1,2,2):(("SAP","SAU","DAU"), ("SP","DAU"), ("SA","SPD-C"), 
		("SA","PDA","ITA"), ("SA","IDA","PTA"), ("SA","IDAITA")),
	# (2,2,1,1,2):(("SP","DAU"), ("SAP","SAU","DAU"), ("SA","PDA","ITA"), 
	# 	("SA","IDA","PTA"), ("SA","IDAITA")),
	# (2,1,1,1,1,2):(("SP","SAU","DAU"), ("SP","PDA","ITA"), ("SP","IDA","PTA"), 
	# 	("SP","IDAITA"), ("SA","SP","DAU"), ("SA","SA","PDA","ITA"), 
	# 	("SA","SA","IDA","PTA"), ("SA","SA","IDAITA")),
	(1,1,1,1,2,2):(("SP","SPD-C"), ("SP","SAU","DAU"), ("SP","PDA","ITA"), 
		("SP","IDA","PTA"), ("SP","IDAITA"), ("SA","SP","DAU"), 
		("SA","SA","SPD-C")),
	# (1,1,2,1,1,2):(("SP","SAU","DAU"), ("SP","PDA","ITA"), ("SP","IDA","PTA"), 
	# 	("SP","IDAITA"), ("SA","SP","DAU"), ("SA","SAP","SAU","DAU"),
	# 	("SAP","SAU","PDA","ITA"), ("SA","SA","IDA","PTA"), ("SA","SA","IDAITA")),
	# (2,2,1,1,1,1):(("SP","DAU"), ("SAP","SAU","DAU"), ("SAP","SAU","PDA","ITA"), 
	# 	("SA","SA","IDA","PTA"), ("SA","SA","IDAITA")),
	(2,1,2,1):(("SPD-C",), ("SAU","DAU"), ("PDA","ITA"), ("IDA","PTA"), ("IDAITA",)),
	(2,1,1,2):(("SPD-C",), ("SAU","DAU"), ("PDA","ITA"), ("IDA","PTA"), ("IDAITA",)),
	# (2,1,1,1,1):(("SPD-C",), ("SAU","DAU"), ("PDA","ITA"), ("IDA","PTA"), ("IDAITA")),
	(1,1,1,2,1):(("SP","DAU"), ("SA","SPD-C"))
}
ci2_from_subdom_with_rest = {
	(2,2,2,2):(("PDAX","TAU"),),
	(2,1,1,2,2):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	# (2,2,1,1,2):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	# (2,1,1,1,1,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"), 
	# 	("SA","SPD-C","TAU")),
	(1,1,1,1,2,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"),
		("SA","SPD-C","TAU")),
	# (1,1,2,1,1,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"), 
	# 	("SA","SPD-C","TAU")),
	# (2,2,1,1,1,1):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	(2,1,2,1):(("PDAX","TAU"),), (2,1,1,2):(("PDAX","TAU"),),
	# (2,1,1,1,1):(("PDAX","TAU"),),
	(1,1,1,2,1):(("SAU","PDAX","TAU"), ("SPD-C","TAU"))
}
ci1_from_subdom_no_rest = {
	(2,2,2,2):(("SAP","SAU","DAU"), ("SP","DAU"), ("SAU","PDA","ITA"), 
		("SA","IDA","PTA"), ("SA","IDAITA")),
	(2,1,1,2,2):(("SA","SP","DAU"), ("SP","SAU","DAU"), ("SP","PDA","ITA"), 
		("SP","IDA","PTA"), ("SP","IDAITA")),
	# (2,2,1,1,2):(("SP","SPD-C"), ("SP","SAU","DAU"), ("SP","PDA","ITA"), 
	# 	("SP","IDA","PTA"), ("SP","IDAITA"), ("SA","SA","SPD-C"), 
	# 	("SA","SA","PDA","ITA"), ("SA","SA","IDA","PTA"), ("SA","SA","IDAITA")),
	# (2,1,1,1,1,2):(("SP","SA","SPD-C"), ("SP","SAP","SAU","DAU"), 
	# 	("SP","SA","PDA","ITA"), ("SP","SA","IDA","PTA"), ("SP","SA","IDAITA")),
	(1,1,1,1,2,2): (("SP","SP","DAU"), ("SP","SAP","SAU","DAU"), 
		("SP","SA","PDA","ITA"), ("SP","SA","IDA","PTA"), ("SP","SA","IDAITA")),
	# (1,1,2,1,1,2):(("SP","SA","SPD-C"), ("SP","SAP","SAU","DAU"), 
	# 	("SP","SA","PDA","ITA"), ("SP","SA","IDA","PTA"), ("SP","SA","IDAITA"),
	# 	("SA","SP","SPD-C"), ("SA","SP","SAU","DAU"), ("SA","SP","PDA","ITA"),
	# 	("SA","SP","IDA","PTA"), ("SA","SP","IDAITA")),
	# (2,2,1,1,1,1):(("SP","SP","DAU"), ("SP","SAP","SAU","DAU"), 
	# 	("SP","SA","PDA","ITA"), ("SP","SA","IDA","PTA"), ("SP","SA","IDAITA"), 
	# 	("SA","SA","SP","DAU")),
	(2,1,2,1):(("SP","DAU"), ("SAP","SAU","DAU"), ("SA","PDA","ITA"), 
		("SA","IDA","PTA"), ("SA","IDAITA")),
	(2,1,1,2):(("SP","DAU"), ("SAP","SAU","DAU"), ("SA","PDA","ITA"), 
		("SA","IDA","PTA"), ("SA","IDAITA")),
	# (2,1,1,1,1):(("SP","SPD-C"), ("SP","SAU","PDA"), ("SP","PDA","ITA"), 
	# 	("SP","IDA","PTA"), ("SP","IDAITA")),
	(1,1,1,2,1):(("SP","SAU","DAU"), ("SP","PDA","ITA"), ("SP","IDA","PTA"), 
		("SP","IDAITA"))
}
ci2_from_subdom_no_rest = {
	(2,2,2,2):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	(2,1,1,2,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"), 
		("SA","SPD-C","TAU")),
	# (2,2,1,1,2):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU")),
	# (2,1,1,1,1,2):(("SA","SP","PDAX","TAU"), ("SP","SAU","PDAX","TAU")),
	(1,1,1,1,2,2):(("SA","SP","PDAX","TAU"), ("SP","SAU","PDAX","TAU"),
		("SP","SPD-C","DAU")),
	# (1,1,2,1,1,2):(("SA","SP","PDAX","TAU"), ("SP","SAU","PDAX","TAU")),
	# (2,2,1,1,1,1):(("SP","SAU","PDAX","TAU"), ("SP","SPD-C","TAU")),
	(2,1,2,1):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	(2,1,1,2):(("SAU","PDAX","TAU"), ("SPD-C","TAU")),
	# (2,1,1,1,1):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU")),
	(1,1,1,2,1):(("SAP","SAU","PDAX","TAU"), ("SP","PDAX","TAU"), 
		("SA","SPD-C","TAU"))
}

""" Some BI sequences use subdominant chords: subsidiary progression
Numbers in sequences to allow duplicate progressions with different rhythms
Attempting to find all the sweet rhythms (manually)
	Don't use passing chord on strong part of beat!!!!
	Accent chords (e.g., I64) should be on strong part of beat
	Consecutive tonic accent chords are boring. 
Arranged by rhythm: prolongation(s) -> TPS-I(s) -> TPS-C(s) -> subsidiary(s)"""
# bi1_rhythms_of_2 = {
# 	("TA",):(2,2), ("TP",):(1,1,2), ("TAS","DAU"):(1,1,2) 
# }
bi1_rhythms_of_3 = {
	("TP","TA"):(2,1,2,1), ("TP","TPS-I"):(2,1,2,1), 
	("TA","TAS","DAU"):(2,1,2,1), ("TPS-C","DAU"): (2,1,2,1), 
	("TAS","SA","DAU"):(2,1,2,1), 
	("TP2","TA"):(2,1,1,2), ("TP2","TPS-I"):(2,1,1,2),
	("TA","TAS","DAU2"):(2,1,1,2), ("TPS-C","DAU2"):(2,1,1,2),
	("TAS","SA","DAU2"):(2,1,1,2),
	# ("TP","TP"):(2,1,1,1,1), ("TP","TA","TPS-I"):(2,1,1,1,1),
	# ("TPS-C","SA","DAU"):(2,1,1,1,1), ("TPS-C","SPD-C"):(2,1,1,1,1),
	# ("TA","TAS","SPD-C"):(2,1,1,1,1),
	("TA","TP","TA"):(1,1,1,2,1), ("TA","TP","TPS-I"):(1,1,1,2,1),
	("TA","TPS-C","DAU"):(1,1,1,2,1)
}
bi1_rhythms_of_4 = {
	("TP","TA"): (2,2,2,2), ("TP","TPS-I"):(2,2,2,2), 
	("TPS-C","DAU"): (2,2,2,2), ("TAS","SA","DAU"):(2,2,2,2), 
	("TA","TAS","DAU"):(2,2,2,2), ("TAS", "SPD-C"):(2,2,2,2), 
	("0TP","VI"):(2,2,2,2),
	("TA","TP","TA"):(2,1,1,2,2), ("TA","TP","TPS-I"):(2,1,1,2,2), 
	("TP","TA","TPS-I"):(2,1,1,2,2), ("TPS-C","SA","DAU"):(2,1,1,2,2),
	("TA","TPS-C","DAU"):(2,1,1,2,2), ("TP","TAS","DAU"):(2,1,1,2,2), 
	# ("TP2","TA","TPS-I"):(2,2,1,1,2), ("TPS-C","SA","DAU2"): (2,2,1,1,2), 
	# ("TA","TAS","SPD-C"):(2,2,1,1,2), ("TA","TAS","SA","DAU"):(2,2,1,1,2),
	# ("TA","TP","TP"):(2,1,1,1,1,2), ("TA","TP","TA","TPS-I"):(2,1,1,1,1,2),
	# ("TPS-C","SA","SA","DAU"):(2,1,1,1,1,2), ("TPS-C","SA","SPD-C"):(2,1,1,1,1,2),
	# ("TP","TAS","SPD-C"):(2,1,1,1,1,2), ("TP","TAS","SA","DAU"):(2,1,1,1,1,2), 
	# ("TP","TA","TAS","DAU"):(2,1,1,1,1,2),
	("TP","TP","TA"):(1,1,1,1,2,2), ("TP","TP","TPS-I"):(1,1,1,1,2,2),
	("TP","TPS-C","DAU"):(1,1,1,1,2,2), ("TP","TAS","SA","DAU2"):(1,1,1,1,2,2),
	# ("TP","TA","TP"):(1,1,2,1,1,2), ("TA","TP2","TA","TPS-I"):(1,1,2,1,1,2),
	# ("TA","TPS-C","SPD-C"):(1,1,2,1,1,2), ("TPS-C","SA2","SPD-C"):(1,1,2,1,1,2),
	# ("TP","TAS","SA","DAU2"):(1,1,2,1,1,2), ("TP2","TAS","SPD-C"):(1,1,2,1,1,2),
	("TDP","TA","TPS-I"):(1,1,1,1,2,2), ("TDP","TAS","DAU"):(1,1,1,1,2,2),
	("TDP","VI","TA"):(1,1,1,1,2,2),
	# ("TA","TAS","SA","SPD-C"):(2,2,1,1,1,1)
}

# Nested dicts to prevent excessive if statements
chord_groups = {
	"TA": accent_tonic, "TP": expand_tonic1, "TDP": expand_tonic2, 
	"0TP": expand_tonic3, "TPS-I": tonic_to_subdom2, "TPS-C": tonic_to_subdom3, 
	"TAS": tonic_to_subdom1, "SA": accent_subdom1, "SP": expand_subdom1, 
	"DAU": subdom_to_dom1, "SPD-C": subdom_to_dom2, "SAP": accent_subdom1, 
	"SAU": accent_subdom1, "PTA": dom_to_tonic1, "IDA": subdom_to_dom3,
	"IDAITA": subdom_to_tonic1
}
# 3/4, 4/4, 9/8, 12/8
time_sigs = ((3,2), (4,2), (3,3), (4,3))
chord_names = {
	"1":"I", "2":"II", "3":"III", "4":"IV", "5":"V", "6":"VI", "7":"VII",
	"530":"", "753":"7", "630":"6", "653": "65", "640":"64", 
	"643": "43", "642":"42"   
}
# First index: semitone difference. Second index: generic interval.
# P = perfect, d = diminished, A = augmented, M = major, m = minor
interval_names = {
	(0,0): "P8", (0,1): "d2", (1,0): "A1", (1,1): "m2", (2,1): "M2", (2,2): "d3",
	(3,1): "A2", (3,2): "m3", (4,2): "M3", (4,3): "d4", (5,2): "A3", (5,3): "P4",
	(6,3): "A4", (6,4): "d5", (7,4): "P5", (7,5): "d6", (8,4): "A5", (8,5): "m6",
	(9,5): "M6", (9,6): "d7", (10,5): "A6", (10,6): "m7", (11,6): "M7", 
	(11,7): "d8", (0,6): "A7"
}
harmonic_dissonance = ("d2", "A1", "m2", "M2", "d3", "A2", "d4", "A3", "P4", 
	"A4", "d5", "d6", "A5", "d7", "A6", "m7", "M7", "d8")
# Use root notes of chords
sec_doms_in_major = {
	0: (0,0,0,-1), 1: (0,1,0,0), 2: (0,1,0,0), 5: (0,1,0,0), 6: (0,1,1,0)
}
sec_doms_in_minor = {
	0: (0,1,0,-1), 1: (0,1,1,0), 2: (0,0,-1,-1), 5: (1,1,1,0), 6: (-1,0,0,0) 
}

# Check for duplicate overriding keys in dicts 


