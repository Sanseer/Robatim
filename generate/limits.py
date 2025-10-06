from collections import defaultdict, deque
from fractions import Fraction
from functools import partial
import random
import time
from typing import Iterator

from generate import rules, theory


class CompositionError(Exception):
    def __str__(self) -> str:
        return f"Composition failed: {self.args[0]}"


class ImprobableError(Exception):
    def __str__(self) -> str:
        return f"Unpromising path: {self.args[0]}"


class SequencePartial:
    known_uniques = {0: 3, 1: 4, 2: 5}

    def __init__(
        self,
        sequence_prospects: list[list[theory.VariantStack]],
        chosen_modes: list[theory.ModalScale],
        is_antecedent: bool,
        is_intermediate_sequence: bool,
    ) -> None:
        self.final_index = len(sequence_prospects) - 1
        self.uniques = defaultdict(set)
        for k, v in self.known_uniques.items():
            self.uniques[k].add(v)
            self.uniques[v].add(k)

        for propagate_index, prospect_stacks in enumerate(sequence_prospects):
            if not prospect_stacks:
                raise CompositionError(f"No prospects at index {propagate_index}.")
        self.sequence_prospects = sequence_prospects

        self.dotted_counts = [0, 0, 0, 0]
        self.flattened_pitch = chosen_modes[0].flattened_pitch
        self.allowed_fifth_endpoints = {
            endpoint
            for chosen_mode in chosen_modes
            for endpoint in chosen_mode.fifth_endpoints
        }
        self.allowed_fourth_endpoints = {
            endpoint
            for chosen_mode in chosen_modes
            for endpoint in chosen_mode.fourth_endpoints
        }
        self.start_time = time.time()

        self.backtrack_adjacencies: list[dict[int, set[int]]] = [
            defaultdict(set) for _ in range(6)
        ]
        self.is_antecedent = is_antecedent
        self.is_intermediate_sequence = is_intermediate_sequence
        self.test_suites: list[list[partial[bool]]]
        self.create_test_suite()

    def create_test_suite(self) -> None:
        full_to_full = (
            partial(
                rules.checked_solo_transition,
                flattened_pitch=self.flattened_pitch,
            ),
            partial(rules.are_measure_stacks_unique),
            partial(rules.checked_dissonant_pass),
            partial(rules.checked_broken_parallels),
            partial(rules.checked_dotted_adjacent),
            partial(rules.checked_cross_measures),
            partial(rules.checked_quartet_transition),
            partial(
                rules.checked_endpoints,
                allowed_fifth_endpoints=self.allowed_fifth_endpoints,
                allowed_fourth_endpoints=self.allowed_fourth_endpoints,
            ),
        )
        self.test_suites = [
            list(full_to_full),
            list(full_to_full),
            list(full_to_full),
            list(full_to_full),
            list(full_to_full),
        ]

    def prune(self) -> list[theory.VariantStack]:
        starting_prospects_ids = {
            index_prospect.id for index_prospect in self.sequence_prospects[-1]
        }
        backtrack_attempts: list[dict[int, set[int]]] = [
            defaultdict(set) for _ in range(6)
        ]

        def recursive_clear(failed_index: int, failed_id: int) -> None:
            if failed_index == 5:
                starting_prospects_ids.remove(failed_id)
                if not starting_prospects_ids:
                    raise ImprobableError("Prescreening failed.")
                return

            backtrack_ids = backtrack_attempts[failed_index][failed_id]
            for backtrack_id in backtrack_ids:
                relevant_adjancencies = self.backtrack_adjacencies[failed_index + 1][
                    backtrack_id
                ]
                relevant_adjancencies.remove(failed_id)
                if not relevant_adjancencies:
                    recursive_clear(failed_index + 1, backtrack_id)

        print("Prescreening prospects")
        viable_prospects_ids = starting_prospects_ids
        for second_index in range(5, 0, -1):
            first_index = second_index - 1
            viable_second_prospects = [
                theory.BaseMeasureStack.obj_cache[viable_prospects_id]
                for viable_prospects_id in viable_prospects_ids
            ]
            current_tests = self.test_suites[first_index]
            viable_prospects_ids = set()
            for second_prospect in viable_second_prospects:
                second_prospect_id = second_prospect.id
                prospect_has_solution = False
                for first_prospect in self.sequence_prospects[first_index]:
                    first_prospect_id = first_prospect.id
                    if second_prospect_id in rules.absolute_failures[first_prospect_id]:
                        continue

                    for current_test in current_tests:
                        if not current_test(first_prospect, second_prospect):
                            break
                    else:
                        self.backtrack_adjacencies[second_index][
                            second_prospect_id
                        ].add(first_prospect_id)
                        backtrack_attempts[first_index][first_prospect_id].add(
                            second_prospect_id
                        )
                        viable_prospects_ids.add(first_prospect_id)
                        prospect_has_solution = True

                if not prospect_has_solution:
                    recursive_clear(second_index, second_prospect_id)

        starting_points = [
            theory.BaseMeasureStack.obj_cache[starting_id]
            for starting_id in starting_prospects_ids
        ]

        return starting_points

    def increment_dotted_counts(self, current_stack: theory.VariantStack) -> bool:
        dotted_increments = [0, 0, 0, 0]
        if isinstance(current_stack, theory.FullMeasureStack):
            for voice_index, voice_measure in enumerate(current_stack):
                if voice_measure[0].duration == Fraction("3/4"):
                    if self.dotted_counts[voice_index] == 1:
                        return False
                    dotted_increments[voice_index] += 1

            for voice_index, dotted_increment in enumerate(dotted_increments):
                self.dotted_counts[voice_index] += dotted_increment
        return True

    def decrement_dotted_counts(self, current_stack: theory.VariantStack) -> None:
        if isinstance(current_stack, theory.FullMeasureStack):
            for voice_index, voice_measure in enumerate(current_stack):
                if voice_measure[0].duration == Fraction("3/4"):
                    self.dotted_counts[voice_index] -= 1

    def get_solution(
        self,
        current_index: int,
        current_stack: theory.VariantStack,
        current_path: deque[theory.VariantStack],
    ) -> Iterator[list[theory.VariantStack]]:
        if current_index == 0:
            solution_id = [
                [voice_measure.id for voice_measure in stack] for stack in current_path
            ]
            print(f"Found solution: {solution_id}")
            yield list(current_path)
            return

        prospect_ids = self.backtrack_adjacencies[current_index][current_stack.id]
        stack_options = [
            theory.BaseMeasureStack.obj_cache[prospect_id]
            for prospect_id in prospect_ids
        ]
        random.shuffle(stack_options)

        attempted_index = current_index - 1
        while stack_options:
            chosen_stack = stack_options.pop()
            if self.increment_dotted_counts(chosen_stack):
                current_path.appendleft(chosen_stack)
                if self.path_is_valid(current_path, attempted_index):
                    solution_iter = self.get_solution(
                        attempted_index, chosen_stack, current_path
                    )
                    yield from solution_iter

                self.decrement_dotted_counts(chosen_stack)
                current_path.popleft()

        if time.time() - self.start_time > 600:
            raise CompositionError("Time limit elapsed.")

    def path_is_valid(
        self,
        current_path: deque[theory.VariantStack],
        attempted_index: int,
    ) -> bool:
        test_suite = [
            partial(
                rules.checked_consecutive_durations,
                current_path,
            ),
            partial(
                rules.checked_consecutive_skips,
                current_path,
            ),
            partial(
                rules.checked_consecutive_intervals,
                current_path,
            ),
            partial(
                rules.checked_melodic_outline,
                current_path,
                self.allowed_fifth_endpoints,
            ),
            partial(rules.checked_melodic_bounds, current_path),
        ]

        for unique_index in self.uniques[attempted_index]:
            if unique_index > attempted_index:
                comparator_stack = current_path[unique_index - attempted_index]
                test_suite.append(
                    partial(
                        rules.are_measure_stacks_unique,
                        current_path[0],
                        comparator_stack,
                    )
                )

        if len(current_path) >= 3:
            test_suite.append(
                partial(
                    rules.checked_melodic_activity,
                    current_path[0],
                    current_path[1],
                    current_path[2],
                    self.__class__.__name__,
                    attempted_index,
                )
            )

        return all(test() for test in test_suite)

    def prescreen_prospects(self) -> list[theory.VariantStack]:
        for transition_index in range(5):
            if self.is_antecedent:
                is_cadence = transition_index == 4
            else:
                is_cadence = transition_index == 3
            if is_cadence:
                self.test_suites[transition_index][-1:-1] = [
                    partial(rules.checked_bass_suspension),
                    partial(rules.checked_upper_suspension),
                ]

            if transition_index == 4 and not self.is_antecedent:
                self.test_suites[transition_index].append(
                    partial(rules.checked_cadential_successor)
                )
            else:
                if is_cadence:
                    allowed_vectors = {0, -1}
                else:
                    allowed_vectors = {0, -1, 1, -2, 2, -3, 3, -4, 4}
                self.test_suites[transition_index].append(
                    partial(
                        rules.checked_superius_transition,
                        allowed_vectors=allowed_vectors,
                    )
                )

            allowed_downbeat_unison = (
                transition_index == 4 and not self.is_intermediate_sequence
            )
            self.test_suites[transition_index].extend(
                [
                    partial(
                        rules.checked_duo_transition,
                        allowed_downbeat_unison=allowed_downbeat_unison,
                    ),
                    partial(rules.checked_trio_transition),
                ]
            )
        return self.prune()

    def realize(self) -> Iterator[list[theory.VariantStack]]:
        starting_points = self.prescreen_prospects()
        print("Prescreen complete")
        random.shuffle(starting_points)

        self.start_time = time.time()
        for starting_point in starting_points:
            solution_iter = self.get_solution(
                self.final_index, starting_point, deque([starting_point])
            )
            yield from solution_iter
            print("Starting point failed. Choosing anew.")
        print("Propagation exhausted. Backtracking to previous sequence.")


class BasseDansePartial(SequencePartial):
    known_uniques = {1: 4, 2: 5}

    def create_test_suite(self) -> None:
        super().create_test_suite()
        self.test_suites[0] = [
            partial(
                rules.checked_solo_partial_transition,
                flattened_pitch=self.flattened_pitch,
            ),
            partial(rules.checked_partial_cross_pitches),
            partial(rules.checked_quartet_transition),
            partial(
                rules.checked_endpoints,
                allowed_fifth_endpoints=self.allowed_fifth_endpoints,
                allowed_fourth_endpoints=self.allowed_fourth_endpoints,
            ),
        ]

    def prescreen_prospects(self) -> list[theory.VariantStack]:
        for transition_index in range(5):
            if is_authentic_cadence := transition_index == 3:
                self.test_suites[transition_index][-1:-1] = [
                    partial(rules.checked_bass_suspension),
                    partial(rules.checked_upper_suspension),
                ]
            if transition_index == 4:
                self.test_suites[transition_index].append(
                    partial(rules.checked_cadential_successor)
                )
            else:
                if is_authentic_cadence:
                    allowed_vectors = {0, -1}
                else:
                    allowed_vectors = {0, -1, 1, -2, 2, -3, 3, -4, 4}
                self.test_suites[transition_index].append(
                    partial(
                        rules.checked_superius_transition,
                        allowed_vectors=allowed_vectors,
                    )
                )

            allowed_downbeat_unison = transition_index == 0 or transition_index == 4
            self.test_suites[transition_index].extend(
                [
                    partial(
                        rules.checked_duo_transition,
                        allowed_downbeat_unison=allowed_downbeat_unison,
                    ),
                    partial(rules.checked_trio_transition),
                ]
            )
        return self.prune()


class BranleSimplePartial(SequencePartial):
    pass


class BranleGaySemelPartial(SequencePartial):
    pass


class ScorePart:
    def __init__(self, clef: str, will_refrain: bool) -> None:
        self.clef = clef
        self.will_refrain = will_refrain
        self.sections: list[list[theory.SpecificNote | theory.RestNote]] = []

    def __iter__(self) -> Iterator[theory.SpecificNote | theory.RestNote]:
        for section in self.sections:
            for _ in range(2):
                for sound_obj in section:
                    yield sound_obj
        if self.will_refrain:
            for _ in range(2):
                for sound_obj in self.sections[0]:
                    yield sound_obj

    def add_section(
        self, sound_sequence: Iterator[theory.SpecificNote | theory.RestNote]
    ) -> None:
        self.sections.append(list(sound_sequence))


TwoDimensionStack = list[list[theory.VariantStack]]


class DanceScore:
    def __init__(
        self,
        chosen_mode: theory.ModalScale,
        clef_group: list[str],
        score_sequences: TwoDimensionStack,
        chosen_instrument: theory.MidiInstrument,
        tempo: int,
        will_refrain: bool,
    ) -> None:
        self.scale = chosen_mode
        print(f"Using {chosen_instrument}")
        self.instrument = chosen_instrument
        """You can have two parts with the same clef 
        (e.g., contratenor and tenor voices using the alto clef) 
        Therefore, a list is used instead of a dictionary"""
        self.parts = [ScorePart(clef, will_refrain) for clef in clef_group]

        for score_sequence in score_sequences:
            for score_part, voice_measures in zip(self.parts, zip(*score_sequence)):
                score_part.add_section(
                    sound_obj
                    for voice_measure in voice_measures
                    for sound_obj in voice_measure
                )
        self.tempo = tempo
