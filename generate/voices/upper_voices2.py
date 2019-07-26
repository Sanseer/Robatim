import itertools
from tqdm import tqdm
import random
import copy

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b
from generate.voices.voicelead2 import VoiceLeadMixin
from generate.voices.voicelead3 import MelodyMixin

class VoiceCombiner():

	def __init__(self):
		self.note_index = 0
		self.sequence_length = (Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length)
		self.soprano_chord_pitches = []
		self.soprano_chord_pitches.extend((None,) * self.sequence_length)
		self.soprano_full_pitches = []
		self.soprano_full_pitches.extend((None,) * self.sequence_length)
		self.lower_voice_pitches = self.soprano_chord_pitches[:]
		self.possible_soprano_pitches = self.soprano_chord_pitches[:]
		self.possible_lower_pitches = self.soprano_chord_pitches[:]

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

		self.composite_lower_intervals = [self.bass_tenor_intervals,
			self.bass_alto_intervals, self.tenor_alto_intervals]
		self.composite_lower_motions = [self.bass_tenor_motion, 
			self.bass_alto_motion, self.tenor_alto_motion]
		self.composite_soprano_intervals = [self.bass_soprano_intervals, 
			self.tenor_soprano_motion, self.alto_soprano_intervals]
		self.composite_soprano_motions = [self.bass_soprano_motion,
			self.tenor_soprano_motion, self.alto_soprano_motion]

		self.flat_restless_rhythms = []
		for rhythm in Voice.note_values:
			if type(rhythm) == int:
				self.flat_restless_rhythms.append(rhythm)

		self.nested_restless_rhythms = copy.deepcopy(Voice.measure_rhythms)
		if Voice.half_rest_ending:
			self.nested_restless_rhythms[3].pop()
			self.nested_restless_rhythms[7].pop()

		self.chordal_seventh = None

	@property
	def inside_score(self):
		return self.note_index < self.sequence_length

	def create_parts(self):
		self.populate_note()
		self.combo_choice = self.possible_lower_pitches[0][0]
		self.lower_voice_pitches[0] = self.combo_choice
		self.possible_soprano_pitches[0] = self.create_soprano_options()
		# if not self.possible_soprano_pitches[0]:
		# 	print(self.lower_voice_pitches)
		# 	print(self.possible_soprano_pitches)
		# 	print(self.soprano_pitch_choices)
		# 	print(self.soprano_scale_choices)
		# 	raise ValueError
		self.validate_lower_notes()
		self.add_lower_notes()
		self.split_notes()
		self.add_melody()

	def create_soprano_options(self):
		self.all_pitches = self.create_chord_pitches()

		if Voice.chromatics[self.note_index] == "2Dom":
			self.add_chromatics(self.convert_sec_dom)
		elif Voice.chromatics[self.note_index] == "2Dim":
			self.add_chromatics(self.convert_sec_dim)
		elif Voice.chromatics[self.note_index] in idms_b.mode_notes.keys():
			self.add_chromatics(self.convert_mode)

		chord_scale_combo = {
			self.make_scale_pitch(Voice.bass_pitches[self.note_index]), 
			self.make_scale_pitch(self.combo_choice[0]),
			self.make_scale_pitch(self.combo_choice[1])
		}
		self.soprano_pitch_choices = [
			pitch for pitch in self.all_pitches if pitch >= self.combo_choice[1]		
		]
		self.soprano_scale_choices = [
			self.make_scale_pitch(pitch) for pitch in self.soprano_pitch_choices
		]
		if self.chord_degree_to_pitch(0) in chord_scale_combo:
			self.chordal_root = True
		else:
			self.chordal_root = False
		if self.chord_degree_to_pitch(1) in chord_scale_combo:
			self.chordal_third = True
		else:
			self.chordal_third = False
		if self.chord_degree_to_pitch(2) in chord_scale_combo:
			self.chordal_fifth = True
		else:
			self.chordal_fifth = False
		if not self.chordal_root or self.note_index == self.sequence_length - 1:
			return self.add_soprano_notes(0)
		elif not self.chordal_third:
			return self.add_soprano_notes(1)
		current_chord = self.get_chord()
		if (not self.chordal_fifth and 
		  current_chord != idms_b.V7 and
		  current_chord not in Voice.idms_mode.consonant_triads):
			return self.add_soprano_notes(2)
		if self.is_seventh_chord(): 
			if self.chord_degree_to_pitch(3) in chord_scale_combo:
				self.chordal_seventh = True
			else:
				self.chordal_seventh = False
			if not self.chordal_seventh:
				return self.add_soprano_notes(3)
		return self.soprano_pitch_choices
	
	def add_soprano_notes(self, chord_position):
		final_notes = []
		melodic_note = self.chord_degree_to_pitch(chord_position)
		for scale_pitch, actual_pitch in zip(
			self.soprano_scale_choices, self.soprano_pitch_choices):
			if scale_pitch == melodic_note:
				final_notes.append(actual_pitch)
		return final_notes

	def populate_note(self):
		self.all_pitches = self.create_chord_pitches()

		if Voice.chromatics[self.note_index] == "2Dom":
			self.add_chromatics(self.convert_sec_dom)
		elif Voice.chromatics[self.note_index] == "2Dim":
			self.add_chromatics(self.convert_sec_dim)
		elif Voice.chromatics[self.note_index] in idms_b.mode_notes.keys():
			self.add_chromatics(self.convert_mode)

		lower_pitch_combos = self.create_pitch_combos()
		self.possible_lower_pitches[self.note_index] = self.arrange_pitch_combos(
			lower_pitch_combos)

	def create_chord_pitches(self):
		current_chord = self.get_chord()
		chord_root_degree = idms_b.chord_members[current_chord][0]
		chord_length = len(idms_b.chord_members[current_chord])

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

		if (Voice.chromatics[self.note_index] not in {"2Dom", "2Dim"} and 
		  Voice.mode == "aeolian"):
			if chord_root_degree == 4:
				chord_increments[1] += 1
			elif chord_root_degree == 6:
				chord_increments[0] += 1

		# add chromatics here?

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

	def add_chromatics(self, convert_func):
		fixed_pitches = [] 
		for pitch in self.all_pitches:
			fixed_pitches.append(pitch +  convert_func(self.get_chord(), pitch))

		self.all_pitches = fixed_pitches

	def create_pitch_combos(self):

		double_pitch_combos = list(itertools.combinations_with_replacement(
			self.all_pitches, 2))

		for t_pitch, a_pitch in double_pitch_combos[:]:
			if not 48 <= t_pitch <= 69 or not 48 <= a_pitch <= 74:
				double_pitch_combos.remove((t_pitch, a_pitch))

		approved_combos = []
		for t_pitch, a_pitch in double_pitch_combos:
			if self.is_voice_lead(t_pitch, a_pitch):
				approved_combos.append((t_pitch, a_pitch))

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
			complete_rank.append(len(set(scale_pitches)))

		# arrange one list using another list as key
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
		old_tenor_note = self.lower_voice_pitches[self.note_index - 1][0]
		old_alto_note = self.lower_voice_pitches[self.note_index - 1][1]
		for chord in chord_group:
			new_tenor_note = chord[0] 
			new_alto_note = chord[1]
			movement = abs(new_tenor_note - old_tenor_note)
			movement += abs(new_alto_note - old_alto_note)
			chord_motions.append(int(movement))
		motion_sort = [x for _,x in sorted(zip(chord_motions, chord_group))]

		return motion_sort

	def add_lower_notes(self):
		"""Fills up a blank template with notes for soprano, alto, and tenor"""
		self.note_index = 0
		while self.lower_voice_pitches[self.note_index] is not None:
			self.note_index += 1
		self.populate_note()
		last_combo = self.lower_voice_pitches[self.note_index - 1]

		with tqdm(total=len(self.possible_lower_pitches[0])) as pbar:
			while None in self.lower_voice_pitches:
				if self.possible_lower_pitches[self.note_index]:
					self.combo_choice = \
					self.possible_lower_pitches[self.note_index][0]
					self.possible_soprano_pitches[self.note_index] = \
					self.create_soprano_options()
					# if not self.possible_soprano_pitches[self.note_index]:
						# check reason for making mistakes
						# print(Voice.bass_pitches[self.note_index])
						# print(self.combo_choice)
						# print(self.all_pitches)
						# print(self.soprano_pitch_choices)
						# print(self.soprano_scale_choices)
						# print(self.chordal_root, self.chordal_third, self.chordal_fifth, self.chordal_seventh)
						# print(self.get_chord(), self.note_index)
						# self.possible_lower_pitches[self.note_index].remove(self.combo_choice)
						# continue
						# raise ValueError
					self.validate_lower_notes()
					self.lower_voice_pitches[self.note_index] = self.combo_choice
					last_combo = self.combo_choice
					self.note_index += 1
					if self.inside_score:
						self.populate_note()
				else:
					self.possible_lower_pitches[self.note_index] = None
					if self.note_index == 1:
						pbar.update(1)
					elif self.note_index == 0:
						raise IndexError("The chord progression has failed")
					self.erase_lower_notes()
					# store failed progressions in txt file up to point of impasse
					self.note_index -= 1
					self.possible_lower_pitches[self.note_index].remove(last_combo)
					self.lower_voice_pitches[self.note_index] = None
					last_combo = self.lower_voice_pitches[self.note_index - 1]

		print(self.possible_soprano_pitches)

	def erase_lower_notes(self):
		if Voice.tenor_motion: 
			Voice.tenor_motion.pop()
			Voice.alto_motion.pop()
			[motion_list.pop() for motion_list in self.composite_lower_motions]
		[interval_list.pop() for interval_list in self.composite_lower_intervals]

	def validate_lower_notes(self):

		self.add_voice_intervals()

		if self.note_index > 0:
			self.add_voice_motion(Voice.tenor_motion, 0, self.combo_choice[0])
			self.add_voice_motion(Voice.alto_motion, 1, self.combo_choice[1])

			self.add_motion_types()

	def add_voice_intervals(self):
		self.bass_tenor_intervals.append(self.get_interval(
			Voice.bass_pitches[self.note_index], self.combo_choice[0]))
		self.bass_alto_intervals.append(self.get_interval(
			Voice.bass_pitches[self.note_index], self.combo_choice[1]))
		self.tenor_alto_intervals.append(self.get_interval(
			self.combo_choice[0], self.combo_choice[1]))

	def add_voice_motion(self, voice_motion, voice_index, new_pitch):
		if new_pitch < self.lower_voice_pitches[self.note_index - 1][voice_index]:
			voice_motion.append(-1)
		elif new_pitch > self.lower_voice_pitches[self.note_index - 1][voice_index]:
			voice_motion.append(1)
		elif new_pitch == self.lower_voice_pitches[self.note_index - 1][voice_index]:
			voice_motion.append(0)

	def add_motion_types(self):
		self.add_motion_type(Voice.bass_motion, Voice.tenor_motion, 
			self.bass_tenor_motion, self.bass_tenor_intervals)
		self.add_motion_type(Voice.bass_motion, Voice.alto_motion, 
			self.bass_alto_motion, self.bass_alto_intervals)
		self.add_motion_type(Voice.tenor_motion, Voice.alto_motion,
			self.tenor_alto_motion, self.tenor_alto_intervals)

	def add_melody(self):
		for note_options in self.possible_soprano_pitches:
			random.shuffle(note_options)

		self.note_index = 0
		chord_combo_options = [[] for _ in range(self.sequence_length)]
		chord_combo_choices = [[] for _ in range(self.sequence_length)]
		chord_combo_options[0] = self.create_soprano_combos()
		Voice.soprano_rhythm = []

		print(self.possible_soprano_pitches)
		# print(Voice.measure_rhythms)
		# print(Voice.note_values)
		# raise Exception("Stop")
		with tqdm(total=len(chord_combo_options[0])) as pbar:
			while None in self.soprano_full_pitches:
				current_note_options = chord_combo_options[self.note_index] 
				if current_note_options:
					self.combo_choice = current_note_options[0]
					melodies, new_rhythm = self.embellish_chord()
					if melodies:
						last_combo = self.combo_choice
						chord_combo_choices[self.note_index] = last_combo
						self.new_melody = random.choice(melodies)
						self.soprano_full_pitches[self.note_index] = self.new_melody
						Voice.soprano_rhythm.append(new_rhythm)
						self.validate_melody()
						self.note_index += 1
						if self.inside_score:
							new_combo_options = self.create_soprano_combos()
							for new_combo in new_combo_options:
								if new_combo[0] == last_combo[-1]:
									chord_combo_options[self.note_index].append(new_combo)
					else:
						current_note_options.remove(self.combo_choice)
				else:
					self.erase_upper_voice()
					if self.note_index == 1:
						pbar.update(1)
					elif self.note_index == 0:
						raise IndexError("The melody has failed")
					self.note_index -= 1
					chord_combo_options[self.note_index].remove(last_combo)
					last_combo = chord_combo_choices[self.note_index - 1]
					chord_combo_choices[self.note_index] = []
					self.soprano_full_pitches[self.note_index] = None	

		Voice.soprano_pitches = self.soprano_full_pitches 
		print(Voice.soprano_pitches)

	def create_soprano_combos(self):
		soprano_combos = []
		if self.note_index == self.sequence_length - 1:
			for current_note in self.possible_soprano_pitches[self.note_index]:
				soprano_combos.append((current_note, current_note))
			return soprano_combos

		for current_note in self.possible_soprano_pitches[self.note_index]:
			for next_note in self.possible_soprano_pitches[self.note_index + 1]:
				soprano_combos.append((current_note, next_note))
		return soprano_combos

	def validate_melody(self):
		self.add_soprano_intervals(Voice.bass_pitches, self.bass_soprano_intervals)
		self.add_soprano_intervals(Voice.tenor_pitches, self. tenor_soprano_intervals)
		self.add_soprano_intervals(Voice.alto_pitches, self.alto_soprano_intervals)

		self.add_soprano_motions(Voice.soprano_motion)

		if self.note_index > 0:
			self.add_soprano_motion_types()

	def add_soprano_intervals(self, pitches, interval_list):
		all_intervals = []
		for new_note in self.new_melody:
			all_intervals.append(self.get_interval(
				pitches[self.note_index], new_note))
		interval_list.append(all_intervals)

	def add_soprano_motions(self, voice_motion):
		all_motions = []
		parallax_melody = self.new_melody[:]
		parallax_melody.append(self.combo_choice[1])
		for current_note, next_note in zip(self.new_melody, parallax_melody[1:]):
			if next_note < current_note:
				all_motions.append(-1)
			elif next_note > current_note:
				all_motions.append(1)
			else:
				all_motions.append(0)

		if self.note_index == self.sequence_length - 1:
			all_motions.pop()

		voice_motion.append(all_motions)

	def add_soprano_motion_types(self):
		self.add_soprano_motion_type(Voice.bass_motion, Voice.soprano_motion,
			self.bass_soprano_motion, self.bass_soprano_intervals)
		self.add_soprano_motion_type(Voice.tenor_motion, Voice.soprano_motion,
			self.bass_tenor_motion, self.bass_tenor_intervals)
		self.add_soprano_motion_type(Voice.alto_motion, Voice.soprano_motion,
			self.bass_alto_motion, self.bass_alto_intervals)

	def add_soprano_motion_type(self, old_motion, new_motion, movements, intervals):
		old_move = old_motion[self.note_index - 1]
		new_move = new_motion[-2][-1]

		if (old_move == new_move and old_move != 0 and 
		  intervals[-1][0] == intervals[-2][-1]):
			movements.append("Parallel")
		elif old_move == new_move and old_move == 0:
			movements.append("No motion")
		elif old_move == -(new_move) and old_move != 0:
			movements.append("Contrary")
		elif (old_move == new_move and intervals[-1][0] != intervals[-2][-1]):
			movements.append("Similar")
		elif ((old_move == 0 or new_move == 0) and 
		  (old_move != 0 or new_move != 0)):
			movements.append("Oblique")
		else:
			raise ValueError("Invalid motion")

	def erase_upper_note(self):
		if self.bass_soprano_motion:
			[motion_list.pop() for motion_list in self.composite_soprano_motions]
		[interval_list.pop() for interval_list in self.composite_soprano_intervals]
		Voice.soprano_rhythm.pop()
		Voice.soprano_motion.pop()

	def split_notes(self):
		for t_pitch, a_pitch in self.lower_voice_pitches:
			Voice.tenor_pitches.append(t_pitch)
			Voice.alto_pitches.append(a_pitch)


class UpperVoices(VoiceLeadMixin, MelodyMixin, VoiceCombiner, Voice):
	pass


class Tenor(Voice):

	def __init__(self):
		self.real_notes = Voice.tenor_pitches
		super().__init__()

class Alto(Voice):

	def __init__(self):
		self.real_notes = Voice.alto_pitches
		super().__init__()


