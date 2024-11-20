from functools import partial
from fractions import Fraction

from generate import theory, limits


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
        if first_pitch.has_interval_shift(second_pitch, ("A4", "d5")):
            return False

        if len(first_voice_measure) > 1 and len(second_voice_measure) > 1:
            first_pitch = first_voice_measure[0].specific_pitch
            second_pitch = first_voice_measure[1].specific_pitch
            third_pitch = second_voice_measure[0].specific_pitch
            fourth_pitch = second_voice_measure[1].specific_pitch

            if first_pitch == third_pitch and second_pitch == fourth_pitch:
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
    is_prelim_check: bool,
    allowed_downbeat_unison: bool,
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
        if is_prelim_check:
            if not is_duo_consonant(
                second_lower_pitch, second_upper_pitch, consonant_ids
            ):
                return False
        elif not allowed_downbeat_unison and second_lower_pitch == second_upper_pitch:
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
    elif lower_voice_distance > 1 or upper_voice_distance > 1:
        if preceded_by_dissonance:
            return False
        if is_prelim_check and not is_duo_consonant(
            second_lower_pitch, second_upper_pitch, consonant_ids
        ):
            return False
    elif not allowed_downbeat_unison and second_lower_pitch == second_upper_pitch:
        return False

    return True


def is_cadential_duo_valid(
    first_lower_note: theory.SpecificNote,
    first_upper_note: theory.SpecificNote,
    second_lower_note: theory.SpecificNote,
    second_upper_note: theory.SpecificNote,
    consonant_ids: tuple[str, ...],
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
    if lower_voice_distance and upper_voice_distance:
        if second_lower_pitch >= first_upper_pitch:
            return False
        if second_upper_pitch <= first_lower_pitch:
            return False
        if not is_duo_consonant(second_lower_pitch, second_upper_pitch, consonant_ids):
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


def checked_duo_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
    second_sequence_index: int,
) -> bool:
    consonant_ids: tuple[str, ...]
    allowed_downbeat_unison = second_sequence_index == 11
    for first_voice_index, second_voice_index in limits.all_voice_pairs:
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
        if not is_perfect_fourth_consonant(
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


def checked_superius_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
    allowed_vectors: set[int],
) -> bool:
    first_superius_pitch = first_measure_stack[-1][-1].specific_pitch
    second_superius_pitch = second_measure_stack[-1][0].specific_pitch
    interval_vector = theory.SpecificPitch.get_interval_vector(
        first_superius_pitch, second_superius_pitch
    )
    return interval_vector in allowed_vectors


valid_cadential_motions = {0: {-4, 3}, 1: {-1}, 2: {0, -2}, 3: {1}}


def checked_cadential_successor(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
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
    return True


def is_superius_duplicated(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
) -> bool:
    first_superius_measure = first_measure_stack[-1]
    second_superius_measure = second_measure_stack[-1]
    return str(first_superius_measure) == str(second_superius_measure)


def is_voice_measure_unique(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
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
    score_sequence: limits.CognizantSequence,
    current_measure_stack: theory.MeasureStack,
) -> bool:
    for duplicate_index in score_sequence.duplicates[propagate_index]:
        prospect_validator = partial(is_superius_duplicated, current_measure_stack)
        index_prospects = sequence_prospects[duplicate_index]
        if not filter_prospects(index_prospects, prospect_validator):
            return False

    for unique_index in score_sequence.uniques[propagate_index]:
        prospect_validator = partial(is_voice_measure_unique, current_measure_stack)
        index_prospects = sequence_prospects[unique_index]
        if not filter_prospects(index_prospects, prospect_validator):
            return False

    if propagate_index != score_sequence.final_index:
        next_index = propagate_index + 1
        next_prospects = sequence_prospects[next_index]
        prospect_validators = [
            partial(checked_solo_transition, current_measure_stack),
            partial(
                checked_duo_transition,
                current_measure_stack,
                second_sequence_index=next_index,
            ),
            partial(checked_trio_transition, current_measure_stack),
            partial(score_sequence.checked_stipulations, next_index),
        ]
        if propagate_index == 4:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    current_measure_stack,
                    allowed_vectors={-1, 1},
                ),
            )
        elif propagate_index == score_sequence.final_index - 2:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    current_measure_stack,
                    allowed_vectors={-1},
                ),
            )
        else:
            prospect_validators.append(
                partial(
                    checked_superius_transition,
                    current_measure_stack,
                    allowed_vectors={0, -1, 1, -2, 2, -3, 3, -4, 4},
                )
            )
        if propagate_index == score_sequence.final_index - 1:
            prospect_validators.insert(
                0, partial(checked_cadential_successor, current_measure_stack)
            )
        for prospect_validator in prospect_validators:
            if not filter_prospects(next_prospects, prospect_validator):
                return False

    if propagate_index != 0:
        previous_index = propagate_index - 1
        previous_prospects = sequence_prospects[previous_index]
        prospect_validators = [
            partial(
                checked_solo_transition,
                second_measure_stack=current_measure_stack,
            ),
            partial(
                checked_duo_transition,
                second_measure_stack=current_measure_stack,
                second_sequence_index=propagate_index,
            ),
            partial(
                checked_trio_transition,
                second_measure_stack=current_measure_stack,
            ),
            partial(score_sequence.checked_stipulations, previous_index),
        ]
        if propagate_index == 5:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    second_measure_stack=current_measure_stack,
                    allowed_vectors={-1, 1},
                ),
            )
        elif propagate_index == score_sequence.final_index - 1:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    second_measure_stack=current_measure_stack,
                    allowed_vectors={-1},
                ),
            )
        else:
            prospect_validators.append(
                partial(
                    checked_superius_transition,
                    second_measure_stack=current_measure_stack,
                    allowed_vectors={0, -1, 1, -2, 2, -3, 3, -4, 4},
                )
            )
        for prospect_validator in prospect_validators:
            if not filter_prospects(previous_prospects, prospect_validator):
                return False

    return True
