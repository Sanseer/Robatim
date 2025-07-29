from fractions import Fraction
from typing import Iterator

from generate import pure, theory


def get_species_role(voice_measure: theory.FullVoiceMeasure) -> tuple[bool, bool]:
    if len(voice_measure) == 1:
        is_diminished_cantus = False
        is_diminished_counter = False
    elif len(voice_measure) > 2:
        first_note, second_note, *_ = voice_measure
        is_diminished_cantus = first_note.duration == Fraction("1/2")

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
            is_diminished_cantus = False
        else:
            is_diminished_cantus = first_note.duration == Fraction("1/2")
        is_diminished_counter = False
    return is_diminished_cantus, is_diminished_counter


def valid_diminished_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    lower_is_diminished_cantus, lower_is_diminished_counter = get_species_role(
        lower_voice_measure
    )
    upper_is_diminished_cantus, upper_is_diminished_counter = get_species_role(
        upper_voice_measure
    )
    if (
        lower_is_diminished_cantus
        and upper_is_diminished_counter
        or lower_is_diminished_counter
        and upper_is_diminished_cantus
    ):
        if lower_is_diminished_cantus:
            lower_pitch = lower_voice_measure[0].specific_pitch
            upper_pitch = upper_voice_measure[1].specific_pitch
            counter_measure = upper_voice_measure
        else:
            lower_pitch = lower_voice_measure[1].specific_pitch
            upper_pitch = upper_voice_measure[0].specific_pitch
            counter_measure = lower_voice_measure
        if not pure.is_duo_consonant(lower_pitch, upper_pitch, consonant_ids):
            return pure.has_passing_figure(
                counter_measure[0].specific_pitch,
                counter_measure[1].specific_pitch,
                counter_measure[2].specific_pitch,
            )
    return True


def valid_dotted_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    lower_is_dotted = lower_voice_measure[0].duration == Fraction("3/4")
    upper_is_dotted = upper_voice_measure[0].duration == Fraction("3/4")
    if lower_is_dotted ^ upper_is_dotted:
        if lower_is_dotted:
            lower_pitch = lower_voice_measure[0].specific_pitch
            upper_pitch = pure.find_pitch(upper_voice_measure)
            dotted_measure = lower_voice_measure
            undotted_measure = upper_voice_measure
        else:
            lower_pitch = pure.find_pitch(lower_voice_measure)
            upper_pitch = upper_voice_measure[0].specific_pitch
            dotted_measure = upper_voice_measure
            undotted_measure = lower_voice_measure
        if not pure.is_duo_consonant(lower_pitch, upper_pitch, consonant_ids):
            if len(undotted_measure) != 2:
                return False
            first_patient_pitch = dotted_measure[0].specific_pitch
            second_patient_pitch = dotted_measure[1].specific_pitch
            if (
                theory.SpecificPitch.get_interval_vector(
                    first_patient_pitch, second_patient_pitch
                )
                != -1
            ):
                return False

            if lower_is_dotted:
                if lower_pitch.has_interval_shift(upper_pitch, ("d5",)):
                    return False
                lower_resolve_pitch = second_patient_pitch
                upper_resolve_pitch = upper_pitch
            else:
                if lower_pitch.has_interval_shift(upper_pitch, ("m2",)):
                    return False
                lower_resolve_pitch = lower_pitch
                upper_resolve_pitch = second_patient_pitch
            if not lower_resolve_pitch.has_interval_shift(
                upper_resolve_pitch, consonant_ids
            ):
                return False
    return True


def valid_broken_parallels(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    lower_voice_iter = iter(lower_voice_measure)
    upper_voice_iter = iter(upper_voice_measure)
    lower_duration = Fraction("0")
    upper_duration = Fraction("0")
    remaining_measure_duration = Fraction("1")

    while remaining_measure_duration:
        if not lower_duration:
            lower_note = next(lower_voice_iter)
            lower_duration = lower_note.duration
            first_lower_pitch = lower_note.specific_pitch
        if not upper_duration:
            upper_note = next(upper_voice_iter)
            upper_duration = upper_note.duration
            first_upper_pitch = upper_note.specific_pitch

        if lower_duration != upper_duration and first_lower_pitch.has_interval_shift(
            first_upper_pitch
        ):
            only_quarters_inbetween = True
            intersect_duration = min(lower_duration, upper_duration)
            if lower_duration > upper_duration:
                lower_duration -= intersect_duration
                remaining_measure_duration -= intersect_duration
                while lower_duration:
                    upper_note = next(upper_voice_iter)
                    upper_duration = upper_note.duration
                    if upper_duration != Fraction("1/4"):
                        only_quarters_inbetween = False

                    intersect_duration = min(lower_duration, upper_duration)
                    lower_duration -= intersect_duration
                    upper_duration -= intersect_duration
                    remaining_measure_duration -= intersect_duration
            else:
                upper_duration -= intersect_duration
                remaining_measure_duration -= intersect_duration
                while upper_duration:
                    lower_note = next(lower_voice_iter)
                    lower_duration = lower_note.duration
                    if lower_duration != Fraction("1/4"):
                        only_quarters_inbetween = False

                    intersect_duration = min(lower_duration, upper_duration)
                    lower_duration -= intersect_duration
                    upper_duration -= intersect_duration
                    remaining_measure_duration -= intersect_duration

            if not remaining_measure_duration:
                return True
            if only_quarters_inbetween:
                if not lower_duration:
                    lower_note = next(lower_voice_iter)
                    lower_duration = lower_note.duration
                second_lower_pitch = lower_note.specific_pitch

                if not upper_duration:
                    upper_note = next(upper_voice_iter)
                    upper_duration = upper_note.duration
                second_upper_pitch = upper_note.specific_pitch

                if pure.is_parallel_perfect(
                    first_lower_pitch,
                    first_upper_pitch,
                    second_lower_pitch,
                    second_upper_pitch,
                ):
                    return False
                first_lower_pitch = second_lower_pitch
                first_upper_pitch = second_upper_pitch
        else:
            intersect_duration = min(lower_duration, upper_duration)
            lower_duration -= intersect_duration
            upper_duration -= intersect_duration
            remaining_measure_duration -= intersect_duration
    return True


def valid_quarter_parallels(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    if not (len(lower_voice_measure) == len(upper_voice_measure) == 4):
        return True
    previous_lower_pitch = lower_voice_measure[0].specific_pitch
    previous_upper_pitch = upper_voice_measure[0].specific_pitch
    lower_voice_sequence = lower_voice_measure.sequence[1:]
    upper_voice_sequence = upper_voice_measure.sequence[1:]

    for lower_note, upper_note in zip(lower_voice_sequence, upper_voice_sequence):
        current_lower_pitch = lower_note.specific_pitch
        current_upper_pitch = upper_note.specific_pitch
        lower_direction = theory.SpecificPitch.get_direction(
            previous_lower_pitch, current_lower_pitch
        )
        upper_direction = theory.SpecificPitch.get_direction(
            previous_upper_pitch, current_upper_pitch
        )
        if lower_direction != upper_direction:
            return True

        previous_lower_pitch = current_lower_pitch
        previous_upper_pitch = current_upper_pitch
    return False


def valid_third_quarter_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    lower_is_whole = pure.is_measure_whole(lower_voice_measure)
    upper_is_whole = pure.is_measure_whole(upper_voice_measure)

    if lower_is_whole ^ upper_is_whole:
        if lower_is_whole:
            counter_measure = upper_voice_measure
            lower_pitch = lower_voice_measure[0].specific_pitch
            upper_pitch = pure.find_pitch(upper_voice_measure)
        else:
            counter_measure = lower_voice_measure
            lower_pitch = pure.find_pitch(lower_voice_measure)
            upper_pitch = upper_voice_measure[0].specific_pitch

        if len(counter_measure) == 2:
            return True
        if not pure.is_duo_consonant(lower_pitch, upper_pitch, consonant_ids):
            if counter_measure[-1].duration == Fraction("1/2"):
                return False
            return pure.is_complete_descent(counter_measure)
    return True


def is_dissonant_idiom(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    lower_is_cantus = lower_voice_measure[-1].duration >= Fraction("1/2")
    upper_is_cantus = upper_voice_measure[-1].duration >= Fraction("1/2")

    if lower_is_cantus ^ upper_is_cantus:
        if lower_is_cantus:
            counter_measure = upper_voice_measure
        else:
            counter_measure = lower_voice_measure
        if len(counter_measure) == 2:
            return False
        return pure.is_complete_descent(counter_measure)
    return False


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


def valid_agogic(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    return not is_agogic_combo(lower_voice_measure, upper_voice_measure)


def valid_diminished_trio(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    middle_is_diminished_cantus, middle_is_diminished_counter = get_species_role(
        middle_voice_measure
    )
    highest_is_diminished_cantus, highest_is_diminished_counter = get_species_role(
        highest_voice_measure
    )

    if (
        middle_is_diminished_cantus
        and highest_is_diminished_counter
        or middle_is_diminished_counter
        and highest_is_diminished_cantus
    ):
        if middle_is_diminished_cantus:
            middle_pitch = middle_voice_measure[0].specific_pitch
            highest_pitch = highest_voice_measure[1].specific_pitch
            counter_measure = highest_voice_measure
        else:
            middle_pitch = middle_voice_measure[1].specific_pitch
            highest_pitch = highest_voice_measure[0].specific_pitch
            counter_measure = middle_voice_measure
        lowest_pitch = pure.find_pitch(lowest_voice_measure, "1/2")
        if not pure.is_perfect_fourth_consonant(
            lowest_pitch, middle_pitch, highest_pitch
        ):
            return pure.has_passing_figure(
                counter_measure[0].specific_pitch,
                counter_measure[1].specific_pitch,
                counter_measure[2].specific_pitch,
            )
    return True


def get_dotted_status(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> tuple[bool, bool, bool]:
    lowest_is_dotted = lowest_voice_measure[0].duration == Fraction("3/4")
    middle_is_dotted = middle_voice_measure[0].duration == Fraction("3/4")
    highest_is_dotted = highest_voice_measure[0].duration == Fraction("3/4")
    return lowest_is_dotted, middle_is_dotted, highest_is_dotted


def valid_dotted_trio(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    lowest_is_dotted, middle_is_dotted, highest_is_dotted = get_dotted_status(
        lowest_voice_measure, middle_voice_measure, highest_voice_measure
    )
    if lowest_is_dotted and middle_is_dotted and highest_is_dotted:
        return False

    if middle_is_dotted ^ highest_is_dotted:
        if middle_is_dotted:
            middle_pitch = middle_voice_measure[0].specific_pitch
            highest_pitch = pure.find_pitch(highest_voice_measure)
            dotted_measure = middle_voice_measure
            undotted_measure = highest_voice_measure
        else:
            middle_pitch = pure.find_pitch(middle_voice_measure)
            highest_pitch = highest_voice_measure[0].specific_pitch
            dotted_measure = highest_voice_measure
            undotted_measure = middle_voice_measure
        lowest_pitch = pure.find_pitch(lowest_voice_measure)

        if not pure.is_perfect_fourth_consonant(
            lowest_pitch, middle_pitch, highest_pitch
        ):
            if len(undotted_measure) != 2:
                return False
            first_patient_pitch = dotted_measure[0].specific_pitch
            second_patient_pitch = dotted_measure[1].specific_pitch
            if (
                theory.SpecificPitch.get_interval_vector(
                    first_patient_pitch, second_patient_pitch
                )
                != -1
            ):
                return False

            if middle_is_dotted:
                lower_resolve_pitch = second_patient_pitch
                upper_resolve_pitch = highest_pitch
            else:
                lower_resolve_pitch = middle_pitch
                upper_resolve_pitch = second_patient_pitch
            return lower_resolve_pitch.has_interval_shift(
                upper_resolve_pitch, ("M3", "m3", "P5")
            )
    return True


def valid_third_quarter_trio(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    middle_is_whole = pure.is_measure_whole(middle_voice_measure)
    highest_is_whole = pure.is_measure_whole(highest_voice_measure)

    if middle_is_whole ^ highest_is_whole:
        if middle_is_whole:
            counter_measure = highest_voice_measure
            middle_pitch = middle_voice_measure[0].specific_pitch
            highest_pitch = pure.find_pitch(highest_voice_measure)
        else:
            counter_measure = middle_voice_measure
            middle_pitch = pure.find_pitch(middle_voice_measure)
            highest_pitch = highest_voice_measure[0].specific_pitch

        if len(counter_measure) == 2:
            return True
        lowest_pitch = pure.find_pitch(lowest_voice_measure)
        if not pure.is_perfect_fourth_consonant(
            lowest_pitch, middle_pitch, highest_pitch
        ):
            if counter_measure[-1].duration == Fraction("1/2"):
                return False
            return pure.is_complete_descent(counter_measure)
    return True


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


def valid_diminished_fourth_species(
    measure_quartet: tuple[
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
    ]
) -> bool:
    patient_indices = []
    agent_indices = []
    for voice_index, voice_measure in enumerate(measure_quartet):
        if voice_measure[0].duration == Fraction("3/4"):
            patient_indices.append(voice_index)
        elif voice_measure[-1].duration == Fraction("1/2"):
            agent_indices.append(voice_index)

    if patient_indices and agent_indices:
        is_diminished_fourth_species = False
        has_imperfect_resolution = False
        lowest_pitch = pure.find_pitch(measure_quartet[0])

        for patient_index in patient_indices:
            for agent_index in agent_indices:
                if patient_index > agent_index:
                    lower_index = agent_index
                    upper_index = patient_index
                else:
                    lower_index = patient_index
                    upper_index = agent_index

                lower_voice_measure = measure_quartet[lower_index]
                upper_voice_measure = measure_quartet[upper_index]
                if not is_diminished_fourth_species:
                    upper_pitch = pure.find_pitch(upper_voice_measure)
                    if lower_index == 0:
                        is_diminished_fourth_species = not pure.is_duo_consonant(
                            lowest_pitch, upper_pitch, pure.lower_voice_consonances
                        )
                    else:
                        lower_pitch = pure.find_pitch(lower_voice_measure)
                        is_diminished_fourth_species = not pure.is_trio_consonant(
                            lowest_pitch, lower_pitch, upper_pitch
                        )
                if not has_imperfect_resolution:
                    has_imperfect_resolution = pure.is_resolution_imperfect(
                        lower_voice_measure, upper_voice_measure
                    )
        return not is_diminished_fourth_species or has_imperfect_resolution
    return True


def valid_regular_fourth_species(
    measure_quartet: tuple[
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
    ]
) -> bool:
    has_dissonant_downbeat = False
    has_imperfect_resolution = False
    lowest_downbeat_pitch = measure_quartet[0][0].specific_pitch

    for first_voice_index, second_voice_index in pure.all_voice_pairs:
        lower_voice_measure = measure_quartet[first_voice_index]
        upper_voice_measure = measure_quartet[second_voice_index]

        if not has_dissonant_downbeat:
            upper_downbeat_pitch = upper_voice_measure[0].specific_pitch
            if first_voice_index == 0:
                has_dissonant_downbeat = not pure.is_duo_consonant(
                    lowest_downbeat_pitch,
                    upper_downbeat_pitch,
                    pure.lower_voice_consonances,
                )
            else:
                lower_downbeat_pitch = lower_voice_measure[0].specific_pitch
                has_dissonant_downbeat = not pure.is_trio_consonant(
                    lowest_downbeat_pitch, lower_downbeat_pitch, upper_downbeat_pitch
                )
        if not has_imperfect_resolution:
            has_imperfect_resolution = pure.is_resolution_imperfect(
                lower_voice_measure, upper_voice_measure
            )
    return not has_dissonant_downbeat or has_imperfect_resolution


def get_pitch_quartet(
    bassus_measure: theory.FullVoiceMeasure,
    tenor_measure: theory.FullVoiceMeasure,
    contratenor_measure: theory.FullVoiceMeasure,
    superius_measure: theory.FullVoiceMeasure,
) -> Iterator[
    tuple[
        tuple[theory.SpecificPitch, theory.SpecificPitch],
        tuple[theory.SpecificPitch, theory.SpecificPitch],
        tuple[theory.SpecificPitch, theory.SpecificPitch],
        tuple[theory.SpecificPitch, theory.SpecificPitch],
    ]
]:
    bassus_iter = iter(bassus_measure)
    tenor_iter = iter(tenor_measure)
    contratenor_iter = iter(contratenor_measure)
    superius_iter = iter(superius_measure)

    bassus_duration = Fraction("0")
    tenor_duration = Fraction("0")
    contratenor_duration = Fraction("0")
    superius_duration = Fraction("0")
    remaining_measure_duration = Fraction("1")

    previous_bassus_pitch = bassus_measure[0].specific_pitch
    previous_tenor_pitch = tenor_measure[0].specific_pitch
    previous_contratenor_pitch = contratenor_measure[0].specific_pitch
    previous_superius_pitch = superius_measure[0].specific_pitch

    while remaining_measure_duration:
        if not bassus_duration:
            bassus_note = next(bassus_iter)
            bassus_duration = bassus_note.duration
        if not tenor_duration:
            tenor_note = next(tenor_iter)
            tenor_duration = tenor_note.duration
        if not contratenor_duration:
            contratenor_note = next(contratenor_iter)
            contratenor_duration = contratenor_note.duration
        if not superius_duration:
            superius_note = next(superius_iter)
            superius_duration = superius_note.duration

        current_bassus_pitch = bassus_note.specific_pitch
        current_tenor_pitch = tenor_note.specific_pitch
        current_contratenor_pitch = contratenor_note.specific_pitch
        current_superius_pitch = superius_note.specific_pitch

        yield (
            (previous_bassus_pitch, current_bassus_pitch),
            (previous_tenor_pitch, current_tenor_pitch),
            (previous_contratenor_pitch, current_contratenor_pitch),
            (previous_superius_pitch, current_superius_pitch),
        )

        intersect_duration = min(
            bassus_duration, tenor_duration, contratenor_duration, superius_duration
        )
        bassus_duration -= intersect_duration
        tenor_duration -= intersect_duration
        contratenor_duration -= intersect_duration
        superius_duration -= intersect_duration
        remaining_measure_duration -= intersect_duration

        previous_bassus_pitch = current_bassus_pitch
        previous_tenor_pitch = current_tenor_pitch
        previous_contratenor_pitch = current_contratenor_pitch
        previous_superius_pitch = current_superius_pitch


def valid_quartet_motion(
    measure_quartet: tuple[
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
    ]
) -> bool:
    for voice_measure in measure_quartet:
        if pure.is_measure_whole(voice_measure):
            return True

    quartet_iter = get_pitch_quartet(*measure_quartet)
    # First value (necessarily) contains duplicate pairs
    next(quartet_iter)
    for bassus_pair, tenor_pair, contratenor_pair, superius_pair in quartet_iter:
        if not checked_quartet_motion(
            bassus_pair, tenor_pair, contratenor_pair, superius_pair
        ):
            return False
    return True
