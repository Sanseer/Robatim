import itertools
from tqdm import tqdm

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b
from generate.voices.voicelead import VoiceLeadMixin


class VoiceCombiner():
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
		chord_root_degree = idms_b.chord_members[current_chord][0]
		chord_length = len(idms_b.chord_members[current_chord])
		all_pitches = self.create_chord_pitches(
			chord_length, chord_root_degree)
		if Voice.chromatics[self.note_index] == "2Dom":
			all_pitches = self.add_chromatics(
				all_pitches, self.convert_sec_dom)
		elif Voice.chromatics[self.note_index] == "2Dim":
			all_pitches = self.add_chromatics(
				all_pitches, self.convert_sec_dim)
		elif Voice.chromatics[self.note_index] in idms_b.mode_notes.keys():
			all_pitches = self.add_chromatics(
				all_pitches, self.convert_mode)

		pitch_combos = self.create_pitch_combos(all_pitches)
		self.possible_pitches[self.note_index] = self.arrange_pitch_combos(
			pitch_combos)

	def create_chord_pitches(self, chord_length, chord_root_degree):
		"""Create a list of all possible pitches for the current chord"""
		all_pitches = []
		high_point = 81
		low_point = Voice.bass_pitches[self.note_index]

		root_pitch = (idms_b.mode_notes[Voice.mode][chord_root_degree] + 
			idms_b.tonics[Voice.tonic])
		chord_increments = [0]
		new_position = chord_root_degree + 2
		for _ in range(chord_length - 1):
			chord_increments.append((idms_b.mode_notes[Voice.mode][new_position] - 
				idms_b.mode_notes[Voice.mode][chord_root_degree]))
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

	def add_chromatics(self, all_pitches, convert_func):
		for index, pitch in enumerate(all_pitches[:]):
			all_pitches[index] += convert_func(self.get_chord(), pitch) 
		return all_pitches

	def create_pitch_combos(self, all_pitches):

		triple_pitch_combos = list(itertools.combinations_with_replacement(
			all_pitches,3))
		# not 48 < a_pitch and not 48 < t_pitch 
		for (t_pitch, a_pitch, s_pitch) in triple_pitch_combos[:]:
			if (not 48 <= t_pitch <= 69 or not 55 <= a_pitch <= 74 or 
			not 59 <= s_pitch <= 81 or 
			Voice.bass_pitches[self.note_index] == t_pitch == a_pitch):
				triple_pitch_combos.remove((t_pitch, a_pitch, s_pitch))

		approved_combos = []
		for (t_pitch, a_pitch, s_pitch) in triple_pitch_combos:
			if self.is_voice_lead(t_pitch, a_pitch, s_pitch):
				approved_combos.append((t_pitch, a_pitch, s_pitch))
		return approved_combos

	def arrange_pitch_combos(self, pitch_combos):
		"""Arrange chords by completeness and then by smoothest motion"""
		complete_rank = []

		for notes in pitch_combos:
			scale_pitches = []
			scale_pitches.append(self.make_scale_pitch(
				Voice.bass_pitches[self.note_index]))
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
					assert(self.note_index != 0), "The chord progression has failed"
					self.erase_last_note()
					# store failed progressions in txt file up to point of impasse
					self.note_index -= 1
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

	def erase_last_note(self):
		if Voice.tenor_motion: 
			Voice.tenor_motion.pop()
			Voice.alto_motion.pop()
			Voice.soprano_motion.pop()
			[motion_list.pop() for motion_list in self.composite_movements]
		[interval_list.pop() for interval_list in self.composite_intervals]

	def split_notes(self):
		for (value1, value2, value3) in self.pitch_amounts:
			Voice.tenor_pitches.append(value1)
			Voice.alto_pitches.append(value2)
			Voice.soprano_pitches.append(value3)

class UpperVoices(VoiceLeadMixin, VoiceCombiner, Voice):
	pass

class Tenor(Voice):

	def __init__(self):
		self.real_notes = Voice.tenor_pitches
		super().__init__()
		self.volume = 80


class Alto(Voice):

	def __init__(self):
		self.real_notes = Voice.alto_pitches
		super().__init__()
		self.volume = 80

