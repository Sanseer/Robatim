from __future__ import annotations
# allows use of an annotation before function definition (Python 3.7+)
import collections
import random
from typing import List, Tuple, Union
from fractions import Fraction

class Engraver:

	# 4/4 time signature
	measure_duration = 1
	scale_obj = None
	time_sig_obj = None
	roman_numerals = ("I", "II", "III", "IV", "V", "VI", "VII")
	note_letters = ("A", "B", "C", "D", "E", "F", "G")


def collapse_magnitude(amount: int) -> int:
	if amount > 0:
		return 1
	elif amount < 0:
		return - 1
	else:
		return 0


class Pitch(Engraver):
	
	def __init__(self, pitch_symbol: str) -> None:

		self.pitch_letter = pitch_symbol[0].upper()
		if self.pitch_letter not in self.note_letters:
			raise ValueError
		self.accidental_symbol = pitch_symbol[1:]
		self.accidental_amount = Pitch.accidental_symbol_to_amount(self.accidental_symbol)

	def __str__(self) -> str:
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
		pitch_letter_convert = self.change_pitch_letter(self, letter_increment)
		final_pitch_obj = self.change_pitch_accidental(
			pitch_letter_convert, pitch_increment
		)
		return final_pitch_obj

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
  

class Scale(Engraver):

	def __init__(self, tonic: str = "C", mode: str = "ionian") -> None:

		mode_wheel = (
			"ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", 
			"locrian",
		)
		scale_index = mode_wheel.index(mode.lower())
		old_pitch_obj = Pitch(tonic)
		self.scale_pitches = [old_pitch_obj]

		scale_increments = (2, 2, 1, 2, 2, 2, 1)
		for _ in range(6):
			new_pitch_obj = old_pitch_obj.shift(1, scale_increments[scale_index])
			self.scale_pitches.append(new_pitch_obj)
			old_pitch_obj = new_pitch_obj
			scale_index = (scale_index + 1) % 7

	def create_chord_pitches(self, chosen_roman_numeral: str, is_triad: bool) -> List[Pitch]:

		root_index = self.roman_numerals.index(chosen_roman_numeral)
		chord_pitches = [self.scale_pitches[root_index]]

		if is_triad:
			chordal_items = 3
		else:
			chordal_items = 4
		pitch_index = root_index
		for _ in range(chordal_items - 1):
			pitch_index = (pitch_index + 2) % 7 
			chord_pitches.append(self.scale_pitches[pitch_index])

		return chord_pitches


class Chord(Engraver):

	triads_figured_bass = {"": 0, "5/3": 0, "6": 1, "6/3": 1, "6/4": 2}
	sevenths_figured_bass = {
		"7": 0, "7/5/3": 0, "6/5": 1, "6/5/3": 1, "4/3": 2, "6/4/3": 2, 
		"6/4/2": 3, "4/2": 3, "2": 3,
	}

	def __init__(
	  self, chord_symbol: str, duration: Union[int, float, Fraction], 
	  relative_offset: Union[int, float, Fraction] = 0, 
	  parent_absolute_offset: Union[int, float, Fraction] = 0) -> None:
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset
		self.duration = duration
		self.pitches = []

		if "V" in chord_symbol or "I" in chord_symbol:
			for num in range(3, 0, -1):
				attempted_roman_numeral = chord_symbol[:num]
				if attempted_roman_numeral in self.roman_numerals:
					bass_figure = chord_symbol[num:]
					break
			else:
				raise ValueError

			if bass_figure in triads_figured_bass:
				inversion_position = triads_figured_bass[bass_figure]
				is_triad = True
			elif bass_figure in sevenths_figured_bass:
				inversion_position = sevenths_figured_bass[bass_figure]
				is_triad = False
			else:
				raise ValueError

			self.pitches = self.scale_obj.create_chord_pitches(
				attempted_roman_numeral, is_triad
			)


class MidiNote(Pitch):

	def __init__(self, pitch_symbol: str, octave_num: int) -> None:
		super().__init__(pitch_symbol)


class Measure(Engraver):

	def __init__(
	  self, relative_offset: Union[int, float, Fraction], 
	  parent_absolute_offset: Union[int, float, Fraction]) -> None:
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
			Chord(chord.symbol, chord.duration, current_offset, self.absolute_offset)
		)

ChordType = collections.namedtuple("ChordType", ["function", "duration"])

class Phrase(Engraver):

	def __init__(
	  self, relative_offset: Union[int, float, Fraction],
	  parent_absolute_offset: Union[int, float, Fraction], 
	  num_measures: int = 8) -> None:
		self.measures = []
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset
		for index in range(num_measures):
			self.measures.append(
				Measure(index * self.measure_duration, self.absolute_offset)
			)
		self.base_melody = []

	def imprint_progression(self) -> None:
		progression = random.choice(self.progressions)
		chosen_progression = progression.realize()
		relative_offset = 0
		for current_chord in chosen_progression:
			measure_index = relative_offset // self.measure_duration
			self.measures[measure_index].imprint_chord(current_chord)
			relative_offset += current_chord.duration 

	def add_melody_notes(self) -> None:

		melodic_divisions = self.time_sig_obj.melodic_divisions
		base_melody_degree_options = []
		base_melody_pitch_options = []
		base_melody_duration = self.measure_duration / melodic_divisions

		for current_measure in self.measures:
			current_offset = 0
			for _ in range(melodic_divisions):
				base_melody_pitch_options.append([])
				base_melody_degree_options.append([])
				current_chord = current_measure.get_chord(current_offset)

				for current_pitch in current_chord.pitches:
					base_melody_pitch_options[-1].append(current_pitch)
					current_degree = self.scale_obj.get_degree(current_pitch)
					base_melody_degree_options[-1].append(current_degree)
				current_offset += base_melody_duration

		base_melody_iter = self.find_melody(
			base_melody_pitch_options, base_melody_degree_options
		)

		while True:
			self.base_melody = next(base_melody_iter, None)
			if self.base_melody is None:
				raise ValueError
			full_melody = self.embellish_melody() 
			if full_melody:
				break 

		for current_measure, measure_notes in zip(self.measures, full_melody):
			current_measure.imprint_notes(measure_notes)


class MiniPeriod(Phrase): 

	def __init__(
	  self, relative_offset: Union[int, float, Fraction],
	  parent_absolute_offset: Union[int, float, Fraction], 
	  num_measures: int = 4) -> None:
		super().__init__(relative_offset, parent_absolute_offset, num_measures)
		self.progressions = (
			Progression( # e.g., I II6 V I
				ChordType("TONIC", self.measure_duration), 
				ChordType("PREDOMINANT", self.measure_duration),
				ChordType("DOMINANT", self.measure_duration), 
				ChordType("TONIC", self.measure_duration),
			),
		)

	def find_melody(self, base_melody_pitch_options, base_melody_degree_options):
		reference_pitch_options = copy.deepcopy(base_melody_pitch_options)
		reference_degree_options = copy.deepcopy(base_melody_degree_options)

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


class Score(Engraver):

	def __init__(self) -> None:
		self.phrases = []

	def create_theme(self) -> None:
		Engraver.scale_obj = Scale("C")
		new_phrase = MiniPeriod(0, 0)
		new_phrase.imprint_progression()
		new_phrase.add_melody_notes()
		self.phrases.append(new_phrase)

	def export_score(self) -> None:
		pass


if __name__ == "__main__":
	my_score = Score()
	my_score.create_theme()
	my_score.export_score()
		