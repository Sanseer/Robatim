import random
from fractions import Fraction

class Score:
	"""Overarching model of a musical piece"""
	
	mode = None
	tonic = None
	style = None
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
		"mixolydian": (0, 2, 4, 5, 7, 9, 10),
		"dorian": (0, 2, 3, 5, 7, 9, 10),
		"aeolian": (0, 2, 3, 5, 7, 8, 10),
		"phrygian": (0, 1, 3, 5, 7, 8, 10),
	}
	note_letters = ("C","D","E","F","G","A","B")
	note_names = (
		("B#","C","Dbb"), ("B##","C#", "Db"), ("C##", "D", "Ebb"), ("D#","Eb"),
		("D##","E","Fb"), ("E#","F","Gbb"), ("E##","F#", "Gb"), ("F##","G","Abb"), 
		("G#", "Ab"), ("G##","A","Bbb"), ("A#","Bb","Cbb"), ("A##","B","Cb"), 
	)

	@classmethod
	def reset(cls, tonic=None, mode=None, style=None):
		"""Reset the variables of the Score class"""
		if mode is not None:
			mode = mode.lower()
		if tonic is not None:
			tonic = tonic.title()
		if mode in cls.mode_notes:
			cls.mode = mode
		elif mode == "major":
			cls.mode = "ionian"
		elif mode == "minor":
			cls.mode = "aeolian"
		elif mode is None: 
			if style == "Mm":
				cls.mode = random.choice(("ionian", "aeolian"))
			elif style == "modal":
				cls.mode = random.choice(
					("lydian", "mixolydian", "dorian", "phrygian")
				)
			else:
				raise ValueError("Invalid mode (style) input")
		else:
			raise ValueError("Invalid mode input")
		cls.style = style

		if tonic is None:
			cls.tonic = cls.choose_key_sig()
		elif tonic in cls.tonics:
			cls.tonic = tonic
		else:
			raise ValueError("Invalid tonic note")
		# elif cls.mode == "aeolian":
		# 	cls.key_sigs = (
		# 		"A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D",
		# 	)

		cls.time_sig = random.choice(cls.time_sigs)
		cls.measure_length = cls.time_sig[0]
		cls.beat_division = cls.time_sig[1]
		if cls.beat_division == 2:
			cls.beat_durations = cls.simple_beat_durations
		elif cls.beat_division == 3:
			cls.beat_durations = cls.compound_beat_durations
		cls.repeat_ending = random.choice((True, False))

	@classmethod
	def choose_key_sig(cls):
		"""Chooses a random key signature from those with a 
		reasonable amount of accidentals"""

		major_scale_keys = (
			"C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F",
		)
		modal_shifts = {
			"dorian": 1, "phrygian": 2, "lydian": 3, "mixolydian": 4, "aeolian": 5,
			"locrian": 6
		}
		if cls.mode == "ionian":
			cls.key_sigs = major_scale_keys
		else:
			modal_scale_keys = []
			for major_scale_key in major_scale_keys:
				degree_index = 0
				base_major_scale = major_scale_key[0]
				letter_index = cls.note_letters.index(base_major_scale)
				scale_pitch = cls.tonics[major_scale_key]
				old_reference_pitch = 0
				while degree_index < modal_shifts[cls.mode]:
					degree_index += 1
					new_reference_pitch = cls.mode_notes["ionian"][degree_index]
					pitch_diff = new_reference_pitch - old_reference_pitch
					scale_pitch = (scale_pitch + pitch_diff) % 12
					letter_index = (letter_index + 1) % 7
					new_base_note_letter = cls.note_letters[letter_index]
					possible_note_names = cls.note_names[scale_pitch]
					for possible_note_name in possible_note_names:
						if possible_note_name[0] == new_base_note_letter:
							chosen_note_name = possible_note_name
							break
					old_reference_pitch = new_reference_pitch
				modal_scale_keys.append(chosen_note_name)
			cls.key_sigs = tuple(modal_scale_keys)
			print(f"Possible key sigs: {cls.key_sigs}")
		return random.choice(cls.key_sigs) 
