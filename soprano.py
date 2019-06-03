import random

from voice import Voice
import idioms as idms

class Soprano(Voice):
	"""Spices up soprano with second- and third-species counterpoint"""

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		super().__init__()

	def do_stuff(self):
		self.group_notes()
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
		self.fig_options = [ [] for _ in range(8)]
		self.fig_choices = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]
		self.final_rhythm = [ [] for _ in range(8)]

		self.create_figures(0,3)
		self.create_figures(4,7)

		self.note_index = 0
		print(self.fig_options)

		self.add_notes(0,3)
		self.note_index += len(self.measure_notes[3])
		self.add_notes(4,7)

		print(self.fig_choices)
		print(self.measure_notes)

		self.create_rhythm(0,3)
		self.create_rhythm(4,7)

		print(self.fig_choices)
		print(Voice.measure_rhythms)
		print(self.final_rhythm)

		self.finalize_part()

		print(self.final_notes)
		print(self.final_rhythm)


	def find_figures(self, current_note, next_note):
		possible_figs = []
		if (Voice.bass_soprano_intervals[self.note_index + 1] 
		  not in idms.harmonic_dissonance):
			if abs(next_note - current_note) == 2:
				possible_figs.append("CPT")
			if Voice.beat_division == 3 and abs(next_note - current_note) == 3:
				possible_figs.append("Double CPT")
		# current_scale_degree = self.make_scale_degree(current_note, False)
		# next_scale_degree = self.make_scale_degree(next_note, False)
		# move = self.move_direction(next_note - current_note)
		if not possible_figs:
			possible_figs.append(None)

		return possible_figs

	def create_figures(self, start, stop):
 		for m_index, chosen_measure in enumerate(
 				self.measure_notes[start:stop]):
 			for current_note in chosen_measure:
 				next_note = self.real_notes[self.note_index + 1]
 				self.fig_options[m_index + start].append(self.find_figures(current_note, next_note))
 				# print(fig_options, current_note, next_note)
 				self.note_index += 1

	def add_notes(self, start, stop):
		for m_index, chosen_measure in enumerate(
				self.measure_notes[start:stop]):
			for n_index, current_note in enumerate(chosen_measure):
				nct = random.choice(
					self.fig_options[m_index + start][n_index])
				next_note = self.real_notes[self.note_index + 1]
				increment = self.move_direction(next_note - current_note)
				if nct == "CPT":
					mid_note = current_note + increment
					self.final_notes[m_index + start].extend(
						(current_note, mid_note))
				elif nct == "Double CPT":
					mid_note1 = current_note + increment
					mid_note2 = mid_note1 + increment
					self.final_notes[m_index + start].extend(
						(current_note, mid_note1, mid_note2))
				elif nct is None:
					self.final_notes[m_index + start].append(current_note)
				self.fig_choices[m_index + start].append(nct)
				self.note_index += 1

	def create_rhythm(self, start, stop):
		for m_index, chosen_measure in enumerate(
				Voice.measure_rhythms[start:stop]):
			for b_index, beat in enumerate(chosen_measure):
				fig = self.fig_choices[m_index + start][b_index]
				if fig:
					if Voice.beat_division == 2:
						self.final_rhythm[m_index + start].extend(
							(beat / 2, beat / 2))
					elif Voice.beat_division == 3 and "Double" in fig:
						self.final_rhythm[m_index + start].extend(
							((beat * idms.THIRD, beat * idms.THIRD, 
								beat * idms.THIRD)))
					elif Voice.beat_division == 3:
						self.final_rhythm[m_index + start].extend(
							(beat * idms.THIRD * 2, beat * idms.THIRD))
				else:
					self.final_rhythm[m_index + start].append(beat)



















			
