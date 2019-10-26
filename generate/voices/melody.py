import itertools
import random
from fractions import Fraction
import logging

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b
from generate.idioms.chord import Chord

class Melody(Voice):
	"""A melody constructor based on a chord progression"""

	def __init__(self):

		self.logger = logging.getLogger("melody")
		melody_handler = logging.FileHandler("logs/melody.log", mode='w')
		melody_handler.setLevel(logging.WARNING)
		melody_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		melody_handler.setFormatter(melody_format)
		self.logger.addHandler(melody_handler)

		#reset, incase of repeat
		Chord.reset_settings()
		Voice.mode = random.choice(("ionian", "aeolian"))
		if Voice.mode == "ionian":
			import generate.idioms.major
			Voice.idms_mode = generate.idioms.major
		elif Voice.mode == "aeolian":
			import generate.idioms.minor
			Voice.idms_mode = generate.idioms.minor

		Voice.time_sig = random.choice(idms_b.time_sigs)
		Voice.tonic = random.choice(self.idms_mode.key_sigs)
		print(f"{Voice.tonic} {Voice.mode}")

		Voice.measure_length = Voice.time_sig[0]
		Voice.beat_division = Voice.time_sig[1]
		if Voice.beat_division == 2:
			Voice.beat_durations = Voice.simple_beat_durations
		elif Voice.beat_division == 3:
			Voice.beat_durations = Voice.compound_beat_durations
		print(f"{Voice.measure_length} beats divided by {Voice.beat_division}")

		self.quick_turn_indices = {2, 5, 6, 9, 10, 13}
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

		self.chordal_voice = False
		self.break_notes = random.choice((True, False))
		self.restart_basic_idea = random.choice((True, False, False))
		Voice.repeat_ending = random.choice((True, False))
		print(f"Repeat ending: {Voice.repeat_ending}")
		print(f"Repeat basic idea: {self.restart_basic_idea}")

		self.melody_range = []
		self.unit_length = 0
		self.current_time = 0
		self.pickup_rhythm = []

		self.pickup_figurations = {
			1: {
				0: ((-1,), (-3,), (0,)), 1: ((-2,), (0,)), 2: ((-4,), (0,)), 3: ((-1,), (0,))
			}
		}
		self.chosen_figurations = [None for _ in range(16)]

		self.all_single_figurations = {
			0: lambda previous, current, slope: [
				((current - 1,), "CN"), ((current + 1,), "CN")],
			1: lambda previous, current, slope: [
				((previous,), "RET"), ((current,), "ANT"), 
				((current + slope,), "IN")],
			2: lambda previous, current, slope: [
				((previous + slope,), "PT"), ((current + slope,), "IN")],
			3: lambda previous, current, slope: [
				((previous + slope * 2,), "PT"), ((current + slope,), "IN")],
			4: lambda previous, current, slope: [
				((previous + slope * 2,), "PT"), ((current + slope,), "IN")],
			5: lambda previous, current, slope: [
				((previous + slope * 2,), "PT"), ((previous + slope * 3,), "PT")],
			6: lambda previous, current, slope: [((current + slope,), "IN")]
		}

		self.all_double_figurations = {
			0: lambda previous, current, slope: [
				((current - 1, current + 1), "DN"), ((current + 1, current - 1), "DN"),
				((current + 2, current + 1), "DCN"), ((current - 2, current - 1), "DCN")],
			1: lambda previous, current, slope: [
				((previous - slope, previous), "DRN"), 
				((current + slope * 2, current + slope), "DRN"), 
				((current, current + slope), "ANT")],
			2: lambda previous, current, slope: [
				((current + slope * 2, current + slope), "DRN")],
			3: lambda previous, current, slope: [
				((previous + slope, previous + slope * 2), "PT"), 
				((current + slope * 2, current + slope), "DRN")],
			4: lambda previous, current, slope: [
				((previous + slope * 2, previous + slope * 3), "PT")],
			5: lambda previous, current, slope: [
				((previous + slope * 2, previous + slope * 4), "PT"),
				((current + slope * 2, current + slope), "DRN")],
			6: lambda previous, current, slope: []
		}
		self.all_triple_figurations = {
			0: lambda previous, current, slope: [],
			1: lambda previous, current, slope: [],
			2: lambda previous, current, slope: [],
			3: lambda previous, current, slope: [
				((previous + slope * 2, previous + slope, previous + slope * 2), "PT")
			],
			4: lambda previous, current, slope: [
				((previous + slope, previous + slope * 2, previous + slope * 3), "PT")
			],
			5: lambda previous, current, slope: [],
			6: lambda previous, current, slope: [],
		}

		self.sheet_notes = []

	def make_melody(self):
		"""Make a random melody from a randomly selected chord progression and rhythm"""
		self.set_scale_midi_pitches()
		self.make_chord_progression()
		self.create_rhythm()
		self.realize_melody()

		self.add_midi_score()

		self.set_sheet_notes()
		self.make_lily_part()
		Voice.midi_score.append(self.midi_notes)

	def set_scale_midi_pitches(self):
		"""Choose all midi pitches that are diatonic to the key signature"""
		current_pitch = -12
		root_pitch = current_pitch + Voice.tonics[Voice.tonic]
		scale_sequence = Voice.mode_notes[Voice.mode]

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
		chord_structure = random.choice(tuple(idms_b.chord_patterns_16))
		Voice.chord_acceleration = idms_b.chord_patterns_16[chord_structure]
		print(f"Chord acceleration: {Voice.chord_acceleration}")
		self.logger.warning(f"{chord_structure}")
		chord_str_sequence = []
		chord_structure_iter = iter(chord_structure)

		chord_pattern = next(chord_structure_iter, None)
		while chord_pattern is not None:
			if chord_pattern == "TON":
				Voice.chord_sequence.append(Chord("0I"))
			elif chord_pattern == "RPT":
				Voice.chord_sequence.append(
					Chord(Voice.chord_sequence[-1].chord_symbol))
			else:
				chord_seq_choices = Voice.idms_mode.chord_ids[chord_pattern]
				chord_seq_choice = random.choice(
					chord_seq_choices[Voice.chord_sequence[-1].chord_symbol])
				if isinstance(chord_seq_choice, str):
					Voice.chord_sequence.append(Chord(chord_seq_choice))
				elif isinstance(chord_seq_choice, tuple):
					for chord_choice in chord_seq_choice:
						Voice.chord_sequence.append(Chord(chord_choice))
			chord_pattern = next(chord_structure_iter, None)

		print(f"Chord sequence: {Voice.chord_sequence}")

	def create_rhythm(self):
		"""Choose a rhythm for the melody with basic/contrasting ideas"""

		raw_rhythm_symbols = []
		for phrase_options in idms_b.rhythm_patterns:
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

		if Voice.time_sig in {(2,2), (4,2)}:
			rhythm_mapping = {
				-1: [(8,)], 0: [(4,4), (6,2)], 1: [(4,4), (6,2)], 
				2:[(3,3,2), (4,2,2), (6,1,1)],
				-2: [(4,4), (6,2)]
			}
		elif Voice.time_sig in {(2,3), (4,3)}:
			rhythm_mapping = {
				-1: [(12,)], 0: [(6,6), (10,2)], 1: [(6,6), (6,2,4), (10,2)], 
				2: [(4,2,6), (4,4,4), (6,6), (6,2,4), (6,4,2), (8,4), (10, 1, 1)],
				-2: [(6,6), (10,2)]
			}
		elif Voice.time_sig == (3,2):
			rhythm_mapping = {
				-1: [(12,)], 0: [(4,4,2,2), (8,2,2), (8,4), (10,2)], 
				1: [(4,4,2,2), (4,4,4), (6,2,4), (8,2,2), (8,4), (10,2)], 
				2:[(4,2,6), (4,4,2,2), (4,4,4), (6,6), (6,2,2,2), (6,2,4), (8,2,2), (10,1,1)],
				-2: [(8,4), (10,2)]
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
			chosen_rhythms[rhythm_symbol] for rhythm_symbol in self.rhythm_symbols]
		self.pickup_rhythm = self.finalized_rhythms[7][1:]

		self.logger.warning(f"Finalized rhythms: {self.finalized_rhythms}")
		self.logger.warning("")
		self.logger.warning("")

	def create_melody_options(self):
		"""Use chord progression to layout possible base melody combinations"""

		phrase4_start_index = 12
		phrase2_start_index = 4
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
			elif chord_index >= phrase4_start_index: 
				for scale_degree in current_scale_degrees:
					if scale_degree >= 4:
						self.all_scale_degree_options[-1].append(scale_degree - 7)

		for scale_degrees in self.all_scale_degree_options:
			random.shuffle(scale_degrees)

		self.all_scale_degree_options.extend([[0], [0]])

	def create_first_melody_note(self):
		"""Setup the tonic starting note"""
		self.chord_index = 0
		self.logger.warning(f"Chord index: {self.chord_index}")
		self.logger.warning(f"Current scale degree options {self.current_scale_degree_options}")
		self.current_degree_choice = self.current_scale_degree_options[0].pop()

		self.chosen_scale_degrees[0] = self.current_degree_choice
		self.logger.warning(f"Chosen scale degree: {self.current_degree_choice}")
		if Voice.pickup:
			self.melodic_direction[0] = '>'
		else:
			self.melodic_direction[0] = '_'
		self.logger.warning(f"Melodic direction: {self.melodic_direction}" )

		self.chord_index += 1
		self.current_scale_degree_options[1] = self.all_scale_degree_options[1][:]
		self.previous_degree_choice = self.current_degree_choice
		self.logger.warning("")
		self.logger.warning("")

	def realize_melody(self):
		"""Map out a validated melody while tracking parameters"""
		self.create_melody_options()
		self.current_scale_degree_options[0].extend(self.all_scale_degree_options[0][:])
		self.create_first_melody_note()

		while None in self.chosen_scale_degrees:
			self.logger.warning(f"Chord index: {self.chord_index}")
			self.logger.warning(f"Current scale degree options: {self.current_scale_degree_options}")
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
		"""Reverse to the previous chord to fix bad notes"""
		self.melodic_direction[self.chord_index] = None
		self.chosen_scale_degrees[self.chord_index] = None
		self.chord_index -= 1
		if self.chord_index < 0:
			raise IndexError

		self.previous_degree_choice = self.chosen_scale_degrees[self.chord_index - 1]
		if not self.melody_figure_options[self.chord_index - 1]:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degrees[self.chord_index] = None
		self.nested_scale_degrees[self.chord_index] = []
		self.chosen_figurations[self.chord_index - 1] = None


	def advance_score(self):
		"""Progress to the next chord after current melody is validated"""
		self.logger.warning(f"Melodic direction {self.melodic_direction}")
		self.logger.warning(f"Chosen scale degrees: {self.chosen_scale_degrees}")
		self.logger.warning("")
		self.logger.warning("")
		self.chord_index += 1
		if self.chord_index < len(self.chosen_scale_degrees):
			self.previous_degree_choice = self.current_degree_choice
			self.current_scale_degree_options[self.chord_index] = (
				self.all_scale_degree_options[self.chord_index][:])

	def attempt_melody_figure(self):
		"""Try all remaining melody figures against current base melody"""
		self.logger.warning("Choosing from remaining figures")
		self.logger.warning(f"Remaining melody figures: {self.melody_figure_options}")
		# only occurs when backtracking
		self.current_degree_choice = self.chosen_scale_degrees[self.chord_index]
		self.logger.warning(f"Chosen scale degree: {self.current_degree_choice}")
		self.logger.warning(f"Previous scale degree: {self.previous_degree_choice}")
		self.reset_unnested_melody()
		if self.validate_melody_figure():
			self.advance_score()
		else:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degrees[self.chord_index] = None

	def attempt_full_melody(self):
		"""Try all possible base melodies and figurations"""
		self.logger.warning("Choosing base note")
		self.current_degree_choice = self.current_scale_degree_options[self.chord_index].pop()
		self.logger.warning(f"Chosen scale degree: {self.current_degree_choice}")
		self.logger.warning(f"Previous scale degree: {self.previous_degree_choice}")

		if self.current_degree_choice == self.previous_degree_choice:
			self.melodic_direction[self.chord_index] = '_'
		elif self.current_degree_choice > self.previous_degree_choice:
			self.melodic_direction[self.chord_index] = '>'
		elif self.current_degree_choice < self.previous_degree_choice:
			self.melodic_direction[self.chord_index] = '<'

		self.reset_unnested_melody()

		self.chosen_scale_degrees[self.chord_index] = self.current_degree_choice 
		if self.validate_base_melody() and self.validate_melody_figure():
			self.advance_score()
		else:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degrees[self.chord_index] = None

	def validate_base_melody(self):
		"""Check current base melody against structural idioms"""
		melodic_mvmt = "".join(
			str(slope) for slope in self.melodic_direction[:self.chord_index + 1])

		self.logger.warning(f"Attempted melodic direction: {melodic_mvmt}")
		self.logger.warning(f"Attempted melody: {self.chosen_scale_degrees}")

		if "_" * 3 in melodic_mvmt:
			self.logger.warning("Long rest!")
			self.logger.warning('*' * 30)
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
			if all_rest_indices - {3, 7}:
				self.logger.warning("Triple repeats only between phrases")
				self.logger.warning('*' * 30)
				return False

		relevant_melodic_mvt = melodic_mvmt[1:]
		if ">>>" in relevant_melodic_mvt:
			self.logger.warning("Ascending cascade")
			self.logger.warning('*' * 30)
			return False
		if melodic_mvmt.count('_') > 8:
			self.logger.warning("Too much pause")
			self.logger.warning('*' * 30)
			return False
		if (self.chord_index == 7 and 
		  self.previous_degree_choice != self.current_degree_choice):
			self.logger.warning("Rest halfway through")
			self.logger.warning('*' * 30)
			return False

		if self.chord_index == 1 and self.chosen_scale_degrees[0:2] == [0, 0]:
			self.logger.warning("Must move away from tonic at start")
			self.logger.warning('*' * 30)
			return False	
		
		current_move_distance = self.current_degree_choice - self.previous_degree_choice
		abs_current_move_distance = abs(current_move_distance)
		if abs_current_move_distance > 7:
			self.logger.warning("Leaps within octave")
			self.logger.warning('*' * 30)
			return False
		if self.chord_index == 14:
			if abs_current_move_distance > 4:
				self.logger.warning("Don't end with a leap")
				self.logger.warning('*' * 30)
				return False
			if relevant_melodic_mvt.count('>') > relevant_melodic_mvt.count('<'):
				self.logger.warning("Descending motion should predominate")
				self.logger.warning('*' * 30)
				return False
		if abs_current_move_distance == 7 and self.chord_index not in {4, 8}:
			self.logger.warning("Octave leap can only occur halfway through")
			self.logger.warning('*' * 30)
			return False
		if (len(self.unnested_scale_degrees) >= 3 and 
		  not Voice.has_proper_leaps(self.unnested_scale_degrees)):
			self.logger.warning("Leap should be followed by contrary stepwise motion (full melody)")
			self.logger.warning('*' * 30)
			return False

		# score divides into 4 sections, 16 items
		# first 2 sections: antecedent
		# last 2 sections: consequent
		current_section = self.chord_index // 4
		section_start_index = current_section * 4
		section_scale_degrees = (
			self.chosen_scale_degrees[section_start_index:section_start_index + 4])
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
					if (scale_degree0 == section_max_degree 
					  and scale_degree0 == scale_degree1):
						break 
				else:
					return False 

		section1 = self.chosen_scale_degrees[:4]
		section2 = self.chosen_scale_degrees[4:8]
		if self.chord_index == 8 and max(section1) == max(section2):
			return False
		section3 = self.chosen_scale_degrees[8:12]
		section4 = self.chosen_scale_degrees[12:]
		if self.chord_index == 15 and max(section3) <= max(section4):
			return False

		if self.chosen_figurations[0] == "IN":
			return False

		num_still_figures = self.chosen_figurations.count("CN")
		num_still_figures += self.chosen_figurations.count("DN")
		num_still_figures += self.chosen_figurations.count("DCN")

		if num_still_figures > 2:
			return False

		if self.chord_index >= 3:
			if (self.chord_index not in self.quick_turn_indices and 
			  melodic_mvmt[self.chord_index - 2:] in {"><>", "<><"}):
				self.logger.warning("No late melodic jukes")
				self.logger.warning('*' * 30)
				return False

			if self.chord_index > 8 and Voice.get_turns(self.chosen_scale_degrees[:self.chord_index + 1]) > 8:
				return False

			if Voice.has_cross_duplicates(self.chosen_scale_degrees[:self.chord_index + 1]):
				self.logger.warning("Don't repeat motifs")
				self.logger.warning('*' * 30)
				return False
			# antepenultimate_degree = self.chosen_scale_degrees[self.chord_index - 2]
			# previous_move_distance = self.previous_degree_choice - antepenultimate_degree

			# previous_move_slope =  Voice.calculate_slope(previous_move_distance)
			# current_move_slope = Voice.calculate_slope(current_move_distance)

			# if (abs(previous_move_distance) >= 5 and 
			#   (abs_current_move_distance > 3 or previous_move_slope == current_move_slope)):
			# 	self.logger.warning("Leap should be followed by stepwise motion (base melody)")
			# 	self.logger.warning('*' * 30)
			# 	return False
			# if previous_move_slope == 0 and current_move_slope != 0:
			# 	scale_degree1 = antepenultimate_degree
			# 	for scale_degree0 in self.chosen_scale_degrees[0:self.chord_index - 2][::-1]:
			# 		old_move_distance = scale_degree1 - scale_degree0
			# 		if  0 < abs(old_move_distance) < 5:
			# 			break
			# 		old_move_slope = Voice.calculate_slope(old_move_distance)

			# 		if old_move_slope == current_move_slope:
			# 			self.logger.warning("Leap should be followed by contrary motion")
			# 			self.logger.warning('*' * 30)
			# 			return False
			# 		if old_move_slope == -current_move_slope:
			# 			if abs_current_move_distance > 3:
			# 				self.logger.warning("Leap should be followed by stepwise motion")
			# 				self.logger.warning('*' * 30)
			# 				return False
			# 			break
			# 		scale_degree1 = scale_degree0
		
		return True

	def validate_melody_figure(self):
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
				self.find_pickup_sequences(self.current_degree_choice))
			return self.find_valid_figure()

		remaining_figures = self.melody_figure_options[self.chord_index - 1]
		if remaining_figures:
			self.logger.warning(f"Remaining melody figures: {remaining_figures}")
			return self.find_valid_figure()

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

		self.logger.warning(f"Possible scale degrees: {possible_scale_degrees}")
		self.melody_figure_options[self.chord_index - 1] = possible_scale_degrees
		return self.find_valid_figure()

	def reset_unnested_melody(self):
		"""Create a unnested sequence of the currently approved melody"""
		self.unnested_scale_degrees = []
		for melody_group in self.nested_scale_degrees[:self.chord_index - 1]:
			for melody_note in melody_group:
				self.unnested_scale_degrees.append(melody_note)
		self.unnested_scale_degrees.append(self.previous_degree_choice)

	def find_valid_figure(self):
		valid_figure = None
		remaining_figures = self.melody_figure_options[self.chord_index - 1]

		random.shuffle(remaining_figures)
		# alias has side effect but allows easier referencing
		while remaining_figures:
			inbetween, fig_type = remaining_figures.pop()
			if min(inbetween) < -3 or max(inbetween) > 7:
				continue
			if self.chord_index - 1 < 11 and min(inbetween) < 0:
				continue

			unnested_scalar_melody = self.unnested_scale_degrees[:]
			unnested_scalar_melody.extend(inbetween)
			self.logger.warning(f"Unnested valid melody: {unnested_scalar_melody}")
			if Voice.has_cross_duplicates(unnested_scalar_melody):
				self.logger.warning("Cross duplicates not allowed!")
				self.logger.warning('*' * 30)
				continue

			if self.chord_index == 12 and max(unnested_scalar_melody) < 6:
				continue
			if self.chord_index == 8:
				section1 = Voice.merge_lists(*self.nested_scale_degrees[:4])
				section2 = Voice.merge_lists(*self.nested_scale_degrees[4:8])

				if max(section1) == max(section2):
					continue

			if (self.restart_basic_idea and self.chord_index == 10 and 
			  Voice.chord_sequence[0] == Voice.chord_sequence[8] and 
			  self.nested_scale_degrees[0] != self.nested_scale_degrees[8]):
				self.logger.warning("Must force restart")
				self.logger.warning('*' * 30)
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
		"""Transform scale degrees into midi pitches"""
		
		fifth_degree_pitch = 7 + Voice.tonics[Voice.tonic]
		while fifth_degree_pitch < 45:
			fifth_degree_pitch += 12
		start_index = Voice.all_midi_pitches.index(fifth_degree_pitch)
		self.melody_range = Voice.all_midi_pitches[start_index:start_index + 11]
		self.logger.warning(f"Melody range: {self.melody_range}")

		self.unit_length = sum(self.finalized_rhythms[0])
		if Voice.time_sig in {(4,3), (4,2)}:
			chord_quarter_length = Voice.measure_length // 2
		else:
			chord_quarter_length = Voice.measure_length
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

		if not Voice.repeat_ending:
			self.midi_notes.append(
				Voice.Note("Rest", self.current_time, Voice.max_note_duration))
			self.current_time += Voice.max_note_duration
			self.add_rest_placeholders()
			return

		second_pickup_fraction = Fraction(
			numerator=sum(self.finalized_rhythms[-5][1:]), denominator=self.unit_length)
		second_pickup_duration = int(
			Voice.max_note_duration * second_pickup_fraction)  

		ending_duration = Voice.max_note_duration - second_pickup_duration
		self.midi_notes.append(
			Voice.Note("Rest", self.current_time, ending_duration))

		self.current_time += ending_duration

		remaining_melody = self.nested_scale_degrees[-4:]
		remaining_melody[0] = remaining_melody[0][1:]

		end_notes_num = self.add_midi_section(remaining_melody, -5, {-5: 1})
		self.unnested_scale_degrees.extend(
			self.unnested_scale_degrees[-end_notes_num:])

		self.midi_notes.append(
			Voice.Note("Rest", self.current_time, Voice.max_note_duration))
		self.current_time += Voice.max_note_duration
		self.add_rest_placeholders()

	def add_pickup_notes(self):
		"""Adds pick up notes to beginning and returns the number of added objects"""
		rest_rhythm = self.finalized_rhythms[7][0]
		Voice.pickup_duration = Voice.max_note_duration
		first_scale_degree = self.unnested_scale_degrees[0]

		note_alterations = {}

		rest_fraction = Fraction(
			numerator=rest_rhythm, denominator=self.unit_length)
		rest_duration = int(Voice.pickup_duration * rest_fraction)
		self.midi_notes.append(Voice.Note("Rest", 0, rest_duration))

		self.chord_index = 0
		pickup_degree_sequence, _ = random.choice(
			self.find_pickup_sequences(first_scale_degree))
		current_time = rest_duration

		unnested_scale_degrees = []
		for note_index, note_rhythm in enumerate(self.pickup_rhythm):
			pickup_scale_degree = pickup_degree_sequence[note_index]
			note_offset = note_alterations.get(pickup_scale_degree % 7, 0)
			midi_pitch = self.melody_range[pickup_scale_degree + 3] + note_offset

			embellish_fraction = Fraction(
				numerator=note_rhythm, denominator=self.unit_length)
			note_duration = int(Voice.pickup_duration * embellish_fraction)
			self.midi_notes.append(
				Voice.Note(midi_pitch, current_time, note_duration))
			unnested_scale_degrees.append(pickup_scale_degree)

			current_time += note_duration

		unnested_scale_degrees.extend(self.unnested_scale_degrees)
		self.unnested_scale_degrees = unnested_scale_degrees

		return len(self.pickup_rhythm)

	def find_pickup_sequences(self, centered_degree):
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

			pickup_scale_options[-1].append(None)

		return pickup_scale_options

	def add_midi_section(
	  self, melody_section, chord_start_index, note_start_indices, index_shift=None):
		"""Add selected midi notes to a sequence using scale degrees"""
		object_index = 0
		melodic_minor = False
		add_rest = False

		for chord_index, scale_group in enumerate(melody_section, chord_start_index):

			chord_name = Voice.chord_sequence[chord_index].chord_name
			if Voice.mode == "ionian" and chord_name in Chord.major_mode_alterations:
				note_alterations = Chord.major_mode_alterations[chord_name]
			elif Voice.mode == "aeolian" and chord_name in Chord.minor_mode_alterations:
				note_alterations = Chord.minor_mode_alterations[chord_name]
			else: 
				note_alterations = {}
				
			if Voice.mode == "aeolian" and chord_name in Voice.dominant_harmony:
				# doesn't count melodic minor if between >= 2 chords
				if melodic_minor: 
					note_alterations[5] = 1 
				else:
					scale_group_str = "".join(str(scale_degree) for scale_degree in scale_group)
					if any(
					  str_combo in scale_group_str 
					  for str_combo in ("56", "65", "-1-2", "-2-1")):
						melodic_minor = True
						note_alterations[5] = 1
						print("Melodic minor!")

			for embellish_index, scale_degree in enumerate(
			  scale_group, note_start_indices.get(chord_index, 0)):
				embellish_duration = self.finalized_rhythms[chord_index][embellish_index]
				# account for negative scale degrees
				note_offset = note_alterations.get(scale_degree % 7, 0)
				embellish_fraction = Fraction(numerator=embellish_duration, denominator=self.unit_length)

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
						Voice.Note("Rest", self.current_time, fixed_note_duration))
					# needed all numbers in unnested sequence for validation
					self.unnested_scale_degrees.pop(object_index + index_shift)
				else:
					self.midi_notes.append(
						Voice.Note(midi_pitch, self.current_time, fixed_note_duration))
					if add_rest:
						self.midi_notes.append(
							Voice.Note("Rest", self.current_time + 960, extra_duration))

				self.current_time += raw_note_duration
				add_rest = False
				object_index += 1

		return object_index

	def add_rest_placeholders(self):
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














