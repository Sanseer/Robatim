from collections import defaultdict, deque
import copy
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
import itertools
import random
import time
from typing import Generic, Iterator, TypeVar

from generate import theory

all_voice_pairs = ((0, 1), (1, 2), (2, 3), (0, 2), (0, 3), (1, 3))


def get_note_duo(
    lower_voice_measure: theory.FullVoiceMeasure | deque[theory.SpecificNote],
    upper_voice_measure: theory.FullVoiceMeasure | deque[theory.SpecificNote],
) -> Iterator[tuple[theory.SpecificNote, theory.SpecificNote]]:
    lower_voice_iter = iter(lower_voice_measure)
    upper_voice_iter = iter(upper_voice_measure)

    lower_voice_note = next(lower_voice_iter)
    upper_voice_note = next(upper_voice_iter)
    lower_voice_duration = lower_voice_note.duration
    upper_voice_duration = upper_voice_note.duration

    while True:
        yield lower_voice_note, upper_voice_note

        intersect_duration = min(lower_voice_duration, upper_voice_duration)
        lower_voice_duration -= intersect_duration
        upper_voice_duration -= intersect_duration

        try:
            if not lower_voice_duration:
                lower_voice_note = next(lower_voice_iter)
                lower_voice_duration = lower_voice_note.duration
            if not upper_voice_duration:
                upper_voice_note = next(upper_voice_iter)
                upper_voice_duration = upper_voice_note.duration
        except StopIteration:
            break


GenericStack = TypeVar("GenericStack", bound=theory.VariantStack)


class CompositionError(Exception):
    def __str__(self) -> str:
        return f"Composition failed: {self.args[0]}"


class SequencePartial(Generic[GenericStack]):
    known_uniques = {0: 3, 1: 4, 2: 5}

    def __init__(
        self,
        sequence_prospects: list[list[GenericStack]],
        has_propagated: partial[bool],
        chosen_modes: list[theory.ModalScale],
    ) -> None:
        self.length = len(sequence_prospects)
        self.final_index = self.length - 1
        self.uniques = defaultdict(set)

        for k, v in self.known_uniques.items():
            self.uniques[k].add(v)
            self.uniques[v].add(k)

        for propagate_index, index_prospects in enumerate(sequence_prospects):
            if not index_prospects:
                raise CompositionError(f"No prospects at index {propagate_index}.")

        self.sequence: list[GenericStack | None] = [None for _ in range(self.length)]
        self.sequence_prospects = copy.deepcopy(sequence_prospects)
        self.has_propagated = has_propagated
        self.realizer = self.collapse(self.sequence_prospects)

        self.dotted_counts = [0, 0, 0, 0]
        self.allowed_fifth_endpoints = {
            str(chosen_mode[0]) for chosen_mode in chosen_modes
        }
        self.allowed_fourth_endpoints = {
            str(chosen_mode[4]) for chosen_mode in chosen_modes
        }
        self.allowed_fourth_endpoints |= self.allowed_fifth_endpoints
        self.start_time = time.time()

    def __iter__(self) -> Iterator[GenericStack | None]:
        return iter(self.sequence)

    def __getitem__(self, index: int) -> GenericStack | None:
        return self.sequence[index]

    def __setitem__(
        self, propagate_index: int, adding_stack: GenericStack | None
    ) -> None:
        existing_stack = self.sequence[propagate_index]
        if isinstance(existing_stack, theory.FullMeasureStack):
            for voice_index, voice_measure in enumerate(existing_stack):
                if voice_measure[0].duration == Fraction("3/4"):
                    self.dotted_counts[voice_index] -= 1
        elif isinstance(adding_stack, theory.FullMeasureStack):
            for voice_index, voice_measure in enumerate(adding_stack):
                if voice_measure[0].duration == Fraction("3/4"):
                    self.dotted_counts[voice_index] += 1
                    if self.dotted_counts[voice_index] > 1:
                        raise CompositionError("Overused dotted rhythm")

        self.sequence[propagate_index] = adding_stack

    def realize(self) -> list[GenericStack]:
        try:
            self.start_time = time.time()
            return next(self.realizer)
        except StopIteration:
            raise CompositionError("Propagation exhausted.")

    def collapse(
        self, sequence_prospects: list[list[GenericStack]]
    ) -> Iterator[list[GenericStack]]:
        lowest_entropy_indices = self.find_lowest_entropy(sequence_prospects)
        # After yielding a solution, a portion of it is erased to look for new solutions
        if not lowest_entropy_indices:
            yield [measure_stack for measure_stack in self if measure_stack is not None]
            return

        chosen_index = random.choice(lowest_entropy_indices)
        slot_options = sequence_prospects[chosen_index]

        while slot_options:
            chosen_item = random.choice(slot_options)
            try:
                self[chosen_index] = chosen_item
            except CompositionError:
                slot_options.remove(chosen_item)
                continue
            modified_prospects = copy.deepcopy(sequence_prospects)
            modified_prospects[chosen_index].clear()
            modified_prospects[chosen_index].append(chosen_item)

            propagate_verdict = self.has_propagated(
                modified_prospects, chosen_index, self, chosen_item
            )
            if propagate_verdict:
                yield from self.collapse(modified_prospects)

            slot_options.remove(chosen_item)
            self[chosen_index] = None
        if time.time() - self.start_time > 600:
            raise CompositionError("Time limit elapsed.")

    def find_lowest_entropy(
        self, sequence_prospects: list[list[GenericStack]]
    ) -> list[int]:
        # arbitrary initial value that is higher than all possible states
        lowest_entropy = 1_000_000_000_000
        lowest_entropy_indices = []

        for current_index, index_choices in enumerate(sequence_prospects):
            if self[current_index] is not None:
                continue
            choice_amount = len(index_choices)

            if choice_amount < lowest_entropy:
                lowest_entropy = choice_amount
                lowest_entropy_indices = [current_index]
            elif choice_amount == lowest_entropy:
                lowest_entropy_indices.append(current_index)

        return lowest_entropy_indices

    def checked_consecutive_durations(
        self,
        propagate_index: int,
        starting_measure_stack: theory.VariantStack,
    ) -> bool:
        voice_index = 0
        for starting_voice_measure in starting_measure_stack:
            voice_measures_to_check = deque([starting_voice_measure])
            previous_voice_measure = starting_voice_measure

            for current_index in range(propagate_index - 1, -1, -1):
                if (current_measure_stack := self[current_index]) is None:
                    break
                current_voice_measure = current_measure_stack[voice_index]
                if (
                    current_voice_measure[-1].duration
                    != previous_voice_measure[0].duration
                ):
                    break

                voice_measures_to_check.appendleft(current_voice_measure)
                if not current_voice_measure.is_rhythm_continuous:
                    break
                previous_voice_measure = current_voice_measure

            previous_voice_measure = starting_voice_measure
            for current_index in range(propagate_index + 1, self.final_index + 1):
                if (current_measure_stack := self[current_index]) is None:
                    break
                current_voice_measure = current_measure_stack[voice_index]
                if (
                    previous_voice_measure[-1].duration
                    != current_voice_measure[0].duration
                ):
                    break

                voice_measures_to_check.append(current_voice_measure)
                if not current_voice_measure.is_rhythm_continuous:
                    break
                previous_voice_measure = current_voice_measure

            if len(voice_measures_to_check) > 1:
                if not self.has_valid_rhythm(voice_measures_to_check):
                    return False
            voice_index += 1
        return True

    def has_valid_rhythm(
        self,
        voice_measures_to_check: deque[theory.VariantVoiceMeasure],
    ) -> bool:
        current_duration = voice_measures_to_check[0].left_bound.rhythm.duration
        duration_count = 0

        for current_voice_measure in voice_measures_to_check:
            if isinstance(current_voice_measure, theory.HalfVoiceMeasure):
                current_duration = Fraction("1/2")
                duration_count = 1
                continue

            first_duration_in_measure = current_voice_measure[0].duration
            if current_duration != first_duration_in_measure:
                current_duration = first_duration_in_measure
                duration_count = 0
            if current_voice_measure.is_rhythm_continuous:
                duration_count += len(current_voice_measure)
                if theory.RhythmBound.limits[current_duration] < duration_count:
                    return False
            else:
                duration_count += current_voice_measure.left_bound.rhythm.count
                if theory.RhythmBound.limits[current_duration] < duration_count:
                    return False
                current_duration = current_voice_measure.right_bound.rhythm.duration
                duration_count = current_voice_measure.right_bound.rhythm.count

        return True

    def checked_consecutive_skips(
        self,
        propagate_index: int,
        starting_measure_stack: theory.VariantStack,
    ) -> bool:
        voice_index = 0
        for starting_voice_measure in starting_measure_stack:
            voice_measures_to_check = deque([starting_voice_measure])
            previous_voice_measure = starting_voice_measure

            for current_index in range(propagate_index - 1, -1, -1):
                if (current_measure_stack := self[current_index]) is None:
                    break
                current_voice_measure = current_measure_stack[voice_index]
                if not self.boundary_creates_skip(
                    current_voice_measure, previous_voice_measure
                ):
                    break

                voice_measures_to_check.appendleft(current_voice_measure)
                if not current_voice_measure.is_skip_continuous:
                    break
                previous_voice_measure = current_voice_measure

            previous_voice_measure = starting_voice_measure
            for current_index in range(propagate_index + 1, self.final_index + 1):
                if (current_measure_stack := self[current_index]) is None:
                    break
                current_voice_measure = current_measure_stack[voice_index]
                if not self.boundary_creates_skip(
                    previous_voice_measure, current_voice_measure
                ):
                    break

                voice_measures_to_check.append(current_voice_measure)
                if not current_voice_measure.is_skip_continuous:
                    break
                previous_voice_measure = current_voice_measure

            if len(voice_measures_to_check) > 1:
                if not self.has_valid_skips(voice_measures_to_check, voice_index):
                    return False
            voice_index += 1
        return True

    @staticmethod
    def boundary_creates_skip(
        first_voice_measure: theory.VariantVoiceMeasure,
        second_voice_measure: theory.VariantVoiceMeasure,
    ) -> bool:
        before_transition_pitch = first_voice_measure[-1].specific_pitch
        after_transition_pitch = second_voice_measure[0].specific_pitch
        interval_distance = theory.SpecificPitch.get_interval_distance(
            before_transition_pitch, after_transition_pitch
        )
        return interval_distance > 1

    def has_valid_skips(
        self,
        voice_measures_to_check: deque[theory.VariantVoiceMeasure],
        voice_index: int,
    ) -> bool:
        skip_count = 0
        previous_voice_measure = voice_measures_to_check[0]

        for current_voice_measure in voice_measures_to_check:
            if isinstance(current_voice_measure, theory.HalfVoiceMeasure):
                skip_count = 0
                previous_voice_measure = current_voice_measure
                continue

            if self.boundary_creates_skip(
                previous_voice_measure, current_voice_measure
            ):
                skip_count += 1
                if theory.SkipBound.limits[voice_index] < skip_count:
                    return False
            else:
                skip_count = 0
            if current_voice_measure.is_skip_continuous:
                skip_count += current_voice_measure.left_bound.skip.count
                if theory.SkipBound.limits[voice_index] < skip_count:
                    return False
            else:
                skip_count += current_voice_measure.left_bound.skip.count
                if theory.SkipBound.limits[voice_index] < skip_count:
                    return False
                skip_count = current_voice_measure.right_bound.skip.count
            previous_voice_measure = current_voice_measure

        return True

    def checked_melodic_bounds(
        self,
        propagate_index: int,
        starting_measure_stack: theory.VariantStack,
    ) -> bool:
        current_superius_measure = starting_measure_stack[-1]
        if isinstance(current_superius_measure, theory.HalfVoiceMeasure):
            current_sequence = deque([current_superius_measure[-1]])
        else:
            current_sequence = deque(current_superius_measure)

        for current_index in range(propagate_index - 1, -1, -1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                current_superius_measure = current_measure_stack[-1]
                if isinstance(current_superius_measure, theory.HalfVoiceMeasure):
                    current_sequence.appendleft(current_superius_measure[-1])
                    break
                else:
                    current_sequence.extendleft(reversed(current_superius_measure))
            else:
                break

        for current_index in range(propagate_index + 1, self.final_index + 1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                current_superius_measure = current_measure_stack[-1]
                if isinstance(current_superius_measure, theory.HalfVoiceMeasure):
                    break
                else:
                    current_sequence.extend(current_superius_measure)
            else:
                break

        # if 3 boundaries is the limit, you need at least 6 notes to exceed it
        if len(current_sequence) < 6:
            return True

        normalized_sequence = [current_sequence[0]]

        for current_note in itertools.islice(
            current_sequence, 1, len(current_sequence)
        ):
            current_duration = current_note.duration

            once_before_note = normalized_sequence[-1]
            previous_duration = once_before_note.duration
            current_direction = theory.SpecificPitch.get_direction(
                once_before_note.specific_pitch, current_note.specific_pitch
            )

            while len(normalized_sequence) > 1:
                twice_before_note = normalized_sequence[-2]
                previous_direction = theory.SpecificPitch.get_direction(
                    twice_before_note.specific_pitch, once_before_note.specific_pitch
                )
                if (
                    current_direction != 0
                    and previous_direction != 0
                    and current_direction != previous_direction
                    and previous_duration <= Fraction("1/4")
                ):
                    normalized_sequence.pop()
                    once_before_note = normalized_sequence[-1]
                    previous_duration = once_before_note.duration
                    current_direction = theory.SpecificPitch.get_direction(
                        once_before_note.specific_pitch, current_note.specific_pitch
                    )
                else:
                    break
            if (
                current_note.specific_pitch == once_before_note.specific_pitch
                and current_duration == previous_duration == Fraction("1/4")
            ):
                normalized_sequence[-1] = theory.SpecificNote(
                    current_note.specific_pitch, Fraction("1/2")
                )
            else:
                normalized_sequence.append(current_note)

        if len(normalized_sequence) < 6:
            return True

        return self.test_pitch_boundaries(normalized_sequence)

    @staticmethod
    def test_pitch_boundaries(normalized_sequence: list[theory.SpecificNote]) -> bool:
        previous_note = normalized_sequence[0]
        previous_vector = 0
        pitch_boundary_count = 0
        pitch_boundaries = set()

        for current_note in normalized_sequence[1:]:
            previous_pitch = previous_note.specific_pitch
            current_pitch = current_note.specific_pitch
            current_vector = theory.SpecificPitch.get_interval_vector(
                previous_pitch, current_pitch
            )
            # checking if signs are the same
            if (current_vector * previous_vector) < 0:
                pitch_boundary_count += 1
                if pitch_boundary_count > 3:
                    return False
                if abs(current_vector) > 1 and abs(previous_vector) > 1:
                    return False

                bound_repr = str(previous_pitch)
                if bound_repr in pitch_boundaries:
                    return False
                pitch_boundaries.add(bound_repr)

            previous_note = current_note
            if current_vector != 0:
                previous_vector = current_vector

        if current_note.duration != Fraction("1"):
            return True
        bound_repr = str(current_pitch)
        return bound_repr not in pitch_boundaries

    def checked_consecutive_intervals(
        self, propagate_index: int, starting_measure_stack: theory.VariantStack
    ) -> bool:
        for first_voice_index, second_voice_index in all_voice_pairs:
            if not self.checked_duo_intervals(
                propagate_index,
                first_voice_index,
                second_voice_index,
                starting_measure_stack,
            ):
                return False
        return True

    def checked_duo_intervals(
        self,
        propagate_index: int,
        first_voice_index: int,
        second_voice_index: int,
        starting_measure_stack: theory.VariantStack,
    ) -> bool:
        lower_voice_measure = starting_measure_stack[first_voice_index]
        upper_voice_measure = starting_measure_stack[second_voice_index]
        if isinstance(lower_voice_measure, theory.HalfVoiceMeasure):
            lower_voice_sequence = deque([lower_voice_measure[-1]])
        else:
            lower_voice_sequence = deque(lower_voice_measure)
            first_lower_pitch = lower_voice_measure[0].specific_pitch
        last_lower_pitch = lower_voice_measure[-1].specific_pitch

        if isinstance(upper_voice_measure, theory.HalfVoiceMeasure):
            upper_voice_sequence = deque([upper_voice_measure[-1]])
        else:
            upper_voice_sequence = deque(upper_voice_measure)
            first_upper_pitch = upper_voice_measure[0].specific_pitch
        last_upper_pitch = upper_voice_measure[-1].specific_pitch

        has_perfect_interval_boundary = False

        if (
            isinstance(lower_voice_measure, theory.FullVoiceMeasure)
            and isinstance(upper_voice_measure, theory.FullVoiceMeasure)
            and first_lower_pitch.has_interval_shift(first_upper_pitch)
        ):
            has_perfect_interval_boundary = True
            lower_motion_count = 0
            upper_motion_count = 0

            previous_lower_pitch = first_lower_pitch
            previous_upper_pitch = first_upper_pitch
            for current_index in range(propagate_index - 1, -1, -1):
                if (current_measure_stack := self.sequence[current_index]) is not None:
                    if isinstance(current_measure_stack, theory.HalfMeasureStack):
                        lower_voice_sequence.appendleft(
                            current_measure_stack[first_voice_index][-1]
                        )
                        upper_voice_sequence.appendleft(
                            current_measure_stack[second_voice_index][-1]
                        )
                        break

                    for current_note in reversed(
                        current_measure_stack[first_voice_index]
                    ):
                        current_lower_pitch = current_note.specific_pitch
                        if current_lower_pitch != previous_lower_pitch:
                            lower_motion_count += 1
                        lower_voice_sequence.appendleft(current_note)
                        previous_lower_pitch = current_lower_pitch

                    for current_note in reversed(
                        current_measure_stack[second_voice_index]
                    ):
                        current_upper_pitch = current_note.specific_pitch
                        if current_upper_pitch != previous_upper_pitch:
                            upper_motion_count += 1
                        upper_voice_sequence.appendleft(current_note)
                        previous_upper_pitch = current_upper_pitch

                    if max(lower_motion_count, upper_motion_count) >= 2:
                        break
                else:
                    break

        if last_lower_pitch.has_interval_shift(last_upper_pitch):
            has_perfect_interval_boundary = True
            lower_motion_count = 0
            upper_motion_count = 0

            previous_lower_pitch = last_lower_pitch
            previous_upper_pitch = last_upper_pitch
            for current_index in range(propagate_index + 1, self.final_index + 1):
                if (current_measure_stack := self.sequence[current_index]) is not None:
                    if isinstance(current_measure_stack, theory.HalfMeasureStack):
                        break

                    for current_note in current_measure_stack[first_voice_index]:
                        current_lower_pitch = current_note.specific_pitch
                        if current_lower_pitch != previous_lower_pitch:
                            lower_motion_count += 1
                        lower_voice_sequence.append(current_note)
                        previous_lower_pitch = current_lower_pitch

                    for current_note in current_measure_stack[second_voice_index]:
                        current_upper_pitch = current_note.specific_pitch
                        if current_upper_pitch != previous_upper_pitch:
                            upper_motion_count += 1
                        upper_voice_sequence.append(current_note)
                        previous_upper_pitch = current_upper_pitch

                    if max(lower_motion_count, upper_motion_count) >= 2:
                        break
                else:
                    break

        if not has_perfect_interval_boundary:
            return True
        if max(len(lower_voice_sequence), len(upper_voice_sequence)) < 3:
            return True
        return self.test_perfect_intervals(lower_voice_sequence, upper_voice_sequence)

    def test_perfect_intervals(
        self,
        lower_voice_sequence: deque[theory.SpecificNote],
        upper_voice_sequence: deque[theory.SpecificNote],
    ) -> bool:
        duo_iter = get_note_duo(lower_voice_sequence, upper_voice_sequence)
        previous_lower_note, previous_upper_note = next(duo_iter)
        previous_lower_pitch = previous_lower_note.specific_pitch
        previous_upper_pitch = previous_upper_note.specific_pitch

        if previous_lower_pitch.has_interval_shift(previous_upper_pitch):
            perfect_interval_count = 1
        else:
            perfect_interval_count = 0

        for current_lower_note, current_upper_note in duo_iter:
            current_lower_pitch = current_lower_note.specific_pitch
            current_upper_pitch = current_upper_note.specific_pitch

            has_lower_voice_moved = previous_lower_pitch != current_lower_pitch
            has_upper_voice_moved = previous_upper_pitch != current_upper_pitch

            if has_lower_voice_moved or has_upper_voice_moved:
                if current_lower_pitch.has_interval_shift(current_upper_pitch):
                    perfect_interval_count += 1
                    if perfect_interval_count > 2:
                        return False
                else:
                    perfect_interval_count = 0
            previous_lower_pitch = current_lower_pitch
            previous_upper_pitch = current_upper_pitch

        return True

    def checked_melodic_outline(
        self, propagate_index: int, starting_measure_stack: theory.VariantStack
    ) -> bool:
        voice_index = -1
        for starting_voice_measure in starting_measure_stack:
            voice_index += 1
            if isinstance(starting_voice_measure, theory.HalfVoiceMeasure):
                pitch_sequence = deque([starting_voice_measure.pitch])
            else:
                pitch_sequence = deque(
                    current_note.specific_pitch
                    for current_note in starting_voice_measure
                )

            include_leftmost_outline = False
            for current_index in range(propagate_index - 1, -1, -1):
                if (current_measure_stack := self[current_index]) is None:
                    break
                current_voice_measure = current_measure_stack[voice_index]
                if isinstance(current_voice_measure, theory.HalfVoiceMeasure):
                    pitch_sequence.appendleft(current_voice_measure.pitch)
                    include_leftmost_outline = True
                    break
                else:
                    pitch_sequence.extendleft(
                        current_note.specific_pitch
                        for current_note in reversed(current_voice_measure)
                    )
            else:
                include_leftmost_outline = True

            include_rightmost_outline = False
            for current_index in range(propagate_index + 1, self.final_index + 1):
                if (current_measure_stack := self[current_index]) is None:
                    break
                current_voice_measure = current_measure_stack[voice_index]
                if isinstance(current_voice_measure, theory.HalfVoiceMeasure):
                    include_rightmost_outline = True
                    break
                else:
                    pitch_sequence.extend(
                        current_note.specific_pitch
                        for current_note in current_voice_measure
                    )
            else:
                include_rightmost_outline = True

            previous_direction = 0
            previous_pitch = pitch_sequence[0]
            prelim_outlines = []
            prelim_outline = [previous_pitch]
            prelim_flags = []

            for current_pitch in itertools.islice(
                pitch_sequence, 1, len(pitch_sequence)
            ):
                current_direction = theory.SpecificPitch.get_direction(
                    previous_pitch, current_pitch
                )
                if current_direction:
                    if previous_direction:
                        if previous_direction == current_direction:
                            prelim_outline.append(current_pitch)
                        else:
                            prelim_outlines.append(prelim_outline)
                            prelim_outline = [previous_pitch, current_pitch]
                            interval_distance = (
                                theory.SpecificPitch.get_interval_distance(
                                    previous_pitch, current_pitch
                                )
                            )
                            prelim_flags.append(interval_distance == 1)
                    else:
                        prelim_outline.append(current_pitch)
                    previous_direction = current_direction

                previous_pitch = current_pitch
            prelim_outlines.append(prelim_outline)
            prelim_flags.append(True)

            if len(prelim_outlines) == 1:
                if include_leftmost_outline and include_rightmost_outline:
                    finalized_outlines = prelim_outlines
                    finalized_flags = prelim_flags
                else:
                    finalized_outlines = []
                    finalized_flags = []
            else:
                finalized_outlines = prelim_outlines[1:-1]
                finalized_flags = prelim_flags[1:-1]
                if include_leftmost_outline:
                    finalized_outlines.insert(0, prelim_outlines[0])
                    finalized_flags.insert(0, prelim_flags[0])
                if include_rightmost_outline:
                    finalized_outlines.append(prelim_outlines[-1])
                    finalized_flags.append(prelim_flags[-1])

            for melodic_outline, followup_flag in zip(
                finalized_outlines, finalized_flags
            ):
                if len(melodic_outline) > 2 and not self.is_valid_outline(
                    melodic_outline, followup_flag
                ):
                    return False
        return True

    def is_valid_outline(
        self,
        melodic_outline: list[theory.SpecificPitch],
        followup_is_stepewise: bool,
    ) -> bool:
        first_pitch = melodic_outline[0]
        last_pitch = melodic_outline[-1]
        voice_distance = theory.SpecificPitch.get_interval_distance(
            first_pitch, last_pitch
        )
        if voice_distance > 7 or voice_distance == 6:
            return False
        current_pitch_endpoints = {
            first_pitch.generic_pitch,
            last_pitch.generic_pitch,
        }
        if voice_distance == 7:
            return bool(current_pitch_endpoints & self.allowed_fifth_endpoints)

        current_direction = theory.SpecificPitch.get_direction(first_pitch, last_pitch)
        augmented_interval = theory.Interval.get("A4")
        diminished_interval = theory.Interval.get("d5")

        if current_direction == -1:
            augmented_interval, diminished_interval = (
                diminished_interval,
                augmented_interval,
            )
        if first_pitch.has_interval_shift(last_pitch, (str(augmented_interval),)):
            return False
        if first_pitch.has_interval_shift(last_pitch, (str(diminished_interval),)):
            if len(melodic_outline) != 5:
                return False
            return followup_is_stepewise

        if voice_distance == 4:
            return bool(current_pitch_endpoints & self.allowed_fifth_endpoints)
        return True


class BasseDansePartial(SequencePartial[theory.VariantStack]):
    known_uniques = {1: 4, 2: 5}


class BranleSimplePartial(SequencePartial[theory.FullMeasureStack]):
    pass


class ScorePart:
    def __init__(self, clef_name: str) -> None:
        self.clef = clef_name
        self.sections: list[list[theory.SpecificNote | theory.RestNote]] = []

    def __iter__(self) -> Iterator[theory.SpecificNote | theory.RestNote]:
        for section in self.sections:
            for _ in range(2):
                for sound_obj in section:
                    yield sound_obj

    def add_section(
        self, sound_sequence: Iterator[theory.SpecificNote | theory.RestNote]
    ) -> None:
        self.sections.append(list(sound_sequence))


TwoDimensionStack = (
    list[list[theory.FullMeasureStack]] | list[list[theory.VariantStack]]
)


class DanceScore:
    def __init__(
        self,
        chosen_mode: theory.ModalScale,
        clef_group: list[str],
        score_sequences: TwoDimensionStack,
        chosen_instruemnt: theory.MidiInstrument,
        tempo: int,
    ) -> None:
        self.scale = chosen_mode
        print(f"Using {chosen_instruemnt}")
        self.instrument = chosen_instruemnt
        """You can have two parts with the same clef 
        (e.g., contratenor and tenor voices using the alto clef) 
        Therefore, a list is used instead of a dictionary"""
        self.parts = [ScorePart(clef_name) for clef_name in clef_group]

        for score_sequence in score_sequences:
            for score_part, voice_measures in zip(self.parts, zip(*score_sequence)):
                score_part.add_section(
                    sound_obj
                    for voice_measure in voice_measures
                    for sound_obj in voice_measure
                )
        self.tempo = tempo
