import random
import pysnooper

from voice import Voice
import idioms as idms

class KBMelody(Voice):

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		self.sheet_notes = []
		self.lily_notes = []
		self.measure_notes = []
		self.measure_rhythms = []
		self.note_index = 0
		self.measure_index = 0
		self.beat_index = 0
		self.old_note, self.new_note = 0, 0
		self.note_values = Voice.note_values[:]
		
	def do_stuff(self):
		self.group_rhythm()
		self.group_notes()
		self.embellish()



	def group_notes(self):
		for rhythm in self.measure_rhythms:
			array = []
			for _ in rhythm:
				array.append(self.real_notes[self.note_index])
				self.note_index += 1
			self.measure_notes.append(array)

		self.note_index = 0

	def group_rhythm(self):
		for _ in range(8):
			array = []
			while sum(array) < Voice.measure_length:
				array.append(int(self.note_values[self.note_index]))
				self.note_index += 1
			self.measure_rhythms.append(array)

		if Voice.half_rest_ending:
			self.measure_rhythms[3].pop()
			self.measure_rhythms[7].pop()

		self.note_index = 0

	def embellish(self):
		self.select_groove(4,7)
		if self.pick_figuration():
			self.create_nonchord_tones()
			self.find_note_index()
			self.fill_notes(1)
		self.select_groove(self.measure_index - 4, self.measure_index - 3)
		if self.pick_figuration():
			self.create_nonchord_tones()
			self.find_note_index()
			self.fill_notes()

	def select_groove(self, start, stop):
		self.measure_index = random.choice(range(start, stop))
		selected_rhythm = self.measure_rhythms[self.measure_index]
		selected_notes = self.measure_notes[self.measure_index]
		self.beat_index = random.choice(range(len(selected_rhythm) - 1))
		self.old_beat = selected_rhythm[self.beat_index]
		self.new_beat = selected_rhythm[self.beat_index + 1]
		self.old_note = selected_notes[self.beat_index]
		self.new_note = selected_notes[self.beat_index + 1]

		if Voice.beat_division == 2:
			self.new_rhythm = idms.simple_embellish_rhythms[
				(self.old_beat, self.new_beat)]
		elif Voice.beat_division == 3:
			self.new_rhythm = idms.compound_embellish_rhythms[
				(self.old_beat, self.new_beat)]

		pitch_distance = abs(self.new_note - self.old_note)
		self.note_choices = list(
			idms.figurations[(Voice.beat_division, pitch_distance)])

	def pick_figuration(self):
		self.selected_fig = None
		diatonic_fig = all(self.is_diatonic(pitch) 
			for pitch in (self.old_note, self.new_note))
		while self.selected_fig is None and self.note_choices:
			self.selected_fig = random.choice(self.note_choices)
			if (not diatonic_fig and 
			any("D" in str(slot) for slot in self.selected_fig)):
				self.note_choices.remove(self.selected_fig)
				self.selected_fig = None

		return self.selected_fig

	def find_note_index(self):
		note_index = 0
		found_index = False
		for measure_index, measure in enumerate(self.measure_notes):
			if found_index:
				break
			for beat_index, note in enumerate(measure):
				if (measure_index == self.measure_index and 
				beat_index == self.beat_index):
					self.note_index = note_index
					found_index = True
					break
				note_index += 1

	# @pysnooper.snoop(watch_explode=('self'))
	def fill_notes(self, attempt=0):
		new_sequence = []
		for move in self.selected_fig:
			new_sequence.append(self.embellishers[move])
		self.real_notes[self.note_index:self.note_index + 2] = new_sequence
		if Voice.half_rest_ending and attempt is 1:
			self.note_index += 1
		self.note_values[self.note_index:self.note_index + 2] = self.new_rhythm
		print(self.note_values, len(self.note_values))
		print(self.real_notes, len(self.real_notes))

	def create_nonchord_tones(self):
		self.embellishers = {
			0: self.old_note, 1: self.new_note, 
			"DUN": self.diatonic_neighbor(1),
			"DLN": self.diatonic_neighbor(-1),
			"CUN": self.chromatic_neighbor(1),
			"CLN": self.chromatic_neighbor(-1),
			"LDFILL0": self.diatonic_fill(0, 0),
			"RDFILL0": self.diatonic_fill(1, 0),
			"LCFILL0": self.chromatic_fill(0, 0),
			"RCFILL0": self.chromatic_fill(1, 0),
			"LCON": self.outer_chromatic(0),
			"RCON": self.outer_chromatic(1),
		}

	def diatonic_neighbor(self, direction):
		if direction > 0:
			current_pitch = max((self.old_note, self.new_note))
		elif direction < 0:
			current_pitch = min((self.old_note, self.new_note))
		while True:
			current_pitch += direction
			if self.is_diatonic(current_pitch):
				return current_pitch

	def chromatic_neighbor(self, direction):
		if direction > 0:
			reference_pitch = max((self.old_note, self.new_note))
		elif direction < 0:
			reference_pitch = min((self.old_note, self.new_note))
		return reference_pitch + direction

	def diatonic_fill(self, origin_index, steps):
		current_pitch = self.set_reference_pitch(origin_index)
		increment = self.find_increment(origin_index)
		counter = 0
		while True:
			current_pitch += increment
			if self.is_diatonic(current_pitch) and counter == steps:
				return current_pitch
			elif self.is_diatonic(current_pitch):
				counter += 1

	def chromatic_fill(self, origin_index, steps):
		current_pitch = self.set_reference_pitch(origin_index)
		increment = self.find_increment(origin_index)
		counter = 0
		while True:
			current_pitch += increment
			if counter == steps:
				return current_pitch

	def outer_chromatic(self, origin_index):
		current_pitch = self.set_reference_pitch(origin_index)
		increment = self.find_increment(origin_index) * -1
		return current_pitch + increment

	def find_increment(self, origin_index):
		slope = self.new_note - self.old_note
		if origin_index == 0 and slope > 0 or origin_index == 1 and slope < 0:
			return -1
		elif origin_index == 1 and slope > 0 or origin_index == 0 and slope < 0:
			return 1
		return 1

	def set_reference_pitch(self, origin_index):
		origin_notes = (self.old_note, self.new_note)
		return origin_notes[origin_index]















			
