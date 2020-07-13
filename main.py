from __future__ import annotations
# allows use of an annotation before function definition (Python 3.7+)
import collections
import copy
import random
from typing import Dict, List, Tuple, Union
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


class Pitch(Engraver):
	
	def __init__(self, pitch_symbol: str) -> None:

		self.pitch_letter = pitch_symbol[0].upper()
		if self.pitch_letter not in self.note_letters:
			raise ValueError
		self.accidental_symbol = pitch_symbol[1:]
		self.accidental_amount = Pitch.accidental_symbol_to_amount(self.accidental_symbol)

	def __repr__(self) -> str:
		return self.pitch_letter + self.accidental_symbol 

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

		# object parameter in both functions for consistency
		# outward-facing methods pass pitch objects implicitly
		# inward-facing methods pass pitch objects explicitly
		interim_obj = self.change_pitch_letter(self, letter_increment)
		final_obj = self.change_pitch_accidental(
			interim_obj, pitch_increment
		)
		return final_obj

	def change_pitch_letter(self, old_pitch_obj: Pitch, letter_increment: int) -> Pitch:

		if letter_increment == 0:
			return old_pitch_obj

		letter_direction = collapse_magnitude(letter_increment)
		half_step_letters = {"B", "C", "E", "F"}
		new_accidental_amount = old_pitch_obj.accidental_amount
		old_pitch_letter = old_pitch_obj.pitch_letter
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

	def change_pitch_accidental(self, old_pitch_obj: Pitch, pitch_increment: int) -> Pitch:

		new_accidental_amount = old_pitch_obj.accidental_amount + pitch_increment
		new_accidental_symbol = Pitch.accidental_amount_to_symbol(new_accidental_amount)
		return Pitch(old_pitch_obj.pitch_letter + new_accidental_symbol)

	def get_lily_format(self) -> str:
		letter_mark = self.pitch_letter.lower()
		if self.accidental_amount > 0:
			accidental_mark = "is" * abs(self.accidental_amount)
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
	special_degrees = {
		"ionian": 0, "dorian": 5, "phrygian": 1, "lydian": 3, "mixolydian": 6, 
		"aeolian": 2, "locrian": 4,
	}

	def __init__(self, tonic: str = "C", mode: str = "ionian") -> None:

		self.mode = mode
		self.special_degree = self.special_degrees[mode]
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
		scale_index = self.mode_wheel.index(self.mode.lower())

		for _ in range(6):
			current_increment = self.scale_increments[scale_index]
			new_pitch_obj = old_pitch_obj.shift(1, current_increment)
			self.scale_pitches_seq.append(new_pitch_obj)

			current_midi_num = (current_midi_num + current_increment) % 12
			self.scale_pitches_dict[new_pitch_obj] = current_midi_num 
			old_pitch_obj = new_pitch_obj
			scale_index = (scale_index + 1) % 7

	def create_chord_pitches(self, chosen_roman_numeral: str, is_triad: bool) -> List[Pitch]:

		root_index = self.roman_numerals.index(chosen_roman_numeral)
		chord_pitches = [self.scale_pitches_seq[root_index]]

		if is_triad:
			chordal_items = 3
		else:
			chordal_items = 4
		pitch_index = root_index
		for _ in range(chordal_items - 1):
			pitch_index = (pitch_index + 2) % 7 
			chord_pitches.append(self.scale_pitches_seq[pitch_index])

		return chord_pitches

	def is_note_diatonic(self, midi_num: int) -> bool:
		base_midi_num = midi_num % 12
		return base_midi_num in self.scale_pitches_dict.values()

	def get_absolute_degree(self, chosen_note: Note) -> int:
		chosen_pitch_name = chosen_note.pitch_symbol
		for scale_degree, pitch_obj in enumerate(self.scale_pitches_seq):
			if str(pitch_obj) == chosen_pitch_name:
				return scale_degree 

	def get_relative_degree(self, starting_note: Note, attempted_note: Note) -> int:
		if starting_note == attempted_note:
			return 0
		attempted_degree = self.get_absolute_degree(attempted_note)
		midi_pitch_diff = attempted_note.midi_num - starting_note.midi_num
		octave_amount = midi_pitch_diff // 12
		return attempted_degree + (octave_amount * 7)


class Chord(Engraver):

	triads_figured_bass = {"": 0, "5/3": 0, "6": 1, "6/3": 1, "6/4": 2}
	sevenths_figured_bass = {
		"7": 0, "7/5/3": 0, "6/5": 1, "6/5/3": 1, "4/3": 2, "6/4/3": 2, 
		"6/4/2": 3, "4/2": 3, "2": 3,
	}

	def __init__(
	  self, chord_symbol: str, duration: Union[int, Fraction], 
	  relative_offset: Union[int, Fraction] = 0, 
	  parent_absolute_offset: Union[int, Fraction] = 0) -> None:
		self.duration = duration
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset
		self.pitches = []

		if "V" in chord_symbol or "I" in chord_symbol:
			for num in range(3, 0, -1):
				attempted_roman_numeral = chord_symbol[:num]
				if attempted_roman_numeral in self.roman_numerals:
					bass_figure = chord_symbol[num:]
					break
			else:
				raise ValueError

			if bass_figure in self.triads_figured_bass:
				self.inversion_position = self.triads_figured_bass[bass_figure]
				is_triad = True
			elif bass_figure in self.sevenths_figured_bass:
				self.inversion_position = self.sevenths_figured_bass[bass_figure]
				is_triad = False
			else:
				raise ValueError

			self.pitches = self.scale_obj.create_chord_pitches(
				attempted_roman_numeral, is_triad
			)


class Duration(Engraver):

	def __init__(self, duration: Union[int, Fraction] = 0, 
	  relative_offset: Union[int, Fraction] = 0, 
	  parent_absolute_offset: Union[int, Fraction] = 0) -> None:
		self.duration = duration
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset

	def get_lily_duration(self) -> str:
		beat_value = self.time_sig_obj.beat_value
		absolute_duration = beat_value * self.duration
		if absolute_duration.numerator == 1:
			return f"{absolute_duration.denominator}"
		elif absolute_duration.numerator == 3:
			return f"{absolute_duration.denominator // 2}." 


class Note(Pitch, Duration):

	def __init__(self, note_designator: Union[int, str], 
	  duration: Union[int, Fraction] = 0, 
	  relative_offset: Union[int, Fraction] = 0, 
	  parent_absolute_offset: Union[int, Fraction] = 0) -> None:
		if isinstance(note_designator, str):
			self.create_note_from_note_symbol(note_designator)
		elif isinstance(note_designator, int):
			self.create_note_from_midi_num(note_designator)
		self.duration = duration
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset

	def create_note_from_midi_num(self, chosen_midi_num) -> None:
		self.midi_num = chosen_midi_num
		base_midi_num = chosen_midi_num % 12

		for pitch_obj, current_midi_num in self.scale_obj.scale_pitches_dict.items():
			if base_midi_num == current_midi_num:
				break
		else:
			raise ValueError
		self.pitch_symbol = str(pitch_obj)
		super().__init__(self.pitch_symbol)
		
		self.octave_number = (self.midi_num // 12) - 1
		if self.pitch_letter == "B" and self.accidental_amount > 0:
			self.octave_number -= 1
		elif self.pitch_letter == "C" and self.accidental_amount < 0:
			self.octave_number += 1

	def create_note_from_note_symbol(self, note_symbol: str) -> None:
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

	def change_pitch_letter(self, old_note_obj, letter_increment: int) -> Note:
		if letter_increment == 0:
			return old_note_obj
		old_pitch_obj = Pitch(old_note_obj.pitch_symbol)
		new_pitch_obj = super().change_pitch_letter(
			old_pitch_obj, letter_increment
		)

		pitch_letter = old_pitch_obj.pitch_letter
		letter_index = self.note_letters.index(pitch_letter)
		if letter_increment < 0:
			change_letter = "B"
			letter_direction = -1
		elif letter_increment > 0:
			change_letter = "C"
			letter_direction = 1

		new_octave_number = old_note_obj.octave_number
		for _ in range(abs(letter_increment)):
			letter_index = (letter_index + letter_direction) % 7 
			pitch_letter = self.note_letters[letter_index]
			if pitch_letter == change_letter:
				new_octave_number += letter_direction

		return Note(f"{new_pitch_obj}{new_octave_number}")

	def change_pitch_accidental(self, old_note_obj, pitch_increment: int) -> Note:
		old_pitch_obj = Pitch(old_note_obj.pitch_symbol)
		new_pitch_obj = super().change_pitch_accidental(
			old_pitch_obj, pitch_increment
		)
		return Note(f"{new_pitch_obj}{old_note_obj.octave_number}")

	def scalar_shift(self, scale_increment: int) -> None:
		for scale_index, pitch_obj in enumerate(self.scale_obj.scale_pitches_seq):
			if str(pitch_obj) == self.pitch_symbol:
				break
		final_index = (scale_index + scale_increment) % 7

		final_pitch_obj = self.scale_obj.scale_pitches_seq[final_index]
		interim_obj = self.change_pitch_letter(self, scale_increment)
		accidental_diff = final_pitch_obj.accidental_amount - interim_obj.accidental_amount
		return self.change_pitch_accidental(interim_obj, accidental_diff)

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

ChordRule = collections.namedtuple("ChordRule", ["function", "parameters"])

class Progression:

	all_chords = {
		"TONIC": ("I", "I6"), 
		"PREDOMINANT": ("VI", "IV6", "IV", "II6", "II"),
		"DOMINANT": ("I64", "V42", "V43", "VII6", "V65", "V6", "V"),
	}

	chord_rules = {}
	
	def __init__(self, *args: Tuple[ChordType, ...]) -> None:
		self.chord_types = args

	def realize(self) -> List[Chord, ...]:

		reference_chord_combos = []
		chosen_chords = []
		remaining_chord_combos = []
		for chord_type in self.chord_types:
			possible_chords = list(self.all_chords[chord_type.function])
			reference_chord_combos.append(possible_chords)
			chosen_chords.append(None)
			remaining_chord_combos.append(None)

		chord_index = 0
		remaining_chord_combos[chord_index] = reference_chord_combos[chord_index][:]
		while None in chosen_chords:
			if remaining_chord_combos[chord_index]:
				chosen_chord = random.choice(remaining_chord_combos[chord_index])
				remaining_chord_combos[chord_index].remove(chosen_chord)

				is_chord_valid = True
				for rule_obj in self.chord_rules[chosen_chord]:
					is_chord_rule_valid = rule_obj.function(*rule_obj.parameters)
					if not is_chord_rule_valid:
						is_chord_valid = False
						break
				else:
					chosen_chords[chord_index] = chosen_chord
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
				chosen_chords[chord_index] = None

		final_chords = []
		for chord_symbol, chord_type in zip(chosen_chords, self.chord_types):
			final_chords.append(Chord(chord_symbol, chord_type.duration))
		return final_chords

ChordType = collections.namedtuple("ChordType", ["function", "duration"])

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
		self.starting_note = None
		self.embellish_rhythms = []
		self.has_rest_ending = False

	def imprint_progression(self) -> None:
		progression = random.choice(self.progressions)
		chosen_progression = progression.realize()
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
		self.has_rest_ending = self.base_degrees[-2] == 0

		rhythm_finder = self.choose_embellish_rhythms()
		self.embellish_rhythms = next(rhythm_finder)
		print(f"Embellish rhythms: {self.embellish_rhythms}")
		while True:
			full_melody = self.embellish_melody()
			if full_melody:
				break
			if not next(base_melody_finder):
				raise ValueError
			self.has_rest_ending = self.base_degrees[-2] == 0
			self.embellish_rhythms = next(rhythm_finder)
			print(f"Embellish rhythms: {self.embellish_rhythms}")

		full_melody_iter = iter(full_melody)
		for current_measure in self.measures:
			for _ in self.time_sig_obj.melodic_divisions:
				note_group = next(full_melody_iter)
				for measure_note in note_group:
					if isinstance(measure_note, Note):
						current_measure.imprint_temporal_obj(measure_note)
		rest_ending_count = full_melody.count("REST")
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

	def get_modal_notes(self, start: int, stop: int) -> List[Note]:
		possible_notes = []
		for midi_num in range(start, stop):
			if self.scale_obj.is_note_diatonic(midi_num):
				possible_notes.append(Note(midi_num))
		print(f"Possible melody notes: {possible_notes}")
		return possible_notes

	def find_base_melody(
	  self, base_melody_note_options: List[List[Note]]) -> bool:

		reference_note_options = copy.deepcopy(base_melody_note_options)
		self.base_melody = [None for _ in base_melody_note_options]
		self.base_degrees = self.base_melody[:]

		tonic_pitch_symbol = str(self.scale_obj.scale_pitches_seq[0])
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

		while True:
			if current_note_options: 
				attempted_note = random.choice(current_note_options)
				current_note_options.remove(attempted_note)
				attempted_scale_degree = self.scale_obj.get_relative_degree(
					starting_note, attempted_note
				)

				if self.test_melody_note(
				  note_index, attempted_note, attempted_scale_degree):
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
					yield False
					
				note_index -= 1
				current_note_options = base_melody_note_options[note_index]
				self.base_melody[note_index] = None
				self.base_degrees[note_index] = None

	def test_melody_note(
	  self, note_index: int, attempted_note: Note, attempted_degree: int) -> bool:

		if not -2 <= attempted_degree <= 9:
			return False
		if note_index == 0:
			if attempted_degree not in {0, 2, 4}:
				return False
		if (1 <= note_index <= 2 and 
		  abs(attempted_degree - self.base_degrees[0]) > 2):
			return False 

		if note_index >= 2:
			if (self.base_degrees[note_index - 2] == 
			  self.base_degrees[note_index - 1] == attempted_degree):
				return False
			current_leap = attempted_degree - self.base_degrees[note_index - 1]
			previous_leap = self.base_degrees[note_index - 1] - self.base_degrees[note_index - 2]
			if abs(current_leap) > 4:
				return False 
			elif (abs(previous_leap) > 2 and 
			  collapse_magnitude(previous_leap) == collapse_magnitude(current_leap)):
				return False
			elif abs(previous_leap) == 4 and abs(current_leap) != 1:
				return False
			elif abs(previous_leap) == 3 and not 1 <= abs(current_leap) <= 2:
				return False
			if attempted_degree != 0 and self.base_degrees.count(attempted_degree) > 3:
				return False

		if note_index == 3:
			motif_diff = self.base_degrees[1] - self.base_degrees[0]
			if current_leap != motif_diff:
				return False
			if attempted_degree < 0:
				return False
			for current_degree in self.base_degrees[:note_index]:
				if current_degree < 0:
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
		if note_index == 4:
			if attempted_degree in {self.base_degrees[0], self.base_degrees[2]}:
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
		if note_index == 6:
			if attempted_degree != 0 and self.time_sig_obj.symbol in {"6/8", "3/4"}:
				return False
			if attempted_degree != 0 and current_leap != 0:
				motif_shift = self.base_degrees[2] - self.base_degrees[0]
				if self.base_degrees[4] - self.base_degrees[2] != motif_shift:
					return False
				if attempted_degree - self.base_degrees[4] != motif_shift:
					return False
		if note_index == 7:
			if attempted_degree != 0:
				return False
			if self.base_degrees[0] != 0 and self.base_degrees.count(0) > 2:
				return False
			for current_degree in self.base_degrees[6::-1]:
				if current_degree == 0:
					continue
				elif current_degree in {-1, 1, 2}:
					break
				else:
					return False

			negative_degree = False
			negative_turns = 0
			for current_degree in self.base_degrees[6::-1]:
				if current_degree < 0:
					if not negative_degree:
						negative_turns += 1
					negative_degree = True
				else:
					negative_degree = False
			if negative_turns > 2:
				return False

			special_degree = self.scale_obj.special_degree
			special_degree_set = {special_degree, special_degree + 7, special_degree - 7}

			if (attempted_degree not in special_degree_set and 
			  not special_degree_set & set(self.base_degrees)):
				return False

		return True

	def imprint_base_melody(self):

		base_melody_iter = iter(self.base_melody)
		for current_measure in self.measures:
			for measure_fraction in self.time_sig_obj.melodic_divisions:
				current_note_symbol = str(next(base_melody_iter))
				current_measure.imprint_temporal_obj(
					Note(current_note_symbol, self.beats_per_measure * measure_fraction)
				)

	def choose_embellish_rhythms(self) -> None:

		if self.time_sig_obj.symbol == "3/4":
			possible_rhythms = [
				["I1", "I2", "I1", "I2", "I1", "I2", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I3", "I2", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I4", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I3", "I4", "REST", "REST"]
			]
			has_rest_ending_rhythm = self.realize_embellish_rhythm(possible_rhythms)
		else:
			possible_rhythms = [
				["I1", "I1", "I1", "I1", "I1", "I1", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I1", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I2", "I2", "REST", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I2", "REST", "REST"],
			]
			has_rest_ending_rhythm = self.realize_embellish_rhythm(possible_rhythms)
			possible_rhythms = [
				["I1", "I1", "I1", "I1", "I1", "I1", "I1", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I1", "I1", "REST"],
				["I1", "I2", "I1", "I2", "I2", "I2", "I1", "REST"],
				["I1", "I2", "I1", "I2", "I2", "I2", "I2", "REST"],
				["I1", "I2", "I1", "I2", "I1", "I2", "I1", "REST"],
			]
			no_rest_ending_rhythm = self.realize_embellish_rhythm(possible_rhythms)

		while True:
			if self.has_rest_ending:
				yield has_rest_ending_rhythm
			else:
				yield no_rest_ending_rhythm

	def realize_embellish_rhythm(
	  self, possible_rhythms: List[List[str]]) -> List[Union[Tuple[int, ...], str]]:
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
		full_melody = []
		chosen_contours = []

		for note_index, embellish_rhythm in enumerate(self.embellish_rhythms):
			if embellish_rhythm == "REST":
				full_melody.append("REST")
			else:
				full_melody.append(None)
				chosen_contours.append(None)
				possible_contours = self.create_contour_options(note_index, embellish_rhythm)
				if not possible_contours:
					print("Embellishment not possible.")
					return []
				embellish_contour_options.append(possible_contours)

		note_index = 0
		reference_contour_options = copy.deepcopy(embellish_contour_options)
		current_contour_options = embellish_contour_options[note_index]

		features = {}
		if self.embellish_rhythms[0] == self.embellish_rhythms[1]:
			features["motif_rhythm"] = "single"
		else:
			features["motif_rhythm"] = "double"
		features["repeat_ending"] = random.choice(("exact", "accelerate"))
		print(f"Features: {features}")

		while True:
			if current_contour_options:
				chosen_contour = random.choice(current_contour_options)
				current_contour_options.remove(chosen_contour)
				chosen_contours[note_index] = chosen_contour

				starting_note = self.base_melody[note_index]
				full_melody[note_index] = self.realize_melody_contour(
					starting_note, chosen_contour
				)

				if (self.test_contour(note_index, chosen_contours, features) and 
				  self.test_embellishment(note_index, full_melody)):
					note_index += 1
					if None not in full_melody:
						return self.add_embellish_durations(full_melody)
					current_contour_options = embellish_contour_options[note_index]
				else:
					full_melody[note_index] = None
					chosen_contours[note_index] = None
			else:
				embellish_contour_options[note_index] = (
					reference_contour_options[note_index][:]
				)
				if note_index == 0:
					print("Embellishment failed.")
					return []
				note_index -= 1
				current_contour_options = embellish_contour_options[note_index]
				full_melody[note_index] = None
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
		for melodic_idea in all_contour_options[leap_distance]:
			if len(melodic_idea) == embellish_length:
				possible_contours.append(melodic_idea)

		return possible_contours

	def realize_melody_contour(
	  self, starting_note: Note, chosen_contour: Tuple[int, ...]) -> List[Note]:

		realized_melody_fragment = []
		for melody_shift in chosen_contour:
			new_note = starting_note.scalar_shift(melody_shift)
			realized_melody_fragment.append(new_note)
		return realized_melody_fragment

	def test_contour(
	  self, note_index: int, chosen_contours: List[Union[Tuple[int, ...], None]], 
	  features: Dict[str, str]) -> bool:
		if (note_index in {2, 3} and chosen_contours[note_index] != 
		  chosen_contours[note_index - 2]):
			return False
		if note_index in {4, 5} and features["motif_rhythm"] == "single":
			if features["repeat_ending"] == "exact":
				if chosen_contours[note_index] != chosen_contours[note_index - 2]:
					return False
			elif features["repeat_ending"] == "accelerate": 
				if note_index == 5 and chosen_contours[5] != chosen_contours[4]:
					return False
				if chosen_contours[4] not in chosen_contours[2:4]:
					return False
		return True

	def test_embellishment(
	  self, note_index: int, full_melody: List[Union[List[Note], str, None]]) -> bool:
		if note_index >= 2 and note_index % 2 == 0:
			last_previous_note = full_melody[note_index - 1][-1]
			current_first_note = full_melody[note_index][0]
			bar_leap = current_first_note.midi_num - last_previous_note.midi_num
			if abs(bar_leap >= 3): 
				leap_direction = collapse_magnitude(bar_leap)
				for current_note in full_melody[note_index]:
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

		if note_index in {5, 6} and full_melody[note_index][-1] == self.starting_note:
			if self.has_rest_ending and note_index == 5:
				return False
			if not self.has_rest_ending and note_index == 6:
				return False
		return True

	def add_embellish_durations(
	  self, unspaced_melody: List[Union[List[Note], str]]) -> List[Union[List[Note], str]]:
		finalized_melody = []
		melodic_divisions_iter = itertools.cycle(self.time_sig_obj.melodic_divisions)
		for note_group, embellish_rhythm in zip(unspaced_melody, self.embellish_rhythms):
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
		return finalized_melody

	def finalize_theme(self, rest_ending_count: int) -> None:
		rest_ending_symbols = self.time_sig_obj.rest_ending[rest_ending_count]
		starting_note_str = str(self.starting_note)

		for symbol, duration in rest_ending_symbols:
			if symbol == "REST":
				self.measures[-1].imprint_temporal_obj(Rest(duration))
			elif symbol == "NOTE":
				self.measures[-1].imprint_temporal_obj(Note(starting_note_str, duration))


class MiniPeriod(Phrase): 

	def __init__(
	  self, relative_offset: Union[int, Fraction],
	  parent_absolute_offset: Union[int, Fraction], 
	  num_measures: int = 4) -> None:
		super().__init__(relative_offset, parent_absolute_offset, num_measures)
		self.progressions = (
			Progression( # e.g., I II6 V I
				ChordType("TONIC", self.beats_per_measure), 
				ChordType("PREDOMINANT", self.beats_per_measure),
				ChordType("DOMINANT", self.beats_per_measure), 
				ChordType("TONIC", self.beats_per_measure),
			),
		)


class Score(Engraver):

	def __init__(self) -> None:
		self.phrases = []
		self.tempo = None 

	def choose_random_tonic(self) -> str:
		tonic_letter = random.choice(self.note_letters)
		accidental_symbol = random.choice(("#", "", "b"))
		return tonic_letter + accidental_symbol

	def create_tonal_theme(self) -> None:
		tonic_pitch = self.choose_random_tonic()
		mode_choice = random.choice(("major", "minor"))
		Engraver.scale_obj = Scale(tonic_pitch, mode_choice)
		new_phrase = MiniPeriod(0, 0)
		new_phrase.add_melody()
		self.phrases.append(new_phrase)

	def create_modal_theme(self, is_embellished: bool = True) -> None:
		Engraver.style = "modal"
		tonic_pitch = self.choose_random_tonic()
		mode_choice = random.choice(Scale.mode_wheel)

		Engraver.scale_obj = Scale(tonic_pitch, mode_choice)
		chosen_time_sig = random.choice(("6/8", "3/4", "4/4", "2/2"))
		print(f"{tonic_pitch} {mode_choice} in {chosen_time_sig}")
		Engraver.time_sig_obj = TimeSignature(chosen_time_sig)
		self.tempo = random.choice(self.time_sig_obj.tempo_range)
		new_phrase = MiniPeriod(0, 0)
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
		