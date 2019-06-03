import itertools
from tqdm import tqdm
import pysnooper

from voice import Voice
import idioms as idms

class KBUpperVoices(Voice):
	"""Creates chords using bass notes and first-species counterpoint 
	for a chorale style"""

	def __init__(self):
		self.note_index = 0
		self.pitch_amounts = []
		self.possible_pitches = []
		self.pitch_amounts.extend((None,) * 
			(Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length))
		self.possible_pitches.extend((None,) * 
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
		self.populate_note()
		self.combo_choice = self.possible_pitches[0][0]
		self.pitch_amounts[0] = self.combo_choice
		self.validate_notes()
		self.add_notes()
		self.split_notes()

	def populate_note(self):
		"""Adds all valid chord combos to the next rhythmic position"""
		current_chord = self.get_chord()
		chord_root_degree = idms.chord_tones[current_chord][0]
		chord_length = len(idms.chord_tones[current_chord])
		all_pitches = self.create_chord_pitches(
			chord_length, chord_root_degree)
		if Voice.chromatics[self.note_index] == "2Dom":
			all_pitches = self.add_chromatics(
				all_pitches, self.convert_sec_dom)
		elif Voice.chromatics[self.note_index] == "2Dim":
			all_pitches = self.add_chromatics(
				all_pitches, self.convert_sec_dim)
		elif Voice.chromatics[self.note_index] in idms.modes.keys():
			all_pitches = self.add_chromatics(
				all_pitches, self.convert_mode)

		pitch_combos = self.create_pitch_combos(all_pitches)
		self.possible_pitches[self.note_index] = self.arrange_pitch_combos(
			pitch_combos)
		# print([slot if slot == None else len(slot) 
		# 	for slot in self.possible_pitches])

	def create_chord_pitches(self, chord_length, chord_root_degree):
		"""Create a list of all possible pitches for the current chord"""
		all_pitches = []
		high_point = 81
		low_point = Voice.bass_pitches[self.note_index]

		root_pitch = (idms.modes[Voice.mode][chord_root_degree] + 
			idms.tonics[Voice.tonic])
		chord_increments = [0]
		new_position = chord_root_degree + 2
		for _ in range(chord_length - 1):
			chord_increments.append((idms.modes[Voice.mode][new_position] - 
				idms.modes[Voice.mode][chord_root_degree]))
			new_position += 2

		if Voice.chromatics[self.note_index] not in ("2Dom", "2Dim"):
			if Voice.mode == "aeolian" and chord_root_degree == 4:
				chord_increments[1] += 1
			elif Voice.mode == "aeolian" and chord_root_degree == 6:
				chord_increments[0] += 1

		chord_slot = 0
		current_pitch = root_pitch

		while current_pitch < low_point:
			if (chord_length - 1) > chord_slot:
				chord_slot += 1
			elif (chord_length - 1) <= chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_increments[chord_slot]

		while current_pitch <= high_point:
			all_pitches.append(current_pitch)
			if (chord_length - 1) > chord_slot:
				chord_slot += 1
			elif (chord_length - 1) <= chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_increments[chord_slot]

		return all_pitches

	def add_chromatics(self, all_pitches, func):
		for index, pitch in enumerate(all_pitches[:]):
			all_pitches[index] += func(self.get_chord(), pitch) 
		return all_pitches

	def create_pitch_combos(self, all_pitches):

		triple_pitch_combos = list(itertools.combinations_with_replacement(
			all_pitches,3))
		for (t_pitch, a_pitch, s_pitch) in triple_pitch_combos[:]:
			if (not 48 <= t_pitch <= 69 or not 55 <= a_pitch <= 74 or 
			not 59 <= s_pitch <= 81 or 
			Voice.bass_pitches[self.note_index] == t_pitch == a_pitch):
				triple_pitch_combos.remove((t_pitch, a_pitch, s_pitch))

		approved_combos = []
		for (t_pitch, a_pitch, s_pitch) in triple_pitch_combos:
			if self.preprocess_combo(t_pitch, a_pitch, s_pitch):
				approved_combos.append((t_pitch, a_pitch, s_pitch))
		return approved_combos

	def arrange_pitch_combos(self, pitch_combos):
		"""Arrange chords by completeness and then by smoothest motion"""
		complete_rank = []

		for notes in pitch_combos:
			scale_pitches = []
			scale_pitches.append(self.make_scale_pitch(Voice.bass_pitches[self.note_index]))
			scale_pitches.append(self.make_scale_pitch(notes[0]))
			scale_pitches.append(self.make_scale_pitch(notes[1]))
			scale_pitches.append(self.make_scale_pitch(notes[2]))
			complete_rank.append(len(set(scale_pitches)))

		complete_chord_sort = [x for _,x in sorted(zip(
			complete_rank, pitch_combos), reverse=True)]

		if self.note_index == 0:
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
				chord_group))

		if len(chord_index_dividers) > 1:
			smooth_chord_sort.extend(self.arrange_chord_motion(
				complete_chord_sort[stop:]))
		elif len(chord_index_dividers) == 1:
			divider = chord_index_dividers[0]
			smooth_chord_sort.extend(self.arrange_chord_motion(
				complete_chord_sort[:divider]))
			smooth_chord_sort.extend(self.arrange_chord_motion(
				complete_chord_sort[divider:]))
		else:
			return complete_chord_sort
		return smooth_chord_sort

	def arrange_chord_motion(self, chord_group):
		chord_motions = []
		old_tenor_note = self.pitch_amounts[self.note_index - 1][0]
		old_alto_note = self.pitch_amounts[self.note_index - 1][1]
		old_soprano_note = self.pitch_amounts[self.note_index - 1][2]
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
		while self.pitch_amounts[self.note_index] is not None:
			self.note_index += 1
		self.populate_note()
		last_combo = self.pitch_amounts[self.note_index - 1]
		attempts = 0

		# an invalid combo at a note index is often context-sensitive
		with tqdm(total=len(self.possible_pitches[0])) as pbar:
			while None in self.pitch_amounts:
				attempts += 1
				# Prevent CPU overload/encourage optimization
				# assert(attempts < 32000), f"You ran out of tries"
				if self.possible_pitches[self.note_index]:
					self.combo_choice = self.choose_combo()
					self.validate_notes()
					self.pitch_amounts[self.note_index] = self.combo_choice
					last_combo = self.combo_choice
					self.note_index += 1
					if self.note_index < len(self.pitch_amounts):
						self.populate_note()
				else:
					self.possible_pitches[self.note_index] = None
					if self.note_index == 1:
						pbar.update(1)
					assert(self.note_index != 0), "You fail"
					self.erase_last_note()

					self.note_index -= 1
					# if attempts % 3000 == 0:
					# 	print(f"Go back to index {self.note_index}")
					self.possible_pitches[self.note_index].remove(last_combo)
					self.pitch_amounts[self.note_index] = None
					last_combo = self.pitch_amounts[self.note_index - 1]

		print(self.bass_soprano_intervals)
		Voice.bass_soprano_intervals = self.bass_soprano_intervals

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

	def add_voice_intervals(self):
		self.bass_tenor_intervals.append(self.get_interval(
			Voice.bass_pitches[self.note_index], self.combo_choice[0]))
		self.bass_alto_intervals.append(self.get_interval(
			Voice.bass_pitches[self.note_index], self.combo_choice[1]))
		self.bass_soprano_intervals.append(self.get_interval(
			Voice.bass_pitches[self.note_index], self.combo_choice[2]))
		self.tenor_alto_intervals.append(self.get_interval(
			self.combo_choice[0], self.combo_choice[1]))
		self.tenor_soprano_intervals.append(self.get_interval(
			self.combo_choice[0], self.combo_choice[2]))
		self.alto_soprano_intervals.append(self.get_interval(
			self.combo_choice[1], self.combo_choice[2]))

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

	def preprocess_combo(self, t_pitch, a_pitch, s_pitch):
		"""Remove bad pitch combos based on counterpoint and voice leading"""

		b_pitch = Voice.bass_pitches[self.note_index]
		full_scale_combo = ((self.make_scale_pitch(b_pitch), 
		self.make_scale_pitch(t_pitch),
		self.make_scale_pitch(a_pitch), self.make_scale_pitch(s_pitch)))

		bass_soprano_intervals = self.bass_soprano_intervals[:]
		bass_soprano_intervals.append(self.get_interval(b_pitch, s_pitch))

		if (s_pitch <= t_pitch) or (s_pitch <= a_pitch):
			return False
		elif len(set(full_scale_combo)) == 1:
			return False
		elif full_scale_combo.count(11) >= 2:
			# print("Don't repeat leading tone", end=" ")
			return False
		elif (self.is_seventh_chord() and 
			full_scale_combo.count(self.chord_degree_to_pitch(3, 0)) >= 2):
			# print("Don't repeat chordal 7th", end=" ")
			return False
		elif (self.chord_degree_to_pitch(1) not in full_scale_combo):
			return False
		elif self.is_seventh_chord() and len(set(full_scale_combo)) < 3:
			return False
		elif (self.note_index == 0 and 
		bass_soprano_intervals[-1] not in ("P5", "P8", "M3", "m3")):
			return False
		if self.note_index == 0:
			return True

		tenor_motion = Voice.tenor_motion[:]
		alto_motion = Voice.alto_motion[:]
		soprano_motion = Voice.soprano_motion[:]

		self.add_voice_motion(soprano_motion, 2, s_pitch)
		self.add_voice_motion(alto_motion, 1, a_pitch)
		self.add_voice_motion(tenor_motion, 0, t_pitch)

		composite_motion = [tenor_motion, alto_motion, soprano_motion]

		pitch_combo = (t_pitch, a_pitch, s_pitch)
		for voice_index, new_pitch in enumerate(pitch_combo):
			old_pitch = self.pitch_amounts[self.note_index - 1][voice_index]
			if abs(new_pitch - old_pitch) > 12:
				# print("Leap too wide", end=" ")
				return False
			elif abs(new_pitch - old_pitch) in (6,10,11):
				# print("No dissonant leaps")
				return False
			elif (self.make_scale_pitch(old_pitch) == 11 and 
			self.make_scale_pitch(new_pitch) != 0 and 
			not Voice.chromatics[self.note_index] and 
			not Voice.chromatics[self.note_index - 1] and
			(self.get_chord(-1) // 10 != 50_753 or 
			self.make_scale_pitch(new_pitch) != 
			self.chord_degree_to_pitch(2))):
				# print("Leading tone must progress to tonic", end=" ")
				return False
			elif (Voice.chromatics[self.note_index - 1] == "2Dom" and 
			self.make_scale_pitch(old_pitch) == 
			self.chord_degree_to_pitch(1, -1) and 
			abs(new_pitch - old_pitch) != 1 
			and (self.get_chord(-1) // 10 != 50_753 or 
			self.make_scale_pitch(new_pitch) != 
			self.chord_degree_to_pitch(2))):
				# print("Leading tone of 2D must resolve to tonic", end=" ")
				return False
			elif (self.note_index > 1 and
			abs(self.pitch_amounts[self.note_index - 1][voice_index] - 
				self.pitch_amounts[self.note_index - 2][voice_index]) > 5 
			and (abs(new_pitch - old_pitch) > 2 or 
			abs(new_pitch - old_pitch) == 0 or 
			composite_motion[voice_index][-1] == 
			composite_motion[voice_index][-2])):
				# print("Leaps must be followed by contrary steps")
				return False
			# Nested conditional simplifies expressions
			# last item prevent chain skips
			elif (self.is_seventh_chord(-1) and 
			abs(new_pitch - old_pitch) > 2):
				dissonant_pitch = self.chord_degree_to_pitch(3, -1)
				if (self.make_scale_pitch(old_pitch) == dissonant_pitch and 
				not self.is_seventh_chord()):
					return False
				elif (self.make_scale_pitch(old_pitch) == dissonant_pitch and
				self.is_seventh_chord() and
				self.get_root_degree(-1) != self.get_root_degree()):
					return False
				elif (self.make_scale_pitch(old_pitch) == dissonant_pitch and
				self.is_seventh_chord() and 
				self.get_root_degree(-1) == self.get_root_degree() and 
				dissonant_pitch != self.make_scale_pitch(self.combo_choice[0]) and 
				dissonant_pitch != self.make_scale_pitch(self.combo_choice[1]) and
				dissonant_pitch != self.make_scale_pitch(self.combo_choice[2])):
					return False

		bass_soprano_motion = self.bass_soprano_motion[:]
		self.add_motion_type(Voice.bass_motion, soprano_motion, 
			bass_soprano_motion, bass_soprano_intervals)
		old_soprano_note = self.pitch_amounts[self.note_index - 1][2]

		if ((self.note_index == len(self.pitch_amounts) - 1) and 
		(bass_soprano_motion[-1] != "Contrary" or 
		bass_soprano_intervals[-1] != "P8" or
		abs(s_pitch - old_soprano_note) > 2)):
			# print("Must end with contrary motion and tonic by step")
			return False
		elif (self.note_index != len(self.pitch_amounts) - 1 and 
		bass_soprano_intervals[-1] == "P8"):
			# print("Avoiding premature unison")
			return False
		# elif bass_soprano_intervals[-1] in idms.harmonic_dissonance:
		# 	return False
		elif ("P" in bass_soprano_intervals[-1] and 
		"P" in bass_soprano_intervals[-2]):
			# print("Double perfects")
				return False
		elif bass_soprano_motion[-1] == "No motion":
			return False
		elif (bass_soprano_motion[-1] == "Similar" and 
		"P" in bass_soprano_intervals[-1] and 
		abs(s_pitch - old_soprano_note) > 2):
			# print("No hidden 5ths/octaves except soprano moving by step")
			return False
		elif (self.note_index > 1 and Voice.soprano_motion[-1] == 0 and 
		soprano_motion[-2] == 0):
			# print("Triple repeat")
			return False
		elif (self.note_index > 3 and 
		bass_soprano_motion[-1] in ("Parallel", "Similar") and
		bass_soprano_motion[-2] in ("Parallel", "Similar") and
		bass_soprano_motion[-3] in ("Parallel", "Similar") and
		bass_soprano_motion[-4] in ("Parallel", "Similar")):
			# print("Quadruple consecutive parallels. Delete!")
			return False
		elif (self.note_index > 3 and 
		bass_soprano_intervals[-1] == bass_soprano_intervals[-2] ==
		bass_soprano_intervals[-3] == bass_soprano_intervals[-4]):
			# print("Quadruple identical imperfects.")
			return False
		elif (self.note_index == Voice.idea1_length + Voice.idea2_length - 1 and
		abs(s_pitch - old_soprano_note) > 4):
			return False 

		bass_tenor_motion = self.bass_tenor_motion[:]
		bass_alto_motion = self.bass_alto_motion[:]
		tenor_alto_motion = self.tenor_alto_motion[:]
		tenor_soprano_motion = self.tenor_soprano_motion[:]
		alto_soprano_motion = self.alto_soprano_motion[:]

		bass_tenor_intervals = self.bass_tenor_intervals[:]
		bass_alto_intervals = self.bass_alto_intervals[:]
		tenor_alto_intervals = self.tenor_alto_intervals[:]
		tenor_soprano_intervals = self.tenor_soprano_intervals[:]
		alto_soprano_intervals = self.alto_soprano_intervals[:]

		tenor_alto_intervals.append(self.get_interval(t_pitch, a_pitch))
		tenor_soprano_intervals.append(self.get_interval(t_pitch, s_pitch))
		alto_soprano_intervals.append(self.get_interval(a_pitch, s_pitch))
		bass_tenor_intervals.append(self.get_interval(b_pitch, t_pitch))
		bass_alto_intervals.append(self.get_interval(b_pitch, a_pitch))

		self.add_motion_type(Voice.bass_motion, tenor_motion, 
			bass_tenor_motion, bass_tenor_intervals)
		self.add_motion_type(Voice.bass_motion, alto_motion, 
			bass_alto_motion, bass_alto_intervals)
		self.add_motion_type(tenor_motion, alto_motion,
			tenor_alto_motion, tenor_alto_intervals)
		self.add_motion_type(tenor_motion, soprano_motion,
			tenor_soprano_motion, tenor_soprano_intervals),
		self.add_motion_type(alto_motion, soprano_motion,
			alto_soprano_motion, alto_soprano_intervals)

		composite_intervals = [bass_tenor_intervals, bass_alto_intervals, 
			bass_soprano_intervals, tenor_alto_intervals, 
			tenor_soprano_intervals,alto_soprano_intervals]
		composite_movements = [bass_tenor_motion, bass_alto_motion, 
			bass_soprano_motion, tenor_alto_motion, tenor_soprano_motion,
			alto_soprano_motion]

		for interval_list, motion_list in zip(
		composite_intervals, composite_movements):
			if (interval_list[-1] in ("P5","P8") and 
			motion_list[-1] == "Parallel"):
				return False
			elif interval_list[-2] == "A4" and "6" not in interval_list[-1]:
				return False
			elif (interval_list[-2] == "d5" 
			and interval_list[-1] not in ("M3", "m3") 
			and self.get_chord(-1) != idms.VII6):
				return False
			elif (interval_list[-2] == "d5"
			and self.get_chord(-1) == idms.VII6 and 
			interval_list[-1] not in ("P5", "M3", "m3")):
				return False
			elif interval_list[-2] == "d7" and interval_list[-1] != "P5":
				return False
			elif interval_list[-2] == "A2" and interval_list[-1] != "P4":
				return False

		return True

	def erase_last_note(self):
		if Voice.tenor_motion: 
			Voice.tenor_motion.pop()
			Voice.alto_motion.pop()
			Voice.soprano_motion.pop()
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
		super().__init__()


class KBAlto(Voice):

	def __init__(self):
		self.real_notes = Voice.alto_pitches
		super().__init__()


