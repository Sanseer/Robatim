from __future__ import annotations

# allows use of an annotation before function definition (Python 3.7+)
from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
import random
from typing import ClassVar, Generic, Iterator, TypeVar


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


def create_reversible_map(old_mapping: dict[str, str]) -> dict[str, str]:
    new_mapping = {}
    for key, value in old_mapping.items():
        new_mapping[key] = value
        new_mapping[value] = key

    return new_mapping


# PEP 673
TStringDefinedEntity = TypeVar("TStringDefinedEntity", bound="StringDefinedEntity")


class StringDefinedEntity:
    def __init__(self, symbol: str, /) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"'{self}'"

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def clone(self: TStringDefinedEntity) -> TStringDefinedEntity:
        return self.__class__(str(self))


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
    def __init__(self, symbol: str | None = None, /) -> None:
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

    def increment(self, amount: int, /) -> None:
        self.value += amount


TGenericPitch = TypeVar("TGenericPitch", bound="GenericPitch")


class GenericPitch(StringDefinedEntity):
    letters = ("C", "D", "E", "F", "G", "A", "B")

    def __init__(self, symbol: str | None = None, /) -> None:
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

    def increment_value(self, amount: int, /) -> None:
        self.accidental.increment(amount)

    def increment_letter(self, amount: int, /) -> None:
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

    def __init__(self, symbol: str | None = None, /) -> None:
        if symbol is None:
            super().__init__()
            self.octave = random.randint(1, 7)
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
            self.octave = int(octave_symbol)

        self.value = self.letter_map[self.letter]
        # e.g., C4 has midi value 60
        self.value += 12 * (self.octave + 1)
        self.value += self.accidental.value

    def __str__(self) -> str:
        return f"{self.generic_pitch}{self.octave}"

    def increment_value(self, increment: int, /) -> None:
        super().increment_value(increment)
        self.value += increment

    def increment_letter(self, amount: int, /) -> None:
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
                self.octave += direction
        self.letter = current_letter

    @property
    def generic_pitch(self) -> str:
        return super().__str__()

    @property
    def octave(self) -> int:
        return self._octave

    @octave.setter
    def octave(self, value: int) -> None:
        # Cannot go below C0 or above midi pitch 127
        if value > 9 or value < 0:
            raise ValueError
        self._octave = value

    @classmethod
    def get_pitch_from_value(cls, input_value: int, /) -> SpecificPitch:
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

    @staticmethod
    def get_direction(first_pitch: SpecificPitch, second_pitch: SpecificPitch) -> int:
        difference = second_pitch.value - first_pitch.value
        if difference > 0:
            return 1
        elif difference < 0:
            return -1
        return 0

    @staticmethod
    def get_interval_distance(
        first_pitch: SpecificPitch, second_pitch: SpecificPitch
    ) -> int:
        if first_pitch < second_pitch:
            increment = 1
        elif first_pitch > second_pitch:
            increment = -1
        else:
            if first_pitch == second_pitch:
                return 0
            # handles enharmonic equivalents
            first_index = GenericPitch.letters.index(first_pitch.letter)
            second_index = GenericPitch.letters.index(second_pitch.letter)
            if (first_index + 1) % 7 == second_index:
                increment = 1
            elif (first_index - 1) % 7 == second_index:
                increment = -1
            else:
                raise ValueError

        search_pitch = first_pitch.clone()
        interval_count = 0
        while (
            search_pitch.letter != second_pitch.letter
            or search_pitch.octave != second_pitch.octave
        ):
            search_pitch.increment_letter(increment)
            interval_count += 1

        return interval_count

    @classmethod
    def get_interval_vector(
        cls, first_pitch: SpecificPitch, second_pitch: SpecificPitch
    ) -> int:
        interval_distance = cls.get_interval_distance(first_pitch, second_pitch)
        leap_direction = cls.get_direction(first_pitch, second_pitch)
        return interval_distance * leap_direction

    def has_interval_shift(
        self,
        upper_pitch: SpecificPitch,
        interval_reprs: tuple[str, ...] = ("P5", "P8"),
    ) -> bool:
        generic_reprs = {
            (self + Interval.get(interval_repr)).generic_pitch
            for interval_repr in interval_reprs
        }
        return upper_pitch.generic_pitch in generic_reprs

    def consonant_shift(
        self, chosen_scale: GenericScale, chosen_chord: GenericChord, scale_shift: int
    ) -> SpecificPitch:
        if scale_shift == 0:
            return self

        result_pitch = self.clone()
        result_pitch.increment_letter(scale_shift)
        target_pitch_letter = result_pitch.letter

        for chord_pitch in chosen_chord:
            if chord_pitch.letter == target_pitch_letter:
                return SpecificPitch(f"{chord_pitch}{result_pitch.octave}")

        for scale_pitch in chosen_scale:
            if scale_pitch.letter == target_pitch_letter:
                return SpecificPitch(f"{scale_pitch}{result_pitch.octave}")
        else:
            raise ValueError


class Interval(StringDefinedEntity, ValueComparator):
    major_scale_semitones = (0, 2, 4, 5, 7, 9, 11)
    perfect_degrees = {0, 3, 4}
    cache: dict[str, Interval] = {}

    def __init__(self, symbol: str, /) -> None:
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
        reference_quality: IntervalQuality
        self.quality: IntervalQuality
        if simplified_size in self.perfect_degrees:
            reference_quality = PerfectibleQuality("P")
            self.quality = PerfectibleQuality(quality)
        else:
            reference_quality = ImperfectibleQuality("M")
            self.quality = ImperfectibleQuality(quality)

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
    def get(cls, symbol: str, /) -> Interval:
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


class IntervalQuality(StringDefinedEntity):
    inversion_map = create_reversible_map({"P": "P", "A": "d", "M": "m"})
    possible_intervals: tuple[str, ...]

    def __init__(self, symbol: str, /) -> None:
        if len(set(symbol)) != 1:
            raise ValueError
        self.symbol = symbol

    def __str__(self) -> str:
        return self.symbol

    def __invert__(self) -> str:
        return self.inversion_map[self.symbol[0]] * len(self.symbol)

    @property
    def index(self) -> int:
        if self.symbol in self.possible_intervals:
            return self.possible_intervals.index(self.symbol)
        elif "AA" in self.symbol:
            return len(self.possible_intervals) + self.symbol.count("A") - 2
        elif "dd" in self.symbol:
            return 1 - self.symbol.count("d")
        else:
            raise ValueError


class PerfectibleQuality(IntervalQuality):
    possible_intervals = ("d", "P", "A")


class ImperfectibleQuality(IntervalQuality):
    possible_intervals = ("d", "m", "M", "A")


class EngravingError(Exception):
    def __str__(self) -> str:
        return f"Multiple accidentals detected: {self.args[0]}"


class GenericScale(StringDefinedEntity):
    scale_intervals = ["P1", "P5"]

    def __init__(
        self, symbol: str | None = None, /, *, is_practical: bool = True
    ) -> None:
        if symbol is None:
            self.letter = random.choice(GenericPitch.letters)
            self.accidental = Accidental()
        elif not symbol or symbol[0] not in GenericPitch.letters:
            raise ValueError
        else:
            self.letter = symbol[0]
            self.accidental = Accidental(symbol[1:])

        tonic_pitch = GenericPitch(str(self))
        print(f"{self.__class__.__name__} chosen: {tonic_pitch}")

        self._members = [
            tonic_pitch + Interval.get(interval_symbol)
            for interval_symbol in self.scale_intervals
        ]

        """Lilypond can't render triple accidentals. Preventing double accidentals 
        ensures that altered notes don't have triple accidentals."""
        if is_practical:
            for scale_pitch in self._members:
                number_of_accidentals = abs(scale_pitch.accidental.value)
                if number_of_accidentals >= 2:
                    raise EngravingError(scale_pitch)

    def __str__(self) -> str:
        return f"{self.letter}{self.accidental}"

    def __getitem__(self, index: int) -> GenericPitch:
        """Melodic minor sequences use indices -1 and -2 to distinguish from natural
        minor sequences, which use indices 6 and 5. The scale only contains the
        natural version; the implementer must raise the notes themselves"""
        return self._members[index % 7]

    def __iter__(self) -> Iterator[GenericPitch]:
        return iter(self._members)


class ModalScale(GenericScale):
    melodic_minor_degrees = {-1, -2}
    all_modes = (
        "ionian",
        "dorian",
        "phrygian",
        "lydian",
        "mixolydian",
        "aeolian",
        "locrian",
    )

    def __init__(
        self, symbol: str | None = None, /, *, is_practical: bool = True
    ) -> None:
        super().__init__(symbol)
        self.type = self.__class__.__name__[:-5].lower()

    @property
    def flattened_pitch(self) -> GenericPitch:
        flattened_index = 6 - self.all_modes.index(self.type)
        special_pitch = self[flattened_index].clone()
        special_pitch.increment_value(-1)
        return special_pitch

    def scale_shift(
        self,
        previous_specific_pitch: SpecificPitch,
        previous_scale_degree: int,
        current_scale_degree: int,
    ) -> SpecificPitch:
        # identical function signature to cadential_shift (polymorphism)
        if (vector := current_scale_degree - previous_scale_degree) == 0:
            return previous_specific_pitch

        current_specific_pitch = previous_specific_pitch.clone()
        current_specific_pitch.increment_letter(vector)
        target_pitch_letter = current_specific_pitch.letter

        for scale_pitch in self:
            if scale_pitch.letter == target_pitch_letter:
                return SpecificPitch(f"{scale_pitch}{current_specific_pitch.octave}")
        else:
            raise ValueError

    def get_specific_iter(self) -> Iterator[SpecificPitch]:
        current_specific_pitch = SpecificPitch(f"{self[0]}0")
        iterating_intervals = [
            Interval.get(interval_str) for interval_str in self.scale_intervals[1:]
        ]

        while True:
            yield current_specific_pitch
            for current_interval in iterating_intervals:
                yield current_specific_pitch + current_interval

            current_specific_pitch += Interval.get("P8")

    def get_cadential_pitch(self, scale_degree: int) -> GenericPitch:
        cadential_pitch = self[scale_degree].clone()
        if (
            scale_degree in self.melodic_minor_degrees
            and self.scale_intervals[scale_degree][0] == "m"
        ):
            cadential_pitch.increment_value(1)
        return cadential_pitch

    def cadential_shift(
        self,
        previous_specific_pitch: SpecificPitch,
        previous_scale_degree: int,
        current_scale_degree: int,
    ) -> SpecificPitch:
        if (vector := current_scale_degree - previous_scale_degree) == 0:
            return previous_specific_pitch
        current_specific_pitch = previous_specific_pitch.clone()
        current_specific_pitch.increment_letter(vector)

        cadential_generic_pitch = self.get_cadential_pitch(current_scale_degree)
        current_specific_pitch = SpecificPitch(
            f"{cadential_generic_pitch}{current_specific_pitch.octave}"
        )
        return current_specific_pitch

    def random_mode_shift(self) -> ModalScale:
        current_mode = self.type
        available_modes = list(self.all_modes)
        available_modes.remove(current_mode)
        available_modes.remove("locrian")
        new_mode = random.choice(available_modes)

        current_mode_index = self.all_modes.index(current_mode)
        mode_increment = 0

        while current_mode != new_mode:
            current_mode_index = (current_mode_index + 1) % 7
            current_mode = self.all_modes[current_mode_index]
            mode_increment += 1
        new_tonic = self[0] + Interval.get(self.scale_intervals[mode_increment])

        return scale_type_map[new_mode](f"{new_tonic}")


class IonianScale(ModalScale):
    scale_intervals = ["P1", "M2", "M3", "P4", "P5", "M6", "M7"]


class DorianScale(ModalScale):
    scale_intervals = ["P1", "M2", "m3", "P4", "P5", "M6", "m7"]


class PhrygianScale(ModalScale):
    scale_intervals = ["P1", "m2", "m3", "P4", "P5", "m6", "m7"]


class LydianScale(ModalScale):
    scale_intervals = ["P1", "M2", "M3", "A4", "P5", "M6", "M7"]


class MixolydianScale(ModalScale):
    scale_intervals = ["P1", "M2", "M3", "P4", "P5", "M6", "m7"]


class AeolianScale(ModalScale):
    scale_intervals = ["P1", "M2", "m3", "P4", "P5", "m6", "m7"]


scale_type_map = {
    "ionian": IonianScale,
    "dorian": DorianScale,
    "phrygian": PhrygianScale,
    "lydian": LydianScale,
    "mixolydian": MixolydianScale,
    "aeolian": AeolianScale,
}


class MajorScale(GenericScale):
    scale_intervals = ["P1", "M2", "M3", "P4", "P5", "M6", "M7"]
    roman_numeral_to_degree = {
        "I": 0,
        "II": 1,
        "III": 2,
        "IV": 3,
        "V": 4,
        "VI": 5,
        "VII": 6,
    }

    def __init__(
        self, symbol: str | None = None, /, *, is_practical: bool = True
    ) -> None:
        super().__init__(symbol, is_practical=is_practical)
        self.chord_cache: dict[str, GenericChord] = {}

    def get_chord(self, input_symbol: str, /) -> GenericChord:
        if input_symbol in self.chord_cache:
            return self.chord_cache[input_symbol]

        pitch_identifiers = {"#", "b", "V", "I"}
        roman_symbol, chord_modifier = split_by_characters(
            input_symbol, pitch_identifiers
        )

        chosen_pitch = self.get_pitch_from_roman_symbol(roman_symbol)
        new_chord = GenericChord(f"{chosen_pitch}{chord_modifier}")
        self.chord_cache[input_symbol] = new_chord

        return new_chord

    def get_pitch_from_roman_symbol(self, symbol: str, /) -> GenericPitch:
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

        scale_degree = self.roman_numeral_to_degree[current_roman_numeral]
        chosen_pitch = self[scale_degree].clone()
        chosen_pitch.increment_value(new_accidental.value)

        return chosen_pitch

    def get_pitch_from_scale_degree(self, scale_degree: str, /) -> GenericPitch:
        pitch_modifiers = {"b", "#"}
        accidental_repr, degree_repr = split_by_characters(
            scale_degree, pitch_modifiers
        )
        scale_index = int(degree_repr) - 1

        chosen_pitch = self[scale_index].clone()
        accidental_mod = Accidental(accidental_repr)
        chosen_pitch.increment_value(accidental_mod.value)

        return chosen_pitch


class NaturalMinorScale(GenericScale):
    scale_intervals = ["P1", "M2", "m3", "P4", "P5", "m6", "m7"]


class GenericChord(StringDefinedEntity):
    chord_types = {
        "": ["P1", "M3", "P5"],
        "m": ["P1", "m3", "P5"],
        "dim": ["P1", "m3", "d5"],
    }

    def __init__(self, symbol: str | None = None, /) -> None:
        if symbol is None:
            pitch_symbol = str(GenericPitch())
            self.chord_id = random.choice(list(self.chord_types.keys()))
        else:
            pitch_identifiers = {"#", "b", "A", "B", "C", "D", "E", "F", "G"}
            pitch_symbol, chord_id = split_by_characters(symbol, pitch_identifiers)
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

    def clone(self) -> Tessitura:
        return self.__class__(self._lowest_pitch, self._highest_pitch)

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

    def shrink(self, constraint_tessitura: Tessitura) -> bool:
        delta = False
        if constraint_tessitura._lowest_pitch > self._lowest_pitch:
            self.lowest_pitch = constraint_tessitura._lowest_pitch
            delta = True
        if constraint_tessitura._highest_pitch < self._highest_pitch:
            self.highest_pitch = constraint_tessitura._highest_pitch
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

    def find_equivalent_pitches(
        self, generic_pitch: GenericPitch
    ) -> list[SpecificPitch]:
        starting_specific_pitch = SpecificPitch(f"{generic_pitch}0")
        note_iter = starting_specific_pitch.create_iterator(["P8"])
        return self.filter_pitches(note_iter)


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
            self.major_scale = MajorScale(is_practical=False)
            try:
                self.minor_scale = NaturalMinorScale(str(self.major_scale))
            except EngravingError as err:
                print(err)
                print("Reattempting...")
            else:
                break
        print(f"Scale members: {self.minor_scale._members}")
        self._time_sig: TimeSignature
        self.tempo: int
        """The same instrument can be used for multiple parts
        the tuple with an integer distinguishes them from one another
        e.g., 1st Violin vs. 2nd Violin"""
        self.tonal_parts: dict[
            tuple[MidiInstrument, int], list[SpecificNote | SpecificChord | RestNote]
        ]
        self.tonal_parts = defaultdict(list)
        self.drum_parts: list[list[DrumNote | DrumCluster | RestNote]] = []

    @property
    def time_sig(self) -> TimeSignature:
        return self._time_sig

    @time_sig.setter
    def time_sig(self, chosen_time_sig: TimeSignature) -> None:
        self._time_sig = chosen_time_sig
        self.set_tempo()
        print(f"Using {self._time_sig} time. Tempo = {self.tempo}")

    def set_tempo(self) -> None:
        lower_tempo_bound = round(self._time_sig.lower_tempo_bound * 0.975)
        upper_tempo_bound = round(self._time_sig.upper_tempo_bound * 1.025)
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
        return sum(
            (Fraction(str_duration) for str_duration in self.groove_pattern),
            Fraction("0"),
        )


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


@dataclass
class RestNote:
    duration: Fraction


@dataclass
class RhythmBound:
    duration: Fraction
    count: int
    limits = {
        Fraction("1"): 3,
        Fraction("1/2"): 7,
        Fraction("1/4"): 14,
        Fraction("3/4"): 1,
    }


@dataclass
class SkipBound:
    count: int
    limits = {0: 3, 1: 2, 2: 2, 3: 2}


@dataclass
class MeasureBound:
    rhythm: RhythmBound
    skip: SkipBound


@dataclass
class MelodyPack:
    rhythm_durations: list[Fraction]
    melody_contours: list[list[int]]

    def __post_init__(self) -> None:
        left_consecutive_duration = self.rhythm_durations[0]
        left_consecutive_count = 0
        for rhythm_duration in self.rhythm_durations:
            if rhythm_duration != left_consecutive_duration:
                break
            left_consecutive_count += 1

        right_consecutive_duration = self.rhythm_durations[-1]
        right_consecutive_count = 0
        for rhythm_duration in reversed(self.rhythm_durations):
            if rhythm_duration != right_consecutive_duration:
                break
            right_consecutive_count += 1

        self.left_rhythm_bound = RhythmBound(
            left_consecutive_duration, left_consecutive_count
        )
        self.right_rhythm_bound = RhythmBound(
            right_consecutive_duration, right_consecutive_count
        )
        self.is_rhythm_continuous = (
            left_consecutive_duration == right_consecutive_duration
            and left_consecutive_count == len(self.rhythm_durations)
        )

    @staticmethod
    def get_skip_counts(melody_contour: list[int]) -> tuple[int, int]:
        left_skip_count = 0
        for vector in melody_contour:
            if abs(vector) <= 1:
                break
            left_skip_count += 1

        right_skip_count = 0
        for vector in reversed(melody_contour):
            if abs(vector) <= 1:
                break
            right_skip_count += 1

        return left_skip_count, right_skip_count

    @staticmethod
    def check_skip_continuity(
        left_skip_count: int,
        right_skip_count: int,
        melody_contour: list[int],
    ) -> bool:
        if not melody_contour:
            return True
        if not left_skip_count or not right_skip_count:
            return False
        return left_skip_count == right_skip_count == len(melody_contour)


@dataclass
class BaseVoiceMeasure:
    sequence: list[SpecificNote]
    left_bound: MeasureBound
    right_bound: MeasureBound
    is_rhythm_continuous: bool
    is_skip_continuous: bool
    id_count = 0

    def __post_init__(self) -> None:
        self.id = BaseVoiceMeasure.id_count
        BaseVoiceMeasure.id_count += 1

    def __iter__(self) -> Iterator[SpecificNote]:
        return iter(self.sequence)

    def __getitem__(self, index: int) -> SpecificNote:
        return self.sequence[index]

    def __len__(self) -> int:
        return len(self.sequence)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseVoiceMeasure):
            return False
        return self.id == other.id


@dataclass
class FullVoiceMeasure(BaseVoiceMeasure):
    instance_cache: ClassVar[dict[str, FullVoiceMeasure]] = {}

    @staticmethod
    def derive_notation(sequence: list[SpecificNote]) -> str:
        return "+".join(
            f"{current_note.specific_pitch}{current_note.duration}"
            for current_note in sequence
        )

    @classmethod
    def get(
        cls,
        sequence: list[SpecificNote],
        left_bound: MeasureBound,
        right_bound: MeasureBound,
        is_rhythm_continuous: bool,
        is_skip_continuous: bool,
    ) -> FullVoiceMeasure:
        if (notation := cls.derive_notation(sequence)) in cls.instance_cache:
            return cls.instance_cache[notation]
        new_measure = cls(
            sequence, left_bound, right_bound, is_rhythm_continuous, is_skip_continuous
        )
        cls.instance_cache[notation] = new_measure
        return new_measure


half_duration = Fraction("1/2")
half_rest = RestNote(half_duration)


@dataclass
class HalfVoiceMeasure(BaseVoiceMeasure):
    left_bound: MeasureBound = MeasureBound(RhythmBound(Fraction("0"), 0), SkipBound(0))
    right_bound: MeasureBound = MeasureBound(
        RhythmBound(Fraction("1/2"), 1), SkipBound(0)
    )
    is_rhythm_continuous: bool = False
    is_skip_continuous: bool = False
    instance_cache: ClassVar[dict[str, HalfVoiceMeasure]] = {}

    def __post_init__(self) -> None:
        super().__post_init__()
        self.pitch = self.sequence[-1].specific_pitch

    def __iter__(self) -> Iterator:
        yield half_rest
        for current_note in self.sequence:
            yield current_note

    def __getitem__(self, index: int) -> SpecificNote:
        if index != -1 and index != 1:
            raise ValueError
        return self.sequence[-1]

    @classmethod
    def get(cls, chosen_pitch: SpecificPitch) -> HalfVoiceMeasure:
        if (notation := str(chosen_pitch)) in cls.instance_cache:
            return cls.instance_cache[notation]
        new_measure = cls([SpecificNote(chosen_pitch, half_duration)])
        cls.instance_cache[notation] = new_measure
        return new_measure


GenericMeasure = TypeVar("GenericMeasure")


class BaseMeasureStack(Generic[GenericMeasure]):
    id_count = 0
    obj_cache: dict[int, VariantStack] = {}

    def __init__(
        self,
        bassus_measure: GenericMeasure,
        tenor_measure: GenericMeasure,
        contratenor_measure: GenericMeasure,
        superius_measure: GenericMeasure,
    ) -> None:
        self.stack = (
            bassus_measure,
            tenor_measure,
            contratenor_measure,
            superius_measure,
        )
        self.id = BaseMeasureStack.id_count
        BaseMeasureStack.id_count += 1

    def __iter__(self) -> Iterator[GenericMeasure]:
        return iter(self.stack)

    def __getitem__(self, index: int) -> GenericMeasure:
        return self.stack[index]


class FullMeasureStack(BaseMeasureStack[FullVoiceMeasure]):
    instance_cache: dict[str, FullMeasureStack] = {}

    @classmethod
    def get(
        cls,
        bassus_measure: FullVoiceMeasure,
        tenor_measure: FullVoiceMeasure,
        contratenor_measure: FullVoiceMeasure,
        superius_measure: FullVoiceMeasure,
    ) -> FullMeasureStack:
        notation = (
            f"{bassus_measure.id}+{tenor_measure.id}+"
            f"{contratenor_measure.id}+{superius_measure.id}"
        )
        if notation in cls.instance_cache:
            return cls.instance_cache[notation]

        new_stack = cls(
            bassus_measure, tenor_measure, contratenor_measure, superius_measure
        )
        cls.instance_cache[notation] = new_stack
        BaseMeasureStack.obj_cache[new_stack.id] = new_stack
        return new_stack


class HalfMeasureStack(BaseMeasureStack[HalfVoiceMeasure]):
    instance_cache: dict[str, HalfMeasureStack] = {}

    @classmethod
    def get(
        cls,
        bassus_measure: HalfVoiceMeasure,
        tenor_measure: HalfVoiceMeasure,
        contratenor_measure: HalfVoiceMeasure,
        superius_measure: HalfVoiceMeasure,
    ) -> HalfMeasureStack:
        notation = (
            f"{bassus_measure.id}+{tenor_measure.id}+"
            f"{contratenor_measure.id}+{superius_measure.id}"
        )
        if notation in cls.instance_cache:
            return cls.instance_cache[notation]

        new_stack = cls(
            bassus_measure, tenor_measure, contratenor_measure, superius_measure
        )
        cls.instance_cache[notation] = new_stack
        BaseMeasureStack.obj_cache[new_stack.id] = new_stack
        return new_stack


VariantVoiceMeasure = HalfVoiceMeasure | FullVoiceMeasure
VariantStack = HalfMeasureStack | FullMeasureStack


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
