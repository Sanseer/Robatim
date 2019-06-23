import random

from voice import Voice
import idioms.basics as idms_b

class Soprano(Voice):
	"""Spices up soprano with second- and third-species counterpoint"""

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		super().__init__()
		# self.voice_type = "soprano"

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
		print(self.final_notes)

		self.create_rhythm(0,3)
		self.create_rhythm(4,7)

		print(Voice.measure_rhythms)
		print(self.final_rhythm)

		self.finalize_part()

		print(self.final_notes)
		print(self.final_rhythm)


	def find_figures(self, current_note, next_note):
		# remove chromatics and add diatonic figures
		possible_figs = []
		# if (Voice.bass_soprano_intervals[self.note_index + 1] 
		#   not in idms_b.harmonic_dissonance):
		# 	if abs(next_note - current_note) == 2:
		# 		possible_figs.append("CPT")
		# 	if Voice.beat_division == 3 and abs(next_note - current_note) == 3:
		# 		possible_figs.append("Double CPT")
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
							((beat * idms_b.THIRD, beat * idms_b.THIRD, 
								beat * idms_b.THIRD)))
					elif Voice.beat_division == 3:
						self.final_rhythm[m_index + start].extend(
							(beat * idms_b.THIRD * 2, beat * idms_b.THIRD))
				else:
					self.final_rhythm[m_index + start].append(beat)

			# dotted rhythm in simple time
			# 8. 16 or 4. 8

			# use 16th notes with quarter note in place of single figure passing rhythm in simple time
			# 4. 16-16   8. 32-32 simple time
			# 2 8-8 4 16-16 compound time

			# 4. 8 4  8. 16 8 compound time
			
			# use 5/6 1/6 feeling good nina simone compound time
			# 4.-tie-4 8  8.-tie-8 16 compound time

			# acciaccatura
			# anticipation and divided note (whole note becomes two half notes) further embellishment?
			# Double pass in simple time: 4 4 becomes 8-16-16 4

			# a double pass rhythm can embellish itself with a neighbor tone

			# repetition of same note as single embellish
			# 8 8 in simple time
			# 4 8 in compound time

			# super smash bros groove (8-bit music theory)
			# 2 2 2 becomes 2 8. 8. 8 2 simple time
			# 8. 16-tie-8 8  16. 32-tie-16 16
			# demarcate proper beat divisions with beams




















			
