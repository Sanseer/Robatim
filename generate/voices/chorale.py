import itertools
import logging
import random
import time

from generate.voices.voice import Voice

class Chorale(Voice):
	"""A framework for chordal accompaniment"""

	def __init__(self):
		self.chord_index = 0
		self.root_pitch = None
		self.aug2_set = {5, 6}
		self.time0 = 0
		self.time1 = 0

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

		self.composite_intervals = [
			self.bass_tenor_intervals, self.bass_alto_intervals, 
			self.bass_soprano_intervals, self.tenor_alto_intervals, 
			self.tenor_soprano_intervals, self.alto_soprano_intervals,
		]
		self.composite_mvmts = [
			self.bass_tenor_motion, self.bass_alto_motion, 
			self.bass_soprano_motion, self.tenor_alto_motion, 
			self.tenor_soprano_motion, self.alto_soprano_motion,
		]

		self.condensed_chords = []
		self.unique_chord_indices = set()
		self.chosen_chord_voicings = []
		self.possible_chord_voicings = []
		self.unsorted_pitch_combo_sequence = []

		Chorale.create_logger()

	def create_parts(self):
		"""Create a four-part harmonic sequence"""

		self.condense_chords()
		self.make_chord_voicings()
		self.make_accompanyment()

	def condense_chords(self):
		"""Filter out duplicate chords of chord progression"""

		current_chord_obj = Voice.chord_sequence[0]
		self.condensed_chords.append(current_chord_obj)
		self.unique_chord_indices.add(0)
		self.unsorted_pitch_combo_sequence.append(
			self.make_pitch_combos(current_chord_obj)
		)
		previous_chord_obj = current_chord_obj

		for original_chord_index, current_chord_obj in enumerate(Voice.chord_sequence[1:], 1):
			if current_chord_obj != previous_chord_obj:
				self.condensed_chords.append(current_chord_obj)
				self.unique_chord_indices.add(original_chord_index)
				self.unsorted_pitch_combo_sequence.append(
					self.make_pitch_combos(current_chord_obj)
				)
			previous_chord_obj = current_chord_obj

	def make_chord_voicings(self):
		"""Realize voice-leading of chord progression"""

		self.chosen_chord_voicings = [None for _ in self.condensed_chords]
		self.possible_chord_voicings = [None for _ in self.condensed_chords]
		self.possible_chord_voicings[self.chord_index] = self.populate_chord()

		self.time0 = time.time()
		while None in self.chosen_chord_voicings:
			self.combo_choice = next(
				self.possible_chord_voicings[self.chord_index], None
			)
			if self.combo_choice is None:
				self.possible_chord_voicings[self.chord_index] = None
				"""
				cannot track positive progress of maze algorithm
				you don't know how soon to success but you know
				how soon to complete failure
				not useful to negative track because ≈ 10^21 combinations
				means most cases are solved within a few seconds or
				have a very long wait time, hence the timeout below
				"""
				if self.chord_index <= 0:
					print("Harmony failed.")
					raise AssertionError

				self.time1 = time.time()
				if self.time1 - self.time0 > 15:
					print("Harmony taking too long.")
					raise AssertionError

				self.chord_index -= 1
				self.erase_last_chord()
				self.chosen_chord_voicings[self.chord_index] = None
			else:
				self.chosen_chord_voicings[self.chord_index] = self.combo_choice
				self.chord_index += 1
				if self.chord_index < len(self.chosen_chord_voicings):
					self.possible_chord_voicings[self.chord_index] = (
						self.populate_chord()
					)

	def erase_last_chord(self):
		"""Remove last validated chord instance"""

		if self.bass_motion:
			self.bass_motion.pop()
			self.tenor_motion.pop()
			self.alto_motion.pop()
			self.soprano_motion.pop()
			[motion_list.pop() for motion_list in self.composite_mvmts]

		[interval_list.pop() for interval_list in self.composite_intervals]

	def populate_chord(self):
		"""Yields valid chordal voicings as needed"""

		current_chord_obj = self.condensed_chords[self.chord_index]
		current_pitches_dict = current_chord_obj.pitches_to_degrees

		current_chord_members = current_chord_obj.scale_degrees
		unsorted_pitch_combos = self.unsorted_pitch_combo_sequence[self.chord_index]
		current_chord = current_chord_obj.chord_name
		chord_direction = str(current_chord_obj)[0]

		if self.chord_index > 0:
			previous_chord_obj = self.condensed_chords[self.chord_index - 1]
			previous_chord = previous_chord_obj.chord_name
			previous_pitches_dict = previous_chord_obj.pitches_to_degrees
			previous_degree_combo = []
			for pitch in self.chosen_chord_voicings[self.chord_index - 1]:
				previous_degree_combo.append(previous_pitches_dict[pitch])
			previous_chord_members = previous_chord_obj.scale_degrees
		else:
			previous_chord = None
			previous_degree_combo = None
			previous_chord_members = None

		# generator requires passing of parameters to prevent side effects
		# from backtracking
		for pitch_combo in self.arrange_pitch_combos(
		  unsorted_pitch_combos, current_chord_members, current_pitches_dict):
			if self.is_voice_lead(
			  pitch_combo, current_chord, previous_chord, chord_direction, 
			  current_pitches_dict, previous_degree_combo, 
			  previous_chord_members, current_chord_members):
				yield pitch_combo

	def arrange_pitch_combos(
	  self, unsorted_pitch_combos, current_chord_members, current_pitches_dict):
		"""Sort available chord voicings to favor chord density"""

		voicing_groups = [[] for _ in current_chord_members]

		for pitch_combo in unsorted_pitch_combos:
			scale_degrees_used = set()
			for midi_pitch in pitch_combo:
				scale_degrees_used.add(current_pitches_dict[midi_pitch])
			scale_degree_count = len(scale_degrees_used)
			if scale_degree_count > 1:
				voicing_groups[scale_degree_count - 1].append(pitch_combo)

		if self.chord_index == 0:
			for voicing_group in reversed(voicing_groups):
				random.shuffle(voicing_group)
				for pitch_combo in voicing_group:
					yield pitch_combo
		else:
			for unsorted_voicing_group in reversed(voicing_groups):
				sorted_voicing_group = self.sort_voicing_group(unsorted_voicing_group)
				for pitch_combo in sorted_voicing_group:
					yield pitch_combo

	def sort_voicing_group(self, unsorted_voicing_group):
		"""Sort a single grouping of chord voicings to favor stepwise motion"""
		
		note_mvmts = []
		for pitch_combo in unsorted_voicing_group:
			note_mvmt = 0
			for old_note, new_note in zip(
			  self.chosen_chord_voicings[self.chord_index - 1], pitch_combo):
				note_mvmt += abs(new_note - old_note) 

			note_mvmts.append(note_mvmt)

		sorted_voicing_group = [
			pitch_combo 
			for _, pitch_combo in sorted(zip(note_mvmts, unsorted_voicing_group))
		]

		return sorted_voicing_group

	@property
	def octave_above(self):
		return range(self.root_pitch, self.root_pitch + 12)

	@property 
	def octave_below(self):
		return range(self.root_pitch - 12, self.root_pitch)

	def is_voice_lead(
	  self, pitch_combo, current_chord, previous_chord, chord_direction, 
	  current_pitches_dict, previous_degree_combo, previous_chord_members, 
	  current_chord_members):
		"""Check voice-leading of current chord progression"""

		(b_pitch, t_pitch, a_pitch, s_pitch) = pitch_combo
		current_degree_combo = (
			current_pitches_dict[b_pitch], current_pitches_dict[t_pitch], 
			current_pitches_dict[a_pitch], current_pitches_dict[s_pitch]
		)

		# copying lists so that you can test the next chord
		# allows easier discarding of changes if the chord fails
		bass_tenor_intervals = self.bass_tenor_intervals[:]
		bass_tenor_intervals.append(
			self.get_interval(b_pitch, t_pitch, current_pitches_dict)
		)
		bass_alto_intervals = self.bass_alto_intervals[:]
		bass_alto_intervals.append(
			self.get_interval(b_pitch, a_pitch, current_pitches_dict)
		)
		bass_soprano_intervals = self.bass_soprano_intervals[:]
		bass_soprano_intervals.append(
			self.get_interval(b_pitch, s_pitch, current_pitches_dict)
		)
		tenor_alto_intervals = self.tenor_alto_intervals[:]
		tenor_alto_intervals.append(
			self.get_interval(t_pitch, a_pitch, current_pitches_dict)
		)
		tenor_soprano_intervals = self.tenor_soprano_intervals[:]
		tenor_soprano_intervals.append(
			self.get_interval(t_pitch, s_pitch, current_pitches_dict)
		)
		alto_soprano_intervals = self.alto_soprano_intervals[:]
		alto_soprano_intervals.append(
			self.get_interval(a_pitch, s_pitch, current_pitches_dict)
		)

		if self.chord_index == 0:
			if bass_soprano_intervals[-1] not in {"P5", "P8", "M3", "m3"}:
				return False
			self.bass_tenor_intervals.append(bass_tenor_intervals[-1]) 
			self.bass_alto_intervals.append(bass_alto_intervals[-1]) 
			self.bass_soprano_intervals.append(bass_soprano_intervals[-1]) 
			self.tenor_alto_intervals.append(tenor_alto_intervals[-1]) 
			self.tenor_soprano_intervals.append(tenor_soprano_intervals[-1]) 
			self.alto_soprano_intervals.append(alto_soprano_intervals[-1])

			self.root_pitch = b_pitch 
			return True

		if chord_direction == "+" and b_pitch not in self.octave_above:
			return False
		elif chord_direction == "-" and b_pitch not in self.octave_below:
			return False
		elif chord_direction == "0" and b_pitch != self.root_pitch:
			return False

		bass_motion = self.bass_motion[:]
		tenor_motion = self.tenor_motion[:]
		alto_motion = self.alto_motion[:]
		soprano_motion = self.soprano_motion[:]

		self.add_voice_motion(bass_motion, b_pitch, 0)
		self.add_voice_motion(tenor_motion, t_pitch, 1)
		self.add_voice_motion(alto_motion, a_pitch, 2)
		self.add_voice_motion(soprano_motion, s_pitch, 3)

		# bass voice is immutable b/c chord progression
		composite_motion = [tenor_motion, alto_motion, soprano_motion]
		standard_dominant_sevenths = {"V7", "V65", "V43"}
		alt_dominant_sevenths = {"V7/V", "V65/V", "V43/V", "V7/III", "V65/III", "V43/III"}
		for voice_index, new_pitch in enumerate(pitch_combo[1:]):
			previous_degree = previous_degree_combo[voice_index + 1]
			current_degree = current_degree_combo[voice_index + 1]
			old_pitch = (
				self.chosen_chord_voicings[self.chord_index - 1][voice_index + 1]
			) 
			if abs(new_pitch - old_pitch) > 12:
				return False
			if (self.chord_index > 1 and
			  abs(old_pitch - self.chosen_chord_voicings[self.chord_index - 2][voice_index + 1]) > 5 
			  and (abs(new_pitch - old_pitch) > 2 or
			  composite_motion[voice_index][-1] == 
			  composite_motion[voice_index][-2])):
				return False
			if previous_chord in standard_dominant_sevenths:  
				if (current_chord not in self.primary_dominants and
				  previous_degree == previous_chord_members[3]):
					if previous_chord == "V43":
						if not 1 <= abs(old_pitch - new_pitch) <= 2:
							return False
					else:
						if not 1 <= old_pitch - new_pitch <= 2:
							return False
				elif previous_chord == "V7" and previous_degree == 6:
					if voice_index == 2:
						if current_degree != 0:
							return False 
					else:
						if current_degree not in {0, 4}:
							return False
			elif previous_chord in alt_dominant_sevenths:
				if previous_degree == previous_chord_members[3]:
					if previous_chord[:4] == "V43/":
						if not 1 <= abs(old_pitch - new_pitch) <= 2:
							return False
					else:
						if not 1 <= old_pitch - new_pitch <= 2:
							return False
				elif (previous_chord[:3] == "V7/" and 
				  previous_degree == self.leading_degrees[previous_chord]):
					tonic = (previous_degree + 1) % 7
					dominant = (previous_degree - 2) % 7
					if voice_index == 2:
						if current_degree != tonic:
							return False
					else:
						if current_degree not in {tonic, dominant}:
							return False

			if (previous_chord == "I64" and 
			  previous_degree == 0 and current_degree != 6):
				return False
			if (previous_chord in Voice.subdom_sevenths and 
			  previous_degree == previous_chord_members[3] and 
			  not 0 <= old_pitch - new_pitch <= 2):
				return False
			if (current_chord in Voice.subdom_sevenths and
			  current_degree == current_chord_members[3] and
			  abs(new_pitch - old_pitch) > 2):
				return False
			if (Voice.mode == "aeolian" and 
			  current_degree in self.aug2_set and 
			  previous_degree in self.aug2_set and 
			  abs(new_pitch - old_pitch) == 3):
				return False

		bass_tenor_motion = self.bass_tenor_motion[:]
		bass_alto_motion = self.bass_alto_motion[:]
		bass_soprano_motion = self.bass_soprano_motion[:]
		tenor_alto_motion = self.tenor_alto_motion[:]
		tenor_soprano_motion = self.tenor_soprano_motion[:]
		alto_soprano_motion = self.alto_soprano_motion[:]

		self.add_motion_type(
			bass_motion, tenor_motion, bass_tenor_motion, bass_tenor_intervals
		)
		self.add_motion_type(
			bass_motion, alto_motion, bass_alto_motion, bass_alto_intervals
		)
		self.add_motion_type(
			bass_motion, soprano_motion, bass_soprano_motion, bass_soprano_intervals
		)
		self.add_motion_type(
			tenor_motion, alto_motion, tenor_alto_motion, tenor_alto_intervals
		)
		self.add_motion_type(
			tenor_motion, soprano_motion, tenor_soprano_motion, tenor_soprano_intervals
		)
		self.add_motion_type(
			alto_motion, soprano_motion, alto_soprano_motion, alto_soprano_intervals
		)

		old_soprano_note =  self.chosen_chord_voicings[self.chord_index - 1][3] 
		if (self.chord_index == len(self.condensed_chords) - 1 and
		  (bass_soprano_intervals[-1] != "P8" or 
		  bass_soprano_motion[-1] != "Contrary" or 
		  abs(s_pitch - old_soprano_note) > 4)): 
			return False

		composite_intervals = [
			bass_tenor_intervals, bass_alto_intervals, bass_soprano_intervals, 
			tenor_alto_intervals, tenor_soprano_intervals, alto_soprano_intervals,
		]
		composite_mvmts = [
			bass_tenor_motion, bass_alto_motion, bass_soprano_motion, 
			tenor_alto_motion, tenor_soprano_motion, alto_soprano_motion,
		]

		resolve_I6 = {"P5", "M3", "m3"}
		resolve_I = {"M3", "m3"}

		for interval_list, motion_list in zip(
		  composite_intervals, composite_mvmts):
			if (interval_list[-1] in {"P5", "P8"} and 
			  motion_list[-1] == "Parallel"):
				return False
			if (previous_chord in {"VII6", "V43"} and 
			  interval_list[-2] == "d5"):
				if current_chord == "I6" and interval_list[-1] not in resolve_I6:
					return False
				if current_chord == "I" and interval_list[-1] not in resolve_I:
					return False
			elif (previous_chord in {"V43/V", "VII6/V"} and 
			  interval_list[-2] == "d5"):
				if current_chord == "V6" and interval_list[-1] not in resolve_I6:
					return False
				if current_chord == "V" and interval_list[-1] not in resolve_I:
					return False

		# chord succeeded: add new parameters to official sequence
		self.bass_tenor_intervals.append(bass_tenor_intervals[-1]) 
		self.bass_alto_intervals.append(bass_alto_intervals[-1]) 
		self.bass_soprano_intervals.append(bass_soprano_intervals[-1]) 
		self.tenor_alto_intervals.append(tenor_alto_intervals[-1]) 
		self.tenor_soprano_intervals.append(tenor_soprano_intervals[-1]) 
		self.alto_soprano_intervals.append(alto_soprano_intervals[-1]) 

		self.bass_motion.append(bass_motion[-1])
		self.tenor_motion.append(tenor_motion[-1])
		self.alto_motion.append(alto_motion[-1])
		self.soprano_motion.append(soprano_motion[-1])

		self.bass_tenor_motion.append(bass_tenor_motion[-1]) 
		self.bass_alto_motion.append(bass_alto_motion[-1]) 
		self.bass_soprano_motion.append(bass_soprano_motion[-1]) 
		self.tenor_alto_motion.append(tenor_alto_motion[-1]) 
		self.tenor_soprano_motion.append(tenor_soprano_motion[-1]) 
		self.alto_soprano_motion.append(alto_soprano_motion[-1]) 

		return True

	def make_accompanyment(self):
		"""Rhythmically embellish chord progression"""

		if Voice.pickup:
			for _ in range(4):
				Voice.midi_score.append([Voice.Note("Rest", 0, Voice.pickup_duration)])
				Voice.chorale_scale_degrees.append([None])
		else:
			for _ in range(4):
				Voice.midi_score.append([])
				Voice.chorale_scale_degrees.append([])

		chord_accompaniments = {
			(2,2): [
				((960, 960), ({0, 1, 2, 3}, {})),
				((960 * 3 // 2, 480), ({0, 1, 2, 3}, {})),
				((480, 480, 480, 480), ({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {})),
				(
					(480, 240, 480, 240, 480), 
					({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {}, {0, 1, 2, 3}),
				),
			], (2,3): [
				((960, 960), ({0, 1, 2, 3}, {})),
				((960 * 10 // 6, 960 * 2 // 6), ({0, 1, 2, 3}, {})), 
				(
					(960 * 2 // 3, 320, 960 * 2 // 3, 320), 
					({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {}),
				),
			], (3,2): [
				((960, 960 * 2), ({0, 1, 2, 3}, {})),
				((960 * 2, 960), ({0, 1, 2, 3}, {})),
				(
					(480, 480, 480, 480, 480, 480), 
					({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {}, {0, 1, 2, 3}, {}),
				),
			], (4,2): [
				((960, 960), ({0, 1, 2, 3}, {})),
				((960 * 3 // 2, 480), ({0, 1, 2, 3}, {})),
				((480, 480, 480, 480), ({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {})),
				(
					(480, 240, 480, 240, 480), 
					({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {}, {0, 1, 2, 3}),
				), ((960 * 2, 960 * 2), ({0, 1, 2, 3}, {})),
			], (4,3): [
				((960, 960), ({0, 1, 2, 3}, {})),
				((960 * 10 // 6, 960 * 2 // 6), ({0, 1, 2, 3}, {})), 
				(
					(960 * 2 // 3, 320, 960 * 2 // 3, 320), 
					({0, 1, 2, 3}, {}, {0, 1, 2, 3}, {}),
				), ((960 * 2, 960 * 2), ({0, 1, 2, 3}, {}))
			]
		}

		chord_accompaniment = chord_accompaniments[Voice.time_sig]

		if Voice.time_sig[0] == 4:
			if Voice.chord_acceleration:
				chord_accompaniment.pop()

		note_durations, voices_used = random.choice(chord_accompaniment)

		chord_units_used = sum(note_durations) // Voice.max_note_duration
		if chord_units_used == 0:
			chord_units_used = 1
		print(f"Chord units used: {chord_units_used}")
		all_note_durations = [] 
		all_voices_used = []
		note_index = 0
		for _ in range(chord_units_used):
			all_note_durations.append([])
			all_voices_used.append([])
			while sum(all_note_durations[-1]) < Voice.max_note_duration:
				all_note_durations[-1].append(note_durations[note_index])
				all_voices_used[-1].append(voices_used[note_index])
				note_index += 1

		print(f"All note durations: {all_note_durations}")
		print(f"All voices used: {all_voices_used}")
		num_chords = len(Voice.chord_sequence)
		self.current_time = Voice.pickup_duration
		self.add_chord_section(
			0, -2, all_note_durations, all_voices_used, chord_units_used
		)

		end_note_durations = (
			(Voice.max_note_duration,), (Voice.max_note_duration,)
		)
		end_voices_used = [[{0, 1, 2, 3}], [{}]]

		if self.repeat_ending:
			self.add_chord_section(
				-2 % num_chords, num_chords, all_note_durations, 
				all_voices_used, chord_units_used
			)
			self.add_chord_section(
				-4 % num_chords, -2, all_note_durations, all_voices_used, 
				chord_units_used
			)

		self.add_chord_section(
			-2 % num_chords, num_chords, end_note_durations, 
			end_voices_used, 2
		)

	def add_chord_section(
	  self, start_index, end_index, all_note_durations, all_voices_used,
	  chord_units_used):
		"""Extend accompaniment with selected chords"""

		unique_chord_iter = iter(self.chosen_chord_voicings)
		chord_sequence = Voice.chord_sequence[:end_index]

		for chord_index, current_chord_obj in enumerate(chord_sequence):
			if chord_index < start_index:
				if chord_index in self.unique_chord_indices:
					current_pitch_combo = next(unique_chord_iter)
					last_pitch_combo = current_pitch_combo
				continue

			pitches_to_degrees = current_chord_obj.pitches_to_degrees
			note_durations = all_note_durations[chord_index % chord_units_used]
			voices_used = all_voices_used[chord_index % chord_units_used]

			if chord_index in self.unique_chord_indices:
				current_pitch_combo = next(unique_chord_iter)
				last_pitch_combo = current_pitch_combo

				for voice_index, current_pitch in enumerate(current_pitch_combo):
					note_time = self.current_time
					for beat_index, note_duration in enumerate(note_durations):
						if voice_index in voices_used[beat_index]:
							Voice.midi_score[voice_index + 1].append(
								Voice.Note(current_pitch, note_time, note_duration))
							Voice.chorale_scale_degrees[voice_index].append(
								pitches_to_degrees[current_pitch])
						else:
							Voice.midi_score[voice_index + 1].append(
								Voice.Note("Rest", note_time, note_duration))
							Voice.chorale_scale_degrees[voice_index].append(None)
						note_time += note_duration
			else:
				for voice_index, last_pitch in enumerate(last_pitch_combo):
					note_time = self.current_time

					for beat_index, note_duration in enumerate(note_durations):
						if voice_index in voices_used[beat_index]:
							Voice.midi_score[voice_index + 1].append(
								Voice.Note(last_pitch, note_time, note_duration))
							Voice.chorale_scale_degrees[voice_index].append(
								pitches_to_degrees[last_pitch])
						else:
							Voice.midi_score[voice_index + 1].append(
								Voice.Note("Rest", note_time, note_duration))
							Voice.chorale_scale_degrees[voice_index].append(None)
						note_time += note_duration

			self.current_time += Voice.max_note_duration


class Bass(Voice):
	"""The bottom voice of a chorale"""

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[0]
		self.midi_notes = Voice.midi_score[1]

		Bass.create_logger()


class Tenor(Voice):
	"""The second from bottom voice of a chorale"""

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[1]
		self.midi_notes = Voice.midi_score[2]

		Tenor.create_logger()


class Alto(Voice):
	"""The second from top voice of a chorale"""

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[2]
		self.midi_notes = Voice.midi_score[3]

		Alto.create_logger()


class Soprano(Voice):
	"""The top voice of a chorale"""

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[3]
		self.midi_notes = Voice.midi_score[4]

		Soprano.create_logger()

