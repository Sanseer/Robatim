import collections

class Voice:

	chord_sequence = []
	mode = None
	idms_mode = None
	tonic = None
	all_midi_pitches = []
	Note = collections.namedtuple('Note', ["pitch", "time", "duration"])

	mode_notes = {
		"lydian": (0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24),
		"ionian": (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24),
		"mixo": (0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24),
		"dorian": (0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19, 21, 22, 24),
		"aeolian": (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24),
		"phryg": (0, 1, 3, 5, 7, 8, 10, 12, 13, 15, 17, 19, 20, 22, 24) 
	}
	tonics = {
		"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
		"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
	}

	# make into static method
	def calculate_slope(self, move_distance):
		if move_distance < 0:
			return -1
		elif move_distance > 0:
			return 1
		return 0

	@staticmethod
	def has_cross_duplicates(sequence):
		for item1, item2, item3, item4 in zip(
			sequence, sequence[1:], sequence[2:], sequence[3:]):
			if (item1, item2) == (item3, item4):
				return True
		return False
