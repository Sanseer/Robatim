from collections import defaultdict, deque
from fractions import Fraction
from functools import wraps
import itertools
from typing import Callable, Iterator

from generate import theory


def is_lowest_duo_good(
    lower_voice_pitch: theory.SpecificPitch, upper_voice_pitch: theory.SpecificPitch
) -> bool:
    if lower_voice_pitch > upper_voice_pitch:
        return False
    second_voice_boundary = lower_voice_pitch + theory.Interval.get("P12")
    return upper_voice_pitch <= second_voice_boundary


def is_upper_duo_good(
    lower_voice_pitch: theory.SpecificPitch, upper_voice_pitch: theory.SpecificPitch
) -> bool:
    if lower_voice_pitch > upper_voice_pitch:
        return False
    second_voice_boundary = lower_voice_pitch + theory.Interval.get("P8")
    return upper_voice_pitch <= second_voice_boundary


absolute_failures = defaultdict(set)
conditional_successes: dict[str, dict[int, set[int]]] = defaultdict(
    lambda: defaultdict(set)
)

"""Will not use functools.lru_cache; decorator applies to multiple mandatory tests.   
Caller of function needs to know ahead of time if any of the tests will fail 
(via absolute_failures), so they can discard a prospect without testing."""


def cache_variant_to_full_stack(
    func: Callable[[theory.VariantStack, theory.FullMeasureStack], bool]
) -> Callable[[theory.VariantStack, theory.FullMeasureStack], bool]:
    @wraps(func)
    def wrapper(
        first_measure_stack: theory.VariantStack,
        second_measure_stack: theory.FullMeasureStack,
    ) -> bool:
        first_id, second_id = first_measure_stack.id, second_measure_stack.id
        func_successes = conditional_successes[func.__name__]
        if second_id in func_successes[first_id]:
            return True
        if verdict := func(first_measure_stack, second_measure_stack):
            func_successes[first_id].add(second_id)
        else:
            absolute_failures[first_id].add(second_id)
        return verdict

    return wrapper


def cache_full_to_full_stack(
    func: Callable[[theory.FullMeasureStack, theory.FullMeasureStack], bool]
) -> Callable[[theory.FullMeasureStack, theory.FullMeasureStack], bool]:
    @wraps(func)
    def wrapper(
        first_measure_stack: theory.FullMeasureStack,
        second_measure_stack: theory.FullMeasureStack,
    ) -> bool:
        first_id, second_id = first_measure_stack.id, second_measure_stack.id
        func_successes = conditional_successes[func.__name__]
        if second_id in func_successes[first_id]:
            return True
        if verdict := func(first_measure_stack, second_measure_stack):
            func_successes[first_id].add(second_id)
        else:
            absolute_failures[first_id].add(second_id)
        return verdict

    return wrapper


solo_transition_successes: dict[int, set[int]] = defaultdict(set)
solo_transition_failures: dict[int, set[int]] = defaultdict(set)


def checked_solo_transition(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
    flattened_pitch: theory.GenericPitch,
) -> bool:
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        first_id, second_id = first_voice_measure.id, second_voice_measure.id
        if second_id in solo_transition_successes[first_id]:
            continue
        if second_id in solo_transition_failures[first_id]:
            return False

        if checked_solo_motion(
            first_voice_measure, second_voice_measure, flattened_pitch
        ):
            solo_transition_successes[first_id].add(second_id)
        else:
            solo_transition_failures[first_id].add(second_id)
            return False
    return True


def checked_solo_motion(
    first_voice_measure: theory.FullVoiceMeasure,
    second_voice_measure: theory.FullVoiceMeasure,
    flattened_pitch: theory.GenericPitch,
) -> bool:
    first_pitch = first_voice_measure[-1].specific_pitch
    second_pitch = second_voice_measure[0].specific_pitch
    voice_distance = theory.SpecificPitch.get_interval_distance(
        first_pitch, second_pitch
    )
    if voice_distance > 7 or voice_distance == 6:
        return False

    leap_direction = theory.SpecificPitch.get_direction(first_pitch, second_pitch)
    if len(second_voice_measure) > 1:
        resolving_pitch = second_voice_measure[1].specific_pitch
        resolving_direction = theory.SpecificPitch.get_direction(
            second_pitch, resolving_pitch
        )
        if voice_distance == 7 and leap_direction == resolving_direction:
            return False
        if second_voice_measure[0].duration == Fraction("1/4") and voice_distance > 1:
            if len(second_voice_measure) != 4:
                return False
            if resolving_direction != -leap_direction:
                return False
            previous_pitch = resolving_pitch
            for current_note in second_voice_measure.sequence[2:]:
                current_pitch = current_note.specific_pitch
                current_direction = theory.SpecificPitch.get_direction(
                    previous_pitch, current_pitch
                )
                if current_direction != resolving_direction:
                    return False
                previous_pitch = current_pitch

        if (
            second_voice_measure[0].duration == Fraction("1/4")
            and second_voice_measure[1].duration == Fraction("1/4")
            and not checked_chromatic_relation(first_pitch, resolving_pitch)
        ):
            return False
        if (
            voice_distance
            and resolving_direction
            and not test_melodic_pyramid(first_pitch, second_pitch, resolving_pitch)
        ):
            return False

    if voice_distance == 5:
        if second_pitch != first_pitch + theory.Interval.get("m6"):
            return False
        if len(second_voice_measure) == 1:
            return False

        resolving_distance = theory.SpecificPitch.get_interval_distance(
            second_pitch, resolving_pitch
        )
        if resolving_distance != 1:
            return False
        if leap_direction == resolving_direction:
            return False

    # prevents stepwise ascent to picardy third with Phrygian
    if first_pitch.has_interval_shift(second_pitch, ("A2", "A4", "d5")):
        return False

    if len(first_voice_measure) > 1:
        previous_pitch = first_voice_measure[-2].specific_pitch
        previous_direction = theory.SpecificPitch.get_direction(
            previous_pitch, first_pitch
        )
        if (
            voice_distance
            and previous_direction
            and not test_melodic_pyramid(previous_pitch, first_pitch, second_pitch)
        ):
            return False
        if first_voice_measure[-1].duration == Fraction("1/4"):
            if voice_distance != 1:
                return False
            if leap_direction == -1 and previous_direction == 1:
                return False

            if first_voice_measure[-2].duration == Fraction("1/4"):
                if not checked_chromatic_relation(previous_pitch, second_pitch):
                    return False
                # Do not use the same neighbor figure twice in a row
                if (
                    second_voice_measure[0].duration == Fraction("1/4")
                    and second_voice_measure[1].duration == Fraction("1/4")
                    and previous_direction == -1
                    and leap_direction == 1
                    and resolving_direction == -1
                ):
                    next_next_direction = theory.SpecificPitch.get_direction(
                        resolving_pitch, second_voice_measure[2].specific_pitch
                    )
                    if next_next_direction == 1:
                        return False
    if is_agogic_combo(first_voice_measure, second_voice_measure):
        return False
    if first_pitch.generic_pitch == flattened_pitch:
        if leap_direction == 1:
            return False
        if voice_distance > 3:
            return False
    return checked_chromatic_relation(first_pitch, second_pitch)


def checked_endpoints(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
    allowed_fifth_endpoints: set[str],
    allowed_fourth_endpoints: set[str],
) -> bool:
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        first_pitch = first_voice_measure[-1].specific_pitch
        second_pitch = second_voice_measure[0].specific_pitch
        voice_distance = theory.SpecificPitch.get_interval_distance(
            first_pitch, second_pitch
        )

        current_pitch_endpoints = {
            first_pitch.generic_pitch,
            second_pitch.generic_pitch,
        }
        if voice_distance == 7 or voice_distance == 4:
            if not current_pitch_endpoints & allowed_fifth_endpoints:
                return False
        elif voice_distance == 3:
            if not current_pitch_endpoints & allowed_fourth_endpoints:
                return False
    return True


def checked_chromatic_relation(
    first_pitch: theory.SpecificPitch, second_pitch: theory.SpecificPitch
) -> bool:
    if first_pitch.letter == second_pitch.letter:
        return first_pitch.generic_pitch == second_pitch.generic_pitch
    return True


all_voice_pairs = ((0, 1), (1, 2), (2, 3), (0, 2), (0, 3), (1, 3))


def get_measure_quartets(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> Iterator[
    tuple[
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
    ]
]:
    for first_voice_index, second_voice_index in all_voice_pairs:
        first_lower_measure = first_measure_stack[first_voice_index]
        first_upper_measure = first_measure_stack[second_voice_index]
        second_lower_measure = second_measure_stack[first_voice_index]
        second_upper_measure = second_measure_stack[second_voice_index]
        yield first_lower_measure, first_upper_measure, second_lower_measure, second_upper_measure


agogic_directions: dict[int, int] = {}


def get_agogic_direction(chosen_voice_measure: theory.FullVoiceMeasure) -> int:
    if len(chosen_voice_measure) != 3:
        return 0

    first_pitch = chosen_voice_measure[0].specific_pitch
    second_pitch = chosen_voice_measure[1].specific_pitch
    third_pitch = chosen_voice_measure[2].specific_pitch
    first_direction = theory.SpecificPitch.get_direction(first_pitch, second_pitch)
    second_direction = theory.SpecificPitch.get_direction(second_pitch, third_pitch)

    if first_direction != second_direction:
        return 0
    return first_direction


def is_agogic_combo(
    first_voice_measure: theory.FullVoiceMeasure,
    second_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    if (chosen_id := first_voice_measure.id) not in agogic_directions:
        agogic_directions[chosen_id] = get_agogic_direction(first_voice_measure)
    if not (first_direction := agogic_directions[chosen_id]):
        return False
    if (chosen_id := second_voice_measure.id) not in agogic_directions:
        agogic_directions[chosen_id] = get_agogic_direction(second_voice_measure)
    if not (second_direction := agogic_directions[chosen_id]):
        return False

    if first_direction != second_direction:
        return False
    return first_voice_measure[0].duration == second_voice_measure[0].duration


@cache_full_to_full_stack
def checked_cross_measures(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    for (
        first_lower_measure,
        first_upper_measure,
        second_lower_measure,
        second_upper_measure,
    ) in get_measure_quartets(first_measure_stack, second_measure_stack):
        if is_agogic_combo(first_lower_measure, second_upper_measure):
            return False
        if is_agogic_combo(first_upper_measure, second_lower_measure):
            return False
        if (
            len(first_lower_measure) > 1
            and first_lower_measure[-1].duration == Fraction("1/4")
            and first_lower_measure[-2].duration == Fraction("1/4")
        ):
            if not checked_chromatic_relation(
                first_lower_measure[-2].specific_pitch,
                second_upper_measure[0].specific_pitch,
            ):
                return False
        if (
            len(first_upper_measure) > 1
            and first_upper_measure[-1].duration == Fraction("1/4")
            and first_upper_measure[-2].duration == Fraction("1/4")
        ):
            if not checked_chromatic_relation(
                first_upper_measure[-2].specific_pitch,
                second_lower_measure[0].specific_pitch,
            ):
                return False

        if (
            len(second_lower_measure) > 1
            and second_lower_measure[0].duration == Fraction("1/4")
            and second_lower_measure[1].duration == Fraction("1/4")
        ):
            if not checked_chromatic_relation(
                first_upper_measure[-1].specific_pitch,
                second_lower_measure[1].specific_pitch,
            ):
                return False
        if (
            len(second_upper_measure) > 1
            and second_upper_measure[0].duration == Fraction("1/4")
            and second_upper_measure[1].duration == Fraction("1/4")
        ):
            if not checked_chromatic_relation(
                first_lower_measure[-1].specific_pitch,
                second_upper_measure[1].specific_pitch,
            ):
                return False
    return True


def test_melodic_pyramid(
    first_pitch: theory.SpecificPitch,
    second_pitch: theory.SpecificPitch,
    third_pitch: theory.SpecificPitch,
) -> bool:
    first_vector = theory.SpecificPitch.get_interval_vector(first_pitch, second_pitch)
    if first_vector == -2:
        return True
    second_vector = theory.SpecificPitch.get_interval_vector(second_pitch, third_pitch)
    if second_vector == 2:
        return True

    # checking if signs are the same
    if (first_vector * second_vector) < 0:
        return True
    # Upward motion decelerates. Downward motion accelerates.
    return first_vector >= second_vector


def checked_solo_partial_transition(
    first_measure_stack: theory.HalfMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
    flattened_pitch: theory.GenericPitch,
) -> bool:
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        first_id, second_id = first_voice_measure.id, second_voice_measure.id
        if second_id in solo_transition_successes[first_id]:
            continue
        if second_id in solo_transition_failures[first_id]:
            return False

        if checked_partial_solo_motion(
            first_voice_measure, second_voice_measure, flattened_pitch
        ):
            solo_transition_successes[first_id].add(second_id)
        else:
            solo_transition_failures[first_id].add(second_id)
            return False
    return True


def checked_partial_solo_motion(
    first_voice_measure: theory.HalfVoiceMeasure,
    second_voice_measure: theory.FullVoiceMeasure,
    flattened_pitch: theory.GenericPitch,
) -> bool:
    first_pitch = first_voice_measure[-1].specific_pitch
    second_pitch = second_voice_measure[0].specific_pitch
    voice_distance = theory.SpecificPitch.get_interval_distance(
        first_pitch, second_pitch
    )
    if voice_distance > 7 or voice_distance == 6:
        return False

    leap_direction = theory.SpecificPitch.get_direction(first_pitch, second_pitch)
    if voice_distance == 7:
        if len(second_voice_measure) > 1:
            resolving_pitch = second_voice_measure[1].specific_pitch
            resolving_direction = theory.SpecificPitch.get_direction(
                second_pitch, resolving_pitch
            )
            if leap_direction == resolving_direction:
                return False
    elif voice_distance == 5:
        if second_pitch != first_pitch + theory.Interval.get("m6"):
            return False
        if len(second_voice_measure) == 1:
            return False

        resolving_pitch = second_voice_measure[1].specific_pitch
        resolving_distance = theory.SpecificPitch.get_interval_distance(
            second_pitch, resolving_pitch
        )
        if resolving_distance != 1:
            return False
        resolving_direction = theory.SpecificPitch.get_direction(
            second_pitch, resolving_pitch
        )
        if leap_direction == resolving_direction:
            return False

    if second_voice_measure[0].duration == Fraction("1/4") and voice_distance > 1:
        return False
    if first_pitch.has_interval_shift(second_pitch, ("A2", "A4", "d5")):
        return False

    if len(second_voice_measure) > 1:
        next_pitch = second_voice_measure[1].specific_pitch
        if (
            second_voice_measure[0].duration == Fraction("1/4")
            and second_voice_measure[1].duration == Fraction("1/4")
            and not checked_chromatic_relation(first_pitch, next_pitch)
        ):
            return False
        if voice_distance:
            if second_pitch != next_pitch and not test_melodic_pyramid(
                first_pitch, second_pitch, next_pitch
            ):
                return False

    if (
        first_pitch.letter == second_pitch.letter
        and first_pitch.generic_pitch != second_pitch.generic_pitch
    ):
        return False
    if first_pitch.generic_pitch == flattened_pitch:
        if leap_direction == 1:
            return False
        if voice_distance > 3:
            return False
    return True


def get_partial_quartets(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
) -> Iterator[
    tuple[
        theory.VariantVoiceMeasure,
        theory.VariantVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
    ]
]:
    for first_voice_index, second_voice_index in all_voice_pairs:
        first_lower_measure = first_measure_stack[first_voice_index]
        first_upper_measure = first_measure_stack[second_voice_index]
        second_lower_measure = second_measure_stack[first_voice_index]
        second_upper_measure = second_measure_stack[second_voice_index]
        yield first_lower_measure, first_upper_measure, second_lower_measure, second_upper_measure


@cache_variant_to_full_stack
def checked_partial_cross_pitches(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    for (
        first_lower_measure,
        first_upper_measure,
        second_lower_measure,
        second_upper_measure,
    ) in get_partial_quartets(first_measure_stack, second_measure_stack):
        if (
            len(second_lower_measure) > 1
            and second_lower_measure[0].duration == Fraction("1/4")
            and second_lower_measure[1].duration == Fraction("1/4")
        ):
            if not checked_chromatic_relation(
                first_upper_measure[-1].specific_pitch,
                second_lower_measure[1].specific_pitch,
            ):
                return False
        if (
            len(second_upper_measure) > 1
            and second_upper_measure[0].duration == Fraction("1/4")
            and second_upper_measure[1].duration == Fraction("1/4")
        ):
            if not checked_chromatic_relation(
                first_lower_measure[-1].specific_pitch,
                second_upper_measure[1].specific_pitch,
            ):
                return False
    return True


def is_duo_consonant(
    lower_pitch: theory.SpecificPitch,
    upper_pitch: theory.SpecificPitch,
    consonant_ids: tuple[str, ...],
) -> bool:
    return lower_pitch.has_interval_shift(upper_pitch, consonant_ids)


def is_duo_motion_valid(
    first_lower_note: theory.SpecificNote,
    first_upper_note: theory.SpecificNote,
    second_lower_note: theory.SpecificNote,
    second_upper_note: theory.SpecificNote,
    consonant_ids: tuple[str, ...],
    attack_requires_consonance: bool,
    allowed_unison: bool,
) -> bool:
    first_lower_pitch = first_lower_note.specific_pitch
    first_upper_pitch = first_upper_note.specific_pitch
    second_lower_pitch = second_lower_note.specific_pitch
    second_upper_pitch = second_upper_note.specific_pitch

    lower_voice_distance = theory.SpecificPitch.get_interval_distance(
        first_lower_pitch, second_lower_pitch
    )
    upper_voice_distance = theory.SpecificPitch.get_interval_distance(
        first_upper_pitch, second_upper_pitch
    )
    preceded_by_dissonance = not is_duo_consonant(
        first_lower_pitch, first_upper_pitch, consonant_ids
    )

    if lower_voice_distance and upper_voice_distance:
        if second_lower_pitch >= first_upper_pitch:
            return False
        if second_upper_pitch <= first_lower_pitch:
            return False

        lower_voice_direction = theory.SpecificPitch.get_direction(
            first_lower_pitch, second_lower_pitch
        )
        upper_voice_direction = theory.SpecificPitch.get_direction(
            first_upper_pitch, second_upper_pitch
        )
        if preceded_by_dissonance:
            if lower_voice_distance > 1 or upper_voice_distance > 1:
                return False
            if lower_voice_direction == upper_voice_direction:
                return False
        if attack_requires_consonance and not is_duo_consonant(
            second_lower_pitch, second_upper_pitch, consonant_ids
        ):
            return False
        if not allowed_unison and second_lower_pitch == second_upper_pitch:
            return False

        if lower_voice_direction == upper_voice_direction:
            if second_lower_pitch.has_interval_shift(second_upper_pitch):
                if upper_voice_distance != 1:
                    return False
                if lower_voice_distance == 1:
                    return False
                if first_lower_note.duration < Fraction("1/2"):
                    return False
                if first_upper_note.duration < Fraction("1/2"):
                    return False
    elif lower_voice_distance > 1 or upper_voice_distance > 1:
        if preceded_by_dissonance:
            return False
        if attack_requires_consonance and not is_duo_consonant(
            second_lower_pitch, second_upper_pitch, consonant_ids
        ):
            return False
    elif not allowed_unison and second_lower_pitch == second_upper_pitch:
        return False
    if (
        first_lower_pitch.letter == second_upper_pitch.letter
        and first_lower_pitch.generic_pitch != second_upper_pitch.generic_pitch
    ):
        return False
    if (
        first_upper_pitch.letter == second_lower_pitch.letter
        and first_upper_pitch.generic_pitch != second_lower_pitch.generic_pitch
    ):
        return False
    return True


def is_cadential_duo_valid(
    first_lower_note: theory.SpecificNote,
    first_upper_note: theory.SpecificNote,
    second_lower_note: theory.SpecificNote,
    second_upper_note: theory.SpecificNote,
    consonant_ids: tuple[str, ...],
    attack_requires_consonance: bool,
) -> bool:
    first_lower_pitch = first_lower_note.specific_pitch
    first_upper_pitch = first_upper_note.specific_pitch
    second_lower_pitch = second_lower_note.specific_pitch
    second_upper_pitch = second_upper_note.specific_pitch
    if second_lower_pitch == second_upper_pitch:
        return False

    lower_voice_distance = theory.SpecificPitch.get_interval_distance(
        first_lower_pitch, second_lower_pitch
    )
    upper_voice_distance = theory.SpecificPitch.get_interval_distance(
        first_upper_pitch, second_upper_pitch
    )
    if lower_voice_distance and upper_voice_distance:
        if second_lower_pitch >= first_upper_pitch:
            return False
        if second_upper_pitch <= first_lower_pitch:
            return False
        if attack_requires_consonance and not is_duo_consonant(
            second_lower_pitch, second_upper_pitch, consonant_ids
        ):
            return False

        lower_voice_direction = theory.SpecificPitch.get_direction(
            first_lower_pitch, second_lower_pitch
        )
        upper_voice_direction = theory.SpecificPitch.get_direction(
            first_upper_pitch, second_upper_pitch
        )

        if lower_voice_direction == upper_voice_direction:
            if second_lower_pitch.has_interval_shift(second_upper_pitch):
                if upper_voice_distance != 1:
                    return False
                if lower_voice_distance == 1:
                    return False
                if first_lower_note.duration < Fraction("1/2"):
                    return False
                if first_upper_note.duration < Fraction("1/2"):
                    return False

    return True


lower_voice_consonances = ("P8", "P5", "M3", "m3", "M6", "m6")
upper_voice_consonances = ("P8", "P5", "M3", "m3", "M6", "m6", "P4")


def is_bass_suspension_valid(
    first_lower_note: theory.SpecificNote,
    first_upper_note: theory.SpecificNote,
    second_lower_note: theory.SpecificNote,
    second_upper_note: theory.SpecificNote,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    first_lower_pitch = first_lower_note.specific_pitch
    first_upper_pitch = first_upper_note.specific_pitch
    second_lower_pitch = second_lower_note.specific_pitch
    second_upper_pitch = second_upper_note.specific_pitch
    if is_duo_consonant(
        second_lower_pitch,
        second_upper_pitch,
        lower_voice_consonances,
    ):
        return True

    if first_lower_note.duration != Fraction("1/2"):
        return False
    if first_upper_note.duration != Fraction("1/2"):
        return False
    if first_upper_pitch != second_upper_pitch:
        return False
    if not is_duo_consonant(
        first_lower_pitch,
        first_upper_pitch,
        lower_voice_consonances,
    ):
        return False
    if second_lower_pitch.has_interval_shift(second_upper_pitch, ("m2",)):
        return False
    return has_imperfect_resolution(second_measure_stack)


imperfect_consonances = ("M3", "m3", "M6", "m6")


def has_imperfect_resolution(measure_stack: theory.FullMeasureStack) -> bool:
    pitch_quartet = [
        measure_stack[0][-1].specific_pitch,
        measure_stack[1][-1].specific_pitch,
        measure_stack[2][-1].specific_pitch,
        measure_stack[3][-1].specific_pitch,
    ]
    for first_voice_index, second_voice_index in all_voice_pairs:
        lower_pitch = pitch_quartet[first_voice_index]
        upper_pitch = pitch_quartet[second_voice_index]
        if lower_pitch.has_interval_shift(upper_pitch, imperfect_consonances):
            return True
    return False


def checked_duo_transition(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
    allowed_downbeat_unison: bool,
    check_bass_suspension: bool,
) -> bool:
    consonant_ids: tuple[str, ...]
    for first_voice_index, second_voice_index in all_voice_pairs:
        if first_voice_index == 0:
            consonant_ids = lower_voice_consonances
        else:
            consonant_ids = upper_voice_consonances

        if not is_duo_motion_valid(
            first_measure_stack[first_voice_index][-1],
            first_measure_stack[second_voice_index][-1],
            second_measure_stack[first_voice_index][0],
            second_measure_stack[second_voice_index][0],
            consonant_ids,
            False,
            allowed_downbeat_unison,
        ):
            return False

    if check_bass_suspension:
        for upper_voice_index in (1, 2, 3):
            if not is_bass_suspension_valid(
                first_measure_stack[0][-1],
                first_measure_stack[upper_voice_index][-1],
                second_measure_stack[0][0],
                second_measure_stack[upper_voice_index][0],
                second_measure_stack,
            ):
                return False
    return True


def is_perfect_fourth_consonant(
    lowest_pitch: theory.SpecificPitch,
    middle_pitch: theory.SpecificPitch,
    highest_pitch: theory.SpecificPitch,
) -> bool:
    if middle_pitch.has_interval_shift(highest_pitch, ("P4",)):
        return lowest_pitch.has_interval_shift(middle_pitch, ("M3", "m3", "P5"))
    return True


def is_trio_motion_valid(
    first_lowest_pitch: theory.SpecificPitch,
    first_middle_pitch: theory.SpecificPitch,
    first_highest_pitch: theory.SpecificPitch,
    second_lowest_pitch: theory.SpecificPitch,
    second_middle_pitch: theory.SpecificPitch,
    second_highest_pitch: theory.SpecificPitch,
    attack_requires_consonance: bool,
) -> bool:
    middle_voice_distance = theory.SpecificPitch.get_interval_distance(
        first_middle_pitch, second_middle_pitch
    )
    highest_voice_distance = theory.SpecificPitch.get_interval_distance(
        first_highest_pitch, second_highest_pitch
    )
    preceded_by_dissonance = not is_perfect_fourth_consonant(
        first_lowest_pitch, first_middle_pitch, first_highest_pitch
    )

    if middle_voice_distance and highest_voice_distance:
        if preceded_by_dissonance:
            if middle_voice_distance > 1 or highest_voice_distance > 1:
                return False
        if attack_requires_consonance and not is_perfect_fourth_consonant(
            second_lowest_pitch, second_middle_pitch, second_highest_pitch
        ):
            return False
    elif middle_voice_distance > 1 or highest_voice_distance > 1:
        if preceded_by_dissonance:
            return False
        if attack_requires_consonance and not is_perfect_fourth_consonant(
            second_lowest_pitch, second_middle_pitch, second_highest_pitch
        ):
            return False
    return True


def is_cadential_trio_valid(
    first_lowest_pitch: theory.SpecificPitch,
    first_middle_pitch: theory.SpecificPitch,
    first_highest_pitch: theory.SpecificPitch,
    second_lowest_pitch: theory.SpecificPitch,
    second_middle_pitch: theory.SpecificPitch,
    second_highest_pitch: theory.SpecificPitch,
) -> bool:
    has_middle_voice_moved = first_middle_pitch != second_middle_pitch
    has_highest_voice_moved = first_highest_pitch != second_highest_pitch

    if has_middle_voice_moved and has_highest_voice_moved:
        return is_perfect_fourth_consonant(
            second_lowest_pitch, second_middle_pitch, second_highest_pitch
        )
    return True


def is_trio_consonant(
    lowest_pitch: theory.SpecificPitch,
    middle_pitch: theory.SpecificPitch,
    highest_pitch: theory.SpecificPitch,
) -> bool:
    if not is_duo_consonant(middle_pitch, highest_pitch, upper_voice_consonances):
        return False
    return is_perfect_fourth_consonant(lowest_pitch, middle_pitch, highest_pitch)


def is_upper_suspension_valid(
    first_lowest_note: theory.SpecificNote,
    first_middle_note: theory.SpecificNote,
    first_highest_note: theory.SpecificNote,
    second_lowest_pitch: theory.SpecificPitch,
    second_middle_pitch: theory.SpecificPitch,
    second_highest_pitch: theory.SpecificPitch,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    if is_trio_consonant(
        second_lowest_pitch, second_middle_pitch, second_highest_pitch
    ):
        return True

    if first_middle_note.duration != Fraction("1/2"):
        return False
    if first_highest_note.duration != Fraction("1/2"):
        return False
    first_lowest_pitch = first_lowest_note.specific_pitch
    first_middle_pitch = first_middle_note.specific_pitch
    first_highest_pitch = first_highest_note.specific_pitch
    if not (
        first_highest_pitch == second_highest_pitch
        or first_middle_pitch == second_middle_pitch
    ):
        return False
    if not is_trio_consonant(
        first_lowest_pitch,
        first_middle_pitch,
        first_highest_pitch,
    ):
        return False
    if second_middle_pitch.has_interval_shift(second_highest_pitch, ("m2",)):
        return False
    return has_imperfect_resolution(second_measure_stack)


upper_duos = ((1, 2), (1, 3), (2, 3))


def checked_trio_transition(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
    check_upper_suspension: bool,
) -> bool:
    first_lowest_pitch = first_measure_stack[0][-1].specific_pitch
    second_lowest_pitch = second_measure_stack[0][0].specific_pitch
    for second_voice_index, third_voice_index in upper_duos:
        first_middle_pitch = first_measure_stack[second_voice_index][-1].specific_pitch
        first_highest_pitch = first_measure_stack[third_voice_index][-1].specific_pitch
        second_middle_pitch = second_measure_stack[second_voice_index][0].specific_pitch
        second_highest_pitch = second_measure_stack[third_voice_index][0].specific_pitch

        if not is_trio_motion_valid(
            first_lowest_pitch,
            first_middle_pitch,
            first_highest_pitch,
            second_lowest_pitch,
            second_middle_pitch,
            second_highest_pitch,
            False,
        ):
            return False
        if check_upper_suspension:
            if not is_upper_suspension_valid(
                first_measure_stack[0][-1],
                first_measure_stack[second_voice_index][-1],
                first_measure_stack[third_voice_index][-1],
                second_lowest_pitch,
                second_middle_pitch,
                second_highest_pitch,
                second_measure_stack,
            ):
                return False
    return True


@cache_variant_to_full_stack
def checked_quartet_transition(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    bassus_pair = (
        first_measure_stack[0][-1].specific_pitch,
        second_measure_stack[0][0].specific_pitch,
    )
    tenor_pair = (
        first_measure_stack[1][-1].specific_pitch,
        second_measure_stack[1][0].specific_pitch,
    )
    contratenor_pair = (
        first_measure_stack[2][-1].specific_pitch,
        second_measure_stack[2][0].specific_pitch,
    )
    superius_pair = (
        first_measure_stack[3][-1].specific_pitch,
        second_measure_stack[3][0].specific_pitch,
    )

    return checked_quartet_motion(
        bassus_pair, tenor_pair, contratenor_pair, superius_pair
    )


def checked_quartet_motion(
    bassus_pair: tuple[theory.SpecificPitch, theory.SpecificPitch],
    tenor_pair: tuple[theory.SpecificPitch, theory.SpecificPitch],
    contratenor_pair: tuple[theory.SpecificPitch, theory.SpecificPitch],
    superius_pair: tuple[theory.SpecificPitch, theory.SpecificPitch],
) -> bool:
    voice_directions = set()
    bassus_direction = theory.SpecificPitch.get_direction(*bassus_pair)
    if not bassus_direction:
        return True
    voice_directions.add(bassus_direction)

    tenor_direction = theory.SpecificPitch.get_direction(*tenor_pair)
    if not tenor_direction:
        return True
    voice_directions.add(tenor_direction)
    if len(voice_directions) > 1:
        return True

    contratenor_direction = theory.SpecificPitch.get_direction(*contratenor_pair)
    if not contratenor_direction:
        return True
    voice_directions.add(contratenor_direction)
    if len(voice_directions) > 1:
        return True

    superius_direction = theory.SpecificPitch.get_direction(*superius_pair)
    if not superius_direction:
        return True
    voice_directions.add(superius_direction)
    return len(voice_directions) > 1


@cache_full_to_full_stack
def checked_dissonant_pass(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    first_lowest_measure = first_measure_stack[0]
    second_lowest_measure = second_measure_stack[0]

    for stack_index in range(1, 4):
        first_highest_measure = first_measure_stack[stack_index]
        second_highest_measure = second_measure_stack[stack_index]

        if not test_duo_species(
            first_lowest_measure,
            first_highest_measure,
            second_lowest_measure,
            second_highest_measure,
        ):
            return False

    for second_voice_index, third_voice_index in upper_duos:
        first_middle_measure = first_measure_stack[second_voice_index]
        first_highest_measure = first_measure_stack[third_voice_index]
        second_middle_measure = second_measure_stack[second_voice_index]
        second_highest_measure = second_measure_stack[third_voice_index]

        if not test_trio_species(
            first_lowest_measure,
            first_middle_measure,
            first_highest_measure,
            second_middle_measure,
            second_highest_measure,
        ):
            return False
    return True


def test_duo_species(
    first_lower_measure: theory.FullVoiceMeasure,
    first_upper_measure: theory.FullVoiceMeasure,
    second_lower_measure: theory.FullVoiceMeasure,
    second_upper_measure: theory.FullVoiceMeasure,
) -> bool:
    (
        lower_is_real_cantus,
        lower_is_real_counter,
        lower_is_diminished_cantus,
        lower_is_diminished_counter,
    ) = get_species_role(first_lower_measure)
    (
        upper_is_real_cantus,
        upper_is_real_counter,
        upper_is_diminished_cantus,
        upper_is_diminished_counter,
    ) = get_species_role(first_upper_measure)

    if (
        lower_is_real_cantus
        and upper_is_real_counter
        or lower_is_diminished_cantus
        and upper_is_diminished_counter
        or lower_is_real_counter
        and upper_is_real_cantus
        or lower_is_diminished_counter
        and upper_is_diminished_cantus
    ):
        if is_duo_consonant(
            first_lower_measure[-1].specific_pitch,
            first_upper_measure[-1].specific_pitch,
            lower_voice_consonances,
        ):
            return True

        if upper_is_real_counter or upper_is_diminished_counter:
            return has_passing_figure(
                first_upper_measure[-2].specific_pitch,
                first_upper_measure[-1].specific_pitch,
                second_upper_measure[0].specific_pitch,
            )
        return has_passing_figure(
            first_lower_measure[-2].specific_pitch,
            first_lower_measure[-1].specific_pitch,
            second_lower_measure[0].specific_pitch,
        )
    return True


def get_species_role(
    voice_measure: theory.FullVoiceMeasure,
) -> tuple[bool, bool, bool, bool]:
    if len(voice_measure) == 1:
        is_real_cantus = True
        is_real_counter = False
        is_diminished_cantus = False
        is_diminished_counter = False

    elif len(voice_measure) > 2:
        is_real_cantus = False
        is_real_counter = False
        *_, first_note, second_note = voice_measure
        is_diminished_cantus = second_note.duration == Fraction("1/2")

        if first_note.duration != Fraction("1/4"):
            is_diminished_counter = False
        elif second_note.duration != Fraction("1/4"):
            is_diminished_counter = False
        else:
            interval_distance = theory.SpecificPitch.get_interval_distance(
                first_note.specific_pitch, second_note.specific_pitch
            )
            is_diminished_counter = interval_distance == 1
    else:
        first_note, second_note = voice_measure
        if first_note.specific_pitch == second_note.specific_pitch:
            is_real_cantus = True
            is_diminished_cantus = False
        else:
            is_real_cantus = False
            is_diminished_cantus = first_note.duration == Fraction("1/2")

        # The dot should be thought of as a strong quarter in third species.
        is_diminished_counter = first_note.duration == Fraction("3/4")
        if first_note.duration == Fraction("1/2"):
            interval_distance = theory.SpecificPitch.get_interval_distance(
                first_note.specific_pitch, second_note.specific_pitch
            )
            is_real_counter = interval_distance == 1
        else:
            is_real_counter = False
    return is_real_cantus, is_real_counter, is_diminished_cantus, is_diminished_counter


def has_passing_figure(
    first_pitch: theory.SpecificPitch,
    second_pitch: theory.SpecificPitch,
    third_pitch: theory.SpecificPitch,
) -> bool:
    first_vector = theory.SpecificPitch.get_interval_vector(first_pitch, second_pitch)
    second_vector = theory.SpecificPitch.get_interval_vector(second_pitch, third_pitch)
    return first_vector == second_vector


def test_trio_species(
    first_lowest_measure: theory.FullVoiceMeasure,
    first_middle_measure: theory.FullVoiceMeasure,
    first_highest_measure: theory.FullVoiceMeasure,
    second_middle_measure: theory.FullVoiceMeasure,
    second_highest_measure: theory.FullVoiceMeasure,
) -> bool:
    (
        lower_is_real_cantus,
        lower_is_real_counter,
        lower_is_diminished_cantus,
        lower_is_diminished_counter,
    ) = get_species_role(first_middle_measure)
    (
        upper_is_real_cantus,
        upper_is_real_counter,
        upper_is_diminished_cantus,
        upper_is_diminished_counter,
    ) = get_species_role(first_highest_measure)

    if (
        lower_is_real_cantus
        and upper_is_real_counter
        or lower_is_diminished_cantus
        and upper_is_diminished_counter
        or lower_is_real_counter
        and upper_is_real_cantus
        or lower_is_diminished_counter
        and upper_is_diminished_cantus
    ):
        if lower_is_real_cantus or upper_is_real_cantus:
            lowest_pitch = find_pitch(first_lowest_measure)
        else:
            lowest_pitch = first_lowest_measure[-1].specific_pitch
        if is_trio_consonant(
            lowest_pitch,
            first_middle_measure[-1].specific_pitch,
            first_highest_measure[-1].specific_pitch,
        ):
            return True

        if upper_is_real_counter or upper_is_diminished_counter:
            return has_passing_figure(
                first_highest_measure[-2].specific_pitch,
                first_highest_measure[-1].specific_pitch,
                second_highest_measure[0].specific_pitch,
            )
        return has_passing_figure(
            first_middle_measure[-2].specific_pitch,
            first_middle_measure[-1].specific_pitch,
            second_middle_measure[0].specific_pitch,
        )
    return True


def find_pitch(
    voice_measure: theory.FullVoiceMeasure, duration_repr: str = "3/4"
) -> theory.SpecificPitch:
    elapsed_duration = Fraction("0")
    sought_duration = Fraction(duration_repr)
    for specific_note in voice_measure:
        elapsed_duration += specific_note.duration
        if elapsed_duration >= sought_duration:
            return specific_note.specific_pitch
    else:
        raise ValueError


def checked_superius_transition(
    first_measure_stack: theory.VariantStack,
    second_measure_stack: theory.FullMeasureStack,
    allowed_vectors: set[int],
) -> bool:
    first_superius_pitch = first_measure_stack[-1][-1].specific_pitch
    second_superius_pitch = second_measure_stack[-1][0].specific_pitch
    interval_vector = theory.SpecificPitch.get_interval_vector(
        first_superius_pitch, second_superius_pitch
    )
    return interval_vector in allowed_vectors


valid_cadential_motions = {
    0: {-1, 1, -3, 3, -4, 4},
    1: {0, -1, 1},
    2: {0, -1, 1, -2},
    3: {-1, 1},
}


def checked_cadential_successor(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    stack_index = 0
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        first_pitch = first_voice_measure[-1].specific_pitch
        second_pitch = second_voice_measure[0].specific_pitch
        interval_vector = theory.SpecificPitch.get_interval_vector(
            first_pitch, second_pitch
        )
        if interval_vector not in valid_cadential_motions[stack_index]:
            return False
        stack_index += 1

    for (
        first_lower_measure,
        first_upper_measure,
        second_lower_measure,
        second_upper_measure,
    ) in get_measure_quartets(first_measure_stack, second_measure_stack):
        if has_identical_starts(
            first_lower_measure, first_upper_measure
        ) and has_identical_starts(second_lower_measure, second_upper_measure):
            return False
    return True


def has_identical_starts(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    starting_lower_pitch = lower_voice_measure[0].specific_pitch
    starting_upper_pitch = upper_voice_measure[0].specific_pitch
    return starting_lower_pitch.generic_pitch == starting_upper_pitch.generic_pitch


@cache_full_to_full_stack
def are_measure_stacks_unique(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        if len(first_voice_measure) > 1 and len(second_voice_measure) > 1:
            first_pitch = first_voice_measure[0].specific_pitch
            second_pitch = first_voice_measure[1].specific_pitch
            third_pitch = second_voice_measure[0].specific_pitch
            fourth_pitch = second_voice_measure[1].specific_pitch

            if first_pitch == third_pitch and second_pitch == fourth_pitch:
                return False
    return True


def is_parallel_perfect(
    first_lower_pitch: theory.SpecificPitch,
    first_upper_pitch: theory.SpecificPitch,
    second_lower_pitch: theory.SpecificPitch,
    second_upper_pitch: theory.SpecificPitch,
) -> bool:
    lower_vector = theory.SpecificPitch.get_interval_vector(
        first_lower_pitch, second_lower_pitch
    )
    upper_vector = theory.SpecificPitch.get_interval_vector(
        first_upper_pitch, second_upper_pitch
    )
    if not lower_vector or not upper_vector:
        return False
    if lower_vector != upper_vector:
        return False
    for perfect_interval_repr in ("P5", "P8"):
        if first_lower_pitch.has_interval_shift(
            first_upper_pitch, (perfect_interval_repr,)
        ) and second_lower_pitch.has_interval_shift(
            second_upper_pitch, (perfect_interval_repr,)
        ):
            return True
    return False


@cache_full_to_full_stack
def checked_broken_parallels(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    for (
        first_lower_measure,
        first_upper_measure,
        second_lower_measure,
        second_upper_measure,
    ) in get_measure_quartets(first_measure_stack, second_measure_stack):
        second_lower_pitch = second_lower_measure[0].specific_pitch
        second_upper_pitch = second_upper_measure[0].specific_pitch
        if not second_lower_pitch.has_interval_shift(second_upper_pitch):
            continue

        lower_reverse_iter = reversed(first_lower_measure)
        upper_reverse_iter = reversed(first_upper_measure)
        lower_note = next(lower_reverse_iter)
        upper_note = next(upper_reverse_iter)
        lower_duration = lower_note.duration
        upper_duration = upper_note.duration

        if (lower_duration == Fraction("1/4")) ^ (upper_duration == Fraction("1/4")):
            first_lower_pitch = lower_note.specific_pitch
            first_upper_pitch = upper_note.specific_pitch

            if lower_duration == Fraction("1/4"):
                upper_duration -= lower_duration
                while upper_duration > 0:
                    lower_note = next(lower_reverse_iter)
                    first_lower_pitch = lower_note.specific_pitch
                    if is_parallel_perfect(
                        first_lower_pitch,
                        first_upper_pitch,
                        second_lower_pitch,
                        second_upper_pitch,
                    ):
                        return False

                    lower_duration = lower_note.duration
                    if lower_duration != Fraction("1/4"):
                        break
                    upper_duration -= lower_duration
            else:
                lower_duration -= upper_duration
                while lower_duration > 0:
                    upper_note = next(upper_reverse_iter)
                    first_upper_pitch = upper_note.specific_pitch
                    if is_parallel_perfect(
                        first_lower_pitch,
                        first_upper_pitch,
                        second_lower_pitch,
                        second_upper_pitch,
                    ):
                        return False

                    upper_duration = upper_note.duration
                    if upper_duration != Fraction("1/4"):
                        break
                    lower_duration -= upper_duration

    return True


@cache_full_to_full_stack
def checked_dotted_adjacent(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
) -> bool:
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        if first_voice_measure[0].duration != Fraction("3/4"):
            continue
        if second_voice_measure[0].duration != Fraction("3/4"):
            continue
        return False
    return True


inner_voice_indices = {1, 2}


def checked_melodic_activity(
    first_measure_stack: theory.FullMeasureStack,
    second_measure_stack: theory.FullMeasureStack,
    third_measure_stack: theory.FullMeasureStack,
    sequence_name: str,
    attempted_index: int,
) -> bool:
    if attempted_index == 0 and sequence_name == "BasseDansePartial":
        return True
    voice_index = -1
    for first_voice_measure, second_voice_measure, third_voice_measure in zip(
        first_measure_stack, second_measure_stack, third_measure_stack
    ):
        voice_index += 1
        if voice_index in inner_voice_indices:
            continue
        note_section = itertools.chain(
            first_voice_measure, second_voice_measure, third_voice_measure
        )
        pitch_sequence = [current_note.specific_pitch for current_note in note_section]
        min_pitch = min(pitch_sequence)
        max_pitch = max(pitch_sequence)
        voice_distance = theory.SpecificPitch.get_interval_distance(
            min_pitch, max_pitch
        )
        if voice_distance < 2:
            return False
    return True


def checked_consecutive_durations(current_path: deque[theory.VariantStack]) -> bool:
    for voice_index, starting_voice_measure in enumerate(current_path[0]):
        voice_measures_to_check = [starting_voice_measure]
        previous_voice_measure = starting_voice_measure

        for current_stack in itertools.islice(current_path, 1, len(current_path)):
            if isinstance(current_stack, theory.HalfMeasureStack):
                break
            current_voice_measure = current_stack[voice_index]
            if previous_voice_measure[-1].duration != current_voice_measure[0].duration:
                break

            voice_measures_to_check.append(current_voice_measure)
            if not current_voice_measure.is_rhythm_continuous:
                break
            previous_voice_measure = current_voice_measure

        if len(voice_measures_to_check) > 1 and not has_valid_rhythm(
            voice_measures_to_check
        ):
            return False
    return True


def has_valid_rhythm(
    voice_measures_to_check: list[theory.BaseVoiceMeasure],
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

        duration_count += current_voice_measure.left_bound.rhythm.count
        if theory.RhythmBound.limits[current_duration] < duration_count:
            return False
        if not current_voice_measure.is_rhythm_continuous:
            current_duration = current_voice_measure.right_bound.rhythm.duration
            duration_count = current_voice_measure.right_bound.rhythm.count
    return True


def checked_consecutive_skips(current_path: deque[theory.VariantStack]) -> bool:
    for voice_index, starting_voice_measure in enumerate(current_path[0]):
        voice_measures_to_check = [starting_voice_measure]
        previous_voice_measure = starting_voice_measure

        for current_stack in itertools.islice(current_path, 1, len(current_path)):
            if isinstance(current_stack, theory.HalfMeasureStack):
                break
            current_voice_measure = current_stack[voice_index]
            if not boundary_creates_skip(previous_voice_measure, current_voice_measure):
                break

            voice_measures_to_check.append(current_voice_measure)
            if not current_voice_measure.is_skip_continuous:
                break
            previous_voice_measure = current_voice_measure

        if len(voice_measures_to_check) > 1 and not has_valid_skips(
            voice_measures_to_check, voice_index
        ):
            return False
    return True


def boundary_creates_skip(
    first_voice_measure: theory.BaseVoiceMeasure,
    second_voice_measure: theory.BaseVoiceMeasure,
) -> bool:
    before_transition_pitch = first_voice_measure[-1].specific_pitch
    after_transition_pitch = second_voice_measure[0].specific_pitch
    interval_distance = theory.SpecificPitch.get_interval_distance(
        before_transition_pitch, after_transition_pitch
    )
    return interval_distance > 1


def has_valid_skips(
    voice_measures_to_check: list[theory.BaseVoiceMeasure],
    voice_index: int,
) -> bool:
    skip_count = 0
    previous_voice_measure = voice_measures_to_check[0]

    for current_voice_measure in voice_measures_to_check:
        if isinstance(current_voice_measure, theory.HalfVoiceMeasure):
            skip_count = 0
            previous_voice_measure = current_voice_measure
            continue

        if boundary_creates_skip(previous_voice_measure, current_voice_measure):
            skip_count += 1
            if theory.SkipBound.limits[voice_index] < skip_count:
                return False
        else:
            skip_count = 0

        skip_count += current_voice_measure.left_bound.skip.count
        if theory.SkipBound.limits[voice_index] < skip_count:
            return False
        if not current_voice_measure.is_skip_continuous:
            skip_count = current_voice_measure.right_bound.skip.count
        previous_voice_measure = current_voice_measure
    return True


def checked_consecutive_intervals(current_path: deque[theory.VariantStack]) -> bool:
    for first_voice_index, second_voice_index in all_voice_pairs:
        lower_voice_measure = current_path[0][first_voice_index]
        upper_voice_measure = current_path[0][second_voice_index]

        lower_voice_sequence = lower_voice_measure.sequence[:]
        last_lower_pitch = lower_voice_measure[-1].specific_pitch
        upper_voice_sequence = upper_voice_measure.sequence[:]
        last_upper_pitch = upper_voice_measure[-1].specific_pitch

        if not last_lower_pitch.has_interval_shift(last_upper_pitch):
            continue
        lower_motion_count = 0
        upper_motion_count = 0
        previous_lower_pitch = last_lower_pitch
        previous_upper_pitch = last_upper_pitch

        for current_stack in itertools.islice(current_path, 1, len(current_path)):
            if isinstance(current_stack, theory.HalfMeasureStack):
                break

            for current_note in current_stack[first_voice_index]:
                current_lower_pitch = current_note.specific_pitch
                if current_lower_pitch != previous_lower_pitch:
                    lower_motion_count += 1
                lower_voice_sequence.append(current_note)
                previous_lower_pitch = current_lower_pitch

            for current_note in current_stack[second_voice_index]:
                current_upper_pitch = current_note.specific_pitch
                if current_upper_pitch != previous_upper_pitch:
                    upper_motion_count += 1
                upper_voice_sequence.append(current_note)
                previous_upper_pitch = current_upper_pitch

            if max(lower_motion_count, upper_motion_count) >= 2:
                break

        if max(len(lower_voice_sequence), len(upper_voice_sequence)) < 3:
            continue
        if not checked_perfect_intervals(lower_voice_sequence, upper_voice_sequence):
            return False
    return True


def get_note_duo(
    lower_voice_measure: theory.FullVoiceMeasure | list[theory.SpecificNote],
    upper_voice_measure: theory.FullVoiceMeasure | list[theory.SpecificNote],
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


def checked_perfect_intervals(
    lower_voice_sequence: list[theory.SpecificNote],
    upper_voice_sequence: list[theory.SpecificNote],
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
    current_path: deque[theory.VariantStack], allowed_fifth_endpoints: set[str]
) -> bool:
    path_length = len(current_path)
    include_leftmost_outline = (
        isinstance(current_path[0], theory.HalfMeasureStack) or path_length == 6
    )

    for voice_index, starting_voice_measure in enumerate(current_path[0]):
        if isinstance(starting_voice_measure, theory.HalfVoiceMeasure):
            pitch_sequence = [starting_voice_measure.pitch]
        else:
            pitch_sequence = [
                current_note.specific_pitch for current_note in starting_voice_measure
            ]

        for current_stack in itertools.islice(current_path, 1, path_length):
            if isinstance(current_stack, theory.HalfMeasureStack):
                break
            pitch_sequence.extend(
                current_note.specific_pitch
                for current_note in current_stack[voice_index]
            )

        previous_direction = 0
        previous_pitch = pitch_sequence[0]
        prelim_outlines = []
        prelim_outline = [previous_pitch]
        prelim_flags = []

        for current_pitch in pitch_sequence[1:]:
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
                        interval_distance = theory.SpecificPitch.get_interval_distance(
                            previous_pitch, current_pitch
                        )
                        prelim_flags.append(interval_distance == 1)
                else:
                    prelim_outline.append(current_pitch)
                previous_direction = current_direction
            previous_pitch = current_pitch
        prelim_outlines.append(prelim_outline)
        prelim_flags.append(True)

        if len(prelim_outlines) == 1:
            if include_leftmost_outline:
                finalized_outlines = prelim_outlines
                finalized_flags = prelim_flags
            else:
                continue
        else:
            finalized_outlines = prelim_outlines[1:]
            finalized_flags = prelim_flags[1:]
            if include_leftmost_outline:
                finalized_outlines.insert(0, prelim_outlines[0])
                finalized_flags.insert(0, prelim_flags[0])

        for melodic_outline, followup_flag in zip(finalized_outlines, finalized_flags):
            if len(melodic_outline) > 2 and not is_valid_outline(
                melodic_outline, followup_flag, allowed_fifth_endpoints
            ):
                return False
    return True


def is_valid_outline(
    melodic_outline: list[theory.SpecificPitch],
    followup_is_stepewise: bool,
    allowed_fifth_endpoints: set[str],
) -> bool:
    first_pitch, *_, last_pitch = melodic_outline
    voice_distance = theory.SpecificPitch.get_interval_distance(first_pitch, last_pitch)

    if voice_distance > 7:
        return False
    if voice_distance == 6 and len(melodic_outline) != 7:
        return False
    current_pitch_endpoints = {
        first_pitch.generic_pitch,
        last_pitch.generic_pitch,
    }
    if voice_distance == 7:
        return bool(current_pitch_endpoints & allowed_fifth_endpoints)

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
        return bool(current_pitch_endpoints & allowed_fifth_endpoints)
    return True


def checked_melodic_bounds(
    current_path: deque[theory.VariantStack],
) -> bool:
    current_superius_measure = current_path[0][-1]
    current_sequence = current_superius_measure.sequence[:]

    for current_stack in itertools.islice(current_path, 1, len(current_path)):
        if isinstance(current_stack, theory.HalfMeasureStack):
            break
        current_sequence.extend(current_stack[-1])

    # if 3 boundaries is the limit, you need at least 6 notes to exceed it
    if len(current_sequence) < 6:
        return True

    normalized_sequence = [current_sequence[0]]

    for current_note in current_sequence[1:]:
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
                previous_direction * current_direction
            ) < 0 and previous_duration <= Fraction("1/4"):
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
    return test_pitch_boundaries(normalized_sequence)


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
        if (previous_vector * current_vector) < 0:
            pitch_boundary_count += 1
            if pitch_boundary_count > 3:
                return False
            if abs(current_vector) > 1 and abs(previous_vector) > 1:
                return False

            if (bound_repr := str(previous_pitch)) in pitch_boundaries:
                return False
            pitch_boundaries.add(bound_repr)

        previous_note = current_note
        if current_vector:
            previous_vector = current_vector

    if current_note.duration != Fraction("1"):
        return True
    return str(current_pitch) not in pitch_boundaries
