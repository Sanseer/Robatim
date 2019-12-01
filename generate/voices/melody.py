import itertools
import random
from fractions import Fraction
import logging
import time

from generate.voices.voice import Voice
from generate.idioms.chord import Chord
from generate.idioms.progression import Progression
from generate.idioms.score import Score

class Melody(Voice):
	"""A chord-based melody builder"""

	def __init__(self):

		Melody.create_logger()

		#reset, incase of failed melody
		Chord.reset_settings()
		self.progression_obj = Progression()
		print(f"{self.tonic} {self.mode}")
		print(f"{self.measure_length} beats divided by {self.beat_division}")

		self.quick_turn_indices = {2, 5, 6, 9, 10, 13}
		self.good_double_rest_indices = {3, 7}
		self.bad_single_rest_indices = {6, 10, 14}
		self.valid_leap_indices = {4, 8}

		self.rhythm_symbols = [None for _ in range(16)]
		self.finalized_rhythms = {}
		self.nested_scale_degrees = [[] for _ in range(16)]
		self.unnested_scale_degrees = []
		self.midi_notes = []

		self.melodic_direction = [None for _ in range(16)]
		self.chosen_scale_degrees = [None for _ in range(16)]
		self.current_scale_degree_options = [[] for _ in range(16)]
		self.melody_figure_options = [[] for _ in range(15)]
		self.all_scale_degree_options = []

		self.break_notes = random.choice((True, False))
		print(f"Repeat ending: {self.repeat_ending}")

		self.melody_range = []
		self.unit_length = 0
		self.current_time = 0
		self.chord_index = 0
		self.pickup_rhythm = []

		self.time0 = 0
		self.time1 = 0

		self.pickup_figurations = {
			1: {
				0: ((-1,), (-3,), (0,)), 1: ((-2,), (0,)), 2: ((-4,), (0,)), 
				3: ((-1,), (0,)),
			}
		}
		self.chosen_figurations = [None for _ in range(15)]

		self.all_single_figurations = {
			0: lambda previous, current, slope: [
				((current - 1,), "CN"), ((current + 1,), "CN"),
			],
			1: lambda previous, current, slope: [
				((previous,), "RET"), ((current,), "ANT"), 
				((current + slope,), "CIN"), ((previous - slope,), "PIN"),
				((previous - slope * 2,), "OPT"),
			],
			2: lambda previous, current, slope: [
				((previous + slope,), "IPT"), ((current + slope,), "CIN"),
				((current,), "ANT"),
			],
			3: lambda previous, current, slope: [
				((previous + slope * 2,), "IPT"), ((current + slope,), "CIN"),
				((previous + slope,), "IPT"),
			],
			4: lambda previous, current, slope: [
				((previous + slope * 2,), "IPT"), ((current + slope,), "CIN"),
			],
			5: lambda previous, current, slope: [
				((previous + slope * 2,), "IPT"), ((previous + slope * 3,), "IPT"),
			],
			6: lambda previous, current, slope: [((current + slope,), "CIN")],
		}

		self.all_double_figurations = {
			0: lambda previous, current, slope: [
				((current - 1, current + 1), "DN"), 
				((current + 1, current - 1), "DN"),
				((current + 2, current + 1), "DCN"), 
				((current - 2, current - 1), "DCN"),
			],
			1: lambda previous, current, slope: [
				((previous - slope, previous), "OPT"), 
				((current + slope * 2, current + slope), "OPT"), 
				((current, current + slope), "OPT"),
				((previous - slope * 2, previous - slope), "OPT"),
			],
			2: lambda previous, current, slope: [
				((current + slope * 2, current + slope), "OPT"),
				((previous - slope, previous + slope), "OPT"),
				((current, current + slope), "OPT"),
			],
			3: lambda previous, current, slope: [
				((previous + slope, previous + slope * 2), "IPT"), 
				((current + slope * 2, current + slope), "OPT"),
				((previous + slope, current), "IPT"),
			],
			4: lambda previous, current, slope: [
				((previous + slope * 2, previous + slope * 3), "IPT"),
				((previous + slope, previous + slope * 2), "IPT"),
			],
			5: lambda previous, current, slope: [
				((previous + slope * 2, previous + slope * 4), "IPT"),
				((current + slope * 2, current + slope), "OPT"),
			],
			6: lambda previous, current, slope: [],
		}
		self.all_triple_figurations = {
			0: lambda previous, current, slope: [],
			1: lambda previous, current, slope: [],
			2: lambda previous, current, slope: [],
			3: lambda previous, current, slope: [
				((previous + slope * 2, previous + slope, previous + slope * 2), "IPT"),
			],
			4: lambda previous, current, slope: [
				((previous + slope, previous + slope * 2, previous + slope * 3), "IPT"),
			],
			5: lambda previous, current, slope: [],
			6: lambda previous, current, slope: [],
		}

		self.sheet_notes = []

	def make_melody(self):
		"""Make a random melody"""
		self.set_scale_midi_pitches()
		self.make_chord_progression()
		self.create_rhythm()
		self.realize_melody()

		self.add_midi_score()
		self.prepare_score()

		self.set_sheet_notes()
		self.make_lily_part()
		Voice.midi_score.append(self.midi_notes)

	def set_scale_midi_pitches(self):
		"""Choose all midi pitches that are diatonic to the key signature"""
		current_pitch = -12
		root_pitch = current_pitch + self.tonics[self.tonic]
		scale_sequence = self.mode_notes[self.mode]

		all_midi_pitches = []
		while root_pitch < 128:
			for chromatic_shift in scale_sequence:
				current_pitch = root_pitch + chromatic_shift
				if 0 <= current_pitch <= 127:
					Voice.all_midi_pitches.append(current_pitch)
			root_pitch += 12

		self.logger.warning(f"All midi pitches: {Voice.all_midi_pitches}")
		self.logger.warning("")

	def make_chord_progression(self):
		"""Make a chord progression using common practice idioms"""
		major_minor_tonality = ("ionian", "aeolian") 
		if self.mode not in major_minor_tonality:
			temp_mode = self.mode
			Score.mode = random.choice(major_minor_tonality)
		else:
			temp_mode = None
		chord_structure, Voice.chord_acceleration = self.progression_obj.choose_progression_type()
		print(f"Chord acceleration: {Voice.chord_acceleration}")
		self.logger.warning(f"{chord_structure}")

		for chord_pattern in chord_structure:
			chord_seq_choice = self.progression_obj.add_chord_pattern(chord_pattern)
			if isinstance(chord_seq_choice, str):
				Voice.chord_sequence.append(Chord(chord_seq_choice))
			elif isinstance(chord_seq_choice, list):
				for chord_choice in chord_seq_choice:
					Voice.chord_sequence.append(Chord(chord_choice))

		print(f"Chord sequence: {Voice.chord_sequence}")
		if temp_mode is not None:
			Score.mode = temp_mode

	def create_rhythm(self):
		"""Choose a rhythm for the melody with basic/contrasting ideas"""

		raw_rhythm_symbols = []
		for phrase_options in self.rhythm_patterns:
			raw_rhythm_symbols.extend(random.choice(phrase_options))
		if 2 in raw_rhythm_symbols and 1 not in raw_rhythm_symbols:
			for index, rhythm_num in enumerate(raw_rhythm_symbols):
				if rhythm_num > 0:
					self.rhythm_symbols[index] = rhythm_num - 1
				else:
					self.rhythm_symbols[index] = rhythm_num
		else:
			self.rhythm_symbols = raw_rhythm_symbols
		print(f"Rhythm symbols: {self.rhythm_symbols}")

		if self.time_sig in {(2,2), (4,2)}:
			rhythm_mapping = {
				-1: [(8,)], 0: [(4,4), (6,2)], 1: [(4,4), (6,2)], 
				2:[(3,3,2), (4,2,2), (6,1,1)],
				-2: [(4,4), (6,2)],
			}
		elif self.time_sig in {(2,3), (4,3)}:
			rhythm_mapping = {
				-1: [(12,)], 0: [(6,6), (10,2)], 1: [(6,6), (6,2,4), (10,2)], 
				2: [(4,2,6), (4,4,4), (6,6), (6,2,4), (6,4,2), (8,4), (10, 1, 1)],
				-2: [(6,6), (10,2)],
			}
		elif self.time_sig == (3,2):
			rhythm_mapping = {
				-1: [(12,)], 0: [(4,4,2,2), (8,2,2), (8,4), (10,2)], 
				1: [(4,4,2,2), (4,4,4), (6,2,4), (8,2,2), (8,4), (10,2)], 
				2:[(4,2,6), (4,4,2,2), (4,4,4), (6,6), (6,2,2,2), (6,2,4), (8,2,2), (10,1,1)],
				-2: [(8,4), (10,2)],
			}

		chosen_rhythms = {}
		rhythm_symbol_set = set(self.rhythm_symbols)
		if -2 in rhythm_symbol_set:
			Voice.pickup = True
		print(f"Pickup note? {Voice.pickup}")
		for rhythm_symbol in rhythm_symbol_set:
			possible_rhythms = rhythm_mapping[rhythm_symbol]
			random.shuffle(possible_rhythms)
			while True:
				chosen_rhythm = possible_rhythms.pop()
				if chosen_rhythm not in chosen_rhythms.values() or rhythm_symbol == -2:
					chosen_rhythms[rhythm_symbol] = chosen_rhythm
					break

		print(f"Chosen rhythms: {chosen_rhythms}")

		self.finalized_rhythms = [
			chosen_rhythms[rhythm_symbol] for rhythm_symbol in self.rhythm_symbols
		]
		self.pickup_rhythm = self.finalized_rhythms[7][1:]

		self.logger.warning(f"Finalized rhythms: {self.finalized_rhythms}")
		self.logger.warning("")
		self.logger.warning("")

	def create_melody_options(self):
		"""Use chord progression to layout possible base melody scale degrees"""

		phrase2_start_index = 4
		phrase4_start_index = 12
		if str(Voice.chord_sequence[0]) == "0I":
			self.all_scale_degree_options.append([0, 2])
		# separate first note to allow irregular starts e.g., major 2nd
		for chord_index, chord_obj in enumerate(Voice.chord_sequence[1:-2], 1):
			current_scale_degrees = chord_obj.scale_degrees
			# make into set?
			self.all_scale_degree_options.append([])
			self.all_scale_degree_options[-1].extend(current_scale_degrees)
			if phrase2_start_index <= chord_index < phrase4_start_index:
				if 0 in self.all_scale_degree_options[-1]:
					self.all_scale_degree_options[-1].append(7)
			elif chord_index >= 3: 
				for scale_degree in current_scale_degrees:
					if scale_degree >= 4:
						self.all_scale_degree_options[-1].append(scale_degree - 7)

		for scale_degrees in self.all_scale_degree_options:
			random.shuffle(scale_degrees)

		self.all_scale_degree_options.extend([[0], [0]])

	def create_first_melody_note(self):
		"""Reset the first melody note of the sequence"""

		self.logger.warning(f"Chord index: {self.chord_index}")
		# AssertionError singles out this scenario.
		# it traverses the call stack to main.py before being handled.
		# Other exceptions like IndexError can occur elsewhere in class instance
		# and would be silenced by main.py, preventing debugging.
		try:
			self.current_degree_choice = self.current_scale_degree_options[0].pop()
		except IndexError:
			print("Melody failed")
			raise AssertionError
		self.chosen_scale_degrees[0] = self.current_degree_choice
		if Voice.pickup:
			self.melodic_direction[0] = '>'
		else:
			self.melodic_direction[0] = '_'

		self.chord_index += 1
		self.current_scale_degree_options[1] = self.all_scale_degree_options[1][:]
		self.previous_degree_choice = self.current_degree_choice
		self.logger.warning("")
		self.logger.warning("")

	def realize_melody(self):
		"""Create and validate a melody sequence"""
		self.create_melody_options()
		self.current_scale_degree_options[0].extend(self.all_scale_degree_options[0][:])
		self.create_first_melody_note()

		self.time0 = time.time()
		while None in self.chosen_scale_degrees:
			self.logger.warning(f"Chord index: {self.chord_index}")
			if self.chord_index == 0:
				self.create_first_melody_note()
			if self.melody_figure_options[self.chord_index - 1]:
				self.attempt_melody_figure()
			elif self.current_scale_degree_options[self.chord_index]:
				self.attempt_full_melody()
			else:
				self.backtrack_score()

		self.nested_scale_degrees[-1] = [self.current_degree_choice]
		self.logger.warning(f"Nested scale degrees: {self.nested_scale_degrees}")
		self.reset_unnested_melody()
		self.logger.warning(f"Unnested scale degrees: {self.unnested_scale_degrees}")
		print(f"Chosen figurations: {self.chosen_figurations}")

	def backtrack_score(self):
		"""Returns to the previous chord position to fix bad melody notes"""
		self.melodic_direction[self.chord_index] = None
		self.chosen_scale_degrees[self.chord_index] = None
		self.chord_index -= 1

		self.time1 = time.time()
		if self.time1 - self.time0 > 15:
			print("Melody takiing too long.")
			raise AssertionError

		# can't track negative progress because figuration options
		# (as opposed to base melody options) determines # of possible combos.
		# figurations are calculated at the time of validation

		self.previous_degree_choice = self.chosen_scale_degrees[self.chord_index - 1]
		if not self.melody_figure_options[self.chord_index - 1]:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degrees[self.chord_index] = None
		self.nested_scale_degrees[self.chord_index] = []
		self.chosen_figurations[self.chord_index - 1] = None

	def advance_score(self):
		"""Progress to the next chord position after current melody is validated"""

		self.logger.warning(f"Melodic direction {self.melodic_direction}")
		self.logger.warning(f"Chosen scale degrees: {self.chosen_scale_degrees}")
		self.logger.warning("")
		self.logger.warning("")
		self.chord_index += 1
		if self.chord_index < len(self.chosen_scale_degrees):
			self.previous_degree_choice = self.current_degree_choice
			self.current_scale_degree_options[self.chord_index] = (
				self.all_scale_degree_options[self.chord_index][:]
			)

	def attempt_melody_figure(self):
		"""Try the next melody figure using the validated base melody"""

		self.logger.warning("Choosing from remaining figures")
		# only occurs when backtracking
		self.current_degree_choice = self.chosen_scale_degrees[self.chord_index]
		self.reset_unnested_melody()
		if self.has_melody_figure():
			self.advance_score()
		else:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degrees[self.chord_index] = None

	def attempt_full_melody(self):
		"""Try the next base melody +/- figuration at current chord position"""

		self.logger.warning("Choosing base note")
		self.current_degree_choice = (
			self.current_scale_degree_options[self.chord_index].pop()
		)

		if self.current_degree_choice == self.previous_degree_choice:
			self.melodic_direction[self.chord_index] = '_'
		elif self.current_degree_choice > self.previous_degree_choice:
			self.melodic_direction[self.chord_index] = '>'
		elif self.current_degree_choice < self.previous_degree_choice:
			self.melodic_direction[self.chord_index] = '<'

		self.reset_unnested_melody()
		self.chosen_scale_degrees[self.chord_index] = self.current_degree_choice 
		if self.validate_base_melody() and self.has_melody_figure():
			self.advance_score()
		else:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degrees[self.chord_index] = None

	def validate_base_melody(self):
		"""Check current base melody with idioms"""
		melodic_mvmt = "".join(
			str(slope) for slope in self.melodic_direction[:self.chord_index + 1]
		)

		if "_" * 3 in melodic_mvmt:
			# Avoid long rests
			return False
		if "_" * 2 in melodic_mvmt:
			all_rest_indices = set()
			start_index = 0
			while True:
				rest_index = melodic_mvmt.find("__", start_index)
				if rest_index == -1:
					break
				all_rest_indices.add(rest_index)
				start_index = rest_index + 1
			if all_rest_indices - self.good_double_rest_indices:
				# Avoid triple repeats only between phrases")
				return False

		start_index = 0
		while True:
			rest_index = melodic_mvmt.find("_", start_index)

			if rest_index in self.bad_single_rest_indices:
				return False
			if rest_index == -1:
				break
			start_index = rest_index + 1

		relevant_melodic_mvt = melodic_mvmt[1:]	
		
		current_move_distance = self.current_degree_choice - self.previous_degree_choice
		abs_current_move_distance = abs(current_move_distance)
		if abs_current_move_distance > 7:
			# Keep leaps within octave
			return False
		if self.chord_index == 14:
			if abs_current_move_distance > 4:
				# Don't end with a large leap
				return False
			if relevant_melodic_mvt.count('>') > relevant_melodic_mvt.count('<'):
				# Descending motion should predominate
				return False
		if abs_current_move_distance > 4 and self.chord_index not in self.valid_leap_indices:
			# Large leap can only occur halfway through
			return False
		if len(self.unnested_scale_degrees) >= 3: 
			if self.chord_index < 9:
				nested_part_half = self.nested_scale_degrees[:8]
			else: 
				nested_part_half = self.nested_scale_degrees[8:]
			unnested_part_half = Voice.merge_lists(*nested_part_half)
			if not Voice.has_proper_leaps(unnested_part_half):
				# "Leap should be followed by contrary stepwise motion (full melody)"
				return False

		# score divides into 4 sections, 16 items
		# first 2 sections: antecedent
		# last 2 sections: consequent
		current_section = self.chord_index // 4
		section_start_index = current_section * 4
		section_scale_degrees = (
			self.chosen_scale_degrees[section_start_index:section_start_index + 4]
		)
		end_degree = section_scale_degrees[-1]
		while end_degree is None:
			section_scale_degrees.pop()
			end_degree = section_scale_degrees[-1]

		section_max_degree = max(section_scale_degrees)
		if current_section <= 2:
			if section_scale_degrees.count(section_max_degree) > 2:
				return False
			if section_scale_degrees.count(section_max_degree) == 2:
				for scale_degree0, scale_degree1 in zip(
				  section_scale_degrees, section_scale_degrees[1:]):
					if (scale_degree0 == section_max_degree and
					  scale_degree0 == scale_degree1):
						break 
				else:
					return False 

		if self.chord_index == 2 and self.chosen_figurations[0] == "IN":
			return False
		if self.chord_index >= 3:
			previous_melody_note = self.chosen_scale_degrees[self.chord_index - 3]
			for chord_index, melody_group in enumerate(
			  self.nested_scale_degrees[self.chord_index - 3:self.chord_index - 1],
			  self.chord_index - 3):
				for fig_index, current_melody_note in enumerate(melody_group):
					if (abs(current_melody_note - previous_melody_note) > 4 and
					  (fig_index != 0 or chord_index not in self.valid_leap_indices)):
						return False
					previous_melody_note = current_melody_note

		if self.chord_index == 8: 
			section1 = self.chosen_scale_degrees[:4]
			section2 = self.chosen_scale_degrees[4:8]
			if max(section1) == max(section2):
				return False
		elif self.chord_index == 15:
			section3 = self.chosen_scale_degrees[8:12]
			section4 = self.chosen_scale_degrees[12:]
			if max(section3) <= max(section4):
				return False
			if self.nested_scale_degrees[13][-1] - 0 > 4:
				return False
			if (self.chosen_figurations.count("OPT") > 2 and 
			  self.nested_scale_degrees[0:4] != self.nested_scale_degrees[8:12]):
				return False

		num_still_figures = self.chosen_figurations.count("CN")
		num_still_figures += self.chosen_figurations.count("DN")
		num_still_figures += self.chosen_figurations.count("DCN")

		if num_still_figures > 2:
			return False
		if self.chosen_figurations.count("OPT") > 4:
			return False

		if self.chord_index >= 3:
			if (self.chord_index not in self.quick_turn_indices and 
			  melodic_mvmt[self.chord_index - 2:] in {"><>", "<><"}):
				# No late melodic jukes
				return False
		
		return True

	def has_melody_figure(self):
		"""Check specific melody against figuration options"""

		last_rhythm_symbol = self.rhythm_symbols[self.chord_index - 1]
		if last_rhythm_symbol == -1:
			if self.chord_index == 15:
				section3 = Voice.merge_lists(*self.nested_scale_degrees[8:12])
				section4 = Voice.merge_lists(*self.nested_scale_degrees[12:14])

				if max(section3) <= max(section4):
					return False
			self.nested_scale_degrees[self.chord_index - 1] = [self.previous_degree_choice]
			return True
		if last_rhythm_symbol == -2:
			self.melody_figure_options[self.chord_index - 1] = (
				self.get_pickup_sequences(self.current_degree_choice)
			)
			return self.add_valid_figure()

		remaining_figures = self.melody_figure_options[self.chord_index - 1]
		if remaining_figures:
			return self.add_valid_figure()

		degree_mvmt = self.current_degree_choice - self.previous_degree_choice
		melody_slope = Voice.calculate_slope(degree_mvmt)
		degree_mvmt = abs(degree_mvmt)

		embellish_amount = len(self.finalized_rhythms[self.chord_index - 1])
		if embellish_amount == 2:
			all_figurations = self.all_single_figurations
		elif embellish_amount == 3:
			all_figurations = self.all_double_figurations
		elif embellish_amount == 4:
			all_figurations = self.all_triple_figurations
		possible_scale_degrees = all_figurations[degree_mvmt](
			self.previous_degree_choice, self.current_degree_choice, melody_slope)

		self.melody_figure_options[self.chord_index - 1] = possible_scale_degrees
		return self.add_valid_figure()

	def reset_unnested_melody(self):
		"""Create a unnested sequence of the currently approved melody"""
		self.unnested_scale_degrees = []
		for melody_group in self.nested_scale_degrees[:self.chord_index - 1]:
			for melody_note in melody_group:
				self.unnested_scale_degrees.append(melody_note)
		self.unnested_scale_degrees.append(self.previous_degree_choice)

	def add_valid_figure(self):
		"""Find and add specific figuration of base melody using idioms"""
		valid_figure = None
		remaining_figures = self.melody_figure_options[self.chord_index - 1]

		random.shuffle(remaining_figures)
		# alias has side effect but allows easier referencing
		while remaining_figures:
			inbetween, fig_type = remaining_figures.pop()
			if min(inbetween) < -3 or max(inbetween) > 7:
				continue
			if self.chord_index - 1 < 3 and min(inbetween) < 0:
				continue

			unnested_scalar_melody = self.unnested_scale_degrees[:]
			unnested_scalar_melody.extend(inbetween)

			# chord 8 and 12 are short-circuited
			# only need to evaluate once going forward
			if self.chord_index == 13 and max(unnested_scalar_melody) < 5:
				continue
			if self.chord_index == 9:
				section1 = Voice.merge_lists(*self.nested_scale_degrees[:4])
				section2 = Voice.merge_lists(*self.nested_scale_degrees[4:8])

				if max(section1) == max(section2):
					continue

			valid_figure = inbetween
			break

		if valid_figure is None:
			self.logger.warning("Melody failed")
			return False
		self.nested_scale_degrees[self.chord_index - 1] = [
				self.previous_degree_choice, *valid_figure]
		self.chosen_figurations[self.chord_index - 1] = fig_type
		self.logger.warning(f"Nested valid melody: {self.nested_scale_degrees}")
		return True

	def add_midi_score(self):
		"""Transform a scale degree sequence into a midi pitch sequence"""
		
		fifth_degree_pitch = 7 + self.tonics[self.tonic]
		while fifth_degree_pitch < 45:
			fifth_degree_pitch += 12
		start_index = Voice.all_midi_pitches.index(fifth_degree_pitch)
		self.melody_range = Voice.all_midi_pitches[start_index:start_index + 11]
		self.logger.warning(f"Melody range: {self.melody_range}")

		self.unit_length = sum(self.finalized_rhythms[0])
		if self.time_sig in {(4,3), (4,2)}:
			chord_quarter_length = self.measure_length // 2
		else:
			chord_quarter_length = self.measure_length
		self.logger.warning(f"Unit length: {self.unit_length}")
		self.logger.warning(f"Chord quarter length: {chord_quarter_length}")

		Voice.max_note_duration = 960 * chord_quarter_length
		if Voice.pickup:
			index_shift = self.add_pickup_notes()
		else:
			index_shift = 0
		self.current_time = Voice.pickup_duration

		print(f"Break melody: {self.break_notes}")
		self.nested_scale_degrees.pop()
		self.add_midi_section(self.nested_scale_degrees, 0, {}, index_shift)

		self.logger.warning(f"Midi melody: {self.midi_notes}")
		self.unnested_scale_degrees.pop()

		if not self.repeat_ending:
			self.midi_notes.append(
				Voice.Note("Rest", self.current_time, Voice.max_note_duration))
			self.current_time += Voice.max_note_duration
			return

		second_pickup_fraction = Fraction(
			numerator=sum(self.finalized_rhythms[-5][1:]), 
			denominator=self.unit_length
		)
		second_pickup_duration = int(
			Voice.max_note_duration * second_pickup_fraction
		)  

		ending_duration = Voice.max_note_duration - second_pickup_duration
		self.midi_notes.append(
			Voice.Note("Rest", self.current_time, ending_duration)
		)

		self.current_time += ending_duration

		remaining_melody = self.nested_scale_degrees[-4:]
		remaining_melody[0] = remaining_melody[0][1:]

		end_notes_num = self.add_midi_section(remaining_melody, -5, {-5: 1})
		self.unnested_scale_degrees.extend(
			self.unnested_scale_degrees[-end_notes_num:]
		)

		self.midi_notes.append(
			Voice.Note("Rest", self.current_time, Voice.max_note_duration)
		)
		self.current_time += Voice.max_note_duration

	def add_pickup_notes(self):
		"""Adds pickup notes to beginning of the piece"""

		rest_rhythm = self.finalized_rhythms[7][0]
		Voice.pickup_duration = Voice.max_note_duration
		first_scale_degree = self.unnested_scale_degrees[0]

		note_alterations = {}

		rest_fraction = Fraction(
			numerator=rest_rhythm, denominator=self.unit_length
		)
		rest_duration = int(Voice.pickup_duration * rest_fraction)
		self.midi_notes.append(Voice.Note("Rest", 0, rest_duration))

		self.chord_index = 0
		pickup_degree_sequence, _ = random.choice(
			self.get_pickup_sequences(first_scale_degree)
		)
		current_time = rest_duration

		unnested_scale_degrees = []
		for note_index, note_rhythm in enumerate(self.pickup_rhythm):
			pickup_scale_degree = pickup_degree_sequence[note_index]
			note_offset = note_alterations.get(pickup_scale_degree % 7, 0)
			midi_pitch = self.melody_range[pickup_scale_degree + 3] + note_offset

			embellish_fraction = Fraction(
				numerator=note_rhythm, denominator=self.unit_length
			)
			note_duration = int(Voice.pickup_duration * embellish_fraction)
			self.midi_notes.append(
				Voice.Note(midi_pitch, current_time, note_duration)
			)
			unnested_scale_degrees.append(pickup_scale_degree)

			current_time += note_duration

		unnested_scale_degrees.extend(self.unnested_scale_degrees)
		self.unnested_scale_degrees = unnested_scale_degrees

		return len(self.pickup_rhythm)

	def get_pickup_sequences(self, centered_degree):
		"""Create pickup sequences using a reference scale degree"""

		possible_degrees = Voice.chord_sequence[self.chord_index].scale_degrees
		degree_index = possible_degrees.index(centered_degree % 7)
		chord_pickup_choices = self.pickup_figurations[len(self.pickup_rhythm)]
		possible_scale_shifts = chord_pickup_choices[degree_index]

		pickup_scale_options = []
		for chosen_scale_shifts in possible_scale_shifts:
			pickup_scale_options.append([])
			pickup_scale_options[-1].append([])
			for degree_shift in chosen_scale_shifts:
				pickup_scale_options[-1][0].append(centered_degree + degree_shift)

			# accounts for melodic figuration type
			pickup_scale_options[-1].append(None)

		return pickup_scale_options

	def add_midi_section(
	  self, melody_section, chord_start_index, note_start_indices, 
	  index_shift=None):
		"""Add midi notes to the pitch sequence using scale degrees"""

		object_index = 0
		melodic_minor = False
		add_rest = False

		melody_section_iter = iter(melody_section)
		next_scale_group = next(melody_section_iter, None)
		for chord_index, current_scale_group in enumerate(melody_section, chord_start_index):

			next_scale_group = next(melody_section_iter, None)
			current_chord_name = Voice.chord_sequence[chord_index].chord_name
			if self.mode == "ionian" and current_chord_name in Chord.major_mode_alterations:
				note_alterations = Chord.major_mode_alterations[current_chord_name]
			elif self.mode == "aeolian" and current_chord_name in Chord.minor_mode_alterations:
				note_alterations = Chord.minor_mode_alterations[current_chord_name]
			else: 
				note_alterations = {}
				
			if self.mode == "aeolian" and current_chord_name in Voice.dominant_harmony:
				if melodic_minor: 
					note_alterations[5] = 1 
				else:
					# catch raised notes inbetween 2 chords
					next_chord_name = Voice.chord_sequence[chord_index + 1].chord_name
					if next_chord_name in Voice.dominant_harmony:
						affected_scale_group = current_scale_group + next_scale_group
					else:
						affected_scale_group = current_scale_group
					scale_group_str = "".join(
						str(scale_degree) for scale_degree in affected_scale_group
					)
					if any(
					  str_combo in scale_group_str 
					  for str_combo in ("56", "65", "-1-2", "-2-1")):
						melodic_minor = True
						note_alterations[5] = 1
						print("Melodic minor!")

			for embellish_index, scale_degree in enumerate(
			  current_scale_group, note_start_indices.get(chord_index, 0)):
				embellish_duration = self.finalized_rhythms[chord_index][embellish_index]
				# account for negative scale degrees
				note_offset = note_alterations.get(scale_degree % 7, 0)
				embellish_fraction = Fraction(
					numerator=embellish_duration, denominator=self.unit_length
				)

				raw_note_duration = int(
					Voice.max_note_duration * embellish_fraction)
				# integers required for midi output

				if raw_note_duration > 960 and self.rhythm_symbols[chord_index] >= 0 and self.break_notes:
					fixed_note_duration = 960
					add_rest = True
					extra_duration = raw_note_duration - 960
				else:
					fixed_note_duration = raw_note_duration

				midi_pitch = self.melody_range[scale_degree + 3] + note_offset
				if chord_index == 7 and embellish_index == 0 and self.rhythm_symbols[6] == -1:
					self.midi_notes.append(
						Voice.Note("Rest", self.current_time, fixed_note_duration)
					)
					# needed all numbers in unnested sequence for validation
					self.unnested_scale_degrees.pop(object_index + index_shift)
				else:
					self.midi_notes.append(
						Voice.Note(midi_pitch, self.current_time, fixed_note_duration)
					)
					if add_rest:
						self.midi_notes.append(
							Voice.Note("Rest", self.current_time + 960, extra_duration)
						)

				self.current_time += raw_note_duration
				add_rest = False
				object_index += 1

		return object_index

	def prepare_score(self):
		self.add_rest_placeholders()
		if self.mode not in ("ionian", "aeolian"):
			Voice.chord_sequence = (Chord("0I"),) * 16

	def add_rest_placeholders(self):
		"""Modify scale degree sequence to match midi note sequence"""

		unnested_scale_degrees = []
		unnested_melody_iter = iter(self.unnested_scale_degrees)

		for midi_note in self.midi_notes:
			if midi_note.pitch == "Rest":
				unnested_scale_degrees.append(None)

			else:
				unnested_scale_degrees.append(next(unnested_melody_iter))

		self.unnested_scale_degrees = unnested_scale_degrees
		self.logger.warning(f"Final unnested melody: {self.unnested_scale_degrees}")
		self.logger.warning(f"Final nested melody: {self.nested_scale_degrees}")

