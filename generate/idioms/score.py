import random
from fractions import Fraction

class Score:
	"""Overarching model of a musical piece"""
	
	mode = None
	tonic = None
	repeat_ending = None

	# exclude 9/8 because of uneven divisions
	# 2/4, 3/4, 6/8, 4/4, 12/8
	# the difference between duple and quadruple meter is semantic
	time_sigs = ((2,2), (3,2), (2,3), (4,2), (3,2), (4,3))
	time_sig = None
	simple_beat_durations = {
		4: "1", 3: "2.", 2: "2", 1.5: "4.", 1: "4", 0.75: "8.",
		0.5: "8", 0.375: "16.", 0.25: "16", 0.125: "32", 
	}
	compound_beat_durations = {
		4: "1.", Fraction("8/3"): "4", 2: "2.", Fraction("4/3"):"2", 1: "4.",   
		Fraction("2/3"): "4", 0.5: "8.", Fraction("1/3"): "8", 
		Fraction("1/6"): "16"  
	}
	beat_durations = {}
	measure_length = 0
	beat_division = 0

	# 0 = rhythm1
	# 1 = rhythm2 etc.
	# -1 = sustain
	# -2 = pickup
	# duplicate patterns are used to alter selected pattern probability
	rhythm_patterns = (
		((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1)), 
		(
			(0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0 , 2, -1), 
			(0, 2, 0, -1), (0, 1, 2, -1), (0, 2, 1, -1), (0, 0, -1, -1), 
			(0, 1, -1, -1), (0, 2, -1, -1), (0, 0, -1, -1), (0, 1, -1, -1), 
			(0, 2, -1, -1), (0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
			(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2), (0, 0, -1, -2), 
			(0, 1, -1, -2), (0, 2, -1, -2), (0, 0, -1, -2), (0, 1, -1, -2), 
			(0, 2, -1, -2), (0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
		), (
			(0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0, 2, -1), 
			(0, 2, 0, -1), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), 
			(0, 0, 2, 0), (0, 2, 0, 0), (0, 1, 2, -1), (0, 1, 2, 0), 
			(0, 2, 1, -1), (0, 2, 1, 0),
		), ((0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1))
	)
	tonics = {
		"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
		"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
	}
	mode_notes = {
		"lydian": (0, 2, 4, 6, 7, 9, 11),
		"ionian": (0, 2, 4, 5, 7, 9, 11),
		"mixo": (0, 2, 4, 5, 7, 9, 10),
		"dorian": (0, 2, 3, 5, 7, 9, 10),
		"aeolian": (0, 2, 3, 5, 7, 8, 10),
		"phryg": (0, 1, 3, 5, 7, 8, 10) 
	}

	@classmethod
	def reset(cls):
		cls.mode = random.choice(("ionian", "aeolian"))
		if cls.mode == "ionian":
			cls.key_sigs = (
				"C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F",
			)

		elif cls.mode == "aeolian":
			cls.key_sigs = (
				"A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D",
			)

		cls.time_sig = random.choice(cls.time_sigs)
		cls.tonic = random.choice(cls.key_sigs)
		cls.measure_length = cls.time_sig[0]
		cls.beat_division = cls.time_sig[1]
		if cls.beat_division == 2:
			cls.beat_durations = cls.simple_beat_durations
		elif cls.beat_division == 3:
			cls.beat_durations = cls.compound_beat_durations
		cls.repeat_ending = random.choice((True, False))
