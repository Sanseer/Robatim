import collections

from generate.voices.voice import Voice

class Chord:

	chord_members = {
		"I": (0, 2, 4), "V": (4, 6, 1), "V7": (4, 6, 1, 3), "V6":(4, 6, 1) 
	}
	minor_mode_alterations = {
		"V": {6: 1}, "V7": {6: 1}, "V6": {6: 1}
	}
	major_mode_alterations = {
		None: None,
	}
	all_pitches_to_degrees = collections.defaultdict(dict)
	
	bass_degrees = {
		"I": 0, "V": 4, "V7": 4, "V6": 6
	}

	def __init__(self, chord_symbol):
		self.chord_name = chord_symbol[1:] 
		self.chord_symbol = chord_symbol
		self.scale_degrees = Chord.chord_members[self.chord_name]
		self.bass_degree = Chord.bass_degrees[self.chord_name]

		if self.chord_name not in Chord.all_pitches_to_degrees:
			current_pitch = -12
			root_pitch = current_pitch + Voice.tonics[Voice.tonic]
			scale_sequence = Voice.mode_notes[Voice.mode]

			if Voice.mode == "ionian" and self.chord_name in Chord.major_mode_alterations:
				note_alterations = Chord.major_mode_alterations[self.chord_name]
			elif Voice.mode == "aeolian" and self.chord_name in Chord.minor_mode_alterations:
				note_alterations = Chord.minor_mode_alterations[self.chord_name]
			else:
				note_alterations = {}	

			while root_pitch < 128:
				for scale_degree in self.scale_degrees:
					note_shift = note_alterations.get(scale_degree, 0)
					chromatic_shift = scale_sequence[scale_degree] + note_shift
					current_pitch = root_pitch + chromatic_shift
					if 0 <= current_pitch <= 127:
						Chord.all_pitches_to_degrees[self.chord_name][current_pitch] = scale_degree
				root_pitch += 12

		self.pitches_to_degrees = Chord.all_pitches_to_degrees[self.chord_name]

	def __eq__(self, other):
		return self.chord_symbol == other.chord_symbol

	def __str__(self):
		return self.chord_symbol
