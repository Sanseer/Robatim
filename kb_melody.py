import random
import pysnooper

from voice import Voice
import idioms as idms

class KBMelody(Voice):
	"""Spices up soprano with second- and third-species counterpoint"""

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		self.sheet_notes = []
		self.lily_notes = []
		self.measure_notes = []
		self.note_index = 0
		self.note_values = Voice.note_values[:]

	def do_stuff(self):
		self.group_notes()
		self.embellish()

	def create_part(self):
		self.make_letters()
		self.lily_convert()

	def embellish(self):
		fig_options = [ [] for _ in range(8)]
		fig_choices = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]
		self.final_rhythm = [ [] for _ in range(8)]

		for m_index, chosen_measure in enumerate(self.measure_notes[:3]):
			for current_note in chosen_measure:
				next_note = self.real_notes[self.note_index + 1]
				fig_options[m_index].append(self.find_figures(current_note, next_note))
				# print(fig_options, current_note, next_note)
				self.note_index += 1

		self.note_index += len(self.measure_notes[3])

		for m_index, chosen_measure in enumerate(self.measure_notes[4:7]):
			for current_note in chosen_measure:
				next_note = self.real_notes[self.note_index + 1]
				fig_options[m_index + 4].append(self.find_figures(current_note, next_note))
				# print(fig_options, current_note, next_note)
				self.note_index += 1

		self.note_index = 0
		print(fig_options)

		for m_index, chosen_measure in enumerate(self.measure_notes[:3]):
			for n_index, current_note in enumerate(chosen_measure):
				if fig_options[m_index][n_index] != [None]:
					nct = random.choice(fig_options[m_index][n_index])
					next_note = self.real_notes[self.note_index + 1]
					increment = self.move_direction(next_note - current_note)
					if nct == "CPT":
						mid_note = current_note + increment
						self.final_notes[m_index].extend((current_note, mid_note))
					elif nct == "Double CPT":
						mid_note1 = current_note + increment
						mid_note2 = mid_note1 + increment
						self.final_notes[m_index].extend((current_note, mid_note1, mid_note2))
				else:
					nct = None
					self.final_notes[m_index].append(current_note)
				fig_choices[m_index].append(nct)
				self.note_index += 1

		self.note_index += len(self.measure_notes[3])

		for m_index, chosen_measure in enumerate(self.measure_notes[4:7]):
			for n_index, current_note in enumerate(chosen_measure):
				if fig_options[m_index + 4][n_index] != [None]:
					nct = random.choice(fig_options[m_index + 4][n_index])
					next_note = self.real_notes[self.note_index + 1]
					increment = self.move_direction(next_note - current_note)
					if nct == "CPT":
						mid_note = current_note + increment
						self.final_notes[m_index + 4].extend((current_note, mid_note))
					elif nct == "Double CPT":
						mid_note1 = current_note + increment
						mid_note2 = mid_note1 + increment
						self.final_notes[m_index + 4].extend((current_note, mid_note1, mid_note2))
				else:
					nct = None
					self.final_notes[m_index + 4].append(current_note)
				fig_choices[m_index + 4].append(nct)
				self.note_index += 1

		# self.final_notes[3] = self.measure_notes[3]
		# self.final_notes[7] = self.measure_notes[7]

		# if Voice.half_rest_ending:
		# 	self.final_notes[3].append("REST")
		# 	self.final_notes[7].append("REST")

		print(self.measure_notes)
		print(self.final_notes)
		print(fig_options)
		print(fig_choices)

		for m_index, chosen_measure in enumerate(Voice.measure_rhythms[:3]):
			for b_index, beat in enumerate(chosen_measure):
				fig = fig_choices[m_index][b_index]
				if fig:
					if Voice.beat_division == 2:
						self.final_rhythm[m_index].extend((beat / 2, beat / 2))
					elif Voice.beat_division == 3 and "Double" in fig:
						self.final_rhythm[m_index].extend(
							(beat * idms.THIRD, beat * idms.THIRD, beat * idms.THIRD))
					elif Voice.beat_division == 3:
						self.final_rhythm[m_index].extend(
							(beat * idms.THIRD * 2, beat * idms.THIRD))
				else:
					self.final_rhythm[m_index].append(beat)

		for m_index, chosen_measure in enumerate(Voice.measure_rhythms[4:7]):
			for b_index, beat in enumerate(chosen_measure):
				fig = fig_choices[m_index + 4][b_index]
				if fig:
					if Voice.beat_division == 2:
						self.final_rhythm[m_index + 4].extend((beat / 2, beat / 2))
					elif Voice.beat_division == 3 and "Double" in fig:
						self.final_rhythm[m_index + 4].extend(
							(beat * idms.THIRD, beat * idms.THIRD, beat * idms.THIRD))
					elif Voice.beat_division == 3:
						self.final_rhythm[m_index + 4].extend(
							(beat * idms.THIRD * 2, beat * idms.THIRD))
				else:
					self.final_rhythm[m_index + 4].append(beat)


		print(fig_choices)
		print(Voice.measure_rhythms)
		print(self.final_rhythm)

		self.final_notes[3] = self.measure_notes[3]
		self.final_notes[7] = self.measure_notes[7]
		self.final_rhythm[3] = Voice.measure_rhythms[3]
		self.final_rhythm[7] = Voice.measure_rhythms[7]

		if Voice.half_rest_ending:
			self.final_notes[3].append("REST")
			self.final_notes[7].append("REST")

		self.final_rhythm = self.flatten_sequence(self.final_rhythm)
		self.final_notes = self.flatten_sequence(self.final_notes)

		print(fig_choices)
		print(self.final_notes, len(self.final_notes))
		print(self.final_rhythm, len(self.final_rhythm))


	def find_figures(self, current_note, next_note):
		possible_figs = []
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

 
	# @property
	# def notes(self):
	# 	return self.create_rests(self.real_notes[:])

	# @property
	# def groove(self):
	# 	return self.note_values

		# embellish compound time sig with one note 2_1 rhythm

















			
