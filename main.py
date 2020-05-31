from __future__ import annotations
# allows use of an annotation before function definition (Python 3.7+)
import random
from typing import List, Tuple, Union
from fractions import Fraction

class Engraver:

	# 4/4 time signature
	measure_duration = 1
	scale_obj = None
	roman_numerals = ("I", "II", "III", "IV", "V", "VI", "VII")
	note_letters = ("A", "B", "C", "D", "E", "F", "G")


def collapse_magnitude(amount: int) -> int:
	if amount > 0:
		return 1
	if amount < 0:
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


class ChordType:

	def __init__(
	  self, chord_designator: str, chord_conditional: str, 
	  duration: Union[int, float, Fraction] = 0) -> None:
		self.duration = duration
		self.chord_designator = chord_designator
		self.chord_conditional = chord_conditional  

	def realize(self) -> Chord:
		if self.chord_designator == "SINGLE":
			return Chord(self.chord_conditional, self.duration)


class Note(Engraver):

	def __init__(self, midi_pitch: int) -> None:
		self.midi_pitch = midi_pitch
		self.pitch_name = ""


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

	def imprint_progression(self) -> None:
		progression = random.choice(self.progressions)
		chosen_progression = progression.realize()
		relative_offset = 0
		for current_chord in chosen_progression:
			measure_index = relative_offset // self.measure_duration
			self.measures[measure_index].imprint_chord(current_chord)
			relative_offset += current_chord.duration 


class MiniPeriod(Phrase): 

	def __init__(
	  self, relative_offset: Union[int, float, Fraction],
	  parent_absolute_offset: Union[int, float, Fraction], 
	  num_measures: int = 4) -> None:
		super().__init__(relative_offset, parent_absolute_offset, num_measures)
		self.progressions = (
			Progression( # e.g., I II6 V I
				ChordType("SINGLE", "I", self.measure_duration), 
				ChordType("MULTI", "SUBDOM_-1", self.measure_duration),
				ChordType("MULTI", "DOM_-1", self.measure_duration), 
				ChordType("SINGLE", "I", self.measure_duration),
			),
		)

	def add_melody_notes(self) -> None:
		pass


class Progression:
	
	def __init__(self, *args: Tuple[ChordType, ...]) -> None:
		self.chord_types = args

	def realize(self) -> List[Chord]:
		chord_sequence = []
		for chord_type in self.chord_types:
			chord_sequence.append(chord_type.realize())
		return chord_sequence


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
		