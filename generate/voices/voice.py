import collections
from fractions import Fraction

class Voice:

	chord_sequence = []
	mode = None
	idms_mode = None
	tonic = None
	pickup = False
	repeat_ending = False
	all_midi_pitches = []

	chord_acceleration = False

	Note = collections.namedtuple('Note', ["pitch", "time", "duration"])
	midi_score = []
	lily_score = []
	chorale_scale_degrees = []
	dominant_harmony = {"V", "V7", "V6", "V65", "VII6", "V43", "V42"}

	beat_division = 0
	measure_length = 0
	pickup_duration = 0
	max_note_duration = 0
	time_sig = (4, 2)
	voice_volumes = (70, 50, 50, 50)

	bass_motion = []
	tenor_motion = []
	alto_motion = []
	soprano_motion = []

	mode_notes = {
		"lydian": (0, 2, 4, 6, 7, 9, 11),
		"ionian": (0, 2, 4, 5, 7, 9, 11),
		"mixo": (0, 2, 4, 5, 7, 9, 10),
		"dorian": (0, 2, 3, 5, 7, 9, 10),
		"aeolian": (0, 2, 3, 5, 7, 8, 10),
		"phryg": (0, 1, 3, 5, 7, 8, 10) 
	}
	tonics = {
		"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
		"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
	}

	note_letters = ("C","D","E","F","G","A","B")

	note_names = (
		("B#","C","Dbb"), ("B##","C#", "Db"), ("C##", "D", "Ebb"), ("D#","Eb"),
		("D##","E","Fb"), ("E#","F","Gbb"), ("E##","F#", "Gb"), ("F##","G","Abb"), 
		("G#", "Ab"), ("G##","A","Bbb"), ("A#","Bb","Cbb"), ("A##","B","Cb"), 
	)

	simple_beat_durations = {
		4: "1", 3: "2.", 2: "2", 1.5: "4.", 1: "4", 0.75: "8.",
		0.5: "8", 0.375: "16.", 0.25: "16", 0.125: "32", 
	}
	compound_beat_durations = {
		4: "1.", Fraction("8/3"): "4", 2: "2.", Fraction("4/3"):"2", 1: "4.",   
		Fraction("2/3"): "4", 0.5: "8.", Fraction("1/3"): "8", 
		Fraction("1/6"): "16"  
	}
	beat_durations = {}
	interval_names = {
		(0,0): "P8", (0,1): "d2", (1,0): "A1", (1,1): "m2", (2,1): "M2", (2,2): "d3",
		(3,1): "A2", (3,2): "m3", (4,2): "M3", (4,3): "d4", (5,2): "A3", (5,3): "P4",
		(6,3): "A4", (6,4): "d5", (7,4): "P5", (7,5): "d6", (8,4): "A5", (8,5): "m6",
		(9,5): "M6", (9,6): "d7", (10,5): "A6", (10,6): "m7", (11,6): "M7", 
		(11,7): "d8", (0,6): "A7", (11,0): "d8"
	}

	@staticmethod
	def calculate_slope(move_distance):
		"""Discerns negative and positive numbers"""
		if move_distance < 0:
			return -1
		elif move_distance > 0:
			return 1
		return 0

	@staticmethod
	def has_cross_duplicates(sequence):
		"""Determines any two items of the sequence immediately repeats themselves"""
		item1 = None
		item2 = None
		item3 = None
		item4 = None
		for index, current_value in enumerate(sequence):
			if item4 != current_value:
				item1, item2, item3 = item2, item3, item4
				item4 = current_value

				if (item1, item2) == (item3, item4):
					return True

		return False

	@staticmethod
	def get_turns(sequence):
		"""Returns the number of times the direction of a sequence changes"""
		search_slope = 0
		turns = 0
		iter_sequence = iter(sequence)
		old_item = next(iter_sequence, None)
		new_item = next(iter_sequence, None)
		while new_item is not None:
			current_slope = Voice.calculate_slope(new_item - old_item)

			if 0 != current_slope != search_slope:
				turns += 1 
				search_slope = current_slope

			old_item = new_item
			new_item = next(iter_sequence, None)
		return turns

	@staticmethod
	def has_proper_leaps(sequence):
		"""Check for contrary stepwise motion following leaps"""
		current_leap_slope = None
		current_move_slope = None
		previous_degree_mvmt = 0
		for scale_degree0, scale_degree1 in zip(sequence, sequence[1:]):
			current_degree_mvmt = scale_degree1 - scale_degree0
			current_move_slope = Voice.calculate_slope(current_degree_mvmt)

			if current_leap_slope == current_move_slope:
				return False
			if current_leap_slope == -current_move_slope:
				if abs(current_degree_mvmt) > 1:
					return False
				current_leap_slope = None
			elif abs(current_degree_mvmt) > 2:
				current_leap_slope = current_move_slope

			previous_degree_mvmt = current_degree_mvmt

		return True

	@staticmethod
	def partition_rhythm(beat_durations, object_duration):
		"""Split a complex beat duration into simpler durations"""
		rhythm_partitions = []
		remaining_rhythm = object_duration
		for current_rhythm in beat_durations:
			if current_rhythm <= remaining_rhythm:
				rhythm_partitions.append(current_rhythm)
				remaining_rhythm -= current_rhythm
			if remaining_rhythm == 0:
				return rhythm_partitions

	@staticmethod
	def merge_lists(*args):
	    """Shallow adding of lists"""
	    result_list = []
	    for selected_list in args:
	        result_list.extend(selected_list)

	    return result_list

	@staticmethod
	def get_item_lengths(sequence):
		return [len(item) for item in sequence]

	@staticmethod
	def accumulate_product(sequence):
		total = 1
		for amount in sequence:
			total *= amount
		return total

	@staticmethod
	def split_combo_amounts(sequence):
		split_amounts = []
		for item_index, outer_num in enumerate(sequence[:-1]):
			total = 1
			for inner_count in sequence[item_index + 1:]:
				total *= inner_count
			split_amounts.append(total)

		return split_amounts

	def set_sheet_notes(self):
		"""Convert midi pitches into sheet music note names"""

		tonic_letter = Voice.tonic.replace('#',"").replace('b',"")
		tonic_index = Voice.note_letters.index(tonic_letter)

		self.logger.warning(len(self.midi_notes))
		self.logger.warning(len(self.unnested_scale_degrees))

		for midi_note, scale_degree in zip(
		  self.midi_notes, self.unnested_scale_degrees):
			self.logger.warning(midi_note)
			self.logger.warning(scale_degree)
			if scale_degree is None:
				self.sheet_notes.append(None)
				continue
			true_midi_pitch = midi_note.pitch
			scale_midi_pitch =  true_midi_pitch % 12
			possible_note_names = Voice.note_names[scale_midi_pitch]

			note_letter_index = (tonic_index + scale_degree) % 7
			note_letter = Voice.note_letters[note_letter_index]
			octave = true_midi_pitch // 12 - 1

			for possible_note_name in possible_note_names:
				if note_letter in possible_note_name:
					self.sheet_notes.append(f"{possible_note_name}{octave}")
					break

		self.logger.warning(f"Sheet notes: {self.sheet_notes}")

	def make_lily_part(self):
		"""Write sheet music text notation for voice part"""

		object_index = 0
		if Voice.pickup:
			object_duration = Voice.pickup_duration // 960
			lily_part = [f"\\partial {Voice.beat_durations[object_duration]}"]
		else:
			lily_part = []

		for midi_note, sheet_note in zip(self.midi_notes, self.sheet_notes):
			self.logger.warning(midi_note)
			self.logger.warning(sheet_note)
			self.logger.warning(object_index)

			object_duration = Fraction(numerator=midi_note.duration, denominator=960)
			object_rhythm = Voice.partition_rhythm(
				Voice.beat_durations, object_duration)
			if sheet_note is None:
				lily_rest = ""
				for rest_part in object_rhythm[:-1]:
					lily_rest = "".join([
						lily_rest, "r", Voice.beat_durations[rest_part], " "])

				lily_rest = "".join([
					lily_rest, "r", Voice.beat_durations[object_rhythm[-1]]])

				lily_part.append(lily_rest)
				continue

			accidental_mark = ""
			octave_mark = ""
			note_letter = sheet_note[0].lower()
			register_shift = 0

			# B# is technically in the octave above (starting from C)
			# Cb is technically in the octave below
			if sheet_note.startswith(("B#","B##")):
				register_shift = -1
			elif sheet_note.startswith(("Cb","Cbb")):
				register_shift = 1
			octave = int(sheet_note[-1]) + register_shift
			if octave < 3:
				octave_shift = 3 - octave
				octave_mark = str(octave_shift * ',')
			elif octave > 3:
				octave_shift = octave - 3
				octave_mark = str(octave_shift * "'")
			if '#' in sheet_note or 'b' in sheet_note:
				accidental = sheet_note[1]
				if accidental == '#':
					accidental_amount = sheet_note.count('#')
					accidental_mark = "is" * accidental_amount
				elif accidental == 'b':
					accidental_amount = sheet_note.count('b')
					accidental_mark = "es" * accidental_amount

			lily_note = ""
			for beat_part in object_rhythm[:-1]:
				lily_note = "".join([
					lily_note, note_letter, accidental_mark, octave_mark,
					Voice.beat_durations[beat_part], "~ "])

			lily_note = "".join([
				lily_note, note_letter, accidental_mark, octave_mark, 
				Voice.beat_durations[object_rhythm[-1]]])

			lily_part.append(lily_note)
			object_index += 1

		lily_string = " ".join(note for note in lily_part) 
		Voice.lily_score.append(lily_string)
		self.logger.warning(f"Lily part: {lily_part}")

	def get_interval(self, old_pitch, new_pitch, current_pitches_dict):
		"""Returns the specific interval of two pitches"""
		pitch_diff = new_pitch - old_pitch
		chromatic_diff = pitch_diff % 12

		old_degree = current_pitches_dict[old_pitch]
		new_degree = current_pitches_dict[new_pitch]

		generic_interval = new_degree - old_degree
		if generic_interval < 0:
			generic_interval += 7

		return Voice.interval_names[(chromatic_diff, generic_interval)]

	def add_voice_motion(self, voice_motion, new_pitch, voice_index):
		old_pitch = self.chosen_chord_voicings[self.chord_index - 1][voice_index]
		if new_pitch < old_pitch:
			voice_motion.append(-1)
		elif new_pitch > old_pitch:
			voice_motion.append(1)
		else:
			voice_motion.append(0)

	def add_motion_type(self, old_motion, new_motion, movements, intervals):
		old_move = old_motion[-1]
		new_move = new_motion[-1]
		if (old_move == new_move and old_move != 0 and 
		  intervals[-1] == intervals[-2]):
			movements.append("Parallel")
		elif old_move == new_move and old_move == 0:
			movements.append("No motion")
		elif old_move == -(new_move):
			movements.append("Contrary")
		elif (old_move == new_move and intervals[-1] != intervals[-2]):
			movements.append("Similar")
		elif ((old_move == 0 or new_move == 0) and 
		  (old_move != 0 or new_move != 0)):
			movements.append("Oblique")
		else:
			raise ValueError("Invalid motion")

	def create_part(self):
		self.set_sheet_notes()
		self.make_lily_part()




