from collections import defaultdict, deque
import copy
from dataclasses import dataclass
from fractions import Fraction
import random
from typing import Callable, Iterator

from generate import theory


@dataclass
class ConsecutiveMarker:
    duration: Fraction
    rhythm_count: int
    skip_count: int


@dataclass
class ScoreRule:
    direction: str
    voice_index: int
    rule: ConsecutiveMarker


class Stipulation:
    def __init__(self, score_rules: list[ScoreRule]) -> None:
        self.left_marker = {}
        self.right_marker = {}
        for score_rule in score_rules:
            if score_rule.direction == "left":
                self.left_marker[score_rule.voice_index] = score_rule.rule
            else:
                self.right_marker[score_rule.voice_index] = score_rule.rule


class CognizantSequence:
    rhythm_limits = {
        Fraction("1"): 3,
        Fraction("1/2"): 7,
        Fraction("1/4"): 14,
        Fraction("3/4"): 1,
    }
    skip_limits = {0: 3, 1: 2, 2: 2, 3: 2}
    all_voice_indices = (0, 1, 2, 3)
    known_duplicates = {0: 6, 1: 7, 2: 8}
    known_uniques = {0: 3, 1: 4, 2: 5}

    def __init__(self, length: int) -> None:
        self.sequence: list[theory.MeasureStack | None] = [None for _ in range(length)]
        self.final_index = length - 1
        self.duplicates = defaultdict(set)
        self.uniques = defaultdict(set)

        for k, v in self.known_duplicates.items():
            self.duplicates[k].add(v)
            self.duplicates[v].add(k)

        for k, v in self.known_uniques.items():
            self.uniques[k].add(v)
            self.uniques[v].add(k)

    def __iter__(self) -> Iterator[theory.MeasureStack | None]:
        return iter(self.sequence)

    def __getitem__(self, index: int) -> theory.MeasureStack | None:
        return self.sequence[index]

    def __setitem__(
        self, index: int, measure_stack: theory.MeasureStack | None
    ) -> None:
        self.sequence[index] = measure_stack

    @staticmethod
    def get_stipulation(measure_stack: theory.MeasureStack) -> Stipulation:
        score_rules = []

        for voice_index, voice_measure in enumerate(measure_stack):
            consecutive_duration = voice_measure[0].duration
            rhythm_count = 0
            for current_note in voice_measure:
                if current_note.duration == consecutive_duration:
                    rhythm_count += 1
                else:
                    break

            previous_pitch = voice_measure[0].specific_pitch
            skip_count = 0
            for current_note in voice_measure[1:]:
                current_pitch = current_note.specific_pitch
                interval_distance = theory.SpecificPitch.get_interval_distance(
                    previous_pitch, current_pitch
                )
                if interval_distance > 1:
                    skip_count += 1
                else:
                    break
                previous_pitch = current_pitch

            consecutive_marker = ConsecutiveMarker(
                consecutive_duration, rhythm_count, skip_count
            )
            score_rules.append(ScoreRule("left", voice_index, consecutive_marker))

            consecutive_duration = voice_measure[-1].duration
            rhythm_count = 0
            for current_note in reversed(voice_measure):
                if current_note.duration == consecutive_duration:
                    rhythm_count += 1
                else:
                    break

            previous_pitch = voice_measure[-1].specific_pitch
            skip_count = 0
            for current_note in reversed(voice_measure[:-1]):
                current_pitch = current_note.specific_pitch
                interval_distance = theory.SpecificPitch.get_interval_distance(
                    previous_pitch, current_pitch
                )
                if interval_distance > 1:
                    skip_count += 1
                else:
                    break
                previous_pitch = current_pitch

            consecutive_marker = ConsecutiveMarker(
                consecutive_duration, rhythm_count, skip_count
            )
            score_rules.append(ScoreRule("right", voice_index, consecutive_marker))

        return Stipulation(score_rules)

    def checked_stipulations(
        self,
        propagate_index: int,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        attempted_stipulation = self.get_stipulation(attempted_measure_stack)
        if propagate_index == self.final_index:
            test_rhythm = self.test_rhythm_leftward
            test_skips = self.test_skips_leftward
        elif propagate_index == 0:
            test_rhythm = self.test_rhythm_rightward
            test_skips = self.test_skips_rightward
        else:
            test_rhythm = self.test_rhythm_dual_outward
            test_skips = self.test_skips_dual_outward
        global_consecutive_tests = [test_rhythm, test_skips]

        for voice_index in self.all_voice_indices:
            left_marker = attempted_stipulation.left_marker[voice_index]
            right_marker = attempted_stipulation.right_marker[voice_index]
            num_of_notes = len(attempted_measure_stack[voice_index])
            local_consecutive_tests = global_consecutive_tests[:]

            if (
                left_marker.duration == right_marker.duration
                and left_marker.rhythm_count == num_of_notes
                and propagate_index != 0
                and propagate_index != self.final_index
            ):
                local_consecutive_tests[0] = self.test_rhythm_single_outward

            if left_marker.skip_count == right_marker.skip_count:
                if left_marker.skip_count == 0:
                    local_consecutive_tests[1] = self.test_null
                elif (
                    left_marker.skip_count == num_of_notes - 1
                    and propagate_index != 0
                    and propagate_index != self.final_index
                ):
                    local_consecutive_tests[1] = self.test_skips_single_outward

            verdict = all(
                consecutive_test(
                    propagate_index,
                    voice_index,
                    attempted_stipulation,
                    attempted_measure_stack,
                )
                for consecutive_test in local_consecutive_tests
            )
            if not verdict:
                return False

        if propagate_index in range(6):
            return self.test_melodic_bounds(
                propagate_index, attempted_measure_stack, (0, 1, 2, 3, 4, 5)
            )
        elif propagate_index == 10:
            # superius cadential measure hard-coded as stepwise motion to tonic
            return True
        else:
            return self.test_melodic_bounds(
                propagate_index, attempted_measure_stack, (6, 7, 8, 9, 11)
            )

    def test_rhythm_leftward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        left_marker = attempted_stipulation.left_marker[voice_index]
        consecutive_duration = left_marker.duration
        consecutive_count = left_marker.rhythm_count

        for current_index in range(propagate_index - 1, -1, -1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in reversed(current_measure_stack[voice_index]):
                    if current_note.duration != consecutive_duration:
                        break
                    consecutive_count += 1
                else:
                    continue
                break
            else:
                break

        consecutive_limit = self.rhythm_limits[consecutive_duration]
        return consecutive_count <= consecutive_limit

    def test_rhythm_rightward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        right_marker = attempted_stipulation.right_marker[voice_index]
        consecutive_duration = right_marker.duration
        consecutive_count = right_marker.rhythm_count

        for current_index in range(propagate_index + 1, self.final_index + 1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in current_measure_stack[voice_index]:
                    if current_note.duration != consecutive_duration:
                        break
                    consecutive_count += 1
                else:
                    continue
                break
            else:
                break

        consecutive_limit = self.rhythm_limits[consecutive_duration]
        return consecutive_count <= consecutive_limit

    def test_rhythm_dual_outward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        left_condition = self.test_rhythm_leftward(
            propagate_index, voice_index, attempted_stipulation, attempted_measure_stack
        )
        if not left_condition:
            return False
        right_condition = self.test_rhythm_rightward(
            propagate_index, voice_index, attempted_stipulation, attempted_measure_stack
        )
        return right_condition

    def test_rhythm_single_outward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        left_marker = attempted_stipulation.left_marker[voice_index]
        consecutive_duration = left_marker.duration
        consecutive_count = left_marker.rhythm_count

        for current_index in range(propagate_index - 1, -1, -1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in reversed(current_measure_stack[voice_index]):
                    if current_note.duration != consecutive_duration:
                        break
                    consecutive_count += 1
                else:
                    continue
                break
            else:
                break

        for current_index in range(propagate_index + 1, self.final_index + 1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in current_measure_stack[voice_index]:
                    if current_note.duration != consecutive_duration:
                        break
                    consecutive_count += 1
                else:
                    continue
                break
            else:
                break

        consecutive_limit = self.rhythm_limits[consecutive_duration]
        return consecutive_count <= consecutive_limit

    def test_null(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        return True

    def test_skips_leftward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        left_marker = attempted_stipulation.left_marker[voice_index]
        previous_pitch = attempted_measure_stack[voice_index][0].specific_pitch
        skip_count = left_marker.skip_count

        for current_index in range(propagate_index - 1, -1, -1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in reversed(current_measure_stack[voice_index]):
                    current_pitch = current_note.specific_pitch
                    interval_distance = theory.SpecificPitch.get_interval_distance(
                        previous_pitch, current_pitch
                    )
                    if interval_distance > 1:
                        skip_count += 1
                    else:
                        break
                    previous_pitch = current_pitch
                else:
                    continue
                break
            else:
                break

        consecutive_limit = self.skip_limits[voice_index]
        return skip_count <= consecutive_limit

    def test_skips_rightward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        right_marker = attempted_stipulation.right_marker[voice_index]
        previous_pitch = attempted_measure_stack[voice_index][-1].specific_pitch
        skip_count = right_marker.skip_count

        for current_index in range(propagate_index + 1, self.final_index + 1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in current_measure_stack[voice_index]:
                    current_pitch = current_note.specific_pitch
                    interval_distance = theory.SpecificPitch.get_interval_distance(
                        previous_pitch, current_pitch
                    )
                    if interval_distance > 1:
                        skip_count += 1
                    else:
                        break
                    previous_pitch = current_pitch
                else:
                    continue
                break
            else:
                break

        consecutive_limit = self.skip_limits[voice_index]
        return skip_count <= consecutive_limit

    def test_skips_dual_outward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        left_condition = self.test_skips_leftward(
            propagate_index, voice_index, attempted_stipulation, attempted_measure_stack
        )
        if not left_condition:
            return False
        right_condition = self.test_skips_rightward(
            propagate_index, voice_index, attempted_stipulation, attempted_measure_stack
        )
        return right_condition

    def test_skips_single_outward(
        self,
        propagate_index: int,
        voice_index: int,
        attempted_stipulation: Stipulation,
        attempted_measure_stack: theory.MeasureStack,
    ) -> bool:
        left_marker = attempted_stipulation.left_marker[voice_index]
        previous_pitch = attempted_measure_stack[voice_index][0].specific_pitch
        skip_count = left_marker.skip_count

        for current_index in range(propagate_index - 1, -1, -1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in reversed(current_measure_stack[voice_index]):
                    current_pitch = current_note.specific_pitch
                    interval_distance = theory.SpecificPitch.get_interval_distance(
                        previous_pitch, current_pitch
                    )
                    if interval_distance > 1:
                        skip_count += 1
                    else:
                        break
                    previous_pitch = current_pitch
                else:
                    continue
                break
            else:
                break

        previous_pitch = attempted_measure_stack[voice_index][-1].specific_pitch

        for current_index in range(propagate_index + 1, self.final_index + 1):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                for current_note in current_measure_stack[voice_index]:
                    current_pitch = current_note.specific_pitch
                    interval_distance = theory.SpecificPitch.get_interval_distance(
                        previous_pitch, current_pitch
                    )
                    if interval_distance > 1:
                        skip_count += 1
                    else:
                        break
                    previous_pitch = current_pitch
                else:
                    continue
                break
            else:
                break

        consecutive_limit = self.skip_limits[voice_index]
        return skip_count <= consecutive_limit

    def test_melodic_bounds(
        self,
        propagate_index: int,
        attempted_measure_stack: theory.MeasureStack,
        pertinent_indices: tuple[int, ...],
    ) -> bool:
        current_sequence = deque(attempted_measure_stack[-1])
        reference_index = pertinent_indices.index(propagate_index)

        for current_index in reversed(pertinent_indices[:reference_index]):
            if (current_measure_stack := self.sequence[current_index]) is not None:
                current_sequence.extendleft(reversed(current_measure_stack[-1]))
            else:
                break

        for current_index in pertinent_indices[reference_index + 1 :]:
            if (current_measure_stack := self.sequence[current_index]) is not None:
                current_sequence.extend(current_measure_stack[-1])
            else:
                break

        # if 3 boundaries is the limit, you need at least 6 notes to exceed it
        if len(current_sequence) < 6:
            return True

        normalized_sequence = [current_sequence[0]]
        note_index = 1

        while note_index < len(current_sequence):
            current_note = current_sequence[note_index]
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
            note_index += 1

        if len(normalized_sequence) < 6:
            return True

        return self.test_pitch_boundaries(normalized_sequence)

    @staticmethod
    def test_pitch_boundaries(normalized_sequence: list[theory.SpecificNote]) -> bool:
        previous_note = normalized_sequence[0]
        previous_vector = 0
        pitch_boundary_count = 0
        note_index = 1
        pitch_boundaries = set()

        while note_index < len(normalized_sequence):
            current_note = normalized_sequence[note_index]
            current_vector = theory.SpecificPitch.get_interval_vector(
                previous_note.specific_pitch, current_note.specific_pitch
            )
            if (
                current_vector != 0
                and previous_vector != 0
                # checking if signs are the same
                and (current_vector * previous_vector) < 0
            ):
                pitch_boundary_count += 1
                if pitch_boundary_count > 3:
                    return False
                if abs(current_vector) > 1 and abs(previous_vector) > 1:
                    return False

                bound_repr = str(previous_note.specific_pitch)
                if bound_repr in pitch_boundaries:
                    return False
                pitch_boundaries.add(bound_repr)

            previous_note = current_note
            if current_vector != 0:
                previous_vector = current_vector
            note_index += 1

        return True


class DanceScore:
    def __init__(
        self,
        chosen_scale: theory.ModalScale,
        clef_group: list[str],
        score_sequence: CognizantSequence,
        chosen_instruemnt: theory.MidiInstrument,
    ) -> None:
        self.scale = chosen_scale
        print(f"Using {chosen_instruemnt}")
        self.instrument = chosen_instruemnt
        """You can have two parts with the same clef 
        (e.g., contratenor and tenor voices using the alto clef) 
        Therefore, a list is used instead of a dictionary"""
        self.parts = []

        voice_measures: tuple[theory.MelodicSequence, ...]
        for clef_name, voice_measures in zip(clef_group, zip(*score_sequence)):
            melodic_sequence = [
                specific_note
                for voice_measure in voice_measures
                for specific_note in voice_measure
            ]
            self.parts.append((clef_name, melodic_sequence))
        self.tempo = random.randint(195, 215)


class WaveFunction:
    """A permutation-solving algorithm expecting one or more correct answers."""

    def __init__(
        self,
        sequence_prospects: list[list],
        has_propagated: Callable[
            [list, int, CognizantSequence, theory.MeasureStack], bool
        ],
    ) -> None:
        for propagate_index, index_prospects in enumerate(sequence_prospects):
            if not index_prospects:
                raise ValueError(f"No prospects at index {propagate_index}")

        self.sequence_prospects = copy.deepcopy(sequence_prospects)
        self.has_propagated = has_propagated
        """A sequence is not necessarily validated from left to right 
        but is instead validated based on entropy. 
        The propagate function should account for this unpredictable validation order."""
        self.final_sequence = CognizantSequence(len(sequence_prospects))

    def __iter__(self) -> Iterator[CognizantSequence]:
        """If this part is confusing, watch this video: https://www.youtube.com/watch?v=2SuvO4Gi7uY
        This could have been implemented iteratively rather than recursively but
        recursion provides a cleaner solution, especially when backtracking."""
        return self.collapse(self.sequence_prospects)

    def collapse(self, sequence_prospects: list[list]) -> Iterator[CognizantSequence]:
        lowest_entropy_indices = self.find_lowest_entropy(sequence_prospects)
        # After yielding a solution, a portion of it is erased to look for new solutions
        if not lowest_entropy_indices:
            yield self.final_sequence
            return

        chosen_index = random.choice(lowest_entropy_indices)
        slot_options = sequence_prospects[chosen_index]

        while slot_options:
            chosen_item = random.choice(slot_options)
            self.final_sequence[chosen_index] = chosen_item
            modified_prospects = copy.deepcopy(sequence_prospects)
            modified_prospects[chosen_index].clear()
            modified_prospects[chosen_index].append(chosen_item)

            propagate_verdict = self.has_propagated(
                modified_prospects, chosen_index, self.final_sequence, chosen_item
            )
            if propagate_verdict:
                yield from self.collapse(modified_prospects)

            slot_options.remove(chosen_item)
            self.final_sequence[chosen_index] = None

    def find_lowest_entropy(self, sequence_prospects: list[list]) -> list[int]:
        # arbitrary initial value that is higher than all possible states
        lowest_entropy = 1_000_000_000_000
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
