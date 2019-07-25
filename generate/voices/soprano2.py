from generate.voices.voice import Voice
from generate.idioms import basics as idms_b

class Soprano(Voice):

	def __init__(self):
		self.final_notes = []
		self.final_rhythm = []
		self.phantom_notes = []
		super().__init__()

	def create_part(self):
		for rhythm in Voice.note_values:
			if type(rhythm) == int:
				current_notes = Voice.soprano_pitches[self.note_index]
				self.final_notes.extend(current_notes)
				self.final_rhythm.extend(Voice.soprano_rhythm[self.note_index])
				embellish_notes = len(current_notes) - 1
				self.phantom_notes.append(current_notes[0])
				if embellish_notes > 0:
					self.phantom_notes.extend((None,) * embellish_notes)
				self.note_index += 1
			elif type(rhythm) == str:
				self.final_notes.append("REST")
				self.phantom_notes.append("REST")
				self.final_rhythm.append(rhythm)

		print(self.final_notes, len(self.final_notes))
		print(self.final_rhythm)
		print(self.phantom_notes, len(self.phantom_notes))

		self.make_letters()
		self.lily_convert()

	def make_letters(self):
		self.note_index = -1
		tonic_letter = Voice.tonic.replace("#","").replace("b","")
		self.tonic_index = idms_b.pitch_letters.index(tonic_letter)
		for final_note, phantom_note in zip(self.final_notes, self.phantom_notes):
			if type(phantom_note) == int:
				self.note_index += 1
			if type(final_note) == int:
				self.sheet_notes.append(self.make_letter(final_note))
			elif type(final_note) == str:
				self.sheet_notes.append(final_note)
