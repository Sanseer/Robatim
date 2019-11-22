import collections

from generate.voices.voice import Voice

class Chord:
	"""A grouping of scale degrees and corresponding pitches"""

	chord_members = {
		"I": (0, 2, 4), "I6": (0, 2, 4), "V": (4, 6, 1), "V7": (4, 6, 1, 3), 
		"V6":(4, 6, 1), "VII6": (6, 1, 3), "V65": (4, 6, 1, 3), 
		"V43": (4, 6, 1, 3), "V42": (4, 6, 1, 3), "II": (1, 3, 5), 
		"II6": (1, 3, 5), "IV": (3, 5, 0), "IV_MAJOR": (3, 5, 0), 
		"IV_MINOR": (3, 5, 0), "I64": (0, 2, 4), "VI": (5, 0, 2), 
		"IV6": (3, 5, 0), "IV6_MAJOR": (3, 5, 0), "II7": (1, 3, 5, 0), 
		"II65": (1, 3, 5, 0), "II43": (1, 3, 5, 0), "II42": (1, 3, 5, 0),
		"IV7": (3, 5, 0, 2), "IV65": (3, 5, 0, 2), "IV65_MAJOR": (3, 5, 0, 2) 
	}
	minor_mode_alterations = {
		"V": {6: 1}, "V7": {6: 1}, "V6": {6: 1}, "VII6": {6: 1}, "V65": {6: 1},
		"V43": {6: 1}, "V42": {6: 1}, "IV_MAJOR": {5: 1}, "IV6_MAJOR": {5: 1},
		"IV65_MAJOR": {6: 1},
	}
	major_mode_alterations = {
		"IV_MINOR": {5: -1},
	}
	all_pitches_to_degrees = collections.defaultdict(dict)
	bass_degrees = {
		"I": 0, "I6": 2, "V": 4, "V7": 4, "V6": 6, "VII6": 1, "V65": 6,
		"V43": 1, "V42": 3, "II": 1, "II6": 3, "IV": 3, "IV_MAJOR": 3, 
		"IV_MINOR": 3, "I64": 4, "VI": 5, "IV6": 5, "IV6_MAJOR": 5, "II7": 1,
		"II65": 3, "II43": 5, "II42": 0, "IV7": 3, "IV65": 5, "IV65_MAJOR": 5,
	}

	def __init__(self, chord_symbol):
		self.chord_name = chord_symbol[1:] 
		self.chord_symbol = chord_symbol
		self.scale_degrees = self.chord_members[self.chord_name]
		self.bass_degree = self.bass_degrees[self.chord_name]

		if self.chord_name not in self.all_pitches_to_degrees:
			current_pitch = -12
			root_pitch = current_pitch + Voice.tonics[Voice.tonic]
			scale_sequence = Voice.mode_notes[Voice.mode]

			if Voice.mode == "ionian" and self.chord_name in self.major_mode_alterations:
				note_alterations = self.major_mode_alterations[self.chord_name]
			elif Voice.mode == "aeolian" and self.chord_name in self.minor_mode_alterations:
				note_alterations = self.minor_mode_alterations[self.chord_name]
			else:
				note_alterations = {}	

			while root_pitch < 128:
				for scale_degree in self.scale_degrees:
					note_shift = note_alterations.get(scale_degree, 0)
					chromatic_shift = scale_sequence[scale_degree] + note_shift
					current_pitch = root_pitch + chromatic_shift
					if 0 <= current_pitch <= 127:
						self.all_pitches_to_degrees[self.chord_name][current_pitch] = scale_degree
				root_pitch += 12

		self.pitches_to_degrees = self.all_pitches_to_degrees[self.chord_name]

	def __eq__(self, other):
		return self.chord_symbol == other.chord_symbol

	def __repr__(self):
		return self.chord_symbol

	@staticmethod
	def reset_settings():
		"""Removes all pitch-to-scale degree assignments"""
		Chord.all_pitches_to_degrees = collections.defaultdict(dict)
