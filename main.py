from __future__ import annotations
# allows use of an annotation before function definition (Python 3.7+)
import collections
import copy
import random
from typing import List, Tuple, Union
from fractions import Fraction

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
	def beat_value(self):
		return self.time_sig_obj.beat_value


class TimeSignature:

	beat_values = {
		"6/8": Fraction(3, 8),
	}

	def __init__(self, symbol: str) -> None:
		self.symbol = symbol
		if self.symbol == "6/8":
			self.beats_per_measure = 2
			self.melodic_divisions = [Fraction(1,2), Fraction(1,2)]
		self.beat_value = self.beat_values[self.symbol]


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
  

class Scale(Engraver):

	mode_wheel = (
		"ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", 
		"locrian",
	)

	def __init__(self, tonic: str = "C", mode: str = "ionian") -> None:

		self.mode = mode
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
	  self, chord_symbol: str, duration: Union[int, float, Fraction], 
	  relative_offset: Union[int, float, Fraction] = 0, 
	  parent_absolute_offset: Union[int, float, Fraction] = 0) -> None:
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


class Note(Pitch):

	def __init__(self, note_designator: Union[int, str], 
	  duration: Union[int, float, Fraction] = 0, 
	  relative_offset: Union[int, float, Fraction] = 0, 
	  parent_absolute_offset: Union[int, float, Fraction] = 0) -> None:
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

	def convert_to_lily_note(self) -> str:
		if self.octave_number > 3:
			octave_mark = "'" * (self.octave_number - 3)
		elif self.octave_number < 3:
			octave_mark = "," * (3 - self.octave_number)
		else:
			octave_mark = ""

		pitch_mark = self.pitch_letter.lower()
		if self.accidental_amount > 0:
			accidental_mark = "is" * abs(self.accidental_amount)
		if self.accidental_amount < 0:
			accidental_mark = "es" * abs(self.accidental_amount)
		else:
			accidental_mark = ""

		lily_duration = self.convert_to_lily_duration()
		return f"{pitch_mark}{accidental_mark}{octave_mark}{lily_duration}"

	def convert_to_lily_duration(self) -> str:
		absolute_duration = self.beat_value * self.duration
		if absolute_duration.numerator == 1:
			return f"{absolute_duration.denominator}"
		elif absolute_duration.numerator == 3:
			return f"{absolute_duration.denominator // 2}." 


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
			Chord(str(chord), chord.duration, current_offset, self.absolute_offset)
		)

	def imprint_note(self, note: Note) -> None:
		if self.notes:
			current_offset = self.notes[-1].relative_offset + self.notes[-1].duration
		else:
			current_offset = 0
		self.notes.append(
			Note(str(note), note.duration, current_offset, self.absolute_offset)
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
	  self, relative_offset: Union[int, float, Fraction],
	  parent_absolute_offset: Union[int, float, Fraction], 
	  num_measures: int = 8) -> None:
		self.measures = []
		self.relative_offset = relative_offset
		self.absolute_offset = relative_offset + parent_absolute_offset
		for index in range(num_measures):
			self.measures.append(
				Measure(index * self.beats_per_measure, self.absolute_offset)
			)
		self.base_melody = []

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

		base_melody_note_options = self.get_melody_options()
		base_melody_finder = self.find_base_melody(base_melody_note_options)

		next(base_melody_finder)
		if not is_embellished:
			self.set_base_rhythm()
			for current_measure in self.measures:
				print(current_measure.notes)

		# while True: 
		# 	if not next(base_melody_finder):
		# 		raise ValueError
		# 	full_melody = self.embellish_melody() 
		# 	if full_melody:
		# 		break 

		# for current_measure, measure_notes in zip(self.measures, full_melody):
		# 	current_measure.imprint_notes(measure_notes)

	def get_melody_options(self) -> List[List[Note, ...], ...]:

		base_melody_note_options = []

		all_modal_notes = self.get_modal_notes(59, 85)
		for current_measure in self.measures:
			current_offset = 0
			for measure_fraction in self.time_sig_obj.melodic_divisions:
				if self.style == "tonal":
					base_melody_note_options.append(
						current_measure.get_chord(current_offset)
					) 
				elif self.style == "modal":
					base_melody_note_options.append(all_modal_notes[:]) 
				current_offset += (self.beats_per_measure * measure_fraction)

		return base_melody_note_options

	def get_modal_notes(self, start: int, stop: int) -> List[Note, ...]:
		possible_notes = []
		for midi_num in range(start, stop):
			if self.scale_obj.is_note_diatonic(midi_num):
				possible_notes.append(Note(midi_num))
		print(f"Possible melody notes: {possible_notes}")
		return possible_notes

	def find_base_melody(
	  self, base_melody_note_options: List[List[Note, ...], ...]) -> bool:

		reference_note_options = copy.deepcopy(base_melody_note_options)
		base_melody_length = len(base_melody_note_options)
		self.base_melody = [None for _ in range(base_melody_length)]
		self.base_degrees = self.base_melody[:]

		tonic_pitch_symbol = str(self.scale_obj.scale_pitches_seq[0])
		for current_note in reference_note_options[0]:
			if tonic_pitch_symbol == current_note.pitch_symbol:
				starting_note = current_note
				break
		if starting_note.midi_num in {59, 60} and random.choice((True, False)):
			starting_note = starting_note.shift(7, 12)
		print(f"Starting note: {starting_note}")

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

					if note_index == base_melody_length:
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
					return False
					
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
		if note_index == 1:
			if abs(attempted_degree - self.base_degrees[0]) > 2:
				return False 

		if note_index == 2:
			if abs(attempted_degree - self.base_degrees[0]) > 2:
				return False
		if note_index >= 2:
			if (self.base_degrees[note_index - 2] == 
			  self.base_degrees[note_index - 1] == attempted_degree):
				return False
			if abs(attempted_degree - self.base_degrees[note_index - 1]) > 4:
				return False 
		if note_index == 3:
			motif_diff = self.base_degrees[1] - self.base_degrees[0]
			if attempted_degree - self.base_degrees[2] != motif_diff:
				return False

		if note_index == 7:
			if attempted_degree != 0:
				return False
			if self.base_degrees[0] != 0 and self.base_degrees[1:].count(0) > 2:
				return False
			for current_degree in self.base_degrees[6::-1]:
				if current_degree == 0:
					continue
				elif current_degree in {-1, 1, 2}:
					break
				else:
					return False

		return True

	def set_base_rhythm(self):

		base_melody_iter = iter(self.base_melody)
		for current_measure in self.measures:
			for measure_fraction in self.time_sig_obj.melodic_divisions:
				current_note_symbol = str(next(base_melody_iter))
				current_measure.imprint_note(
					Note(current_note_symbol, self.beats_per_measure * measure_fraction)
				)


class MiniPeriod(Phrase): 

	def __init__(
	  self, relative_offset: Union[int, float, Fraction],
	  parent_absolute_offset: Union[int, float, Fraction], 
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
		print(f"{tonic_pitch} {mode_choice}")
		Engraver.scale_obj = Scale(tonic_pitch, mode_choice)
		Engraver.time_sig_obj = TimeSignature("6/8")
		new_phrase = MiniPeriod(0, 0)
		new_phrase.add_melody(is_embellished)
		self.phrases.append(new_phrase)

	def export_score(self) -> None:
		all_phrase_markings = []
		for current_phrase in self.phrases:
			all_measure_markings = []
			for current_measure in current_phrase.measures:
				all_note_markings = []

				for current_note in current_measure.notes:
					note_mark = current_note.convert_to_lily_note()
					all_note_markings.append(note_mark)

				all_note_markings = " ".join(all_note_markings)
				all_measure_markings.append(all_note_markings)

			all_measure_markings = " | ".join(all_measure_markings)
			all_phrase_markings.append(all_measure_markings)
		all_phrase_markings = " | ".join(all_phrase_markings)

		print(all_phrase_markings)


if __name__ == "__main__":
	my_score = Score()
	my_score.create_modal_theme(False)
	my_score.export_score()
		