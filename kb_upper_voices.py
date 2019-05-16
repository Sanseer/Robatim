import itertools
import random

from voice import Voice
import idioms as idms

class KBUpperVoices(Voice):
	"""Creates chords using bass notes for a keyboard style tune"""

	def __init__(self):
		self.note_index = 0
		self.fault_index = None
		self.pitch_amounts = []
		self.possible_pitches = []
		self.pitch_amounts.extend(("Blank",) * 
			(Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length))
		self.possible_pitches.extend(("Blank",) * 
			(Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length))

		self.bass_tenor_intervals = []
		self.bass_alto_intervals = []
		self.bass_soprano_intervals = []
		self.tenor_alto_intervals = []
		self.tenor_soprano_intervals = []
		self.alto_soprano_intervals = []
		self.bass_tenor_motion = []
		self.bass_alto_motion = []
		self.bass_soprano_motion = []
		self.tenor_alto_motion = []
		self.tenor_soprano_motion = []
		self.alto_soprano_motion = []

		# Intentional alias
		self.composite_intervals = [self.bass_tenor_intervals, 
			self.bass_alto_intervals, self.bass_soprano_intervals, 
			self.tenor_alto_intervals, self.tenor_soprano_intervals,
			self.alto_soprano_intervals]
		self.composite_movements = [self.bass_tenor_motion, 
			self.bass_alto_motion, self.bass_soprano_motion, 
			self.tenor_alto_motion, self.tenor_soprano_motion,
			self.alto_soprano_motion]
		assert(len(Voice.bass_pitches) == len(self.pitch_amounts))

	def create_parts(self):
		self.populate_note(self.note_index)
		while self.pitch_amounts[0] == "Blank":
			self.combo_choice = self.possible_pitches[0][0]
			self.pitch_amounts[0] = self.combo_choice
			if self.validate_notes():
				break
			self.possible_pitches[0].remove(self.combo_choice)
			self.pitch_amounts[0] = "Blank"
			self.erase_last_note()
		self.add_notes()
		self.split_notes()

	def populate_note(self, index):
		# use index attribute?
		current_chord = abs(Voice.chord_path[index])
		chord_root = idms.chord_tones[current_chord][0]
		chord_length = len(idms.chord_tones[current_chord])
		all_pitches = self.create_chord_pitches(index,chord_length, chord_root)
		if Voice.chromatics[index] == "2D":
			all_pitches = self.add_chromatics(index, all_pitches)

		pitch_combos = self.create_pitch_combos(all_pitches)
		self.possible_pitches[index] = self.arrange_pitch_combos(
			index, pitch_combos)
		print(len(self.possible_pitches[self.note_index]), "options left", end=" ")

	def create_chord_pitches(self, index, chord_length, chord_root):
		all_pitches = []
		# high_point = 66
		high_point = 81
		low_point = Voice.bass_pitches[index]

		root_pitch = idms.modes[Voice.mode][chord_root] + idms.tonics[Voice.tonic]
		chord_pitches = [0]
		new_position = chord_root + 2
		for _ in range(chord_length - 1):
			chord_pitches.append((idms.modes[Voice.mode][new_position] - 
				idms.modes[Voice.mode][chord_root]))
			new_position += 2

		if Voice.mode == "aeolian" and chord_root == 4:
			chord_pitches[1] += 1
		elif Voice.mode == "aeolian" and chord_root == 6:
			chord_pitches[0] += 1

		chord_slot = 0
		current_pitch = root_pitch

		while current_pitch < low_point:
			if (chord_length - 1) >= chord_slot:
				chord_slot += 1
			if (chord_length - 1) < chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_pitches[chord_slot]
			# print("Shifting pitch", end=" ")

		while current_pitch <= high_point:
			if (chord_length - 1) >= chord_slot:
				all_pitches.append(current_pitch)
				chord_slot += 1
			if (chord_length - 1) < chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_pitches[chord_slot]
			# print("Adding pitch", end=" ")

		return all_pitches

	def add_chromatics(self, nc_index, all_pitches):
		for index, pitch in enumerate(all_pitches[:]):
			all_pitches[index] += self.convert_sec_dom(
				Voice.chord_path[nc_index], pitch) 
		return all_pitches

	def create_pitch_combos(self, all_pitches):
		# pitch_combos = list(itertools.combinations_with_replacement(
		# 	all_pitches, 3))
		# for (value1, value2, value3) in pitch_combos[:]:
		# 	if ((value1 == value2 == value3) or 
		# 		(Voice.bass_pitches[index] == value1 == value2) or
		# 		max(value1, value2, value3) - min(value1, value2, value3) > 12 or 
		# 		Voice.bass_pitches[index] == value1 == value2 - 12 == value3 - 12 or
		# 		Voice.bass_pitches[index] == value1 - 12 == value2 - 24 == value3 - 24 or
		# 		Voice.bass_pitches[index] == value1 - 12 == value2 - 12 == value3 - 24):
		# 		pitch_combos.remove((value1, value2, value3))
		double_pitch_combos = list(itertools.combinations_with_replacement(
			all_pitches,2))
		for (t_pitch, a_pitch) in double_pitch_combos[:]:
			if (t_pitch > 66 or a_pitch > 66 or a_pitch - t_pitch > 12 or 
				Voice.bass_pitches[self.note_index] == t_pitch == a_pitch):
				double_pitch_combos.remove((t_pitch, a_pitch))
		soprano_pitches = [pitch for pitch in all_pitches if pitch > 58]

		triple_pitch_combos = []
		for (t_pitch, a_pitch) in double_pitch_combos:
			for s_pitch in soprano_pitches:
				if self.preprocess_combo(t_pitch, a_pitch, s_pitch):
					triple_pitch_combos.append((t_pitch, a_pitch, s_pitch))
		return triple_pitch_combos

	def arrange_pitch_combos(self, index, pitch_combos):
		"""Arrange chords by completeness and smoothest motion"""
		complete_rank = []

		for notes in pitch_combos:
			scale_pitches = []
			scale_pitches.append(self.make_scale_pitch(Voice.bass_pitches[index]))
			scale_pitches.append(self.make_scale_pitch(notes[0]))
			scale_pitches.append(self.make_scale_pitch(notes[1]))
			scale_pitches.append(self.make_scale_pitch(notes[2]))
			if len(set(scale_pitches)) == 1: 
				print(Voice.bass_pitches[index], notes[0], notes[1], notes[2])
				raise Exception("Complete unison")
			complete_rank.append(len(set(scale_pitches)))

		complete_chord_sort = [x for _,x in sorted(zip(
			complete_rank, pitch_combos), reverse=True)]
		# print(complete_chord_sort)

		if index == 0:
			return complete_chord_sort

		complete_rank = sorted(complete_rank, reverse=True)
		chord_index_dividers = []
		chord_types = sorted(list(set(complete_rank)), reverse=True)
		for chord_type in chord_types[1:]:
			chord_index_dividers.append(complete_rank.index(chord_type))

		smooth_chord_sort = []
		for slot in range(len(chord_index_dividers) - 1):
			start = chord_index_dividers[slot]
			stop = chord_index_dividers[slot + 1]
			chord_group = complete_chord_sort[start:stop]
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, chord_group))

		if len(chord_index_dividers) > 1:
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, complete_chord_sort[stop:]))
		elif len(chord_index_dividers) == 1:
			divider = chord_index_dividers[0]
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, complete_chord_sort[:divider]))
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, complete_chord_sort[divider:]))
		else:
			return complete_chord_sort

		return smooth_chord_sort

	def arrange_chord_motion(self, index, chord_group):
		chord_motions = []
		old_tenor_note = self.pitch_amounts[index - 1][0]
		old_alto_note = self.pitch_amounts[index - 1][1]
		old_soprano_note = self.pitch_amounts[index - 1][2]
		for chord in chord_group:
			new_tenor_note = chord[0] 
			new_alto_note = chord[1]
			new_soprano_note = chord[2]
			movement = abs(new_tenor_note - old_tenor_note)
			movement += abs(new_alto_note - old_alto_note)
			movement += abs(new_soprano_note - old_soprano_note)
			chord_motions.append(int(movement))
		motion_sort = [x for _,x in sorted(zip(chord_motions, chord_group))]

		return motion_sort

	def add_notes(self):
		"""Fills up a blank template with notes for soprano, alto, and tenor"""
		self.note_index = 0
		while self.pitch_amounts[self.note_index] != "Blank":
			self.note_index += 1
		self.populate_note(self.note_index)
		last_combo = self.pitch_amounts[self.note_index - 1]
		attempts = 0

		while "Blank" in self.pitch_amounts:
			attempts += 1
			# Prevent CPU overload
			assert(attempts < 32000), f"You ran out of tries"
			if self.possible_pitches[self.note_index]:
				self.combo_choice = self.choose_combo()
				if self.validate_notes():
					self.pitch_amounts[self.note_index] = self.combo_choice
					last_combo = self.combo_choice
					self.fault_index = None
					print("Good", end=" ~ ")
					self.note_index += 1
					if self.note_index < len(self.pitch_amounts):
						self.populate_note(self.note_index)
				else:
					print("Bad", end=" ~ ")
					self.remove_culprit(self.combo_choice)
					self.erase_last_note()
			else:
				self.possible_pitches[self.note_index] = "Blank"
				self.populate_note(self.note_index)
				assert(self.note_index != 0), "You fail"
				self.erase_last_note()

				self.note_index -= 1
				print(f"Go back to index {self.note_index}")
				# self.possible_pitches[self.note_index].remove(last_combo)
				self.remove_culprit(last_combo)
				self.pitch_amounts[self.note_index] = "Blank"
				last_combo = self.pitch_amounts[self.note_index - 1]

	def choose_combo(self):
		"""Picks the fullest and smoothest chord from remaining options"""
		return self.possible_pitches[self.note_index][0]

	def validate_notes(self):

		self.add_voice_intervals()

		if self.note_index > 0:
			self.add_voice_motion(Voice.tenor_motion, 0, self.combo_choice[0])
			self.add_voice_motion(Voice.alto_motion, 1, self.combo_choice[1])
			self.add_voice_motion(Voice.soprano_motion, 2, self.combo_choice[2])

			self.add_motion_types()

			Voice.soprano_jumps.append(abs(
				self.combo_choice[2] - self.pitch_amounts[self.note_index - 1][2]))

		return self.is_counterpoint()

	def add_voice_intervals(self):
		self.add_interval(Voice.bass_pitches[self.note_index], self.combo_choice[0], 
			self.bass_tenor_intervals)
		self.add_interval(Voice.bass_pitches[self.note_index], self.combo_choice[1],
			self.bass_alto_intervals)
		self.add_interval(Voice.bass_pitches[self.note_index], self.combo_choice[2],
			self.bass_soprano_intervals)
		self.add_interval(self.combo_choice[0], self.combo_choice[1],
			self.tenor_alto_intervals)
		self.add_interval(self.combo_choice[0], self.combo_choice[2],
			self.tenor_soprano_intervals)
		self.add_interval(self.combo_choice[1], self.combo_choice[2],
			self.alto_soprano_intervals)

	def add_voice_motion(self, voice_motion, voice_index, new_pitch):
		if new_pitch < self.pitch_amounts[self.note_index - 1][voice_index]:
			voice_motion.append(-1)
		elif new_pitch > self.pitch_amounts[self.note_index - 1][voice_index]:
			voice_motion.append(1)
		elif new_pitch == self.pitch_amounts[self.note_index - 1][voice_index]:
			voice_motion.append(0)

	def add_motion_types(self):
		self.add_motion_type(Voice.bass_motion, Voice.tenor_motion, 
			self.bass_tenor_motion, self.bass_tenor_intervals)
		self.add_motion_type(Voice.bass_motion, Voice.alto_motion, 
			self.bass_alto_motion, self.bass_alto_intervals)
		self.add_motion_type(Voice.bass_motion, Voice.soprano_motion, 
			self.bass_soprano_motion, self.bass_soprano_intervals)
		self.add_motion_type(Voice.tenor_motion, Voice.alto_motion,
			self.tenor_alto_motion, self.tenor_alto_intervals)
		self.add_motion_type(Voice.tenor_motion, Voice.soprano_motion,
			self.tenor_soprano_motion, self.tenor_soprano_intervals),
		self.add_motion_type(Voice.alto_motion, Voice.soprano_motion,
			self.alto_soprano_motion, self.alto_soprano_intervals)

	def is_counterpoint(self):

		if self.note_index == 0:
			if self.bass_soprano_intervals[-1] in ("P5","P8"):
				return True
			else:
				return False 
		elif not self.is_universal_counterpoint():
			return False
		elif not self.is_specific_counterpoint():
			return False

		return True

	def preprocess_combo(self, t_pitch, a_pitch, s_pitch):
		"""Clears out inappropriate pitch combos"""
		b_pitch = Voice.bass_pitches[self.note_index]
		if (s_pitch < t_pitch) or (s_pitch < a_pitch):
			return False
		elif (self.make_scale_pitch(b_pitch) == 
		self.make_scale_pitch(t_pitch) == self.make_scale_pitch(a_pitch) == 
		self.make_scale_pitch(s_pitch)):
			return False
		if self.note_index == 0:
			return True

		# prevents recursive clutter later on by removing obvious bad notes 
		# preprocess > assign culprit > single deletion
		bass_soprano_interval = [self.bass_soprano_intervals[-1]]
		self.add_interval(b_pitch, s_pitch, bass_soprano_interval)
		soprano_move = []
		self.add_voice_motion(soprano_move, 2, s_pitch)
		bass_soprano_move = []
		self.add_motion_type(Voice.bass_motion, soprano_move, 
		bass_soprano_move, bass_soprano_interval)

		old_soprano_note = self.pitch_amounts[self.note_index - 1][2]
		if ((self.note_index == len(self.pitch_amounts) - 1) and 
		(bass_soprano_move[-1] != "Contrary" or 
		bass_soprano_interval[-1] != "P8" or
		self.calculate_leap(old_soprano_note, s_pitch) > 2)):
			# print("Must end with contrary motion and tonic")
			return False
		elif (self.note_index != len(self.pitch_amounts) - 1 and 
		bass_soprano_interval[-1] == "P8"):
			# print("Avoiding premature unison")
			return False
		elif bass_soprano_interval[-1] in idms.harmonic_dissonance:
			return False
		elif ("P" in bass_soprano_interval[-1] and 
		"P" in bass_soprano_interval[-2]):
			# print("Double perfects")
			return False
		elif bass_soprano_move[-1] == "No motion":
			return False
		elif (bass_soprano_move[-1] == "Similar" and 
		bass_soprano_interval[-1] == "P5"):
			# print("No hidden 5ths")
			return False

		return True

	def is_universal_counterpoint(self):
		for interval_list, motion_list in zip(
		self.composite_intervals, self.composite_movements):
			if (interval_list[-1] in ("P5","P8") and 
			motion_list[-1] == "Parallel"):
				return self.assign_culprit(None)

		for voice_index, new_pitch in enumerate(self.combo_choice):
			old_pitch = self.pitch_amounts[self.note_index -1][voice_index]
			if self.calculate_leap(old_pitch, new_pitch) > 12:
				# print("Leap too wide")
				return self.assign_culprit(voice_index)
			elif ((self.make_scale_pitch(old_pitch) + 1) == 12 and 
			self.make_scale_pitch(new_pitch) != 0 and 
			not Voice.chromatics[self.note_index]):
				# print("Leading tone must progress to tonic")
				return self.assign_culprit(voice_index)
			elif (Voice.chromatics[self.note_index - 1] and 
				self.revert_sec_dom(old_pitch, -1) == 11 and
				self.calculate_leap(old_pitch, new_pitch) != 1):
				# print("Leading tone of 2D must resolve to tonic")
				return self.assign_culprit(None)
			elif (not Voice.chromatics[self.note_index - 1] and 
			self.is_seventh_chord(-1) and 
			self.calculate_leap(old_pitch, new_pitch) != 1):
				old_chord = abs(Voice.chord_path[self.note_index - 1])
				new_chord = abs(Voice.chord_path[self.note_index])
				dissonant_degree = idms.chord_tones[old_chord][3]
				dissonant_pitch = self.degree_to_pitch(dissonant_degree, -1)
				# print("Must transfer or resolve dissonant 7th")
				if old_pitch == dissonant_pitch and not self.is_seventh_chord():
					return self.assign_culprit(voice_index)
				elif (old_pitch == dissonant_pitch and self.is_seventh_chord() and
				new_chord // 10000 != old_chord // 10000):
					return self.assign_culprit(None)
		return True

	def is_specific_counterpoint(self):
		old_soprano_note = self.pitch_amounts[self.note_index - 1][2]

		if (self.note_index > 1 and Voice.soprano_motion[-1] == 0 and 
		Voice.soprano_motion[-2] == 0):
			# print("Triple repeat")
			return self.assign_culprit(2)
		elif (self.note_index > 1 and Voice.soprano_jumps[-2] > 5 and
		(self.calculate_leap(old_soprano_note, self.combo_choice[2]) > 2 or 
		self.calculate_leap(old_soprano_note, self.combo_choice[2]) == 0 or
		Voice.soprano_motion[-1] == Voice.soprano_motion[-2])):
			# print("Leaps must be followed by contrary steps")
			return self.assign_culprit(2)
		elif (self.note_index > 2 and 
		self.bass_soprano_motion[-1] == "Parallel" and
		self.bass_soprano_motion[-2] == "Parallel" and
		self.bass_soprano_motion[-3] == "Parallel"):
			# print("Three consecutive parallels. Delete!")
			return self.assign_culprit(2)
		elif not self.is_voice_range(2):
			return self.assign_culprit(2)

		return True

	def assign_culprit(self, voice_index):
		self.fault_index = voice_index
		return False

	def remove_culprit(self, bad_combo):
		"""Removes all combinations with problematic note"""
		if type(self.fault_index) == int:
			# print("Removing culprit", end=" ")
			fault_note = bad_combo[self.fault_index]
			combo_options = self.possible_pitches[self.note_index]
			[self.possible_pitches[self.note_index].remove(pitch_combo) 
			for pitch_combo in combo_options 
			if pitch_combo[self.fault_index] == fault_note]
		else: 
			# print("No culprit", end=" ")
			self.possible_pitches[self.note_index].remove(bad_combo)

	def erase_last_note(self):
		if Voice.tenor_motion: 
			Voice.tenor_motion.pop()
			Voice.alto_motion.pop()
			Voice.soprano_motion.pop()
			Voice.soprano_jumps.pop()
			[motion_list.pop() for motion_list in self.composite_movements]
		[interval_list.pop() for interval_list in self.composite_intervals]

	def split_notes(self):
		for index, (value1, value2, value3) in enumerate(self.pitch_amounts):
			Voice.tenor_pitches.append(value1)
			Voice.alto_pitches.append(value2)
			Voice.soprano_pitches.append(value3)

class KBTenor(Voice):

	def __init__(self):
		self.real_notes = Voice.tenor_pitches
		self.sheet_notes = []
		self.lily_notes = []

class KBAlto(Voice):

	def __init__(self):
		self.real_notes = Voice.alto_pitches
		self.sheet_notes = []
		self.lily_notes = []

