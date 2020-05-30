import random
from typing import List, Tuple, Union
from fractions import Fraction

class Engraver:

	# 4/4 time signature
	measure_duration = 1


class Chord(Engraver):

	def __init__(
	  self, symbol: str, duration: Union[int, float, Fraction], 
	  relative_offset: Union[int, float, Fraction], 
	  parent_absolute_offset: Union[int, float, Fraction]) -> None:
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset
		self.duration = duration


class ChordType:

	def __init__(
	  self, chord_designator: str, 
	  duration: Union[int, float, Fraction] = 0) -> None:
		self.duration = duration

	def realize(self) -> Chord:
		pass


class Note(Engraver):

	def __init__(self, midi_pitch: int) -> None:
		self.midi_pitch = midi_pitch


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
				ChordType("RAW_I", self.measure_duration), 
				ChordType("POS_SUBDOM_-1", self.measure_duration),
				ChordType("POS_DOM_-1", self.measure_duration), 
				ChordType("RAW_I", self.measure_duration),
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
		