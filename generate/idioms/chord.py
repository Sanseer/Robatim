import collections

from generate.voices.voice import Voice

class Chord:

	chord_members = {
		"I": (0,2,4), "V": (4,6,1)
	}
	minor_mode_alterations = {
		"V": {4: 0, 6: 1, 1: 0},
	}
	major_mode_alterations = {
		None: None,
	}
	all_pitches_to_degrees = collections.defaultdict(dict)

	def __init__(self, chord_symbol):
		self.chord_name = chord_symbol[1:] 
		self.chord_symbol = chord_symbol
		self.scale_degrees = Chord.chord_members[self.chord_name]

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

			while current_pitch < 128:
				for scale_degree in self.scale_degrees:
					note_shift = note_alterations.get(scale_degree, 0)
					chromatic_shift = scale_sequence[scale_degree] + note_shift
					current_pitch = root_pitch + chromatic_shift
					if 0 < current_pitch < 128:
						Chord.all_pitches_to_degrees[self.chord_name][current_pitch] = scale_degree
				root_pitch += 12
				current_pitch = root_pitch

		self.pitches_to_degrees = Chord.all_pitches_to_degrees[self.chord_name]

	def __eq__(self, other):
		return self.chord_symbol == other.chord_symbol
