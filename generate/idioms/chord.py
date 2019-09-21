from generate.voices.voice import Voice

class Chord:

	all_chord_pitches = {}
	chord_members = {
		"I": (0,2,4), "V": (4,6,1)
	}

	def __init__(self, chord_symbol):
		self.chord_name = chord_symbol[1:] 
		self.scale_degrees = self.chord_members[self.chord_name]
		self.chord_symbol = chord_symbol
		if self.chord_name not in self.all_chord_pitches:
			self.all_pitches = []
			current_pitch = -12
			root_pitch = current_pitch + Voice.tonics[Voice.tonic]
			scale_sequence = Voice.mode_notes[Voice.mode]
			while current_pitch < 128:
				for scale_degree in self.scale_degrees:
					chromatic_shift = scale_sequence[scale_degree]
					current_pitch = root_pitch + chromatic_shift
					self.all_pitches.append(current_pitch)
				root_pitch += 12
				current_pitch = root_pitch

			self.all_pitches = [
				midi_pitch for midi_pitch in self.all_pitches if 0 <= midi_pitch <= 127]

			self.all_pitches.sort()

			self.all_chord_pitches[self.chord_name] = self.all_pitches
		else:
			self.all_pitches = self.all_chord_pitches[self.chord_name]

