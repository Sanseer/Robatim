import collections
from fractions import Fraction
import itertools

from generate.idioms.score import Score

class Voice(Score):

	chord_sequence = []
	pickup = False
	all_midi_pitches = []
	chord_acceleration = False

	Note = collections.namedtuple('Note', ["pitch", "time", "duration"])
	midi_score = []
	lily_score = []
	chorale_scale_degrees = []

	pickup_duration = 0
	max_note_duration = 0
	voice_volumes = (70, 50, 50, 50)

	bass_motion = []
	tenor_motion = []
	alto_motion = []
	soprano_motion = []

	interval_names = {
		(0,0): "P8", (0,1): "d2", (1,0): "A1", (1,1): "m2", (2,1): "M2", 
		(2,2): "d3", (3,1): "A2", (3,2): "m3", (4,2): "M3", (4,3): "d4", 
		(5,2): "A3", (5,3): "P4", (6,3): "A4", (6,4): "d5", (7,4): "P5", 
		(7,5): "d6", (8,4): "A5", (8,5): "m6", (9,5): "M6", (9,6): "d7", 
		(10,5): "A6", (10,6): "m7", (11,6): "M7", (11,7): "d8", (0,6): "A7", 
		(11,0): "d8",
	}
	leading_degrees = {
		"V/V": 3, "V7/V": 3, "V6/V": 3, "V65/V": 3, "V43/V": 3, "VII6/V": 3, 
		"V42/V": 3, "V/III": 1,"V7/III": 1,"V6/III": 1, "V65/III": 1, 
		"V43/III": 1, "VII6/III": 1,
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

	@classmethod
	def get_turns(cls, sequence):
		"""Returns the number of times the direction of a sequence changes"""
		search_slope = 0
		turns = 0
		iter_sequence = iter(sequence)
		old_item = next(iter_sequence, None)
		new_item = next(iter_sequence, None)
		while new_item is not None:
			current_slope = cls.calculate_slope(new_item - old_item)

			if 0 != current_slope != search_slope:
				turns += 1 
				search_slope = current_slope

			old_item = new_item
			new_item = next(iter_sequence, None)
		return turns

	@classmethod
	def has_proper_leaps(cls, sequence):
		"""Check for contrary stepwise motion following leaps"""
		current_leap_slope = None
		current_move_slope = None
		previous_degree_mvmt = 0
		for scale_degree0, scale_degree1 in zip(sequence, sequence[1:]):
			current_degree_mvmt = scale_degree1 - scale_degree0
			current_move_slope = cls.calculate_slope(current_degree_mvmt)

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

	@classmethod
	def make_pitch_combos(cls, current_chord_obj):
		"""Generates voicing combinations for a given chord"""
		current_pitches_dict = current_chord_obj.pitches_to_degrees
		possible_midi_pitches = [[] for _ in range(4)]
		for midi_pitch in current_pitches_dict:
			if 40 <= midi_pitch <= 60:
				possible_midi_pitches[0].append(midi_pitch)
			if 48 <= midi_pitch <= 67:
				possible_midi_pitches[1].append(midi_pitch)
			if 55 <= midi_pitch <= 72:
				possible_midi_pitches[2].append(midi_pitch)
			if 60 <= midi_pitch <= 79:
				possible_midi_pitches[3].append(midi_pitch)
			if midi_pitch > 79:
				break

		current_chord_members = current_chord_obj.scale_degrees
		bass_degree = current_chord_obj.bass_degree
		current_chord = current_chord_obj.chord_name
		# must realize full sequence to prevent iterator exhaustion
		# faster runtime if pitch combos are only calculated once per chord index
		validated_pitch_combos = []
		for chord_combo in itertools.product(*possible_midi_pitches):
			(b_pitch, t_pitch, a_pitch, s_pitch) = chord_combo
			current_degree_combo = (
				current_pitches_dict[b_pitch], current_pitches_dict[t_pitch],
				current_pitches_dict[a_pitch], current_pitches_dict[s_pitch],
			)
			if not b_pitch <= t_pitch <= a_pitch <= s_pitch:
				continue 
			if b_pitch - t_pitch > 24:
				continue
			if a_pitch - t_pitch > 12:
				continue
			if s_pitch - a_pitch > 12:
				continue
			if current_chord_members[0] not in current_degree_combo:
				continue
			if current_chord_members[1] not in current_degree_combo:
				continue
			if len(current_chord_members) == 4:  
				if current_degree_combo.count(current_chord_members[3]) != 1:
					continue 
				if (current_chord in cls.subdom_sevenths and 
				  current_chord != "II7" and 
				  current_chord_members[2] not in current_degree_combo):
					continue
			if bass_degree != current_degree_combo[0]:
				continue
			if current_chord in cls.secondary_dominants: 
				leading_degree = cls.leading_degrees[current_chord]
				if current_degree_combo.count(leading_degree) >= 2:
					continue
			elif current_chord == "I64" and current_degree_combo.count(0) >= 2:
				continue
			elif current_degree_combo.count(6) >= 2:
				continue
			validated_pitch_combos.append(chord_combo)

		return validated_pitch_combos

	def set_sheet_notes(self):
		"""Convert midi pitches into sheet music note names"""

		tonic_letter = self.tonic.replace('#',"").replace('b',"")
		tonic_index = self.note_letters.index(tonic_letter)

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
			possible_note_names = self.note_names[scale_midi_pitch]

			note_letter_index = (tonic_index + scale_degree) % 7
			note_letter = self.note_letters[note_letter_index]
			octave = true_midi_pitch // 12 - 1

			for possible_note_name in possible_note_names:
				if note_letter in possible_note_name:
					self.sheet_notes.append(f"{possible_note_name}{octave}")
					break

		self.logger.warning(f"Sheet notes: {self.sheet_notes}")

	def make_lily_part(self):
		"""Write sheet music text notation for voice part"""

		object_index = 0
		if self.pickup:
			object_duration = self.pickup_duration // 960
			lily_part = [f"\\partial {self.beat_durations[object_duration]}"]
		else:
			lily_part = []

		for midi_note, sheet_note in zip(self.midi_notes, self.sheet_notes):
			self.logger.warning(midi_note)
			self.logger.warning(sheet_note)
			self.logger.warning(object_index)

			object_duration = Fraction(numerator=midi_note.duration, denominator=960)
			object_rhythm = Voice.partition_rhythm(
				self.beat_durations, object_duration
			)
			if sheet_note is None:
				lily_rest = ""
				for rest_part in object_rhythm[:-1]:
					lily_rest = "".join([
						lily_rest, "r", self.beat_durations[rest_part], " "])

				lily_rest = "".join([
					lily_rest, "r", self.beat_durations[object_rhythm[-1]]])

				lily_part.append(lily_rest)
				continue

			accidental_mark = ""
			octave_mark = ""
			note_letter = sheet_note[0].lower()
			register_shift = 0

			# B# is technically in the octave above (starting from C)
			# Cb is technically in the octave below
			if sheet_note.startswith(("B#", "B##")):
				register_shift -= 1
			elif sheet_note.startswith(("Cb", "Cbb")):
				register_shift += 1
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
					self.beat_durations[beat_part], "~ "
				])

			lily_note = "".join([
				lily_note, note_letter, accidental_mark, octave_mark, 
				self.beat_durations[object_rhythm[-1]]
			])

			lily_part.append(lily_note)
			object_index += 1

		lily_string = " ".join(note for note in lily_part) 
		self.lily_score.append(lily_string)
		self.logger.warning(f"Lily part: {lily_part}")

	@classmethod
	def get_interval(cls, old_pitch, new_pitch, current_pitches_dict):
		"""Returns the specific interval of two pitches"""
		pitch_diff = new_pitch - old_pitch
		chromatic_diff = pitch_diff % 12

		old_degree = current_pitches_dict[old_pitch]
		new_degree = current_pitches_dict[new_pitch]

		generic_interval = new_degree - old_degree
		if generic_interval < 0:
			generic_interval += 7

		return cls.interval_names[(chromatic_diff, generic_interval)]

	def add_voice_motion(self, voice_motion, new_pitch, voice_index):
		"""Appends the next voice motion to a sequence"""
		old_pitch = self.chosen_chord_voicings[self.chord_index - 1][voice_index]
		if new_pitch < old_pitch:
			voice_motion.append(-1)
		elif new_pitch > old_pitch:
			voice_motion.append(1)
		else:
			voice_motion.append(0)

	def add_motion_type(self, old_motion, new_motion, movements, intervals):
		"""Appends the next voice motion type to a sequence"""
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




