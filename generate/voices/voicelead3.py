import copy

class MelodyMixin():

	@property
	def current_beat(self):
		return self.flat_restless_rhythms[self.note_index]

	@property
	def measure_index(self):
		note_index = 0
		for m_index, measure in enumerate(self.nested_restless_rhythms):
			for current_beat in measure:
				if note_index == self.note_index:
					return m_index
				note_index += 1

	@property
	def beat_index(self):
		note_index = 0
		for measure in self.nested_restless_rhythms:
			for b_index, current_beat in enumerate(measure):
				if note_index == self.note_index:
					return b_index - len(measure)
				note_index += 1

	def embellish_chord(self):

		embellish_rhythms = {
			4: [2,2], 3: [2,1], 2: [2], 1:[1]
		}

		new_rhythm = embellish_rhythms[self.current_beat]

		first_note = self.combo_choice[0]
		last_note = self.combo_choice[1]

		if (self.measure_index in {3,7} and self.beat_index == -1 
		  or len(new_rhythm) == 1):
			return [[first_note]], [self.current_beat]

		return [[first_note, first_note]], new_rhythm

