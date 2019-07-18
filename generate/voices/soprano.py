import random

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b

class Soprano(Voice):
	"""Spices up soprano with second- and third-species counterpoint"""

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		super().__init__()
		self.fig_options = [ [] for _ in range(8)]
		self.fig_choices = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]
		self.phantom_notes = [ [] for _ in range(8)]
		self.final_rhythm = [ [] for _ in range(8)]
		self.diatonic_neighbors = [ [] for _ in range(8)]
		self.simple_time_rhythms = {
			"1": ((0.5, 0.5), (0.75, 0.25)),
			"2": ((0.75, 0.125, 0.125), (0.375, 0.375, 0.25)), 
			"3": ((0.25, 0.25, 0.25, 0.25), (0.375, 0.125, 0.25, 0.25))
		}
		self.compound_time_rhythms = {
			"1": ((2 * idms_b.THIRD, idms_b.THIRD), (2.5 * idms_b.THIRD, 0.5 * idms_b.THIRD)),
			"2": ((idms_b.THIRD, idms_b.THIRD, idms_b.THIRD), 
				(2 * idms_b.THIRD, 0.5 * idms_b.THIRD, 0.5 * idms_b.THIRD), 
				(0.5, 0.5 * idms_b.THIRD, idms_b.THIRD)),
			"3": ((idms_b.THIRD, idms_b.THIRD, 0.5 * idms_b.THIRD, 
				0.5 * idms_b.THIRD),)
		}
		self.volume = 100

	def do_stuff(self):
		self.group_notes()
		# embellishments should mirror for b1 and c1
		# b2 and c2 can be variations or mirror b1 and c1 or new direction
		# pick up note
		if random.choice((True,)):
			self.embellish()
		else:
			self.final_notes = self.measure_notes
			if Voice.half_rest_ending:
				self.final_notes[3].append("REST")
				self.final_notes[7].append("REST")
			self.final_rhythm = Voice.measure_rhythms
			self.final_rhythm = self.flatten_sequence(self.final_rhythm)
			self.final_notes = self.flatten_sequence(self.final_notes)
			print(self.final_notes)
			print(self.final_rhythm)

	def create_part(self):
		self.make_letters()
		self.lily_convert()

	def embellish(self):

		self.create_figures(0,3)
		self.note_index += len(self.measure_notes[3])
		self.create_figures(4,7)

		self.note_index = 0
		print(self.fig_options)
		print(self.diatonic_neighbors)

		self.add_notes(0,3)
		self.note_index += len(self.measure_notes[3])
		self.add_notes(4,7)

		print(self.fig_choices)
		print(self.measure_notes)
		print(self.final_notes)

		self.create_rhythm(0,3)
		self.create_rhythm(4,7)

		print(Voice.measure_rhythms)
		print(self.final_rhythm)

		self.finalize_flavored_part()
		self.phantom_notes[3] = self.measure_notes[3]
		self.phantom_notes[7] = self.measure_notes[7]
		self.phantom_notes = self.flatten_sequence(self.phantom_notes)

		print(self.final_notes, len(self.final_notes))
		print(self.final_rhythm)

	def create_figures(self, start, stop):
 		for m_index, chosen_measure in enumerate(
 				self.measure_notes[start:stop]):
 			for current_note in chosen_measure:
 				next_note = self.real_notes[self.note_index + 1]
 				fig_results = self.find_figures(current_note, next_note)
 				self.fig_options[m_index + start].append(fig_results[0])
 				self.diatonic_neighbors[m_index + start].append(fig_results[1])
 				self.note_index += 1

	def find_figures(self, current_note, next_note):
		possible_figs = []
		# remove chromatics and add diatonic figures
		# ascertain proper voice leading 
		# (e.g., melodic minor, dissonant 7th resolves down)
		diatonic_neighbors = self.find_diatonic_neighbors(current_note, next_note)
		# outer_neighbors =
		if diatonic_neighbors:
			pass_length = len(diatonic_neighbors)
			if pass_length == 1:
				possible_figs.append(f"{pass_length}D_PT")
			if pass_length == 2:
				possible_figs.append(f"{pass_length}D_PT")
			if pass_length == 3:
				possible_figs.append(f"{pass_length}D_PT")
		if not possible_figs:
			possible_figs.append(None)

		return possible_figs, diatonic_neighbors

	def find_diatonic_neighbors(self, current_note, next_note):
		difference = next_note - current_note
		# print(current_note, next_note)
		# maybe the next note shouldn't be modulation either
		if (abs(difference) <= 2 or abs(difference) > 7 or 
		  self.chromatics[self.note_index]):
			return []
		pitch_neighbors = []
		scale_neighbors = []
		increment = self.move_direction(difference)
		mid_note = current_note
		current_chord = self.get_chord()
		for _ in range(abs(difference) - 1):
			mid_note += increment
			mid_scale_note = self.make_scale_pitch(mid_note)
			if self.mode == "ionian":
				scale_sequence = {0,2,4,5,7,9,11}
			elif self.mode == "aeolian" and increment > 0:
				scale_sequence = {0,2,3,5,7,9,11}
			elif self.mode == "aeolian" and increment < 0:
				scale_sequence = {0,2,3,5,7,8,10}
			if mid_scale_note in scale_sequence:
				pitch_neighbors.append(mid_note)
				scale_neighbors.append(mid_scale_note)
		# print(pitch_neighbors)
		# print(scale_neighbors)
		return pitch_neighbors

	def add_notes(self, start, stop):
		for m_index, chosen_measure in enumerate(
				self.measure_notes[start:stop]):
			for n_index, current_note in enumerate(chosen_measure):
				nct = random.choice(
					self.fig_options[m_index + start][n_index])
				next_note = self.real_notes[self.note_index + 1]
				increment = self.move_direction(next_note - current_note)
				if nct == "CPT":
					mid_note1 = current_note + increment
					self.final_notes[m_index + start].extend(
						(current_note, mid_note1))
				elif nct == "Double CPT":
					mid_note1 = current_note + increment
					mid_note2 = mid_note1 + increment
					self.final_notes[m_index + start].extend(
						(current_note, mid_note1, mid_note2))
				elif nct is None:
					self.final_notes[m_index + start].append(current_note)
					self.phantom_notes[m_index + start].append(current_note)
				elif "D_PT" in nct:
					self.final_notes[m_index + start].append(current_note)
					self.phantom_notes[m_index + start].append(current_note)
					middle_notes = self.diatonic_neighbors[m_index + start][n_index]
					self.final_notes[m_index + start].extend(middle_notes)
					self.phantom_notes[m_index + start].extend(
						len(middle_notes) * (None,))
				self.fig_choices[m_index + start].append(nct)
				self.note_index += 1

	def create_rhythm(self, start, stop):
		for m_index, chosen_measure in enumerate(
				Voice.measure_rhythms[start:stop]):
			for b_index, beat in enumerate(chosen_measure):
				fig = self.fig_choices[m_index + start][b_index]
				if fig:
					if Voice.beat_division == 2:
						rhythm_choice = random.choice(self.simple_time_rhythms[fig[0]])
					elif Voice.beat_division == 3:
						rhythm_choice = random.choice(self.compound_time_rhythms[fig[0]])
					for value in rhythm_choice:
						self.final_rhythm[m_index + start].append(beat * value)
				else:
					self.final_rhythm[m_index + start].append(beat)

	def make_letters(self):
		# deal with raised 9 in minor not diatonic in self.make_letter?
		# if self.voice_type = "soprano"
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
		print(self.sheet_notes, len(self.sheet_notes))




















			
