import random
from typing import List, Tuple, Union
from fractions import Fraction

class Engraver:

	# 4/4 time signature
	measure_duration = 1
	scale_obj = None
	roman_numerals = ("I", "II", "III", "IV", "V", "VI", "VII")

class Scale(Engraver):

	note_letters = ("A", "B", "C", "D", "E", "F", "G")

	def create_chord_pitches(self, chosen_roman_numeral, is_triad) -> List[Pitch]:

		root_index = self.roman_numerals.index(chosen_roman_numeral)
		chord_pitches = [self.scale_pitches[root_index]]

		if is_triad:
			chordal_items = 3
		else:
			chordal_items = 4
		pitch_index = root_index
		for _ in range(chordal_items - 1):
			pitch_index += 2 
			pitch_index %= 7
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


class Pitch:
	pass


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
		new_phrase = MiniPeriod(0, 0)
		new_phrase.imprint_progression()
		new_phrase.add_melody_notes()
		self.phrases.append(new_phrase)

	def export_score(self) -> None:
		pass

my_score = Score()
my_score.create_theme()
my_score.export_score()
		