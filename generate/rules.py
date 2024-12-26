from functools import partial
from fractions import Fraction
from typing import Iterator

from generate import theory, limits


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


def checked_solo_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
    flattened_pitch: theory.GenericPitch,
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
        if first_pitch.has_interval_shift(second_pitch, ("A2", "A4", "d5")):
            return False

        if len(first_voice_measure) > 1:
            previous_pitch = first_voice_measure[-2].specific_pitch
            if (
                first_voice_measure[-1].duration == Fraction("1/4")
                and first_voice_measure[-2].duration == Fraction("1/4")
                and not check_chromatic_relation(previous_pitch, second_pitch)
            ):
                return False
            if voice_distance:
                if previous_pitch != first_pitch and not test_melodic_pyramid(
                    previous_pitch, first_pitch, second_pitch
                ):
                    return False

        if len(second_voice_measure) > 1:
            next_pitch = second_voice_measure[1].specific_pitch
            if (
                second_voice_measure[0].duration == Fraction("1/4")
                and second_voice_measure[1].duration == Fraction("1/4")
                and not check_chromatic_relation(first_pitch, next_pitch)
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

        if len(first_voice_measure) > 1 and len(second_voice_measure) > 1:
            first_pitch = first_voice_measure[0].specific_pitch
            second_pitch = first_voice_measure[1].specific_pitch
            third_pitch = second_voice_measure[0].specific_pitch
            fourth_pitch = second_voice_measure[1].specific_pitch

            if first_pitch == third_pitch and second_pitch == fourth_pitch:
                return False
    return check_cross_pitches(first_measure_stack, second_measure_stack)


def check_chromatic_relation(
    first_pitch: theory.SpecificPitch, second_pitch: theory.SpecificPitch
) -> bool:
    if first_pitch.letter == second_pitch.letter:
        return first_pitch.generic_pitch == second_pitch.generic_pitch
    return True


def get_measure_quartets(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
) -> Iterator[
    tuple[
        theory.MelodicSequence,
        theory.MelodicSequence,
        theory.MelodicSequence,
        theory.MelodicSequence,
    ]
]:
    for first_voice_index, second_voice_index in limits.all_voice_pairs:
        first_lower_measure = first_measure_stack[first_voice_index]
        first_upper_measure = first_measure_stack[second_voice_index]
        second_lower_measure = second_measure_stack[first_voice_index]
        second_upper_measure = second_measure_stack[second_voice_index]
        yield first_lower_measure, first_upper_measure, second_lower_measure, second_upper_measure


def check_cross_pitches(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
) -> bool:
    for (
        first_lower_measure,
        first_upper_measure,
        second_lower_measure,
        second_upper_measure,
    ) in get_measure_quartets(first_measure_stack, second_measure_stack):
        if (
            len(first_lower_measure) > 1
            and first_lower_measure[-1].duration == Fraction("1/4")
            and first_lower_measure[-2].duration == Fraction("1/4")
        ):
            if not check_chromatic_relation(
                first_lower_measure[-2].specific_pitch,
                second_upper_measure[0].specific_pitch,
            ):
                return False
        if (
            len(first_upper_measure) > 1
            and first_upper_measure[-1].duration == Fraction("1/4")
            and first_upper_measure[-2].duration == Fraction("1/4")
        ):
            if not check_chromatic_relation(
                first_upper_measure[-2].specific_pitch,
                second_lower_measure[0].specific_pitch,
            ):
                return False

        if (
            len(second_lower_measure) > 1
            and second_lower_measure[0].duration == Fraction("1/4")
            and second_lower_measure[1].duration == Fraction("1/4")
        ):
            if not check_chromatic_relation(
                first_upper_measure[-1].specific_pitch,
                second_lower_measure[1].specific_pitch,
            ):
                return False
        if (
            len(second_upper_measure) > 1
            and second_upper_measure[0].duration == Fraction("1/4")
            and second_upper_measure[1].duration == Fraction("1/4")
        ):
            if not check_chromatic_relation(
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

    if (first_vector * second_vector) < 0:
        return True
    # Upward motion decelerates. Downward motion accelerates.
    return first_vector >= second_vector


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


def is_bass_suspension_valid(
    first_lower_note: theory.SpecificNote,
    first_upper_note: theory.SpecificNote,
    second_lower_note: theory.SpecificNote,
    second_upper_note: theory.SpecificNote,
    second_measure_stack: theory.MeasureStack,
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


def has_imperfect_resolution(measure_stack: theory.MeasureStack) -> bool:
    pitch_quartet = [
        measure_stack[0][-1].specific_pitch,
        measure_stack[1][-1].specific_pitch,
        measure_stack[2][-1].specific_pitch,
        measure_stack[3][-1].specific_pitch,
    ]
    for first_voice_index, second_voice_index in limits.all_voice_pairs:
        lower_pitch = pitch_quartet[first_voice_index]
        upper_pitch = pitch_quartet[second_voice_index]
        if lower_pitch.has_interval_shift(upper_pitch, imperfect_consonances):
            return True
    return False


def checked_duo_transition(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
    allowed_downbeat_unison: bool,
    check_bass_suspension: bool,
) -> bool:
    consonant_ids: tuple[str, ...]
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
    second_measure_stack: theory.MeasureStack,
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
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
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


def check_dissonant_pass(
    first_measure_stack: theory.MeasureStack,
    second_measure_stack: theory.MeasureStack,
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
    first_lower_measure: theory.MelodicSequence,
    first_upper_measure: theory.MelodicSequence,
    second_lower_measure: theory.MelodicSequence,
    second_upper_measure: theory.MelodicSequence,
) -> bool:
    lower_is_cantus, lower_is_counter = get_species_role(first_lower_measure)
    upper_is_cantus, upper_is_counter = get_species_role(first_upper_measure)

    if lower_is_cantus and upper_is_counter or lower_is_counter and upper_is_cantus:
        if is_duo_consonant(
            first_lower_measure[-1].specific_pitch,
            first_upper_measure[-1].specific_pitch,
            lower_voice_consonances,
        ):
            return True

        if upper_is_counter:
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


def get_species_role(voice_measure: theory.MelodicSequence) -> tuple[bool, bool]:
    if len(voice_measure) == 1:
        is_cantus = True
        is_counter = False
    elif len(voice_measure) > 2:
        is_cantus = False
        is_counter = False
    else:
        first_note, second_note = voice_measure
        if first_note.specific_pitch == second_note.specific_pitch:
            is_cantus = True
        else:
            is_cantus = False

        if first_note.duration == Fraction("1/2"):
            interval_distance = theory.SpecificPitch.get_interval_distance(
                first_note.specific_pitch, second_note.specific_pitch
            )
            if interval_distance == 1:
                is_counter = True
            else:
                is_counter = False
        else:
            is_counter = False

    return is_cantus, is_counter


def has_passing_figure(
    first_pitch: theory.SpecificPitch,
    second_pitch: theory.SpecificPitch,
    third_pitch: theory.SpecificPitch,
) -> bool:
    first_vector = theory.SpecificPitch.get_interval_vector(first_pitch, second_pitch)
    second_vector = theory.SpecificPitch.get_interval_vector(second_pitch, third_pitch)
    return first_vector == second_vector


def test_trio_species(
    first_lowest_measure: theory.MelodicSequence,
    first_middle_measure: theory.MelodicSequence,
    first_highest_measure: theory.MelodicSequence,
    second_middle_measure: theory.MelodicSequence,
    second_highest_measure: theory.MelodicSequence,
) -> bool:
    lower_is_cantus, lower_is_counter = get_species_role(first_middle_measure)
    upper_is_cantus, upper_is_counter = get_species_role(first_highest_measure)

    if lower_is_cantus and upper_is_counter or lower_is_counter and upper_is_cantus:
        if is_trio_consonant(
            find_third_quarter(first_lowest_measure),
            first_middle_measure[-1].specific_pitch,
            first_highest_measure[-1].specific_pitch,
        ):
            return True

        if upper_is_counter:
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


def find_third_quarter(voice_measure: theory.MelodicSequence) -> theory.SpecificPitch:
    elapsed_duration = Fraction("0")
    for specific_note in voice_measure:
        elapsed_duration += specific_note.duration
        if elapsed_duration >= Fraction("3/4"):
            return specific_note.specific_pitch
    else:
        raise ValueError


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


valid_cadential_motions = {
    0: {-1, -3, 3, -4, 4},
    1: {0, -1, 1},
    2: {0, -1, 1, -2},
    3: {-1, 1},
}


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
    lower_voice_measure: theory.MelodicSequence,
    upper_voice_measure: theory.MelodicSequence,
) -> bool:
    starting_lower_pitch = lower_voice_measure[0].specific_pitch
    starting_upper_pitch = upper_voice_measure[0].specific_pitch
    return starting_lower_pitch.generic_pitch == starting_upper_pitch.generic_pitch


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
    flattened_pitch: theory.GenericPitch,
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

    final_index = score_sequence.final_index
    if propagate_index != final_index:
        next_index = propagate_index + 1
        next_prospects = sequence_prospects[next_index]
        is_half_cadence = final_index == 11 and next_index == 5
        is_authentic_cadence = next_index == final_index - 1

        prospect_validators = [
            partial(
                checked_solo_transition,
                current_measure_stack,
                flattened_pitch=flattened_pitch,
            ),
            partial(
                checked_duo_transition,
                current_measure_stack,
                allowed_downbeat_unison=next_index == final_index,
                check_bass_suspension=is_authentic_cadence or is_half_cadence,
            ),
            partial(
                checked_trio_transition,
                current_measure_stack,
                check_upper_suspension=is_authentic_cadence or is_half_cadence,
            ),
            partial(check_dissonant_pass, current_measure_stack),
            partial(score_sequence.checked_stipulations, next_index),
        ]
        if is_authentic_cadence:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    current_measure_stack,
                    allowed_vectors={0, -1},
                ),
            )
        elif next_index == final_index:
            prospect_validators.insert(
                0, partial(checked_cadential_successor, current_measure_stack)
            )
        elif propagate_index == 4:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    current_measure_stack,
                    allowed_vectors={0, -1},
                ),
            )
        elif propagate_index == 5:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    current_measure_stack,
                    allowed_vectors={1},
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
        for prospect_validator in prospect_validators:
            if not filter_prospects(next_prospects, prospect_validator):
                return False

    if propagate_index != 0:
        previous_index = propagate_index - 1
        previous_prospects = sequence_prospects[previous_index]
        is_half_cadence = final_index == 11 and propagate_index == 5
        is_authentic_cadence = propagate_index == final_index - 1

        prospect_validators = [
            partial(
                checked_solo_transition,
                second_measure_stack=current_measure_stack,
                flattened_pitch=flattened_pitch,
            ),
            partial(
                checked_duo_transition,
                second_measure_stack=current_measure_stack,
                allowed_downbeat_unison=propagate_index == final_index,
                check_bass_suspension=is_authentic_cadence or is_half_cadence,
            ),
            partial(
                checked_trio_transition,
                second_measure_stack=current_measure_stack,
                check_upper_suspension=is_authentic_cadence or is_half_cadence,
            ),
            partial(
                check_dissonant_pass,
                second_measure_stack=current_measure_stack,
            ),
            partial(score_sequence.checked_stipulations, previous_index),
        ]
        if is_authentic_cadence:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    second_measure_stack=current_measure_stack,
                    allowed_vectors={0, -1},
                ),
            )
        elif propagate_index == final_index:
            prospect_validators.insert(
                0,
                partial(
                    checked_cadential_successor,
                    second_measure_stack=current_measure_stack,
                ),
            )
        elif propagate_index == 5:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    second_measure_stack=current_measure_stack,
                    allowed_vectors={0, -1},
                ),
            )
        elif propagate_index == 6:
            prospect_validators.insert(
                0,
                partial(
                    checked_superius_transition,
                    second_measure_stack=current_measure_stack,
                    allowed_vectors={1},
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
