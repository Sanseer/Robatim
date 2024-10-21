from functools import partial
from fractions import Fraction

from generate import theory


def is_lowest_duo_good(
    lower_voice_pitch: theory.SpecificPitch, upper_voice_pitch: theory.SpecificPitch
) -> bool:
    if lower_voice_pitch > upper_voice_pitch:
        return False
    second_voice_boundary = lower_voice_pitch + theory.Interval.get("P12")
    if upper_voice_pitch > second_voice_boundary:
        return False
    return True


def is_upper_duo_good(
    lower_voice_pitch: theory.SpecificPitch, upper_voice_pitch: theory.SpecificPitch
) -> bool:
    if lower_voice_pitch > upper_voice_pitch:
        return False
    second_voice_boundary = lower_voice_pitch + theory.Interval.get("P8")
    if upper_voice_pitch > second_voice_boundary:
        return False
    return True


def checked_solo_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
) -> bool:
    for first_voice_measure, second_voice_measure in zip(
        first_measure_stack, second_measure_stack
    ):
        first_pitch = first_voice_measure[-1].specific_pitch
        second_pitch = second_voice_measure[0].specific_pitch
        voice_distance = theory.SpecificPitch.get_interval_distance(
            first_pitch, second_pitch
        )
        if voice_distance > 7 or voice_distance == 6:
            return False

        leap_direction = get_direction(first_pitch, second_pitch)
        if voice_distance == 7 and len(second_voice_measure) > 1:
            resolving_pitch = second_voice_measure[1].specific_pitch
            resolving_direction = get_direction(second_pitch, resolving_pitch)
            if leap_direction == resolving_direction:
                return False

        if voice_distance == 5:
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
            resolving_direction = get_direction(second_pitch, resolving_pitch)
            if leap_direction == resolving_direction:
                return False
        if first_voice_measure[-1].duration <= Fraction("1/4"):
            if voice_distance != 1:
                return False
            if (
                leap_direction == -1
                and first_voice_measure[-2].specific_pitch < first_pitch
            ):
                return False

        if second_voice_measure[0].duration == Fraction("1/4") and voice_distance > 1:
            return False
        current_undesired_values = {
            (first_pitch + theory.Interval.get("A4")).generic_pitch,
            (first_pitch + theory.Interval.get("d5")).generic_pitch,
        }
        if second_pitch.generic_pitch in current_undesired_values:
            return False

        if len(first_voice_measure) > 1 and str(first_voice_measure) == str(
            second_voice_measure
        ):
            return False

    return True


def get_direction(
    previous_pitch: theory.SpecificPitch, current_pitch: theory.SpecificPitch
) -> int:
    difference = current_pitch.value - previous_pitch.value
    if difference > 0:
        return 1
    elif difference < 0:
        return -1
    else:
        return 0


def is_duo_consonant(
    lower_pitch: theory.SpecificPitch,
    upper_pitch: theory.SpecificPitch,
    consonant_ids: set[str],
) -> bool:
    consonant_options = {
        (lower_pitch + theory.Interval.get(consonant_id)).generic_pitch
        for consonant_id in consonant_ids
    }
    return upper_pitch.generic_pitch in consonant_options


def is_duo_motion_valid(
    first_lower_note: theory.SpecificNote,
    first_upper_note: theory.SpecificNote,
    second_lower_note: theory.SpecificNote,
    second_upper_note: theory.SpecificNote,
    consonant_ids: set[str],
    is_prelim_check: bool,
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
        if preceded_by_dissonance:
            if lower_voice_distance > 1 or upper_voice_distance > 1:
                return False
        if is_prelim_check and not is_duo_consonant(
            second_lower_pitch, second_upper_pitch, consonant_ids
        ):
            return False

        lower_voice_direction = get_direction(first_lower_pitch, second_lower_pitch)
        upper_voice_direction = get_direction(first_upper_pitch, second_upper_pitch)

        if lower_voice_direction == upper_voice_direction:
            current_undesired_values = {
                (second_lower_pitch + theory.Interval.get("P5")).generic_pitch,
                (second_lower_pitch + theory.Interval.get("P8")).generic_pitch,
            }
            if second_upper_pitch.generic_pitch in current_undesired_values:
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
        if is_prelim_check and not is_duo_consonant(
            second_lower_pitch, second_upper_pitch, consonant_ids
        ):
            return False

    return True


all_voice_pairs = ((0, 1), (1, 2), (2, 3), (0, 2), (0, 3), (1, 3))
lower_voice_consonances = {"P8", "P5", "M3", "m3", "M6", "m6"}
upper_voice_consonances = lower_voice_consonances | {"P4"}


def checked_duo_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
) -> bool:
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
        ):
            return False
    return True


def is_perfect_fourth_consonant(
    lowest_pitch: theory.SpecificPitch,
    middle_pitch: theory.SpecificPitch,
    highest_pitch: theory.SpecificPitch,
) -> bool:
    concerning_value = (middle_pitch + theory.Interval.get("P4")).generic_pitch
    if highest_pitch.generic_pitch == concerning_value:
        consonant_bass_values = {
            (middle_pitch - theory.Interval.get("M3")).generic_pitch,
            (middle_pitch - theory.Interval.get("m3")).generic_pitch,
            (middle_pitch - theory.Interval.get("P5")).generic_pitch,
        }
        return lowest_pitch.generic_pitch in consonant_bass_values
    return True


def is_trio_motion_valid(
    first_lowest_pitch: theory.SpecificPitch,
    first_middle_pitch: theory.SpecificPitch,
    first_highest_pitch: theory.SpecificPitch,
    second_lowest_pitch: theory.SpecificPitch,
    second_middle_pitch: theory.SpecificPitch,
    second_highest_pitch: theory.SpecificPitch,
    is_prelim_check: bool,
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
        if is_prelim_check and not is_perfect_fourth_consonant(
            second_lowest_pitch, second_middle_pitch, second_highest_pitch
        ):
            return False
    elif middle_voice_distance > 1 or highest_voice_distance > 1:
        if preceded_by_dissonance:
            return False
        if is_prelim_check and not is_perfect_fourth_consonant(
            second_lowest_pitch, second_middle_pitch, second_highest_pitch
        ):
            return False
    return True


bass_trios = ((0, 1, 2), (0, 1, 3), (0, 2, 3))


def checked_trio_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
) -> bool:
    for first_voice_index, second_voice_index, third_voice_index in bass_trios:
        first_lowest_pitch = first_measure_stack[first_voice_index][-1].specific_pitch
        first_middle_pitch = first_measure_stack[second_voice_index][-1].specific_pitch
        first_highest_pitch = first_measure_stack[third_voice_index][-1].specific_pitch

        second_lowest_pitch = second_measure_stack[first_voice_index][0].specific_pitch
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
    return True


def filter_prospects(
    index_prospects: list, has_prospect_succeeded: partial[bool]
) -> list:
    index_prospects[:] = [
        index_prospect
        for index_prospect in index_prospects
        if has_prospect_succeeded(index_prospect)
    ]
    return index_prospects


def has_counterpoint_propagated(
    sequence_prospects: list[list[theory.MeasureStack]],
    propagate_index: int,
    score_sequence: theory.CognizantSequence,
    current_measure_stack: theory.MeasureStack,
) -> bool:
    previous_index = propagate_index - 1
    next_index = propagate_index + 1

    if propagate_index != score_sequence.final_index:
        next_prospects = sequence_prospects[next_index]
        prospect_validators = [
            partial(checked_solo_transition, current_measure_stack),
            partial(checked_duo_transition, current_measure_stack),
            partial(checked_trio_transition, current_measure_stack),
            partial(score_sequence.checked_stipulations, next_index),
        ]
        for prospect_validator in prospect_validators:
            if not filter_prospects(next_prospects, prospect_validator):
                return False

    if propagate_index != 0:
        previous_prospects = sequence_prospects[previous_index]
        prospect_validators = [
            partial(
                checked_solo_transition,
                second_measure_stack=current_measure_stack,
            ),
            partial(
                checked_duo_transition,
                second_measure_stack=current_measure_stack,
            ),
            partial(
                checked_trio_transition,
                second_measure_stack=current_measure_stack,
            ),
            partial(score_sequence.checked_stipulations, previous_index),
        ]
        for prospect_validator in prospect_validators:
            if not filter_prospects(previous_prospects, prospect_validator):
                return False

    return True
