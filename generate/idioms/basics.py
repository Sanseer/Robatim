I, I6, I64 = 10_530_1, 10_630_1, 10_640_1
I_MAJOR = 22_530_1
II, II6 = 20_530_1, 20_630_1
II_MAJOR, II6_MAJOR = 22_530_2, 22_630_2
III = 30_530_1
IV, IV6 = 40_530_1, 40_630_1
IV_MAJOR, IV6_MAJOR = 22_530_4, 22_630_4
V, V6  = 50_530_1, 50_630_1
V7, V65, V43, V42 = 50_753_1, 50_653_1, 50_643_1, 50_642_1
VI = 60_530_1
VII6 = 70_630_1

chord_members = {
	I: (0,2,4), I6: (0,2,4), I64: (0,2,4), I_MAJOR: (0,2,4), II: (1,3,5), 
	II6: (1,3,5), II_MAJOR: (1,3,5), II6_MAJOR: (1,3,5), IV: (3,5,0), 
	IV6: (3,5,0), IV_MAJOR: (3,5,0), IV6_MAJOR: (3,5,0), V: (4,6,1), 
	V6: (4,6,1), V7: (4,6,1,3), V65: (4,6,1,3), V43: (4,6,1,3), V42: (4,6,1,3), 
	VI: (5,0,2), VII6: (6,1,3)
}

bass_notes = {}
for chord, degrees in chord_members.items():
	inversion = chord // 10 % 1000
	if inversion in {530, 753}:
		bass_notes[chord] = degrees[0]
	elif inversion in {630, 653}:
		bass_notes[chord] = degrees[1]
	elif inversion in {640, 643}:
		bass_notes[chord] = degrees[2]
	elif inversion == 642:
		bass_notes[chord] = degrees[3]

assert(len(bass_notes.keys()) == len(chord_members.keys()))

mode_notes = {
	"lydian": (0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24),
	"ionian": (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24),
	"mixo": (0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24),
	"dorian": (0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19, 21, 22, 24),
	"aeolian": (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24),
	"phryg": (0, 1, 3, 5, 7, 8, 10, 12, 13, 15, 17, 19, 20, 22, 24) 
}

note_names = (
	("B#","C","Dbb"), ("B##","C#", "Db"), ("C##", "D", "Ebb"), ("D#","Eb"),
	("D##","E","Fb"), ("E#","F","Gbb"), ("E##","F#", "Gb"), ("F##","G","Abb"), 
	("G#", "Ab"), ("G##","A","Bbb"), ("A#","Bb","Cbb"), ("A##","B","Cb"), 
)
pitch_letters = ("C","D","E","F","G","A","B")

tonics = {
	"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
	"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
}

# only use practical key signatures
# 3/4, 4/4, 9/8, 12/8
time_sigs = ((3,2), (4,2), (3,3), (4,3))
expand_tonic1 = {
	I: ((-V6, I), (-V65, I), (VII6, I6), (V43, I6), (VII6, -I), (V43, -I), 
		(V42, -I6)),
	I6: ((-V6, I), (-V65, I), (-VII6, -I), (-V43, -I), (-VII6, I6), (-V43, I6),
		(V42, -I6))
}
pass_to_tonic = {
	I: ((-V6,), (-V65,), (VII6,), (V43,), (V42,)),
}
# Some of these must return to I, others to I6
double_neighbor1 = {
	I: ((-V6, V43), (-V65, V43), (-V6, VII6), (-V65, VII6), (V43, -V65), 
		(V43, V42), (VII6, V42), (-V6, V42), (-V65, V42)),
	I6: ((V42, -V65),)
}
double_neighbor2 = {
	V65: (I,),
	VII6: (-I,),
	V43: (-I,),
	V42: (-I6,)
}
accent_tonic = {
	I: (I6, -VI), 
	I6: (-I,)
}
pass_to_subdom = {
	I: ((-VI,),)
}
weak_to_subdom2_strong = {
	None: None
}
weak_to_subdom1_strong = {
	I: (II6, IV, I64, -IV6, -VI),
	I6: (II6, IV, I64),
	VI: (-II6, -IV, -I64),
	IV6: (-II6, -IV, -I64)
}
strong_to_subdom2_strong = {
	I: (II6, IV, -IV6, -VI),
	I6: (II6, IV),
	VI: (-II6, -IV, IV6)
}
strong_to_subdom1_strong = {
	I: (II6, IV, I64, -IV6, -VI),
	I6: (II6, IV, I64),
	II: (II6, I64),
	II6: (I64,),
	IV: (II6, I64),
	VI: (-II6, -IV, I64, IV6),
	IV6: (-II6, -IV, I64)
}
strong_to_subdom1_weak = {
	I: (II6, IV, -IV6, -VI),
	I6: (II6, IV),
	II6: (-II,),
	IV: (-II, II6),
	VI: (-II6, -IV, IV6),
	IV6: (-II6, -IV)
}
half_cadence1 = {
	I: (V,),
	I6: (V,),
	II: (V,),
	II6: (V,),
	IV: (V,),
	I64: (V,),
	IV6: (-V,),
	VI: (-V,)
}
# if chord descent, must do complete cadence or V65
half_cadence2 = {
	I: (V, -V6, -V65, VII6, V43, V42),
	I6: (V, -V6, -V65, -VII6, -V43, V42),
	II: (V, -V6, -V65, VII6, V43, V42),
	II6: (V, -V6, -V65, -VII6, -V43, V42),
	IV: (V, -V6, -V65, -VII6, -V43, V42),
	I64: (V, -V42),
	IV6: (-V,),
	VI: (-V,)
}
imperfect_auth_cadence2 = {
	I: (-V6, -V65, VII6, V43, V42),
	I6: (-V6, -V65, -VII6, -V43, V42),
	II: (-V6, -V65, VII6, V43, V42),
	II6: (-V6, -V65, -VII6, -V43, V42),
	IV: (-V6, -V65, -VII6, -V43, V42)
}
imperfect_auth_cadence1 = {
	V6: (I,),
	V65: (I,),
	VII6: (-I, I6),
	V43: (-I, I6),
	V42: (-I6,)
}
perfect_auth_cadence2 = {
	I: (V, V7),
	I6: (V, V7),
	II: (V, V7),
	II6: (V, V7),
	IV: (V, V7),
	I64: (V, V7),
	IV6: (-V, -V7),
	VI: (-V, V7)
}
perfect_auth_cadence1 = {
	V: (I, -I),
	V7: (I, -I)
}
restart_tonic = {
	I: (I6,),
	I6: (-I,),
	V: (I,-I),
	V6: (I,),
	V65: (I,),
	VII6: (-I, I6),
	V43: (-I, I6),
	V42: (-I6,)
}
restart_dom = {
	II: (V, V7),
	II6: (V, V7),
	IV: (V, V7),
	IV_MAJOR: (V, V7),
	I64: (V, V7),
	IV6: (-V, -V7),
	IV6_MAJOR: (-V, -V7),
	VI: (-V, V7)
}

expand_dom = {
	V: (V6, -V42),
	V6: (-V,)
}

ci1_response_rhythms = {
	# double neighbor IAC: 2 1 1 4
	(3,2,1): ((2,1,3),),
	(4,2,2): ((2,2,4),), # 2 1 1 4 
	(4,4): ((2,2,4), (4,2,2)), # 2 1 1 4
	(3,3): ((2,1,3),),
	# (2,1,2,1): ((2,1,3),),
	# (2,2,2,2): ((2,2,4),) # 2 1 1 4 
}
ci2_response_rhythms = {
	(4,4): ((2,2,4),), # 2 1 1 4
	(3,3): ((2,1,3),),
	(2,1,2,1): ((2,1,3),),
	(2,2,2,2): ((2,2,4),) #2 1 1 4
}
# SA1-M ultimate subdominant accent metrically weak
# SA2+M penultimate subdominant accent metrically strong
ci1_tonic_with_rest = {
	(4,4): (("HC1",), ("HC2",)), 
	(2,2,4): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
	(4,2,2): (("HC1",), ("HC2",)),
	# (2,2,2,2): (("M+SA1-M","HC1"), ("IAC2","IAC1")),
	(3,3): (("HC1",), ("HC2",)),
	(2,1,2,1): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
	(2,1,3): (("M+SA1-M", "HC1"), ("M+SA1-M", "HC2"), ("IAC2","IAC1")),
}
ci1_tonic_no_rest = {
	(4,4): (("HC1",), ("HC2",)), 
	(2,2,4): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
	(4,2,2): (("M+SA1+M","HC1"), ("M+SA1+M","HC2")),
	(3,3): (("HC1",), ("HC2",)), 
	(2,1,3): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
}
ci1_subdom_with_rest = {
	(4,4): (("HC1",), ("HC2",)),
	(2,2,4): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
	(4,2,2): (("HC1",), ("HC2",)),
	# (2,2,2,2): (("SA1-M","HC1"), ("IAC2","IAC1")),
	(3,3): (("HC1",), ("HC2",)),
	(2,1,2,1): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
	(2,1,3): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1"))
}
# SA1_W+S weak beat to strong beat accent
# SA1_S+W strong beat to weak beat accent 
# SA1_S+S strong to strong beat accent, same as before
#HVL 06
ci1_subdom_no_rest = {
	(4,4): (("HC1",), ("HC2",)), 
	(2,2,4): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1")),
	(4,2,2): (("M+SA1+M","HC1"), ("M+SA1+M","HC2"), ("IAC2", "IAC1")),
	# use double expand dom
	(3,3): (("HC1",), ("HC2",)),
	(2,1,3): (("M+SA1-M","HC1"), ("M+SA1-M","HC2"), ("IAC2","IAC1"))
}
ci2_tonic_with_rest = {
	None:None
}
ci2_tonic_no_rest = {
	None:None
}
ci2_subdom_with_rest = {
	(2,2,4): (("PAC2","PAC1"),),
	(2,1,3): (("PAC2","PAC1"),)
}
ci2_subdom_no_rest = {
	(2,2,4): (("PAC2","PAC1"),),
	(2,1,3): (("PAC2","PAC1"),),
}
# add incomplete passing chord to restart tonic (using regular elongation)
# weak measure 2
# double neigbor 4 2 2
bi1_rhythms_of_3 = {
	("TA",): (3,3), ("TPT-I",): (3,3), ("TDN1",): (3,2,1)
}
bi1_rhythms_of_4 = {
	("TA",): (4,4), ("TPT-I",): (4,4), ("TDN1",): (4,2,2)
}
# 3 2 1
ci1_rhythms_of_3 = {
	("TP","TA"): (2,1,2,1), ("TA",):(3,3), 
	("M+SA1+M",): (3,3), ("M+SA2+M",):(3,3)
}
# 4 2 2
ci1_rhythms_of_4 = {
	("TP","TA"): (2,2,2,2), ("TA",): (4,4),
	("M+SA1+M",): (4,4), ("M+SA2+M",): (4,4)
}
chord_names = {
	"10":"I", "20":"II", "30":"III", "40":"IV", "50":'V', "60":"VI", "70":"VII",
	"1":"I", "2":"II", "3":"III", "4":"IV", "5":'V', "6":"VI", "7":"VII",
	"11":"CTdim", "21":"Lydian", "22":"Major", "23":"Mixo", "24":"Dorian",
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
# save P4
harmonic_dissonance = {"d2", "A1", "m2", "M2", "d3", "A2", "d4", "A3", 
	"A4", "d5", "d6", "A5", "d7", "A6", "m7", "M7", "d8"}
# Use root notes of chords
# TODO: secondary subdoms
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