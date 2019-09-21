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
		melody_handler = logging.FileHandler("melody.log", mode='w')
		melody_handler.setLevel(logging.WARNING)
		melody_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		melody_handler.setFormatter(melody_format)
		self.logger.addHandler(melody_handler)

		Voice.mode = random.choice(("ionian", "aeolian"))
		if Voice.mode == "ionian":
			import generate.idioms.major
			Voice.idms_mode = generate.idioms.major
		elif Voice.mode == "aeolian":
			import generate.idioms.minor
			Voice.idms_mode = generate.idioms.minor

		time_sig = random.choice(idms_b.time_sigs)
		Voice.tonic = random.choice(self.idms_mode.key_sigs)
		self.logger.warning(f"{Voice.tonic} {Voice.mode}")
		Voice.measure_length = time_sig[0]
		Voice.beat_division = time_sig[1]
		self.logger.warning(f"{Voice.measure_length} beats divided in {Voice.beat_division}")

		self.quick_turn_indices = {2, 5, 6, 9, 10, 13}
		self.rhythm_symbols = [None for _ in range(16)]
		self.finalized_rhythms = {}
		self.nested_full_melody = []
		self.unnested_full_melody = []
		self.midi_melody = []

		self.all_scale_degree_options = []
		self.melodic_direction = []
		self.chosen_scale_degress = []
		self.current_scale_degree_options = []
		self.melody_figure_options = []

		self.all_single_figurations = {
			0: lambda previous, current, slope: [[current - 1], [current + 1]],
			1: lambda previous, current, slope: [[current + slope]],
			2: lambda previous, current, slope: [[previous + slope], [current + slope]],
			3: lambda previous, current, slope: [
				[previous + slope], [previous + slope * 2], [current + slope]],
			4: lambda previous, current, slope: [
				[previous + slope * 2], [current + slope]],
			5: lambda previous, current, slope: [
				[previous + slope * 2], [previous + slope * 3]],
			6: lambda previous, current, slope: [[current + slope]]
		}

		self.all_double_figurations = {
			0: lambda previous, current, slope: [
				[current - 1, current + 1], [current + 1, current - 1],
				[current, current]],
			1: lambda previous, current, slope: [
				[previous - slope, previous], 
				[current + slope, current + slope]],
			2: lambda previous, current, slope: [
				[current + slope * 2, current + slope],
				[previous + slope, previous + slope], 
				[current + slope, current + slope]],
			3: lambda previous, current, slope: [
				[previous + slope, previous + slope * 2], 
				[current + slope, current + slope]],
			4: lambda previous, current, slope: [
				[previous + slope * 2, previous + slope * 3], 
				[previous + slope, previous + slope * 3],
				[previous + slope * 2, previous + slope * 2]],
			5: lambda previous, current, slope: [
				[previous + slope * 2, previous + slope * 4],
				[previous + slope * 2, previous + slope * 2],
				[previous + slope * 3, previous + slope * 3]],
			6: lambda previous, current, slope: [
				[current + slope, current + slope]]
		}

	def set_unnested_full_melody(self):
		"""Create a unnested sequence of the currently approved melody"""
		self.unnested_full_melody = []
		for melody_group in self.nested_full_melody[:self.chord_index - 1]:
			for melody_note in melody_group:
				self.unnested_full_melody.append(melody_note)
		self.unnested_full_melody.append(self.previous_degree_choice)

	def make_melody(self):
		"""Make a random melody from a randomly selected chord progression"""
		self.set_scale_midi_pitches()
		self.make_chord_progression()
		self.create_rhythm()
		self.realize_melody()
		self.plot_midi_notes()
		return self.midi_melody

	def set_scale_midi_pitches(self):
		"""Choose all midi pitches that are diatonic to the key signature"""
		current_pitch = -12
		root_pitch = current_pitch + Voice.tonics[Voice.tonic]
		scale_sequence = Voice.mode_notes[Voice.mode][:7]

		all_midi_pitches = []
		while current_pitch < 128:
			for chromatic_shift in scale_sequence:
				current_pitch = root_pitch + chromatic_shift
				all_midi_pitches.append(current_pitch)
			root_pitch += 12

		Voice.all_midi_pitches = [
			midi_pitch for midi_pitch in all_midi_pitches if 0 <= midi_pitch <= 127]

		self.logger.warning(f"All midi pitches: {Voice.all_midi_pitches}")
		self.logger.warning("")

	def make_chord_progression(self):
		"""Make a chord progression using common practice idioms"""
		chord_structure = random.choice(idms_b.chord_patterns_16)
		self.logger.warning(f"{chord_structure}")
		chord_str_sequence = []
		if chord_structure[0] == "TON":
			chord_str_sequence.append("0I")

		for chord_pattern in chord_structure[1:]:
			if chord_pattern == "RPT":
				chord_str_sequence.append(chord_str_sequence[-1])
			else:
				chord_choices = Voice.idms_mode.chord_ids[chord_pattern]
				chord_str_sequence.append(
					random.choice(chord_choices[chord_str_sequence[-1]]))

		self.logger.warning(f"{chord_str_sequence}")
		self.logger.warning("")

		for current_chord_str in chord_str_sequence:
			Voice.chord_sequence.append(Chord(current_chord_str))

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
		self.logger.warning(f"Rhythm symbols: {self.rhythm_symbols}")

		if Voice.beat_division == 2:
			rhythm_mapping = {
				-1: [(8,)], 0: [(4,4), (6,2)], 1: [(4,4), (6,2)], 
				2: [(3,3,2), (6,1,1)]
				}
		elif Voice.beat_division == 3:
			rhythm_mapping = {
				-1: [(12,)], 0: [(8,4), (10, 2)], 1: [(8,4), (10, 2)],
				2: [(10,2), (6,2,4), (4,2,6), (6,4,2), (8,2,2), (10, 1, 1), (6,6), (4,4,4)]
			}

		chosen_rhythms = {}
		for rhythm_symbol in set(self.rhythm_symbols):
			possible_rhythms = rhythm_mapping[rhythm_symbol]
			random.shuffle(possible_rhythms)
			while True:
				chosen_rhythm = possible_rhythms.pop()
				if chosen_rhythm not in chosen_rhythms.values():
					chosen_rhythms[rhythm_symbol] = chosen_rhythm
					break

		self.logger.warning(f"Chosen rhythms: {chosen_rhythms}")

		self.finalized_rhythms = [
			chosen_rhythms[rhythm_symbol] for rhythm_symbol in self.rhythm_symbols]

		self.logger.warning(f"Finalized rhythms: {self.finalized_rhythms}")
		self.logger.warning("")
		self.logger.warning("")

	def create_melody_options(self):
		"""Use chord progression to layout possible base melody combinations"""

		phrase4_start_index = 12
		phrase2_start_index = 4
		include_octave = random.choice((True, False))
		if Voice.chord_sequence[0].chord_symbol == "0I":
			self.all_scale_degree_options.append([0, 2, 4])
		# separate first note to allow irregular starts e.g., major 2nd
		for chord_index, chord_obj in enumerate(Voice.chord_sequence[1:-2], 1):
			current_scale_degrees = chord_obj.scale_degrees
			self.all_scale_degree_options.append([])
			self.all_scale_degree_options[-1].extend(current_scale_degrees)
			if phrase2_start_index <= chord_index < phrase4_start_index:
				if include_octave and 0 in self.all_scale_degree_options[-1]:
					self.all_scale_degree_options[-1].append(7)

			elif chord_index >= phrase4_start_index: 
				for scale_degree in current_scale_degrees:
					if scale_degree >= 4:
						self.all_scale_degree_options[-1].append(scale_degree - 7)

		for scale_degrees in self.all_scale_degree_options:
			random.shuffle(scale_degrees)

		self.all_scale_degree_options.extend([[0], [0]])

	def setup_melody_parameters(self):
		"""Create sequences to track while validating a melody"""

		self.melodic_direction = [None for _ in range(16)]
		self.chosen_scale_degress = [None for _ in range(16)]
		self.current_scale_degree_options = [[] for _ in range(16)]
		self.current_scale_degree_options[0].extend(self.all_scale_degree_options[0][:])
		self.melody_figure_options = [[] for _ in range(16)]
		self.nested_full_melody = [[] for _ in range(16)]

	def create_first_melody_note(self):
		"""Setup the tonic starting note"""
		self.chord_index = 0
		self.logger.warning(f"Chord index: {self.chord_index}")
		self.logger.warning(f"Current scale degree options {self.current_scale_degree_options}")
		self.current_degree_choice = self.current_scale_degree_options[0].pop()

		self.chosen_scale_degress[0] = self.current_degree_choice
		self.logger.warning(f"Chosen scale degree: {self.current_degree_choice}")
		# designates pickup note
		self.melodic_direction[0] = random.choice(('_', '>'))
		self.logger.warning(f"Melodic direction: {self.melodic_direction}" )

		self.chord_index += 1
		self.current_scale_degree_options[1] = self.all_scale_degree_options[1][:]
		self.previous_degree_choice = self.current_degree_choice
		self.logger.warning("")
		self.logger.warning("")

	def realize_melody(self):
		"""Create a melody based on selected rhythm and chords"""
		self.create_melody_options()
		self.setup_melody_parameters()
		self.create_first_melody_note()

		while None in self.chosen_scale_degress:
			self.logger.warning(f"Chord index: {self.chord_index}")
			self.logger.warning(f"Current scale degree options: {self.current_scale_degree_options}")
			if self.melody_figure_options[self.chord_index - 1]:
				self.attempt_melody_figure()
			elif self.current_scale_degree_options[self.chord_index]:
				self.attempt_full_melody()
			else:
				self.backtrack_score()

		self.nested_full_melody[-1] = [self.current_degree_choice]

	def backtrack_score(self):
		"""Reverse to the previous chord to fix bad notes"""
		self.melodic_direction[self.chord_index] = None
		self.chosen_scale_degress[self.chord_index] = None
		self.chord_index -= 1
		if self.chord_index < 0:
			raise IndexError
		self.previous_degree_choice = self.chosen_scale_degress[self.chord_index - 1]
		if not self.melody_figure_options[self.chord_index - 1]:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degress[self.chord_index] = None

	def advance_score(self):
		"""Progress to the next chord after current melody is validated"""
		self.logger.warning(f"Melodic direction {self.melodic_direction}")
		self.logger.warning(f"Chosen scale degrees: {self.chosen_scale_degress}")
		self.logger.warning("")
		self.logger.warning("")
		self.chord_index += 1
		if self.chord_index < len(self.chosen_scale_degress):
			self.previous_degree_choice = self.current_degree_choice
			self.current_scale_degree_options[self.chord_index] = (
				self.all_scale_degree_options[self.chord_index][:])

	def attempt_melody_figure(self):
		"""Try all remaining melody figures against current base melody"""
		self.logger.warning("Choosing from remaining figures")
		self.logger.warning(f"Remaining melody figures: {self.melody_figure_options}")
		# only occurs when backtracking
		self.current_degree_choice = self.chosen_scale_degress[self.chord_index]
		self.logger.warning(f"Chosen scale degree: {self.current_degree_choice}")
		self.logger.warning(f"Previous scale degree: {self.previous_degree_choice}")
		if self.validate_melody_figure():
			self.advance_score()
		else:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degress[self.chord_index] = None

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

		self.chosen_scale_degress[self.chord_index] = self.current_degree_choice 
		if self.validate_base_melody() and self.validate_melody_figure():
			self.advance_score()
		else:
			self.melodic_direction[self.chord_index] = None
			self.chosen_scale_degress[self.chord_index] = None

	def validate_base_melody(self):
		melodic_mvmt = "".join([
			str(slope) for slope in self.melodic_direction[:self.chord_index + 1]])

		self.logger.warning(f"Attempted melodic direction: {melodic_mvmt}")
		self.logger.warning(f"Attempted melody: {self.chosen_scale_degress}")

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

		highest_scale_degree = max(self.chosen_scale_degress[:self.chord_index + 1])
		if (highest_scale_degree > 4 and 
		  self.chosen_scale_degress.count(highest_scale_degree) > 2):
			self.logger.warning("Too much climax")
			self.logger.warning('*' * 30)
			return False
		if highest_scale_degree in self.chosen_scale_degress[12:]:
			self.logger.warning("No climax at ending")
			self.logger.warning('*' * 30)
			return False

		if self.chord_index == 1 and self.chosen_scale_degress[0:2] == [0, 0]:
			self.logger.warning("Must move away from tonic at start")
			self.logger.warning('*' * 30)
			return False	
		
		if (self.chord_index >= 3 and self.chord_index not in self.quick_turn_indices 
			and melodic_mvmt[self.chord_index - 2:] in {"><>", "<><"}):
			self.logger.warning("No late melodic jukes")
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
		if self.chord_index >= 3:
			if (self.chosen_scale_degress[self.chord_index - 1:self.chord_index + 1] == 
			  self.chosen_scale_degress[self.chord_index - 3:self.chord_index - 1]):
				self.logger.warning("Don't repeat motifs")
				self.logger.warning('*' * 30)
				return False
			antepenultimate_degree = self.chosen_scale_degress[self.chord_index - 2]
			previous_move_distance = self.previous_degree_choice - antepenultimate_degree

			previous_move_slope =  self.calculate_slope(previous_move_distance)
			current_move_slope = self.calculate_slope(current_move_distance)

			if (abs(previous_move_distance) >= 5 and 
			  (abs_current_move_distance > 3 or previous_move_slope == current_move_slope)):
				self.logger.warning("Leap should be followed by stepwise motion")
				self.logger.warning('*' * 30)
				return False
			if previous_move_slope == 0 and current_move_slope != 0:
				scale_degree1 = antepenultimate_degree
				for scale_degree0 in self.chosen_scale_degress[0:self.chord_index - 2][::-1]:
					old_move_distance = scale_degree1 - scale_degree0
					if  0 < abs(old_move_distance) < 5:
						break
					old_move_slope = self.calculate_slope(old_move_distance)

					if old_move_slope == current_move_slope:
						self.logger.warning("Leap should be followed by contrary motion")
						self.logger.warning('*' * 30)
						return False
					if old_move_slope == -current_move_slope:
						if abs_current_move_distance > 3:
							self.logger.warning("Leap should be followed by stepwise motion")
							self.logger.warning('*' * 30)
							return False
						break
					scale_degree1 = scale_degree0
		
		return True

	def validate_melody_figure(self):
		if self.chord_index == 15:
			self.nested_full_melody[self.chord_index - 1] = [self.previous_degree_choice]
			return True

		remaining_figures = self.melody_figure_options[self.chord_index - 1]
		if remaining_figures:
			self.logger.warning(f"Remaining melody figures: {remaining_figures}")
			return self.find_valid_figure()

		degree_mvmt = self.current_degree_choice - self.previous_degree_choice
		melody_slope = self.calculate_slope(degree_mvmt)
		degree_mvmt = abs(degree_mvmt)

		if self.rhythm_symbols[self.chord_index - 1] == -1:
			self.nested_full_melody[self.chord_index - 1] = [self.previous_degree_choice]
			return True

		embellish_amount = len(self.finalized_rhythms[self.chord_index - 1])
		if embellish_amount == 2:
			all_figurations = self.all_single_figurations
		elif embellish_amount == 3:
			all_figurations = self.all_double_figurations
		possible_scale_degrees = all_figurations[degree_mvmt](
			self.previous_degree_choice, self.current_degree_choice, melody_slope)

		self.logger.warning(f"Possible scale degrees: {possible_scale_degrees}")
		self.melody_figure_options[self.chord_index - 1] = possible_scale_degrees
		return self.find_valid_figure()

	def find_valid_figure(self):
		valid_figure = None
		self.set_unnested_full_melody()
		remaining_figures = self.melody_figure_options[self.chord_index - 1]
		# alias has side effect but allows easier referencing
		while remaining_figures:
			inbetween = remaining_figures.pop()
			if min(inbetween) < -3 or max(inbetween) > 7:
				continue
			if self.chord_index - 1 < 11 and min(inbetween) < 0:
				continue

			unnested_full_melody = self.unnested_full_melody[:]
			unnested_full_melody.extend(inbetween)
			self.logger.warning(f"Unnested valid melody: {unnested_full_melody}")
			if Voice.has_cross_duplicates(unnested_full_melody):
				self.logger.warning("Cross duplicates not allowed!")
				self.logger.warning('*' * 30)
				continue

			highest_scale_degree = max(unnested_full_melody)
			if (highest_scale_degree > 4 and 
			  unnested_full_melody.count(highest_scale_degree) > 2):
				self.logger.warning("Avoid multiple climaxes")
				self.logger.warning('*' * 30)
				continue

			# you can repeat motifs but only in symmetrical positions

			# twist_notes = []
			# triple_motifs_set = set()
			# full_melody_str = "".join([str(note) for note in unnested_full_melody])
			# for note1, note2, note3 in zip(
			#   unnested_full_melody, unnested_full_melody[1:], unnested_full_melody[2:]):
			# 	new_triple_motif = (note1, note2, note3)
			# 	if new_triple_motif in triple_motifs_set:
			# 		break
			# 	triple_motifs_set.add(new_triple_motif)
			# 	if note1 == note3 and note1 != note2:
			# 		twist_group = [str(note1), str(note2)]
			# 		twist_group.sort()
			# 		if twist_group not in twist_notes:
			# 			twist_notes.append(twist_group)

			# 			self.logger.warning(f"Twist notes: {twist_notes}")
			# 			if len(twist_notes) > 1:
			# 				self.logger.warning(f"Multiple twists not allowed")
			# 				self.logger.warning('*' * 30)
			# 				break
			# 			forward_twist = "".join([*twist_group, twist_group[0]])
			# 			backward_twist = "".join([twist_group[1], *twist_group])
			# 			twist_count = full_melody_str.count(forward_twist)
			# 			twist_count += full_melody_str.count(backward_twist)
			# 			if twist_count >= 2:
			# 				self.logger.warning(f"No twisting melody")
			# 				self.logger.warning('*' * 30)
			# 				break
			# else:
			# 	valid_figure = inbetween
			# 	break

			valid_figure = inbetween
			break


		if valid_figure is None:
			self.logger.warning("Melody failed")
			return False
		self.nested_full_melody[self.chord_index - 1] = [
				self.previous_degree_choice, *valid_figure]
		self.logger.warning(f"Nested valid melody: {self.nested_full_melody}")
		return True

	def plot_midi_notes(self):
		"""Transform scale degrees into midi pitches"""
		
		fifth_degree_pitch = 7 + Voice.tonics[Voice.tonic]
		while fifth_degree_pitch < 45:
			fifth_degree_pitch += 12
		start_index = Voice.all_midi_pitches.index(fifth_degree_pitch)
		melody_range = Voice.all_midi_pitches[start_index:start_index + 11]
		self.logger.warning(f"Melody range: {melody_range}")

		current_time = 0
		if Voice.beat_division == 2:
			unit_length = 8
		elif Voice.beat_division == 3:
			unit_length = 12
		if Voice.measure_length in {2, 4}:
			chord_quarter_length = 2
		elif Voice.measure_length == 3:
			chord_quarter_length = 3

		chord_index = 0
		self.logger.warning(f"Beat division: {Voice.beat_division}")
		self.logger.warning(f"Measure length: {Voice.measure_length}")
		self.logger.warning(f"Unit length: {unit_length}")
		self.logger.warning(f"Chord quarter length: {chord_quarter_length}")
		for scale_group in self.nested_full_melody:
			for embellish_index, scale_pitch in enumerate(scale_group):
				embellish_duration = self.finalized_rhythms[chord_index][embellish_index]
				if Voice.mode == "aeolian" and scale_pitch in {6, -1}:
					offset = 1
				else:
					offset = 0
				embellish_fraction = Fraction(numerator=embellish_duration, denominator=unit_length)

				raw_note_duration = 960 * chord_quarter_length * embellish_fraction

				if raw_note_duration > 960 and self.rhythm_symbols[chord_index] != -1:
					fixed_note_duration = 960
				else:
					fixed_note_duration = raw_note_duration
				midi_pitch = melody_range[scale_pitch + 3]
				self.midi_melody.append(
					Voice.Note(midi_pitch + offset, int(current_time), int(fixed_note_duration)))
				current_time += raw_note_duration
			chord_index += 1

		self.logger.warning(f"Midi melody: {self.midi_melody}")













