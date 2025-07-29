from fractions import Fraction

from generate import theory


all_voice_pairs = ((0, 1), (1, 2), (2, 3), (0, 2), (0, 3), (1, 3))


def is_lowest_duo_good(
    lower_voice_pitch: theory.SpecificPitch, upper_voice_pitch: theory.SpecificPitch
) -> bool:
    return checked_voice_spacing(lower_voice_pitch, upper_voice_pitch, "P12")


def is_upper_duo_good(
    lower_voice_pitch: theory.SpecificPitch, upper_voice_pitch: theory.SpecificPitch
) -> bool:
    return checked_voice_spacing(lower_voice_pitch, upper_voice_pitch, "P8")


def checked_voice_spacing(
    lower_voice_pitch: theory.SpecificPitch,
    upper_voice_pitch: theory.SpecificPitch,
    interval_repr: str,
) -> bool:
    if lower_voice_pitch > upper_voice_pitch:
        return False
    second_voice_boundary = lower_voice_pitch + theory.Interval.get(interval_repr)
    return upper_voice_pitch <= second_voice_boundary


def checked_melodic_pyramid(
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


def is_measure_whole(voice_measure: theory.FullVoiceMeasure) -> bool:
    if len(voice_measure) > 2:
        return False
    return voice_measure[0].specific_pitch == voice_measure[-1].specific_pitch


def is_complete_descent(voice_measure: theory.FullVoiceMeasure) -> bool:
    previous_pitch = voice_measure[0].specific_pitch
    for current_note in voice_measure.sequence[1:]:
        current_pitch = current_note.specific_pitch
        current_direction = theory.SpecificPitch.get_direction(
            previous_pitch, current_pitch
        )
        if current_direction != -1:
            return False
        previous_pitch = current_pitch
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


perfect_interval_reprs = ("P5", "P8")


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
    for perfect_interval_repr in perfect_interval_reprs:
        if first_lower_pitch.has_interval_shift(
            first_upper_pitch, (perfect_interval_repr,)
        ) and second_lower_pitch.has_interval_shift(
            second_upper_pitch, (perfect_interval_repr,)
        ):
            return True
    return False


def is_duo_consonant(
    lower_pitch: theory.SpecificPitch,
    upper_pitch: theory.SpecificPitch,
    consonant_ids: tuple[str, ...],
) -> bool:
    return lower_pitch.has_interval_shift(upper_pitch, consonant_ids)


def is_perfect_fourth_consonant(
    lowest_pitch: theory.SpecificPitch,
    middle_pitch: theory.SpecificPitch,
    highest_pitch: theory.SpecificPitch,
) -> bool:
    if middle_pitch.has_interval_shift(highest_pitch, ("P4",)):
        return lowest_pitch.has_interval_shift(middle_pitch, ("M3", "m3", "P5"))
    return True


lower_voice_consonances = ("P8", "P5", "M3", "m3", "M6", "m6")
upper_voice_consonances = ("P8", "P5", "M3", "m3", "M6", "m6", "P4")


def is_trio_consonant(
    lowest_pitch: theory.SpecificPitch,
    middle_pitch: theory.SpecificPitch,
    highest_pitch: theory.SpecificPitch,
) -> bool:
    if not is_duo_consonant(middle_pitch, highest_pitch, upper_voice_consonances):
        return False
    return is_perfect_fourth_consonant(lowest_pitch, middle_pitch, highest_pitch)


def checked_chromatic_relation(
    first_pitch: theory.SpecificPitch, second_pitch: theory.SpecificPitch
) -> bool:
    if first_pitch.letter == second_pitch.letter:
        return first_pitch.generic_pitch == second_pitch.generic_pitch
    return True


def valid_regular_duo_motion(
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
    if not checked_chromatic_relation(first_lower_pitch, second_upper_pitch):
        return False
    if not checked_chromatic_relation(first_upper_pitch, second_lower_pitch):
        return False
    return True


def valid_regular_trio_motion(
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


def valid_cadential_duo_motion(
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


def valid_cadential_trio_motion(
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


imperfect_consonances = ("M3", "m3", "M6", "m6")


def is_resolution_imperfect(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    lower_pitch = lower_voice_measure[-1].specific_pitch
    upper_pitch = upper_voice_measure[-1].specific_pitch
    return lower_pitch.has_interval_shift(upper_pitch, imperfect_consonances)


def is_transition_tied(
    first_voice_measure: theory.FullVoiceMeasure,
    second_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    return (
        first_voice_measure[-1].specific_pitch == second_voice_measure[0].specific_pitch
    )
