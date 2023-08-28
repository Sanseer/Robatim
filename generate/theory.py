from __future__ import annotations

# allows use of an annotation before function definition (Python 3.7+)
import random
from fractions import Fraction
from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Any, Callable, Iterator, TypeVar
import copy


def create_reversible_map(old_mapping: dict[str, str]) -> dict[str, str]:
    new_mapping = {}
    for key, value in old_mapping.items():
        new_mapping[key] = value
        new_mapping[value] = key

    return new_mapping


# PEP 673
TStringDefinedEntity = TypeVar("TStringDefinedEntity", bound="StringDefinedEntity")


class StringDefinedEntity:
    def __init__(self, symbol: str) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"'{self}'"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def clone(self: TStringDefinedEntity) -> TStringDefinedEntity:
        return self.__class__(str(self))

    @staticmethod
    def split_by_characters(
        input_string: str, segment1_identifiers: set[str]
    ) -> tuple[str, str]:
        for index, character in enumerate(input_string):
            if character not in segment1_identifiers:
                string_segment1 = input_string[:index]
                string_segment2 = input_string[index:]
                break
        else:
            string_segment1 = input_string
            string_segment2 = ""

        return string_segment1, string_segment2


class ValueComparator:
    def __init__(self) -> None:
        self.value: int
        raise NotImplementedError

    def __lt__(self, other: ValueComparator) -> bool:
        return self.value < other.value

    def __le__(self, other: ValueComparator) -> bool:
        return self.value <= other.value

    def __gt__(self, other: ValueComparator) -> bool:
        return self.value > other.value

    def __ge__(self, other: ValueComparator) -> bool:
        return self.value >= other.value


class Accidental(StringDefinedEntity, ValueComparator):
    def __init__(self, symbol: str | None = None) -> None:
        if symbol is None:
            self.value = random.choice([-1, 0, 1])
        else:
            self.value = len(symbol)

            if symbol:
                used_accidental_set = set(symbol)
                if len(used_accidental_set) != 1:
                    raise ValueError
                if used_accidental_set - {"b", "#"}:
                    raise ValueError
                if "b" in used_accidental_set:
                    self.value *= -1

    def __str__(self) -> str:
        if self.value < 0:
            chosen_symbol = "b"
        elif self.value > 0:
            chosen_symbol = "#"
        else:
            return ""

        return chosen_symbol * abs(self.value)

    def increment(self, amount: int) -> None:
        self.value += amount


TGenericPitch = TypeVar("TGenericPitch", bound="GenericPitch")


class GenericPitch(StringDefinedEntity):
    letters = ("C", "D", "E", "F", "G", "A", "B")

    def __init__(self, symbol: str | None = None) -> None:
        if symbol is None:
            self.letter = random.choice(self.letters)
            self.accidental = Accidental()
        elif not symbol or symbol[0] not in self.letters:
            raise ValueError
        else:
            self.letter = symbol[0]
            self.accidental = Accidental(symbol[1:])

    def __str__(self) -> str:
        return f"{self.letter}{self.accidental}"

    def increment_value(self, amount: int) -> None:
        self.accidental.increment(amount)

    def increment_letter(self, amount: int) -> None:
        if amount > 0:
            direction = 1
            half_steps = {"F", "C"}
        elif amount < 0:
            direction = -1
            half_steps = {"E", "B"}
        else:
            return

        current_index = self.letters.index(self.letter)

        for _ in range(abs(amount)):
            current_index += direction
            current_index = current_index % 7
            current_letter = self.letters[current_index]

            if current_letter in half_steps:
                self.accidental.increment(-1 * direction)
            else:
                self.accidental.increment(-2 * direction)
        self.letter = current_letter

    def __add__(self: TGenericPitch, chosen_interval: Interval) -> TGenericPitch:
        new_obj = self.clone()
        new_obj.increment_letter(chosen_interval.size)
        new_obj.increment_value(chosen_interval.value)
        return new_obj

    def __sub__(self: TGenericPitch, chosen_interval: Interval) -> TGenericPitch:
        new_obj = self.clone()
        new_obj.increment_letter(chosen_interval.size * -1)
        new_obj.increment_value(chosen_interval.value * -1)
        return new_obj


class SpecificPitch(GenericPitch, ValueComparator):
    letter_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    value_map = {0: "C", 2: "D", 4: "E", 5: "F", 7: "G", 9: "A", 11: "B"}

    def __init__(self, symbol: str | None = None) -> None:
        if symbol is None:
            super().__init__()
            self._octave = random.randint(1, 7)
        else:
            for index, character in enumerate(symbol):
                if character.isdigit():
                    break
            else:
                raise ValueError

            pitch_symbol = symbol[:index]
            octave_symbol = symbol[index:]
            if not octave_symbol.isdigit():
                raise ValueError

            super().__init__(pitch_symbol)
            self._octave = int(octave_symbol)

        self.value = self.letter_map[self.letter]
        self.value += 12 * (self._octave + 1)
        reference_pitch = GenericPitch(self.letter)
        self.value += self.accidental.value - reference_pitch.accidental.value

    def __str__(self) -> str:
        return f"{self.generic_pitch}{self._octave}"

    def increment_value(self, increment: int) -> None:
        super().increment_value(increment)
        self.value += increment

    def increment_letter(self, amount: int) -> None:
        if amount > 0:
            direction = 1
            half_steps = {"F", "C"}
            octave_step = "C"
        elif amount < 0:
            direction = -1
            half_steps = {"E", "B"}
            octave_step = "B"
        else:
            return

        current_index = self.letters.index(self.letter)

        for _ in range(abs(amount)):
            current_index += direction
            current_index = current_index % 7
            current_letter = self.letters[current_index]

            if current_letter in half_steps:
                self.accidental.increment(-1 * direction)
            else:
                self.accidental.increment(-2 * direction)

            if current_letter == octave_step:
                self._octave += direction
        self.letter = current_letter

    @property
    def generic_pitch(self) -> str:
        return super().__str__()

    @property
    def octave(self) -> int:
        return self._octave

    @classmethod
    def get_pitch_from_value(cls, input_value: int) -> SpecificPitch:
        simplified_value = input_value % 12
        if simplified_value in cls.value_map:
            shift = 0
            accidental_symbol = ""
        else:
            shift = -1
            accidental_symbol = "#"

        letter = cls.value_map[simplified_value + shift]
        octave = (input_value // 12) - 1

        return cls(f"{letter}{accidental_symbol}{octave}")

    def create_iterator(self, chosen_intervals: list[str]) -> Iterator[SpecificPitch]:
        iterating_intervals = [
            Interval.get(interval_str) for interval_str in chosen_intervals
        ]
        current_pitch = self
        yield current_pitch

        while True:
            for current_interval in iterating_intervals:
                current_pitch += current_interval
                yield current_pitch


class Interval(StringDefinedEntity, ValueComparator):
    major_scale_semitones = (0, 2, 4, 5, 7, 9, 11)
    perfect_degrees = {0, 3, 4}
    cache: dict[str, Interval] = {}

    def __init__(self, symbol: str) -> None:
        for index, character in enumerate(symbol):
            if character.isdigit():
                if character == "0":
                    raise ValueError
                break
        else:
            raise ValueError

        quality = symbol[:index]
        size = symbol[index:]

        if not size.isdigit():
            raise ValueError

        # Programmers count from zero. Unison (P1) should be P0.
        self.size = int(size) - 1
        simplified_size = self.size % 7
        if simplified_size in self.perfect_degrees:
            reference_quality = IntervalQuality("P", "perfect")
            self.quality = IntervalQuality(quality, "perfect")
        else:
            reference_quality = IntervalQuality("M", "imperfect")
            self.quality = IntervalQuality(quality, "imperfect")

        self.value = self.major_scale_semitones[simplified_size]
        current_size = self.size
        while current_size != simplified_size:
            current_size -= 7
            self.value += 12

        self.value += self.quality.index - reference_quality.index
        if self.value < 0:
            raise ValueError

    def __str__(self) -> str:
        return f"{self.quality}{self.size + 1}"

    @classmethod
    def get(cls, symbol: str) -> Interval:
        # Interval construction is time-consuming
        if symbol in cls.cache:
            return cls.cache[symbol]
        new_interval = cls(symbol)
        cls.cache[symbol] = new_interval
        return new_interval

    def __invert__(self) -> Interval:
        if self.size >= 7 or self.value >= 12:
            raise ValueError
        new_size = 7 - self.size
        return Interval.get(f"{~self.quality}{new_size + 1}")


class IntervalQuality:
    interval_choices = {"perfect": ("d", "P", "A"), "imperfect": ("d", "m", "M", "A")}
    inversion_map = create_reversible_map({"P": "P", "A": "d", "M": "m"})

    def __init__(self, symbol: str, designation: str) -> None:
        self.possible_intervals = self.interval_choices[designation]

        if len(set(symbol)) != 1:
            raise ValueError
        if symbol in self.possible_intervals:
            self.index = self.possible_intervals.index(symbol)
        elif "AA" in symbol:
            self.index = symbol.count("A") + len(self.possible_intervals) - 2
        elif "dd" in symbol:
            self.index = symbol.count("d") * -1 + 1
        else:
            raise ValueError

    def __str__(self) -> str:
        n = len(self.possible_intervals)
        if 0 <= self.index < n:
            return self.possible_intervals[self.index]
        elif self.index < 0:
            return "d" * (1 - self.index)
        else:
            return "A" * (self.index - n + 2)

    def __invert__(self) -> str:
        old_symbol = str(self)
        return self.inversion_map[old_symbol[0]] * len(old_symbol)


class EngravingError(Exception):
    def __str__(self) -> str:
        return f"Double accidentals detected: {self.args[0]}"


class Scale(GenericPitch):
    roman_numerals = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5, "VII": 6}

    def __init__(self, symbol: str | None = None) -> None:
        super().__init__(symbol)
        self.chord_cache: dict[str, GenericChord] = {}
        tonic_pitch = GenericPitch(str(self))
        print(f"Chosen scale: {tonic_pitch}")

        major_scale_intervals = ["P1", "M2", "M3", "P4", "P5", "M6", "M7"]
        self._members = [
            tonic_pitch + Interval.get(interval_symbol)
            for interval_symbol in major_scale_intervals
        ]

        """Lilypond can't render triple accidentals. 
        Preventing double accidentals on the major scale ensures that 
        altered notes don't have triple accidentals."""
        for scale_pitch in self._members:
            number_of_accidentals = abs(scale_pitch.accidental.value)
            if number_of_accidentals >= 2:
                raise EngravingError(scale_pitch)

    def __getitem__(self, index: int) -> GenericPitch:
        return self._members[index]

    def get_chord(self, input_symbol: str) -> GenericChord:
        if input_symbol in self.chord_cache:
            return self.chord_cache[input_symbol]

        pitch_identifiers = {"#", "b", "V", "I"}
        roman_numeral, chord_modifier = self.split_by_characters(
            input_symbol, pitch_identifiers
        )

        chosen_pitch = self.get_pitch_from_roman_numeral(roman_numeral)
        chord_symbol = "".join([str(chosen_pitch), chord_modifier])
        new_chord = GenericChord(chord_symbol)
        self.chord_cache[input_symbol] = new_chord

        return new_chord

    def get_pitch_from_roman_numeral(self, symbol: str) -> GenericPitch:
        roman_numeral_hierarchy = ("VII", "VI", "IV", "V", "III", "II", "I")

        for current_roman_numeral in roman_numeral_hierarchy:
            if current_roman_numeral in symbol:
                break
        else:
            raise ValueError

        index = symbol.index(current_roman_numeral)
        accidental_symbol = symbol[:index]
        new_accidental = Accidental(accidental_symbol)
        if current_roman_numeral != symbol[index:]:
            raise ValueError

        scale_degree = self.roman_numerals[current_roman_numeral]
        chosen_pitch = self[scale_degree].clone()
        chosen_pitch.increment_value(new_accidental.value)

        return chosen_pitch


class GenericChord(StringDefinedEntity):
    chord_types = {
        "": ["P1", "M3", "P5"],
        "m": ["P1", "m3", "P5"],
        "dim": ["P1", "m3", "d5"],
    }

    def __init__(self, symbol: str | None = None) -> None:
        if symbol is None:
            pitch_symbol = str(GenericPitch())
            self.chord_id = random.choice(list(self.chord_types.keys()))
        else:
            pitch_identifiers = {"#", "b", "A", "B", "C", "D", "E", "F", "G"}
            pitch_symbol, chord_id = self.split_by_characters(symbol, pitch_identifiers)
            if chord_id not in self.chord_types:
                raise ValueError
            self.chord_id = chord_id
        chord_intervals = self.chord_types[self.chord_id]

        tonic_pitch = GenericPitch(pitch_symbol)
        self._members = [
            tonic_pitch + Interval.get(chord_interval)
            for chord_interval in chord_intervals
        ]

    def __str__(self) -> str:
        return f"{self._members[0]}{self.chord_id}"

    def __getitem__(self, index: int) -> GenericPitch:
        return self._members[index]

    def __iter__(self) -> Iterator[GenericPitch]:
        return iter(self._members)

    def get_interval(self, pitch_index: int) -> Interval:
        return Interval.get(self.chord_types[self.chord_id][pitch_index])


class Tessitura:
    chord_interval_map = {
        "": ["M3", "m3", "P4"],
        "m": ["m3", "M3", "P4"],
        "dim": ["m3", "m3", "A4"],
    }

    def __init__(
        self, lowest_pitch: SpecificPitch, highest_pitch: SpecificPitch
    ) -> None:
        if lowest_pitch > highest_pitch:
            raise ValueError
        self._lowest_pitch = lowest_pitch
        self._highest_pitch = highest_pitch

    @property
    def lowest_pitch(self) -> SpecificPitch:
        return self._lowest_pitch

    @lowest_pitch.setter
    def lowest_pitch(self, input_pitch: SpecificPitch) -> None:
        if input_pitch > self._highest_pitch:
            raise ValueError
        self._lowest_pitch = input_pitch

    @property
    def highest_pitch(self) -> SpecificPitch:
        return self._highest_pitch

    @highest_pitch.setter
    def highest_pitch(self, input_pitch: SpecificPitch) -> None:
        if input_pitch < self._lowest_pitch:
            raise ValueError
        self._highest_pitch = input_pitch

    def __contains__(self, input_obj: SpecificPitch | NoteCluster | Tessitura) -> bool:
        if isinstance(input_obj, SpecificPitch):
            return self._lowest_pitch <= input_obj <= self._highest_pitch

        elif isinstance(input_obj, NoteCluster):
            first_conditional = self._lowest_pitch <= input_obj[0]
            second_conditional = self._highest_pitch >= input_obj[-1]
            return first_conditional and second_conditional

        elif isinstance(input_obj, Tessitura):
            first_conditional = self._lowest_pitch <= input_obj.lowest_pitch
            second_conditional = self._highest_pitch >= input_obj.highest_pitch
            return first_conditional and second_conditional

    def filter(self, obj_collection: deque[SpecificPitch] | deque[NoteCluster]) -> None:
        # The assumption is that the objects are in ascending order
        # This should be faster than list comprehension since you only check the ends
        while obj_collection and obj_collection[0] not in self:
            obj_collection.popleft()
        while obj_collection and obj_collection[-1] not in self:
            obj_collection.pop()

    def has_contracted(
        self, input_pitch_min: SpecificPitch, input_pitch_max: SpecificPitch
    ) -> bool:
        delta = False
        if input_pitch_min > self._lowest_pitch:
            self.lowest_pitch = input_pitch_min
            delta = True
        if input_pitch_max < self._highest_pitch:
            self.highest_pitch = input_pitch_max
            delta = True

        return delta

    def filter_pitches(
        self, pitch_iterator: Iterator[SpecificPitch]
    ) -> list[SpecificPitch]:
        available_pitches = []
        current_pitch = next(pitch_iterator)

        while current_pitch < self._lowest_pitch:
            current_pitch = next(pitch_iterator)
        while current_pitch <= self._highest_pitch:
            available_pitches.append(current_pitch)
            current_pitch = next(pitch_iterator)

        return available_pitches

    def find_closed_voicings(
        self, input_generic_chord: GenericChord
    ) -> deque[NoteCluster]:
        iterating_intervals = self.chord_interval_map[input_generic_chord.chord_id]
        starting_specific_pitch = SpecificPitch(f"{input_generic_chord[0]}0")
        chord_iter = starting_specific_pitch.create_iterator(iterating_intervals)
        available_pitches = self.filter_pitches(chord_iter)

        # triads are assumed
        result = [
            NoteCluster(input_generic_chord, available_pitches[index : index + 3])
            for index in range(len(available_pitches) - 2)
        ]
        return deque(result)


class NoteCluster:
    def __init__(
        self, generic_chord: GenericChord, members: list[SpecificPitch]
    ) -> None:
        self.generic_chord = generic_chord
        self._members = members

    def __getitem__(self, index: int) -> SpecificPitch:
        return self._members[index]

    def __iter__(self) -> Iterator[SpecificPitch]:
        return iter(self._members)

    def __repr__(self) -> str:
        return str(self._members)


class AbstractScore:
    def __init__(self) -> None:
        while True:
            try:
                self.scale = Scale()
            except EngravingError as err:
                print(err)
                print("Reattempting...")
            else:
                break
        print(f"Scale members: {self.scale._members}")
        self.time_sig: TimeSignature
        self.tempo: int
        """The same instrument can be used for multiple parts
        the tuple with an integer distinguishes them from one another
        e.g., 1st Violin vs. 2nd Violin"""
        self.tonal_parts: dict[
            tuple[MidiInstrument, int], list[SpecificNote | SpecificChord | RestNote]
        ]
        self.tonal_parts = defaultdict(list)
        self.drum_parts: list[list[DrumNote | DrumCluster | RestNote]] = []

    def set_tempo(self) -> None:
        lower_tempo_bound = round(self.time_sig.lower_tempo_bound * 0.975)
        upper_tempo_bound = round(self.time_sig.upper_tempo_bound * 1.025)
        self.tempo = random.randint(lower_tempo_bound, upper_tempo_bound)


# Dataclasses are preferred over named tuples because the former type-checks attributes
@dataclass
class TimeSignature:
    name: str
    lower_tempo_bound: int
    upper_tempo_bound: int
    groove_pattern: list[str]

    def __str__(self):
        return self.name

    @property
    def groove_duration(self) -> Fraction:
        result = sum(Fraction(str_duration) for str_duration in self.groove_pattern)
        return Fraction(result)


@dataclass
class SpecificNote:
    specific_pitch: SpecificPitch
    duration: Fraction


@dataclass
class SpecificChord:
    note_cluster: NoteCluster
    duration: Fraction


@dataclass
class DrumNote:
    pitch: int
    duration: Fraction


# MidiInstrument needs to be hashable to serve as key in tonal_parts dict
@dataclass(frozen=True)
class MidiInstrument:
    name: str
    number: int
    lower_bound: int
    upper_bound: int


@dataclass
class RestNote:
    duration: Fraction


class DrumCluster:
    def __init__(self, members: list[DrumNote | RestNote], duration: Fraction) -> None:
        self._members = [
            member.pitch for member in members if isinstance(member, DrumNote)
        ]
        self.duration = duration

    def __iter__(self) -> Iterator[int]:
        return iter(self._members)


class DrumSequence:
    drum_mapping = {
        "SN": (38, 40),
        "TOMMH": (48,),
        "TOMML": (47,),
        "TOML": (45,),
        "TOMFH": (43,),
        "TOMFL": (41,),
        "CYM": (49, 52, 55, 57),
    }

    def __init__(self, drum_notes_repr: list[str]) -> None:
        self._members: list[DrumNote | RestNote | DrumCluster] = []
        for drum_note_repr in drum_notes_repr:
            instrument_id, str_duration = drum_note_repr.split(":")
            if instrument_id == "R":
                self._members.append(RestNote(Fraction(str_duration)))
            else:
                drum_pitch = random.choice(self.drum_mapping[instrument_id])
                self._members.append(DrumNote(drum_pitch, Fraction(str_duration)))

    def __iter__(self) -> Iterator[DrumNote | RestNote | DrumCluster]:
        return iter(self._members)

    def append(self, drum_note: DrumNote | RestNote | DrumCluster) -> None:
        self._members.append(drum_note)

    def __add__(self, other: DrumSequence) -> DrumSequence:
        merged_drum_sequence = DrumSequence([])
        self_iter = iter(self._members)
        other_iter = iter(other._members)

        self_drum_item = next(self_iter, None)
        other_drum_item = next(other_iter, None)

        while (
            self_drum_item is not None
            and other_drum_item is not None
            and not isinstance(self_drum_item, DrumCluster)
            and not isinstance(other_drum_item, DrumCluster)
        ):
            remainder_duration = Fraction("0")
            if self_drum_item.duration > other_drum_item.duration:
                merged_duration = other_drum_item.duration
                merged_drum_sequence.append(
                    DrumCluster([self_drum_item, other_drum_item], merged_duration)
                )
                remainder_iter = other_iter
                remainder_duration = self_drum_item.duration - merged_duration
            elif self_drum_item.duration < other_drum_item.duration:
                merged_duration = self_drum_item.duration
                merged_drum_sequence.append(
                    DrumCluster([self_drum_item, other_drum_item], merged_duration)
                )
                remainder_iter = self_iter
                remainder_duration = other_drum_item.duration - merged_duration
            else:
                merged_drum_sequence.append(
                    DrumCluster(
                        [self_drum_item, other_drum_item], self_drum_item.duration
                    )
                )
            while remainder_duration > 0:
                next_drum_item = next(remainder_iter)
                merged_drum_sequence.append(next_drum_item)
                remainder_duration -= next_drum_item.duration

            self_drum_item = next(self_iter, None)
            other_drum_item = next(other_iter, None)

        return merged_drum_sequence


class WaveFunction:
    """A permutation-solving algorithm expecting one or more correct answers."""

    def __init__(
        self,
        sequence_prospects: list[list] | list[deque],
        has_propagated: Callable[[list, int, list, Any], bool],
    ) -> None:
        self.sequence_prospects = copy.deepcopy(sequence_prospects)
        self.has_propagated = has_propagated
        """A sequence is not necessarily validated from left to right 
        but is instead validated based on entropy. 
        The propagate function should account for this unpredictable validation order."""
        self.final_sequence = [None for _ in sequence_prospects]

    def __iter__(self) -> Iterator[list]:
        """If this part is confusing, watch this video: https://www.youtube.com/watch?v=2SuvO4Gi7uY
        This could have been implemented iteratively rather than recursively but
        recursion provides a cleaner solution, especially when backtracking."""
        for result in self.collapse(self.sequence_prospects):
            if isinstance(result, bool):
                raise ValueError
            else:
                yield result

    def collapse(
        self, sequence_prospects: list[list] | list[deque]
    ) -> Iterator[list | bool]:
        """Propagation requires removal of multiple items from a collection.
        SpecificPitch objects are not hashable, so we cannot create a set.
        Deque allows fast removal from ends of a collection of mutable objects."""

        lowest_entropy_indices = self.find_lowest_entropy(sequence_prospects)
        # After yielding a solution, a portion of it is erased to look for new solutions
        if not lowest_entropy_indices:
            yield True
            yield False

        chosen_index = random.choice(lowest_entropy_indices)
        slot_options = sequence_prospects[chosen_index]

        while slot_options:
            chosen_item = random.choice(slot_options)
            self.final_sequence[chosen_index] = chosen_item
            modified_prospects = copy.deepcopy(sequence_prospects)

            propagate_verdict = self.has_propagated(
                modified_prospects, chosen_index, self.final_sequence, chosen_item
            )
            if propagate_verdict:
                recursive_stack = self.collapse(modified_prospects)
                while next(recursive_stack, False):
                    yield self.final_sequence

            slot_options.remove(chosen_item)
            self.final_sequence[chosen_index] = None

    def find_lowest_entropy(
        self, sequence_prospects: list[list] | list[deque]
    ) -> list[int]:
        # arbitrary initial value that is higher than all possible states
        lowest_entropy = 10000
        lowest_entropy_indices = []

        for current_index, index_choices in enumerate(sequence_prospects):
            if self.final_sequence[current_index] is not None:
                continue
            choice_amount = len(index_choices)

            if choice_amount < lowest_entropy:
                lowest_entropy = choice_amount
                lowest_entropy_indices = [current_index]
            elif choice_amount == lowest_entropy:
                lowest_entropy_indices.append(current_index)

        return lowest_entropy_indices
