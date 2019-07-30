import copy

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b


class MelodyMixin():

	@property
	def current_beat(self):
		return self.flat_restless_rhythms[self.note_index]

	def set_measure_index(self):
		note_index = 0
		for m_index, measure in enumerate(self.nested_restless_rhythms):
			for current_beat in measure:
				if note_index == self.note_index:
					self.measure_index = m_index
					return
				note_index += 1

	def set_beat_index(self):
		note_index = 0
		for measure in self.nested_restless_rhythms:
			for b_index, current_beat in enumerate(measure):
				if note_index == self.note_index:
					self.beat_index = b_index - len(measure)
					return
				note_index += 1

	def embellish_chord(self):

		embellish_rhythms = {
			4: [2,2], 3: [2,1], 2: [2], 1:[1]
		}

		new_rhythm = embellish_rhythms[self.current_beat]

		self.first_note = self.combo_choice[0]
		self.last_note = self.combo_choice[1]

		if abs(self.first_note - self.last_note) >= 12:
			print("Leap too wide")
			return [], []

		if (self.measure_index in {3,7} and self.beat_index == -1 
		  or len(new_rhythm) == 1):
			print("No embellishment.")
			melodies = [[self.first_note]]
			new_rhythm = [self.current_beat]
		else:
			melodies = self.create_embellishments()
			if not melodies:
				[], []
		if self.note_index == self.sequence_length - 1:
			# also needs validation
			return melodies, new_rhythm
		approved_melodies = []
		for melody in melodies:
			self.new_melody = melody
			if self.validate_embellishment():
				approved_melodies.append(melody)

		print(f"Approved melodies: {approved_melodies}")
		return approved_melodies, new_rhythm
		# return [[first_note, first_note]], new_rhythm

	def shift_scale_degree(self, original_scale_degree, shift_amount):
		new_scale_degree = original_scale_degree + shift_amount
		return self.center_scale_degree(new_scale_degree)

	def create_embellishments(self):
		possible_melodies = []
		pitch_difference = self.last_note - self.first_note
		print(f"Pitch difference: {pitch_difference}", end=" ")
		increment = self.move_direction(pitch_difference)
		print(f"Increment: {increment}", end=" ")
		low_point = Voice.tenor_pitches[self.note_index]
		print(f"Low point: {low_point}")
		high_point = 81

		begin_degree = self.get_scale_degree(self.first_note)
		print(f"Begin degree: {begin_degree}", end=" ")
		# fix index_shift, how to determine scale degree from starting pitch
		end_degree = self.get_scale_degree(self.last_note)
		print(f"End degree: {end_degree}", end=" ")

		if begin_degree < end_degree:
			if increment > 0:
				scale_difference = end_degree - begin_degree
			elif increment < 0:
				scale_difference = abs(begin_degree - end_degree + 7)
		elif begin_degree > end_degree:
			if increment > 0:
				scale_difference = abs(end_degree - begin_degree + 7)
			elif increment < 0: 
				scale_difference = begin_degree - end_degree
		else:
			scale_difference = 0
		print(f"Scale difference: {scale_difference}")
		# begin_index = pitch_sequence.index(self.first_note)
		# end_index = pitch_sequence.index(self.last_note)

		if scale_difference == 1:
			middle_note = self.increment_pitch(
				self.last_note, end_degree, increment)
			# middle_note = pitch_sequence[end_index + increment]
			if low_point <= middle_note <= high_point:
				possible_melodies.append([self.first_note, middle_note])
		elif scale_difference == 2:
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, increment)
			# middle_note = pitch_sequence[begin_index + increment]
			possible_melodies.append([self.first_note, middle_note])
			middle_note = self.increment_pitch(
				self.last_note, end_degree, increment)
			# middle_note = pitch_sequence[end_index + increment]
			if low_point <= middle_note <= high_point:
				possible_melodies.append([self.first_note, middle_note])
		elif scale_difference == 3:
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, increment * 2)
			# middle_note = pitch_sequence[begin_index + (increment * 2)]
			possible_melodies.append([self.first_note, middle_note])
		elif scale_difference == 4:
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, increment * 2)
			# middle_note = pitch_sequence[begin_index + (increment * 2)]
			possible_melodies.append([self.first_note, middle_note])
		elif scale_difference == 5:
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, increment * 2)
			# middle_note = pitch_sequence[begin_index + (increment * 2)]
			possible_melodies.append([self.first_note, middle_note])
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, increment * 3)
			# middle_note = pitch_sequence[begin_index + (increment * 3)]
			possible_melodies.append([self.first_note, middle_note])
		elif scale_difference == 0:
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, 1)
			if low_point <= middle_note <= high_point:
				possible_melodies.append([self.first_note, middle_note])
			middle_note = self.increment_pitch(
				self.first_note, begin_degree, -1)
			if low_point <= middle_note <= high_point:
				possible_melodies.append([self.first_note, middle_note])


		print(f"Possible melodies: {possible_melodies}")
		# if scale_difference == 0 and begin_index != 0:
		# 	middle_note = pitch_sequence[begin_index - 1]
		# 	possible_melodies.append([self.note_index, middle_note])
		# if scale_difference == 0 and end_index != len(pitch_sequence) - 1:
		# 	middle_note = pitch_sequence[begin_index + 1]
		# 	possible_melodies.append([self.note_index, middle_note])

		return possible_melodies

	def validate_embellishment(self):

		bass_soprano_intervals = copy.deepcopy(self.bass_soprano_intervals)
		tenor_soprano_intervals = copy.deepcopy(self.tenor_soprano_intervals)
		alto_soprano_intervals = copy.deepcopy(self.alto_soprano_intervals)

		composite_intervals = [
			bass_soprano_intervals, tenor_soprano_intervals, 
			alto_soprano_intervals]

		self.add_soprano_intervals(Voice.bass_pitches, bass_soprano_intervals)
		self.add_soprano_intervals(Voice.tenor_pitches, tenor_soprano_intervals)
		self.add_soprano_intervals(Voice.alto_pitches, alto_soprano_intervals)

		bass_soprano_intervals.append([self.get_interval(
			Voice.bass_pitches[self.note_index + 1], self.combo_choice[1], 1)])
		tenor_soprano_intervals.append([self.get_interval(
			Voice.tenor_pitches[self.note_index + 1], self.combo_choice[1], 1)])
		alto_soprano_intervals.append([self.get_interval(
			Voice.alto_pitches[self.note_index + 1], self.combo_choice[1], 1)]) 

		for interval_list in composite_intervals:
			if (interval_list[-2][-1] in idms_b.harmonic_dissonance and 
			  (abs(self.new_melody[-1] - self.first_note) > 2 or 
			  abs(self.new_melody[-1] - self.last_note) > 2) or 
			  (self.first_note == self.last_note and
			  self.new_melody[-1] - self.first_note <= 2)):
				print("Harmonic dissonance moves by step")
				return False

		soprano_motion = copy.deepcopy(Voice.soprano_motion)
		self.add_soprano_motions(soprano_motion)

		bass_soprano_motion = self.bass_soprano_motion[:]
		tenor_soprano_motion = self.tenor_soprano_motion[:]
		alto_soprano_motion = self.alto_soprano_motion[:]
		if self.note_index > 0:
			previous_note = self.soprano_full_pitches[self.note_index - 1][-1]
		if (self.note_index > 0 and len(self.new_melody) >= 2 and
		  abs((previous_note - self.first_note)) > 5  and
		  (abs(self.first_note - self.new_melody[1]) > 2 or 
		  soprano_motion[-2][-1] == soprano_motion[-1][0])):
			print("Leap followed by step within 2 chords")
			return False
		elif (self.note_index > 1 and 
		  len(self.soprano_full_pitches[self.note_index - 1]) == 1 and
		  abs(self.soprano_full_pitches[self.note_index - 2][-1] - previous_note) > 5 and
		  (abs(previous_note - self.first_note) > 2 or 
		  soprano_motion[-2][-1] == soprano_motion[-1][0])):
			print("Leap followed by step within 3 chords")
			return False

		self.add_soprano_motion_type(
			Voice.bass_motion, soprano_motion, bass_soprano_motion, 
			bass_soprano_intervals, 1)
		self.add_soprano_motion_type(
			Voice.tenor_motion, soprano_motion, tenor_soprano_motion, 
			tenor_soprano_intervals, 1)
		self.add_soprano_motion_type(
			Voice.alto_motion, soprano_motion, alto_soprano_motion, 
			alto_soprano_intervals, 1)

		composite_movements = [
			bass_soprano_motion, tenor_soprano_motion, alto_soprano_motion
		]

		downbeat_motions = []

		if self.last_note < self.first_note:
			new_move = -1
		elif self.last_note > self.first_note:
			new_move = 1
		else:
			new_move = 0 
		self.add_custom_motion_type(
			Voice.bass_motion, new_move, downbeat_motions, 
			bass_soprano_intervals, 1)
		self.add_custom_motion_type(
			Voice.tenor_motion, new_move, downbeat_motions, 
			tenor_soprano_intervals, 1)
		self.add_custom_motion_type(
			Voice.alto_motion, new_move, downbeat_motions, 
			alto_soprano_intervals, 1)

		for interval_list, motion_list, consecutive_downbeat in zip(
			composite_intervals, composite_movements, downbeat_motions):
			if (motion_list[-1] == "Parallel" and interval_list[-1][0] in {"P5", "P8"} and 
			  interval_list[-2][-1] in {"P5", "P8"}): 
				return False
		# 	elif (consecutive_downbeat == "Parallel" and interval_list[-1][0] in {"P5", "P8"} and 
		# 	  interval_list[-2][0] in {"P5", "P8"}):
		# 		return False

		return True

		# passing tone dissonance approached and continued by step
		# consonances can be approached by leap as well as by step
		# unisons can appear on the second half note 
		# if left by stepwise motion in the opposite direction of approach
		# Avoid parallel fifths on directly adjacent and consecutive first beats

	def add_custom_motion_type(
	  self, old_motion, new_move, movements, intervals, index_shift,
	  beat_index=0):
		old_move = old_motion[self.note_index - 1 + index_shift]

		if (old_move == new_move and old_move != 0 and 
		  intervals[-1][0] == intervals[-2][beat_index]):
			movements.append("Parallel")
		elif old_move == new_move and old_move == 0:
			movements.append("No motion")
		elif old_move == -(new_move) and old_move != 0:
			movements.append("Contrary")
		elif (old_move == new_move and 
		  intervals[-1][0] != intervals[-2][beat_index]):
			movements.append("Similar")
		elif ((old_move == 0 or new_move == 0) and 
		  (old_move != 0 or new_move != 0)):
			movements.append("Oblique")
		else:
			raise ValueError("Invalid motion")






