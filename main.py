from __future__ import annotations
# allows use of an annotation before function definition (Python 3.7+)
import copy
import random
from typing import List, Tuple, Union, NamedTuple, Callable
from fractions import Fraction
import itertools

from midiutil import MIDIFile

class Engraver:

	scale_obj = None
	time_sig_obj = None
	style = None
	roman_numerals = ("I", "II", "III", "IV", "V", "VI", "VII")
	note_letters = ("C", "D", "E", "F", "G", "A", "B")
	scale_increments = (2, 2, 1, 2, 2, 2, 1)

	@property 
	def beats_per_measure(self):
		return self.time_sig_obj.beats_per_measure

	@property
	def tonic_pitch(self):
		return self.scale_obj.scale_pitches_seq[0]


class TimeSignature:

	all_beat_values = {
		"6/8": Fraction(3, 8),  "4/4": Fraction(1, 4),
		"2/2": Fraction(1, 2), "3/4": Fraction(1, 4),
	}
	all_beats_per_measure = { 
		"6/8": 2, "4/4": 4, "2/2": 2, "3/4": 3,
	}
	all_melodic_divisions = {
		"6/8": (Fraction(1, 2), Fraction(1, 2)), 
		"4/4": (Fraction(1, 2), Fraction(1, 2)),
		"2/2": (Fraction(1, 2), Fraction(1, 2)),
		"3/4": (Fraction(2, 3), Fraction(1, 3)),
	}
	all_tempo_ranges = {
		"6/8": range(38, 59), "4/4": range(90, 125),
		"2/2": range(53, 101), "3/4": range(80, 141),
	}
	all_rhythms = {
		"6/8": {
			"I1": ((4, 2), (3, 1, 2), (4, 1, 1)),
			"I2": ((3, 1, 2), (4, 2))
		},
		"4/4": {
			"I1": ((6, 2), (4, 2, 2), (4, 4)),
			"I2": ((4, 4), (4, 2, 2))
		},
		"2/2": {
			"I1": ((6, 2), (4, 2, 2), (4, 4)),
			"I2": ((4, 4), (4, 2, 2))
		},
		"3/4": {
			"I1": ((1, 1), (1,)),
			"I2": ((2, 2), (2,)),
			"I3": ((1, 1), (1,)),
			"I4": ((2, 2), (2,))
		},
	}
	all_rest_endings = {
		"6/8": {2: (("NOTE", 1), ("REST", 1))},
		"4/4": {1: (("NOTE", 1), ("REST", 1)), 2: (("NOTE", 2), ("REST", 2))},
		"2/2": {
			1: (("NOTE", Fraction(1, 2)), ("REST", Fraction(1, 2))), 
			2: (("NOTE", 1), ("REST", 1))
		}, "3/4": {2: (("NOTE", 2), ("REST", 1))}
	}

	def __init__(self, symbol: str) -> None:
		self.symbol = symbol
		self.beats_per_measure = self.all_beats_per_measure[symbol]
		self.melodic_divisions = self.all_melodic_divisions[symbol] 
		self.tempo_range = self.all_tempo_ranges[symbol] 
		self.rhythms = self.all_rhythms[symbol] 
		self.rest_ending = self.all_rest_endings[symbol] 
		self.beat_value = self.all_beat_values[self.symbol]


def collapse_magnitude(amount: int) -> int:
	if amount > 0:
		return 1
	elif amount < 0:
		return -1
	else:
		return 0


def collapse_sequence(nested_sequence: List[List[int]]) -> List[int]:
	unnested_sequence = []
	for group in nested_sequence:
		for item in group:
			unnested_sequence.append(item)
	return unnested_sequence


def find_slopes(sequence: List[int]) -> List[List[int]]:
	all_slopes = []
	current_slope = [sequence[0]]
	current_sign = collapse_magnitude(sequence[1] - sequence[0])
	
	for previous_value, current_value in zip(sequence, sequence[1:]):
		current_direction = collapse_magnitude(current_value - previous_value)
		if current_direction in {0, current_sign}:
			current_slope.append(current_value)
		else:
			if current_sign == 0:
				current_sign = current_direction
				current_slope.append(current_value)
			else:
				current_sign = current_direction
				all_slopes.append(current_slope)
				current_slope = [previous_value, current_value]

	all_slopes.append(current_slope)
	return all_slopes


class Pitch(Engraver):
	
	def __init__(self, pitch_symbol: str) -> None:

		self.pitch_letter = pitch_symbol[0].upper()
		if self.pitch_letter not in self.note_letters:
			raise ValueError
		self.accidental_symbol = pitch_symbol[1:]
		self.accidental_amount = Pitch.accidental_symbol_to_amount(self.accidental_symbol)

	def __repr__(self) -> str:
		return self.pitch_letter + self.accidental_symbol 

	def __add__(self, interval_obj: Interval) -> Note:
		interim_obj = self.change_pitch_letter(interval_obj.generic_interval)
		return interim_obj.change_pitch_accidental(interval_obj.midi_distance)

	@staticmethod
	def accidental_symbol_to_amount(accidental_symbol: str) -> int:

		if len(set(accidental_symbol)) > 1:
			raise ValueError

		if "#" in accidental_symbol:
			return accidental_symbol.count("#")
		elif "b" in accidental_symbol:
			return accidental_symbol.count("b") * -1
		elif not accidental_symbol:
			return 0
		else:
			raise ValueError

	@staticmethod
	def accidental_amount_to_symbol(accidental_amount: int) -> str:
		
		if accidental_amount > 0:
			return "#" * accidental_amount
		elif accidental_amount < 0:
			return "b" * abs(accidental_amount)
		else:
			return ""

	def shift(self, letter_increment: int, pitch_increment: int) -> Pitch:

		interim_obj = self.change_pitch_letter(letter_increment)
		return interim_obj.change_pitch_accidental(pitch_increment)

	def change_pitch_letter(self, letter_increment: int) -> Pitch:

		if letter_increment == 0:
			return self

		letter_direction = collapse_magnitude(letter_increment)
		half_step_letters = {"B", "C", "E", "F"}
		new_accidental_amount = self.accidental_amount
		old_pitch_letter = self.pitch_letter
		old_letter_index = self.note_letters.index(old_pitch_letter)

		for _ in range(abs(letter_increment)):
			new_letter_index = (old_letter_index + letter_direction) % 7 
			new_pitch_letter = self.note_letters[new_letter_index]
			pitch_pair = {new_pitch_letter, old_pitch_letter}
			if len(half_step_letters & pitch_pair) == 2:
				new_accidental_amount -= letter_direction
			else:
				new_accidental_amount -= (letter_direction * 2)
			old_pitch_letter = new_pitch_letter
			old_letter_index = new_letter_index

		new_accidental_symbol = Pitch.accidental_amount_to_symbol(new_accidental_amount)
		return Pitch(new_pitch_letter + new_accidental_symbol)

	def change_pitch_accidental(self, pitch_increment: int) -> Pitch:

		new_accidental_amount = self.accidental_amount + pitch_increment
		new_accidental_symbol = Pitch.accidental_amount_to_symbol(new_accidental_amount)
		return Pitch(self.pitch_letter + new_accidental_symbol)

	def get_lily_format(self) -> str:
		letter_mark = self.pitch_letter.lower()
		if self.accidental_amount > 0:
			accidental_mark = "is" * self.accidental_amount
		elif self.accidental_amount < 0:
			accidental_mark = "es" * abs(self.accidental_amount)
		else:
			accidental_mark = ""
		return letter_mark + accidental_mark
  

class Scale(Engraver):

	mode_wheel = (
		"ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", 
		"locrian",
	)

	def __init__(self, tonic: str = "C", input_mode: str = "ionian") -> None:

		if input_mode == "major":
			proxy_mode = "ionian"
			self.mode = input_mode
		elif input_mode == "minor":
			proxy_mode = "aeolian"
			self.mode = input_mode
		else:
			self.mode = proxy_mode = input_mode
			special_degrees = {
				"ionian": 0, "dorian": 5, "phrygian": 1, "lydian": 3, 
				"mixolydian": 6, "aeolian": 2, "locrian": 4,
			}
			self.special_degree = special_degrees[input_mode]

		tonic_pitch_obj = Pitch(tonic)
		tonic_pitch_letter = tonic_pitch_obj.pitch_letter
		current_midi_num = 0

		for current_pitch_letter, scale_increment in zip(self.note_letters, self.scale_increments):
			if current_pitch_letter == tonic_pitch_letter:
				break
			current_midi_num += scale_increment

		current_midi_num += tonic_pitch_obj.accidental_amount
		current_midi_num %= 12
		old_pitch_obj = tonic_pitch_obj
		self.scale_pitches_seq = [old_pitch_obj]
		self.scale_pitches_dict = {old_pitch_obj: current_midi_num}
		scale_index = self.mode_wheel.index(proxy_mode.lower())

		for _ in range(6):
			current_increment = self.scale_increments[scale_index]
			new_pitch_obj = old_pitch_obj.shift(1, current_increment)
			self.scale_pitches_seq.append(new_pitch_obj)

			current_midi_num = (current_midi_num + current_increment) % 12
			self.scale_pitches_dict[new_pitch_obj] = current_midi_num 
			old_pitch_obj = new_pitch_obj
			scale_index = (scale_index + 1) % 7

	def get_absolute_degree(self, chosen_note: Note) -> int:
		chosen_pitch_letter = chosen_note.pitch_letter
		for scale_degree, pitch_obj in enumerate(self.scale_pitches_seq):
			if pitch_obj.pitch_letter == chosen_pitch_letter:
				return scale_degree 

	def get_relative_degree(self, starting_note: Note, attempted_note: Note) -> int:
		if starting_note == attempted_note:
			return 0
		attempted_degree = self.get_absolute_degree(attempted_note)
		midi_pitch_diff = attempted_note.midi_num - starting_note.midi_num
		octave_amount = midi_pitch_diff // 12
		return attempted_degree + (octave_amount * 7)


class Interval:

	def __init__(
	  self, interval_quality: str, generic_interval: int, 
	  interval_direction: int = 1) -> None:
		self.interval_quality = interval_quality
		self.generic_interval = abs(generic_interval) * interval_direction
		if interval_direction not in {1, -1}:
			raise ValueError
		self.interval_direction = interval_direction

		# unison should be zero for symmetry with negative intervals
		if self.generic_interval == 0:
			self.possible_qualities = ["P", "A"]
		elif self.generic_interval % 7 in {0, 3, 4,}:
			self.possible_qualities = ["d", "P", "A"]
		elif self.generic_interval % 7 in {1, 2, 5, 6}:
			self.possible_qualities = ["d", "m", "M", "A"]
		if not self.validate_interval_quality():
			raise ValueError

		self.midi_distance = self.get_midi_distance()

	def validate_interval_quality(self) -> None:
		if self.interval_quality[0] not in self.possible_qualities:
			return False
		if len(self.interval_quality) > 1:
			if "d" in self.interval_quality:
				chosen_character = "d"
			elif "A" in self.interval_quality:
				chosen_character = "A"
			else:
				return False

			if chosen_character * len(self.interval_quality) != self.interval_quality:
				return False
		return True

	def get_midi_distance(self) -> int:

		simple_generic_interval = self.generic_interval
		while not -6 <= simple_generic_interval <= 6:
			simple_generic_interval += (7 * self.interval_direction * -1)
		if simple_generic_interval in {0, 3, 4, -3, -4}:
			current_interval_quality = "P"
		else:
			if self.generic_interval > 0:
				current_interval_quality = "M"
			elif self.generic_interval < 0:
				current_interval_quality = "m"

		reference_scale = Scale()
		final_scale_pitch = reference_scale.scale_pitches_seq[simple_generic_interval]
		reference_midi_num = reference_scale.scale_pitches_dict[final_scale_pitch]
		midi_distance = reference_midi_num * self.interval_direction % 12
		midi_distance *= self.interval_direction

		current_generic_interval = simple_generic_interval
		while current_generic_interval != self.generic_interval:
			midi_distance += (self.interval_direction * 12)
			current_generic_interval += (self.interval_direction * 7)

		starting_quality_num = self.get_quality_num(current_interval_quality)
		ending_quality_num = self.get_quality_num(self.interval_quality)
		if starting_quality_num == ending_quality_num:
			return midi_distance

		interval_increment = ending_quality_num - starting_quality_num
		midi_distance += (interval_increment * self.interval_direction)
		if midi_distance < 0 and self.generic_interval > 0:
			raise ValueError
		if midi_distance > 0 and self.generic_interval < 0:
			raise ValueError
		return midi_distance

	def __repr__(self):
		return f"{self.interval_quality}{abs(self.generic_interval) + 1}"

	def shift_interval_quality(self, increment: int) -> Interval:

		quality_num = self.get_quality_num(self.interval_quality)
		quality_num += increment
		quality_span = len(self.possible_qualities)

		if 0 <= quality_num < quality_span:
			new_interval_quality = self.possible_qualities[quality_num] 
		elif quality_num < 0:
			new_interval_quality = "d" * abs(quality_num - 1) 
		elif quality_num >= quality_span:
			new_interval_quality = "A" * (quality_num - quality_span + 2)

		return Interval(new_interval_quality, self.generic_interval)

	def get_quality_num(self, interval_quality: str) -> int: 
		quality_span = len(self.possible_qualities)

		if interval_quality in self.possible_qualities:
			quality_num = self.possible_qualities.index(interval_quality)
		elif "d" in interval_quality:
			quality_num = (interval_quality.count("d") * -1) + 1
		elif "A" in interval_quality:
			quality_num = quality_span + interval_quality.count("A") - 2

		return quality_num

	@staticmethod
	def create_from_symbol(
	  interval_symbol: str, is_rising: bool = True) -> Interval:

		for symbol_index, character in enumerate(interval_symbol):
			if character.isdigit():
				break
		else:
			raise ValueError

		interval_quality = interval_symbol[:symbol_index]
		generic_interval = int(interval_symbol[symbol_index:]) - 1
		if is_rising:
			interval_direction = 1
		else:
			interval_direction = -1
		return Interval(interval_quality, generic_interval, interval_direction) 


class Duration(Engraver):

	def __init__(self, duration: Union[int, Fraction] = 0, 
	  relative_offset: Union[int, Fraction] = 0, 
	  parent_absolute_offset: Union[int, Fraction] = 0) -> None:
		self.duration = duration
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset

	def get_lily_duration(self) -> str:
		absolute_duration = self.time_sig_obj.beat_value * self.duration
		if absolute_duration.numerator == 1:
			return f"{absolute_duration.denominator}"
		elif absolute_duration.numerator == 3:
			return f"{absolute_duration.denominator // 2}." 


class Note(Pitch, Duration):

	def __init__(self, note_symbol: str, 
	  duration: Union[int, Fraction] = 0, 
	  relative_offset: Union[int, Fraction] = 0, 
	  parent_absolute_offset: Union[int, Fraction] = 0) -> None:
		self.duration = duration
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset

		self.octave_number = int(note_symbol[-1])
		self.pitch_symbol = note_symbol[:-1]
		super().__init__(self.pitch_symbol)
		current_midi_num = (self.octave_number + 1) * 12

		for note_letter, scale_increment in zip(self.note_letters, self.scale_increments):
			if note_letter == self.pitch_letter:
				break
			current_midi_num += scale_increment
		current_midi_num += self.accidental_amount

		self.midi_num = current_midi_num

	def __repr__(self):
		return f"{self.pitch_symbol}{self.octave_number}"

	def __eq__(self, other):
		return self.__str__() == other.__str__()

	def __lt__(self, other):
		return self.midi_num < other.midi_num

	def __le__(self, other):
		return self.midi_num <= other.midi_num

	def __gt__(self, other):
		return self.midi_num > other.midi_num

	def __ge__(self, other):
		return self.midi_num >= other.midi_num

	def __sub__(self, starting_note: Note) -> Interval:

		if self.octave_number == starting_note.octave_number:
			ending_pitch_index = self.note_letters.index(self.pitch_letter)
			starting_pitch_index = self.note_letters.index(starting_note.pitch_letter)
			if ending_pitch_index > starting_pitch_index:
				letter_direction = 1
			elif starting_pitch_index > ending_pitch_index:
				letter_direction = -1 

		elif self.octave_number > starting_note.octave_number:
			letter_direction = 1
		elif starting_note.octave_number > self.octave_number:
			letter_direction = -1
		current_note = starting_note

		generic_interval = 0
		while current_note.octave_number != self.octave_number:
			current_note = current_note.change_pitch_letter(
				letter_direction
			)
			generic_interval += letter_direction

		while current_note.pitch_letter != self.pitch_letter:
			current_note = current_note.change_pitch_letter(
				letter_direction
			) 
			generic_interval += letter_direction


		""" In a major scale, intervals from the tonic up to another
		scale degree are major or perfect and intervals from the tonic
		down to another scale degree are minor or perfect"""
		guide_scale = Scale(starting_note.pitch_symbol)
		guide_scale_pitches = guide_scale.scale_pitches_seq

		current_pitch = guide_scale_pitches[0]
		scale_index = 0

		while current_pitch.pitch_letter != self.pitch_letter:
			scale_index = (scale_index + letter_direction) % 7
			current_pitch = guide_scale_pitches[scale_index]

		if scale_index in {0, 3, 4}:
			interval_quality = "P"
		elif scale_index in {1, 2, 5, 6}:
			if letter_direction < 0:
				interval_quality = "m"
			elif letter_direction > 0:
				interval_quality = "M"
		current_interval = Interval(interval_quality, generic_interval)

		if self.pitch_letter == starting_note.pitch_letter:
			if self > starting_note:
				symbol_direction = 1
			elif starting_note > self:
				symbol_direction = -1
			else:
				symbol_direction = 0
		else:
			symbol_direction = letter_direction

		accidental_diff = self.accidental_amount - current_pitch.accidental_amount
		accidental_direction = collapse_magnitude(accidental_diff)
		interval_direction = accidental_direction * symbol_direction

		while self.pitch_symbol != str(current_pitch):
			current_pitch = current_pitch.change_pitch_accidental(
				accidental_direction
			)
			current_interval = current_interval.shift_interval_quality(
				interval_direction
			)

		return current_interval

	def change_pitch_letter(self, letter_increment: int) -> Note:
		if letter_increment == 0:
			return self
		old_pitch_obj = Pitch(self.pitch_symbol)
		new_pitch_obj = old_pitch_obj.change_pitch_letter(
			letter_increment
		)

		pitch_letter = old_pitch_obj.pitch_letter
		letter_index = self.note_letters.index(pitch_letter)
		if letter_increment < 0:
			change_letter = "B"
			letter_direction = -1
		elif letter_increment > 0:
			change_letter = "C"
			letter_direction = 1

		new_octave_number = self.octave_number
		for _ in range(abs(letter_increment)):
			letter_index = (letter_index + letter_direction) % 7 
			pitch_letter = self.note_letters[letter_index]
			if pitch_letter == change_letter:
				new_octave_number += letter_direction

		return Note(f"{new_pitch_obj}{new_octave_number}")

	def change_pitch_accidental(self, pitch_increment: int) -> Note:
		old_pitch_obj = Pitch(self.pitch_symbol)
		new_pitch_obj = old_pitch_obj.change_pitch_accidental(
			pitch_increment
		)
		return Note(f"{new_pitch_obj}{self.octave_number}")

	def scalar_shift(self, scale_increment: int) -> None:
		for scale_index, pitch_obj in enumerate(self.scale_obj.scale_pitches_seq):
			if str(pitch_obj) == self.pitch_symbol:
				break
		final_index = (scale_index + scale_increment) % 7

		final_pitch = self.scale_obj.scale_pitches_seq[final_index]
		interim_note = self.change_pitch_letter(scale_increment)
		accidental_diff = final_pitch.accidental_amount - interim_note.accidental_amount
		return interim_note.change_pitch_accidental(accidental_diff)

	def get_lily_format(self) -> str:
		if self.octave_number > 3:
			octave_mark = "'" * (self.octave_number - 3)
		elif self.octave_number < 3:
			octave_mark = "," * (3 - self.octave_number)
		else:
			octave_mark = ""

		pitch_mark = super().get_lily_format()
		lily_duration = self.get_lily_duration()
		return f"{pitch_mark}{octave_mark}{lily_duration}"


class ChordPitchIterator(Engraver):

	def __init__(self, chord, current_octave, starting_direction):
		self.chord_length = len(chord.pitches)
		self.current_octave = current_octave - starting_direction
		self.arranged_pitches = sorted(
			chord.pitches, 
			key=lambda pitch: self.note_letters.index(pitch.pitch_letter)
		)
		if starting_direction == 1:
			self.current_index = -1
		elif starting_direction == -1:
			self.current_index = self.chord_length
		else:
			raise ValueError

	def shift(self, direction, cuttoff_index):
		self.current_index = (self.current_index + direction) % self.chord_length 
		if self.current_index == cuttoff_index:
			self.current_octave = self.current_octave + direction
		new_pitch = self.arranged_pitches[self.current_index]
		return Note(f"{new_pitch}{self.current_octave}")

	def next(self):
		return self.shift(1, 0)

	def prev(self):
		return self.shift(-1, self.chord_length - 1)


class Chord(Engraver):

	triads_figured_bass = {"": 0, "5/3": 0, "6": 1, "6/3": 1, "6/4": 2}
	sevenths_figured_bass = {
		"7": 0, "7/5/3": 0, "6/5": 1, "6/5/3": 1, "4/3": 2, "6/4/3": 2, 
		"6/4/2": 3, "4/2": 3, "2": 3,
	}
	triad_intervals = {
		"MAJ": ("M3", "P5"), "MIN": ("m3", "P5"), "AUG": ("M3", "A5"),
		"DIM": ("m3", "d5"),
	}
	seventh_chord_intervals = {
		"MAJ": ("M3", "P5", "M7"), "MAJ-MIN": ("M3", "P5", "m7"), 
		"MIN": ("m3", "P5", "m7"), "HALF-DIM": ("m3", "d5", "m7"),
		"DIM": ("m3", "d5", "d7"), 
	}

	def __init__(
	  self, chord_symbol: str, duration: Union[int, Fraction], 
	  relative_offset: Union[int, Fraction] = 0, 
	  parent_absolute_offset: Union[int, Fraction] = 0) -> None:
		self.duration = duration
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset
		self.chord_symbol = chord_symbol

		roman_symbol, chord_quality = chord_symbol.split("_")
		for accidental_index, character in enumerate(roman_symbol):
			if character not in {"#", "b"}:
				break
		else:
			raise ValueError

		accidental_symbol = roman_symbol[0:accidental_index]
		roman_symbol = roman_symbol[accidental_index:]
		for num in range(3, 0, -1):
			roman_numeral = roman_symbol[:num]
			if roman_numeral in self.roman_numerals:
				bass_figure = roman_symbol[num:]
				break
		else:
			raise ValueError

		if bass_figure in self.triads_figured_bass:
			self.inversion_position = self.triads_figured_bass[bass_figure]
			chosen_intervals = self.triad_intervals[chord_quality]
		elif bass_figure in self.sevenths_figured_bass:
			self.inversion_position = self.sevenths_figured_bass[bass_figure]
			chosen_intervals = self.seventh_chord_intervals[chord_quality]
		else:
			raise ValueError
			
		scale_degree = self.roman_numerals.index(roman_numeral)
		reference_scale = Scale(str(self.tonic_pitch))
		root_pitch = reference_scale.scale_pitches_seq[scale_degree]
		accidental_amount = Pitch.accidental_symbol_to_amount(accidental_symbol)
		root_pitch = root_pitch.change_pitch_accidental(accidental_amount)

		self.pitches = [root_pitch]
		for interval_symbol in chosen_intervals:
			new_interval = Interval.create_from_symbol(interval_symbol)
			new_pitch = root_pitch + new_interval
			self.pitches.append(new_pitch)

	def __repr__(self):
		return self.chord_symbol

	def get_chord_notes(self, start_midi_num, stop_midi_num) -> List[Note]:
		starting_octave = (start_midi_num // 12) + 1
		chord_pitch_iter = ChordPitchIterator(self, starting_octave, -1)
		current_note = chord_pitch_iter.prev()
		while current_note.midi_num >= start_midi_num:
			current_note = chord_pitch_iter.prev()

		chord_notes = []
		current_note = chord_pitch_iter.next() 
		while current_note.midi_num < stop_midi_num:
			chord_notes.append(current_note)
			current_note = chord_pitch_iter.next()

		return chord_notes


class Rest(Duration):

	def get_lily_format(self):
		return f"r{self.get_lily_duration()}"


class Measure(Engraver):

	def __init__(
	  self, relative_offset: Union[int, Fraction], 
	  parent_absolute_offset: Union[int, Fraction]) -> None:
		self.notes = []
		self.chords = []
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset

	def imprint_chord(self, chord: Chord) -> None:
		if self.chords:
			current_offset = self.chords[-1].relative_offset + self.chords[-1].duration
		else:
			current_offset = 0
		self.chords.append(
			Chord(str(chord), chord.duration, current_offset, self.absolute_offset)
		)

	def imprint_temporal_obj(self, chosen_obj: Union[Note, Rest]) -> None:
		if self.notes:
			current_offset = self.notes[-1].relative_offset + self.notes[-1].duration
		else:
			current_offset = 0
		if isinstance(chosen_obj, Note):
			self.notes.append(
				Note(str(chosen_obj), chosen_obj.duration, current_offset, self.absolute_offset)
			)
		elif isinstance(chosen_obj, Rest):
			self.notes.append(
				Rest(chosen_obj.duration, current_offset, self.absolute_offset)
			)

	def get_chord(self, chosen_offset) -> Chord:
		if len(self.chords) == 1:
			return self.chords[0]
		for current_chord in self.chords:
			if current_chord.relative_offset == chosen_offset:
				return current_chord
		else:
			raise ValueError


class ChordRule(NamedTuple):
	function: Callable[..., bool]
	parameters: Tuple

	@staticmethod
	def is_start_chord(progression_obj, chord_index, verdict):
		if chord_index != 0:
			return True
		return verdict

	@staticmethod
	def is_end_chord(progression_obj, chord_index, verdict):
		if chord_index != progression_obj.length - 1:
			return True
		return verdict

	@staticmethod
	def can_succeed(progression_obj, chord_index, predecessors):
		if chord_index == 0:
			return True
		return progression_obj.chord_symbols[chord_index - 1] in predecessors


class Progression(Engraver):

	chord_rules = {
		"I_MAJ": (
			ChordRule(ChordRule.is_start_chord, (True,)),
			ChordRule(ChordRule.is_end_chord, (True,)),
			ChordRule(ChordRule.can_succeed, ({"V_MAJ", "V6_MAJ", "VII6_DIM"},))
		), "I6_MAJ": (
			ChordRule(ChordRule.is_start_chord, (False,)),
			ChordRule(ChordRule.is_end_chord, (False,)),
			ChordRule(ChordRule.can_succeed, ({"VII6_DIM", "IV6_MIN"},))
		), "V_MAJ": (
			ChordRule(
				ChordRule.can_succeed, 
				({"IV6_MAJ", "IV6_MIN", "II6_MIN", "II6_DIM"},)
			),
		), "V6_MAJ": (
			ChordRule(
				ChordRule.can_succeed, 
				({"I_MAJ", "I6_MAJ", "I_MIN", "I6_MIN"},)
			),
		), "VII6_DIM": (
			ChordRule(
				ChordRule.can_succeed, 
				({"I_MAJ", "I6_MAJ", "I_MIN", "I6_MIN"},)
			),
		), "IV6_MIN": (
			ChordRule(ChordRule.can_succeed, ({"I_MAJ"},)),
		), "II6_MIN": (
			ChordRule(ChordRule.can_succeed, ({"I_MAJ"},)),
		), "I_MIN": (
			ChordRule(ChordRule.is_start_chord, (True,)),
			ChordRule(ChordRule.is_end_chord, (True,)),
			ChordRule(ChordRule.can_succeed, ({"V_MAJ", "V6_MAJ", "VII6_DIM"},))
		), "I6_MIN": (
			ChordRule(ChordRule.is_start_chord, (False,)),
			ChordRule(ChordRule.is_end_chord, (False,)),
			ChordRule(ChordRule.can_succeed, ({"VII6_DIM", "IV6_MAJ"},))
		), "IV6_MAJ": (
			ChordRule(ChordRule.can_succeed, ({"I_MIN"},)),
		), "II6_DIM": (
			ChordRule(ChordRule.can_succeed, ({"I_MIN"},)),
		),
	}
	
	def __init__(self, *args: Tuple[ChordType, ...]) -> None:
		self.chord_types = args
		self.length = len(self.chord_types)
		self.chord_symbols = []

	def __repr__(self):
		return " | ".join(chord_type.function for chord_type in self.chord_types)

	def realize(self) -> List[Chord, ...]:

		if self.scale_obj.mode == "major":
			all_chords = {
				"TONIC": ("I_MAJ", "I6_MAJ"), 
				"PREDOMINANT": ("IV6_MIN", "II6_MIN"),
				"DOMINANT": ("V6_MAJ", "VII6_DIM", "V_MAJ"),
			}
		elif self.scale_obj.mode == "minor":
			all_chords = {
				"TONIC": ("I_MIN", "I6_MIN"),
				"PREDOMINANT": ("IV6_MAJ", "II6_DIM"),
				"DOMINANT": ("V6_MAJ", "VII6_DIM", "V_MAJ"),
			}

		reference_chord_combos = []
		remaining_chord_combos = []
		for chord_type in self.chord_types:
			possible_chords = list(all_chords[chord_type.function])
			reference_chord_combos.append(possible_chords)
			self.chord_symbols.append(None)
			remaining_chord_combos.append(None)

		chord_index = 0
		remaining_chord_combos[chord_index] = reference_chord_combos[chord_index][:]
		while None in self.chord_symbols:
			if remaining_chord_combos[chord_index]:
				chosen_chord = random.choice(remaining_chord_combos[chord_index])
				remaining_chord_combos[chord_index].remove(chosen_chord)

				is_chord_valid = True
				for rule_obj in self.chord_rules[chosen_chord]:
					is_chord_rule_valid = rule_obj.function(
						self, chord_index, *rule_obj.parameters
					)
					if not is_chord_rule_valid:
						is_chord_valid = False
						break
				else:
					self.chord_symbols[chord_index] = chosen_chord
					chord_index += 1
					try:
						remaining_chord_combos[chord_index] = reference_chord_combos[chord_index][:]
					except IndexError:
						continue

			if not is_chord_valid and not remaining_chord_combos[chord_index]:
				remaining_chord_combos[chord_index] = None
				if chord_index == 0:
					raise IndexError
				chord_index -= 1
				self.chord_symbols[chord_index] = None

		final_chords = []
		for chord_symbol, chord_type in zip(self.chord_symbols, self.chord_types):
			final_chords.append(Chord(chord_symbol, chord_type.duration))
		return final_chords


class Phrase(Engraver):

	def __init__(
	  self, relative_offset: Union[int, Fraction],
	  parent_absolute_offset: Union[int, Fraction], 
	  num_measures: int = 8) -> None:
		self.measures = []
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset

		for index in range(num_measures):
			self.measures.append(
				Measure(index * self.beats_per_measure, self.absolute_offset)
			)
		self.base_melody = []
		self.full_melody = []

		self.starting_note = None
		self.embellish_rhythms = []
		self.theme_type = None

		if self.time_sig_obj.symbol in {"6/8", "3/4"}:
			self.has_rest_ending = True
		else:
			self.has_rest_ending = random.choice((True, False))
		print(f"Has rest ending? {self.has_rest_ending}")

	def imprint_progression(self) -> None:
		progression = random.choice(self.progressions)
		print(progression)
		chosen_progression = progression.realize()
		print(f"Chosen progression: {chosen_progression}")
		relative_offset = 0
		for current_chord in chosen_progression:
			measure_index = relative_offset // self.beats_per_measure
			self.measures[measure_index].imprint_chord(current_chord)
			relative_offset += current_chord.duration 

	def add_melody(self, is_embellished: bool) -> None:

		if self.style == "tonal":
			self.imprint_progression()

		base_melody_note_options = self.get_base_melody_options()
		base_melody_finder = self.find_base_melody(base_melody_note_options)

		next(base_melody_finder)
		if not is_embellished:
			self.imprint_base_melody()
			return

		rhythm_finder = self.choose_embellish_rhythms()
		self.embellish_rhythms = next(rhythm_finder)
		print(f"Embellish rhythms: {self.embellish_rhythms}")
		while True:
			if self.embellish_melody():
				break
			if not next(base_melody_finder):
				raise ValueError
			self.embellish_rhythms = next(rhythm_finder)
			print(f"Embellish rhythms: {self.embellish_rhythms}")

		full_melody_iter = iter(self.full_melody)
		for current_measure in self.measures:
			for _ in self.time_sig_obj.melodic_divisions:
				note_group = next(full_melody_iter)
				for measure_note in note_group:
					if isinstance(measure_note, Note):
						current_measure.imprint_temporal_obj(measure_note)
		rest_ending_count = self.full_melody.count("REST")
		self.finalize_theme(rest_ending_count)

	def get_base_melody_options(self) -> List[List[Note]]:

		base_melody_note_options = []

		start_midi_num = 59
		stop_midi_num = 85
		if self.style == "modal":
			all_modal_notes = self.get_modal_notes(start_midi_num, stop_midi_num)
		for current_measure in self.measures:
			current_offset = 0
			for measure_fraction in self.time_sig_obj.melodic_divisions:
				if self.style == "tonal":
					current_chord = current_measure.get_chord(current_offset)
					base_melody_note_options.append(
						current_chord.get_chord_notes(start_midi_num, stop_midi_num)
					) 
				elif self.style == "modal":
					base_melody_note_options.append(all_modal_notes[:]) 
				current_offset += (self.beats_per_measure * measure_fraction)

		return base_melody_note_options

	def get_modal_notes(self, start_midi_num: int, stop_midi_num: int) -> List[Note]:
		possible_notes = []
		current_octave = start_midi_num // 12
		current_note = Note(f"{self.tonic_pitch}{current_octave}")

		while current_note.midi_num >= start_midi_num:
			current_note = current_note.scalar_shift(-1) 

		current_note = current_note.scalar_shift(1)
		while current_note.midi_num < stop_midi_num:
			possible_notes.append(current_note)
			current_note = current_note.scalar_shift(1)

		return possible_notes

	def find_base_melody(
	  self, base_melody_note_options: List[List[Note]]) -> bool:

		reference_note_options = copy.deepcopy(base_melody_note_options)
		self.base_melody = [None for _ in base_melody_note_options]
		self.base_degrees = self.base_melody[:]

		tonic_pitch_symbol = str(self.tonic_pitch)
		for current_note in reference_note_options[0]:
			if tonic_pitch_symbol == current_note.pitch_symbol:
				starting_note = current_note
				break
		if starting_note.midi_num in {59, 60} and random.choice((True, False)):
			starting_note = starting_note.shift(7, 12)
		print(f"Starting note: {starting_note}")
		self.starting_note = starting_note

		note_index = 0
		current_note_options = base_melody_note_options[note_index]
		self.theme_type = random.choice(
			("early_sentence", "late_sentence", "bounce")
		)  
		print(f"Theme type: {self.theme_type}")

		while True:
			if current_note_options: 
				attempted_note = random.choice(current_note_options)
				current_note_options.remove(attempted_note)
				attempted_scale_degree = self.scale_obj.get_relative_degree(
					starting_note, attempted_note
				)

				if self.test_melody_note(note_index, attempted_scale_degree):
					self.base_melody[note_index] = attempted_note
					self.base_degrees[note_index] = attempted_scale_degree
					note_index += 1

					if None not in self.base_melody:
						note_index -= 1
						print(self.base_degrees)
						print(self.base_melody)
						yield True
						self.base_melody[note_index] = None
						self.base_degrees[note_index] = None
						continue
					current_note_options = base_melody_note_options[note_index]

			else:
				base_melody_note_options[note_index] = (
					reference_note_options[note_index][:]
				)
				if note_index == 0:
					raise IndexError
					
				note_index -= 1
				current_note_options = base_melody_note_options[note_index]
				self.base_melody[note_index] = None
				self.base_degrees[note_index] = None

	def test_melody_note(self, note_index: int, attempted_degree: int) -> bool:

		if not -2 <= attempted_degree <= 7:
			return False
		if note_index == 0:
			if attempted_degree not in {0, 2, 4, 7}:
				return False
		if note_index >= 1:
			current_leap = attempted_degree - self.base_degrees[note_index - 1]
			if abs(current_leap) > 4:
				return False 

		if note_index >= 2:
			previous_leap = self.base_degrees[note_index - 1] - self.base_degrees[note_index - 2]
			if (self.base_degrees[note_index - 2] == 
			  self.base_degrees[note_index - 1] == attempted_degree):
				return False
			elif (abs(previous_leap) > 2 and 
			  collapse_magnitude(previous_leap) == collapse_magnitude(current_leap)):
				return False
			elif 3 <= abs(previous_leap) <= 4 and not 1 <= abs(current_leap) <= 2:
				return False
			if attempted_degree != 0 and self.base_degrees.count(attempted_degree) > 3:
				return False

		if note_index >= 3:
			used_motifs = set()
			base_degrees = self.base_degrees[:]
			base_degrees[note_index] = attempted_degree 
			for degree0, degree1 in zip(base_degrees, base_degrees[1:]):
				if degree1 is None:
					break
				new_motif = (degree0, degree1)
				if new_motif in used_motifs:
					return False
				elif new_motif != (0, 0): 
					used_motifs.add(new_motif)

		if self.theme_type == "early_sentence":
			if note_index == 0 and attempted_degree == 7:
				return False
			if 1 <= note_index <= 2 and abs(attempted_degree - self.base_degrees[0]) > 2:
				return False
			if note_index == 3:
				motif_diff = self.base_degrees[1] - self.base_degrees[0]
				if current_leap != motif_diff:
					return False
			if (note_index == 4 and 
			  attempted_degree in {self.base_degrees[0], self.base_degrees[2]}):
				return False
			if note_index == 5:
				new_motif_direction = collapse_magnitude(current_leap)
				old_motif_direction = collapse_magnitude(
					self.base_degrees[1] - self.base_degrees[0]
				)
				if new_motif_direction != old_motif_direction:
					return False
				if attempted_degree in {self.base_degrees[1], self.base_degrees[3]}:
					return False

		if self.theme_type == "late_sentence":
			if note_index == 1 and attempted_degree != self.base_degrees[0]:
				return False
			if note_index == 2 and abs(current_leap) > 2:
				return False 
			if note_index == 5:
				motif_diff = self.base_degrees[3] - self.base_degrees[2]
				if current_leap != motif_diff:
					return False
			if (3 <= note_index <= 4 and 
			  not -2 <= attempted_degree - self.base_degrees[2] <= 0):
				return False

		if self.theme_type == "bounce":
			if attempted_degree != 0 and note_index == 3:
				return False
			if note_index == 7:
				temp_base_degrees = self.base_degrees
				temp_base_degrees[-1] = 0

				if max(temp_base_degrees[:4]) <= max(temp_base_degrees[4:]):
					return False
				if max(temp_base_degrees) != temp_base_degrees[1]:
					return False

		if note_index == 6:
			if self.base_degrees[1:6].count(0) > 1:
				return False
			if attempted_degree != 0 and self.has_rest_ending:
				return False
			if attempted_degree == 0 and not self.has_rest_ending:
				return False
		if note_index == 7:
			if attempted_degree != 0:
				return False
			for current_degree in self.base_degrees[6::-1]:
				if current_degree == 0:
					continue
				elif current_degree in {-1, 1, 2}:
					break
				else:
					return False

			temp_base_degrees = self.base_degrees[:]
			temp_base_degrees[-1] = 0

			if self.has_dissonant_interval(temp_base_degrees, self.base_melody):
				return False

		return True

	def has_dissonant_interval(
	  self, numbered_sequence: List[int], note_sequence: List[Note]) -> bool:

		dissonant_intervals = {"M7", "m7", "d5", "A4"}
		temp_note_index = 0
		slopes = find_slopes(numbered_sequence)
		for slope in slopes[:-1]:
			new_note1 = note_sequence[temp_note_index]
			temp_note_index += (len(slope) - 1)  
			new_note2 = note_sequence[temp_note_index]
			current_interval = new_note2 - new_note1
			if str(current_interval) in dissonant_intervals:
				return True

		new_note1 = note_sequence[temp_note_index]
		current_interval = self.starting_note - new_note1
		if str(current_interval) in dissonant_intervals:
			return True

		return False

	def imprint_base_melody(self):

		if self.has_rest_ending:
			base_melody = self.base_melody[:-2]
			rest_ending_count = 2
		else:
			base_melody = self.base_melody[:-1]
			rest_ending_count = 1
		base_melody_iter = iter(base_melody)
		for current_measure in self.measures:
			for measure_fraction in self.time_sig_obj.melodic_divisions:
				try:
					current_note_symbol = str(next(base_melody_iter))
				except StopIteration:
					break
				current_measure.imprint_temporal_obj(
					Note(current_note_symbol, self.beats_per_measure * measure_fraction)
				)

		self.finalize_theme(rest_ending_count)

	def choose_embellish_rhythms(self) -> None:

		if self.time_sig_obj.symbol == "3/4":
			possible_rhythms = [
				["I1", "I2", "I1", "I2", "I1", "I2", "REST", "REST"],
				["I1", "I2", "I3", "I4", "I3", "I4", "REST", "REST"]
			]
			has_rest_ending_rhythm = self.realize_embellish_rhythm(possible_rhythms)
		else:
			possible_rhythms = [
				["I1", "I1", "I1", "I1", "I1", "I1", "REST", "REST"],
				["I1", "I1", "I2", "I1", "I1", "I1", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I2", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I2", "I2", "REST", "REST"],
				["I1", "I1", "I1", "I1", "I2", "I2", "REST", "REST"],
			]
			has_rest_ending_rhythm = self.realize_embellish_rhythm(possible_rhythms)
			possible_rhythms = [
				["I1", "I1", "I1", "I1", "I1", "I1", "I1", "REST"],
				["I1", "I1", "I1", "I1", "I1", "I1", "I2", "REST"],
				["I1", "I2", "I1", "I2", "I2", "I2", "I2", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I2", "I2", "REST"],
			]
			no_rest_ending_rhythm = self.realize_embellish_rhythm(possible_rhythms)

		while True:
			if self.has_rest_ending:
				yield has_rest_ending_rhythm
			else:
				yield no_rest_ending_rhythm

	def realize_embellish_rhythm(
	  self, possible_rhythms: List[List[str]]) -> List[Union[Tuple[int, ...], str]]:
			if self.theme_type == "early_sentence":
				while True:
					embellish_symbols = random.choice(possible_rhythms)
					if embellish_symbols[0] != embellish_symbols[2]:
						continue
					if embellish_symbols[1] != embellish_symbols[3]:
						continue
					break
			else:
				embellish_symbols = random.choice(possible_rhythms)
			rhythm_mapping = {}
			embellish_rhythms = []

			for embellish_symbol in set(embellish_symbols):
				if embellish_symbol == "REST":
					rhythm_mapping[embellish_symbol] = embellish_symbol
					continue

				rhythm_choices = self.time_sig_obj.rhythms[embellish_symbol]
				while True:
					rhythm_choice = random.choice(rhythm_choices)
					if rhythm_choice not in rhythm_mapping.values():
						rhythm_mapping[embellish_symbol] = rhythm_choice
						break

			for embellish_symbol in embellish_symbols:
				embellish_rhythms.append(rhythm_mapping[embellish_symbol])
			return embellish_rhythms

	def embellish_melody(self):
		embellish_contour_options = []
		self.full_melody = []
		chosen_contours = []

		for note_index, embellish_rhythm in enumerate(self.embellish_rhythms):
			if embellish_rhythm == "REST":
				self.full_melody.append("REST")
			else:
				self.full_melody.append(None)
				chosen_contours.append(None)
				possible_contours = self.create_contour_options(note_index, embellish_rhythm)
				if not possible_contours:
					print("Embellishment not possible.")
					return False
				embellish_contour_options.append(possible_contours)

		note_index = 0
		reference_contour_options = copy.deepcopy(embellish_contour_options)
		current_contour_options = embellish_contour_options[note_index]

		while True:
			if current_contour_options:
				chosen_contour = random.choice(current_contour_options)
				current_contour_options.remove(chosen_contour)
				chosen_contours[note_index] = chosen_contour

				starting_note = self.base_melody[note_index]
				self.full_melody[note_index] = self.realize_melody_contour(
					starting_note, chosen_contour
				)

				if (self.test_contour(note_index, chosen_contours) and 
				  self.test_embellishment(note_index)):
					note_index += 1
					if None not in self.full_melody:
						self.add_embellish_durations()
						return True
					current_contour_options = embellish_contour_options[note_index]
				else:
					self.full_melody[note_index] = None
					chosen_contours[note_index] = None
			else:
				embellish_contour_options[note_index] = (
					reference_contour_options[note_index][:]
				)
				if note_index == 0:
					print("Embellishment failed.")
					return False
				note_index -= 1
				current_contour_options = embellish_contour_options[note_index]
				self.full_melody[note_index] = None
				chosen_contours[note_index] = None

	def create_contour_options(
	  self, note_index: int, embellish_rhythm: Tuple[int, ...]) -> List[Tuple[int, ...]]:
		embellish_length = len(embellish_rhythm)
		all_contour_options = {
			0: ((0,), (0, 1), (0, -1), (0, -1, -2), (0, -2, -1), (0, 2, 1), (0, 1, 0)),
			-1: ((0,), (0, 0), (0, 1), (0, -1), (0, -2), (0, -1, -2), (0, 1, 0), (0, 2, 1)),
			-2: ((0,), (0, -1), (0, -3), (0, 0, -1), (0, -1, -2), (0, -1, 0), (0, 1, -1)),
			-3: ((0, 0),),
			-4: ((0, -2), (0, -2, -3)),
			1: ((0,), (0, 2), (0, 1, 2)),
			2: ((0,), (0, 1), (0, 0, 1), (0, 1, 0), (0, 1, 2)),
			3: ((0, 4), (0, -1, -2), (0, 1, 2)),
		}

		possible_contours = []
		current_scale_degree = self.base_degrees[note_index]
		next_scale_degree = self.base_degrees[note_index + 1]
		leap_distance = next_scale_degree - current_scale_degree
		try: 
			for melodic_idea in all_contour_options[leap_distance]:
				if len(melodic_idea) == embellish_length:
					possible_contours.append(melodic_idea)
		except KeyError:
			print(f"Interval of {leap_distance} not possible")

		return possible_contours

	def realize_melody_contour(
	  self, starting_note: Note, chosen_contour: Tuple[int, ...]) -> List[Note]:

		realized_melody_fragment = []
		for melody_shift in chosen_contour:
			new_note = starting_note.scalar_shift(melody_shift)
			realized_melody_fragment.append(new_note)
		return realized_melody_fragment

	def test_contour(
	  self, note_index: int, chosen_contours: List[Union[Tuple[int, ...], None]]) -> bool:
		if self.theme_type == "early_sentence":
			if (note_index in {2, 3} and chosen_contours[note_index] != 
			  chosen_contours[note_index - 2]):
				return False
		return True

	def test_embellishment(self, note_index: int) -> bool:
		if note_index >= 2 and note_index % 2 == 0:
			last_previous_note = self.full_melody[note_index - 1][-1]
			current_first_note = self.full_melody[note_index][0]
			bar_leap = current_first_note.midi_num - last_previous_note.midi_num
			if abs(bar_leap >= 3): 
				leap_direction = collapse_magnitude(bar_leap)
				for current_note in self.full_melody[note_index]:
					resolve_leap = current_note.midi_num - current_first_note.midi_num  
					if resolve_leap != 0:
						resolve_direction = collapse_magnitude(resolve_leap)
						if leap_direction == resolve_direction:
							return False
						if bar_leap == 3 and abs(resolve_leap) > 2:
							return False
						if bar_leap >= 4 and abs(resolve_leap) > 1:
							return False 
						break

		if self.has_rest_ending and note_index == 5:
			return self.has_proper_notes(note_index)
		if not self.has_rest_ending and note_index == 6:
			return self.has_proper_notes(note_index)

		return True

	def has_proper_notes(self, note_index) -> bool:

		if self.full_melody[note_index][-1] == self.starting_note:
			return False

		temp_melody = collapse_sequence(self.full_melody[:note_index])
		temp_melody.append(self.starting_note)
		temp_midi_nums = [new_note.midi_num for new_note in temp_melody]
		if self.has_dissonant_interval(temp_midi_nums, temp_melody):
			return False

		all_degrees_set = {
			self.scale_obj.get_absolute_degree(current_note)
			for current_note in temp_melody
		}
		if self.scale_obj.special_degree not in all_degrees_set:
			return False 

		return True

	def add_embellish_durations(self) -> List[Union[List[Note], str]]:
		finalized_melody = []
		melodic_divisions_iter = itertools.cycle(self.time_sig_obj.melodic_divisions)
		for note_group, embellish_rhythm in zip(self.full_melody, self.embellish_rhythms):
			measure_fraction = next(melodic_divisions_iter)
			if note_group == "REST":
				finalized_melody.append("REST")
				continue
			finalized_melody.append([])
			embellish_rhythm_sum = sum(embellish_rhythm)

			for current_note, embellish_value in zip(note_group, embellish_rhythm):
				embellish_fraction = Fraction(embellish_value, embellish_rhythm_sum)  
				finalized_duration = embellish_fraction * measure_fraction * self.beats_per_measure
				finalized_melody[-1].append(Note(str(current_note), finalized_duration))

		print(f"Finalized melody: {finalized_melody}")
		self.full_melody = finalized_melody

	def finalize_theme(self, rest_ending_count: int) -> None:
		rest_ending_symbols = self.time_sig_obj.rest_ending[rest_ending_count]
		starting_note_str = str(self.starting_note)

		for symbol, duration in rest_ending_symbols:
			if symbol == "REST":
				self.measures[-1].imprint_temporal_obj(Rest(duration))
			elif symbol == "NOTE":
				self.measures[-1].imprint_temporal_obj(Note(starting_note_str, duration))


class ChordType(NamedTuple):
	function: str
	duration: int


class MiniTheme(Phrase): 

	def __init__(
	  self, relative_offset: Union[int, Fraction],
	  parent_absolute_offset: Union[int, Fraction], 
	  num_measures: int = 4) -> None:
		super().__init__(relative_offset, parent_absolute_offset, num_measures) 
		self.progressions = [
			Progression(
				ChordType("TONIC", self.beats_per_measure), 
				ChordType("PREDOMINANT", self.beats_per_measure),
				ChordType("DOMINANT", self.beats_per_measure), 
				ChordType("TONIC", self.beats_per_measure),
			),
		]
		if self.time_sig_obj.symbol != "3/4":
			half_measure_duration = self.beats_per_measure // 2
			other_progressions = (
				Progression(
					ChordType("TONIC", self.beats_per_measure),
					ChordType("DOMINANT", self.beats_per_measure),
					ChordType("TONIC", half_measure_duration),
					ChordType("DOMINANT", half_measure_duration),
					ChordType("TONIC", self.beats_per_measure)
				), 
			)
			self.progressions.extend(other_progressions)


class Score(Engraver):

	def __init__(self) -> None:
		self.phrases = []
		self.tempo = None 

	@classmethod
	def choose_random_tonic(cls) -> str:
		tonic_letter = random.choice(cls.note_letters)
		accidental_symbol = random.choice(("#", "", "b"))
		return tonic_letter + accidental_symbol

	def create_tonal_theme(self, is_embellished: bool = True) -> None:
		Engraver.style = "tonal"
		mode_choice = random.choice(("major", "minor"))
		tonic_pitch = self.choose_random_tonic()
		Engraver.scale_obj = Scale(tonic_pitch, mode_choice)
		print(f"{tonic_pitch} {mode_choice}")
		self.setup_theme(is_embellished)

	def create_modal_theme(self, is_embellished: bool = True) -> None:
		Engraver.style = "modal"
		mode_choice = random.choice(Scale.mode_wheel)
		tonic_pitch = self.choose_random_tonic()
		Engraver.scale_obj = Scale(tonic_pitch, mode_choice)
		print(f"{tonic_pitch} {mode_choice}")
		self.setup_theme(is_embellished)

	def setup_theme(self, is_embellished: bool) -> None:
		chosen_time_sig = random.choice(("6/8", "3/4", "4/4", "2/2"))
		print(f"Time sig = {chosen_time_sig}")
		Engraver.time_sig_obj = TimeSignature(chosen_time_sig)
		self.tempo = random.choice(self.time_sig_obj.tempo_range)
		new_phrase = MiniTheme(0, 0)
		new_phrase.add_melody(is_embellished)
		self.phrases.append(new_phrase)

	def export_score(self) -> None:
		self.export_lily_score()
		self.export_midi_score()

	def export_lily_score(self) -> None:
		lily_note_string = self.create_lily_note_string()
		tonic_pitch_obj = self.scale_obj.scale_pitches_seq[0]
		header_text = "\ttitle = " 
		header_text += f"\"Medley in {tonic_pitch_obj} {self.scale_obj.mode}\"\n"
		header_text += "\tcomposer = \"Robatim\""

		part_name = "melody"
		lily_tonic_pitch = tonic_pitch_obj.get_lily_format()
		beat_obj = Duration(1)
		variable_text_seq = [
			part_name, "= { \\key", f"{lily_tonic_pitch}", f"\\{self.scale_obj.mode}", 
			"\\time", f"{self.time_sig_obj.symbol}", "\\tempo", 
			f"{beat_obj.get_lily_duration()}", f"= {self.tempo}", 
			f"{lily_note_string}", "}"
		]
		variable_text = " ".join(variable_text_seq)

		score_text = "\t\\new PianoStaff <<\n"
		score_text += "\t\t\\new Staff <<\n" 
		score_text += "\t\t\t\\new Voice \\clef \"treble\" { \\"
		score_text += part_name
		score_text += " }\n\t\t>>\n"
		score_text += "\t>>\n\t\\layout {}"

		with open("logs/blank_template.txt", "r") as f:
			lily_sheet = f.read()

		lily_sheet = lily_sheet.replace("HEADER_PLACEHOLDER", header_text)
		lily_sheet = lily_sheet.replace("VARIABLE_PLACEHOLDER", variable_text)
		lily_sheet = lily_sheet.replace("SCORE_PLACEHOLDER", score_text)

		with open("logs/lily_output.txt", "w") as f:
			f.write(lily_sheet)

	def create_lily_note_string(self) -> str:
		all_phrase_markings = []
		for current_phrase in self.phrases:
			all_measure_markings = []
			for current_measure in current_phrase.measures:
				all_note_markings = []

				for current_obj in current_measure.notes:
					obj_mark = current_obj.get_lily_format()
					all_note_markings.append(obj_mark)

				all_note_markings = " ".join(all_note_markings)
				all_measure_markings.append(all_note_markings)

			all_measure_markings = " | ".join(all_measure_markings)
			all_phrase_markings.append(all_measure_markings)
		all_phrase_markings = " | ".join(all_phrase_markings)
		return all_phrase_markings

	def export_midi_score(self):
		my_midi = MIDIFile(1, eventtime_is_ticks=True)
		print(f"Tempo: {self.tempo}")
		my_midi.addTempo(0, 0, self.tempo)
		my_midi.addProgramChange(0, 0, 0, 73)

		for current_phrase in self.phrases:
			for current_measure in current_phrase.measures:
				for current_obj in current_measure.notes:
					offset_in_ticks = int(current_obj.absolute_offset * 960)
					duration_in_ticks = int(current_obj.duration * 960)
					if isinstance(current_obj, Note):
						my_midi.addNote(
							0, 0, current_obj.midi_num, offset_in_ticks, 
							duration_in_ticks, 100
						)

		try: 
			with open("theme.mid", "wb") as midi_output:
				my_midi.writeFile(midi_output)
		except PermissionError:
			print("You must close the previous midi file to overwrite it.")


if __name__ == "__main__":
	my_score = Score()
	my_score.create_modal_theme()
	my_score.export_score()
		