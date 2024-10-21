import json
import random
from collections import defaultdict
from typing import Iterator, Callable

from generate import theory, export, rules

with open("dance.json", "r") as f:
    idioms = json.load(f)

scale_map = {
    "ionian": theory.IonianScale,
    "dorian": theory.DorianScale,
    "mixolydian": theory.MixolydianScale,
    "aeolian": theory.AeolianScale,
}


def get_new_score() -> theory.DanceScore:
    clef_group = random.choice(idioms["clef_groups"])
    print(f"{clef_group = }")
    voice_tessituras = {}

    voice_names = ["bassus", "tenor", "contratenor", "superius"]
    for clef_name, voice_name in zip(clef_group, voice_names):
        pitch_min_str, pitch_max_str = idioms["clef_ranges"][clef_name]
        pitch_min = theory.SpecificPitch(pitch_min_str)
        pitch_max = theory.SpecificPitch(pitch_max_str)

        voice_tessituras[voice_name] = theory.Tessitura(pitch_min, pitch_max)

    tonic_pitch_str, chosen_mode = random.choice(idioms["available_keys"])
    chosen_scale = scale_map[chosen_mode](tonic_pitch_str)
    revert_duration = export.LilypondFactory.revert_duration
    pitch_sequences = defaultdict(list)

    for voice_name, voice_tessitura in voice_tessituras.items():
        available_pitches = voice_tessitura.filter_pitches(
            chosen_scale.get_specific_iter()
        )

        for starting_pitch in available_pitches:
            for rhythm_id, melody_contours in idioms["rhythms"].items():
                rhythm_durations = [
                    revert_duration(rhythm_repr) for rhythm_repr in rhythm_id.split()
                ]
                for melody_contour in melody_contours:
                    pitch_sequence = [
                        theory.SpecificNote(starting_pitch, rhythm_durations[0])
                    ]
                    previous_pitch = starting_pitch
                    for rhythm_duration, vector in zip(
                        rhythm_durations[1:], melody_contour
                    ):
                        new_pitch = chosen_scale.scale_shift(previous_pitch, vector)
                        if new_pitch not in voice_tessitura:
                            break
                        pitch_sequence.append(
                            theory.SpecificNote(new_pitch, rhythm_duration)
                        )
                        previous_pitch = new_pitch
                    else:
                        pitch_sequences[voice_name].append(pitch_sequence)

    measure_stack_groups = get_measure_stacks(pitch_sequences)
    total_measure_count = sum(len(v) for v in measure_stack_groups.values())
    print(f"Generated {total_measure_count} measures")
    sequence_prospects = get_sequence_prospects(measure_stack_groups)
    prospect_counts = [len(index_prospects) for index_prospects in sequence_prospects]
    print(f"Allocated available measures: {prospect_counts}")

    possible_measure_sequences = theory.WaveFunction(
        sequence_prospects, rules.has_counterpoint_propagated
    )
    score_sequence = next(iter(possible_measure_sequences))
    chosen_instruemnt = theory.MidiInstrument(*random.choice(idioms["instruments"]))

    return theory.DanceScore(
        chosen_scale, clef_group, score_sequence, chosen_instruemnt
    )


DuoMeasureTest = tuple[
    theory.MelodicSequence,
    theory.MelodicSequence,
    tuple[Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...],
    set[str],
]


def count_whole_notes(measure_stack: theory.MeasureStack) -> int:
    return sum(1 for voice_measure in measure_stack if len(voice_measure) == 1)


def get_measure_stacks(
    pitch_sequences: dict[str, list[theory.MelodicSequence]]
) -> dict[str, list[theory.MeasureStack]]:
    duos_to_check: tuple[DuoMeasureTest, ...]
    measure_stack_groups = defaultdict(list)
    for bassus_measure in pitch_sequences["bassus"]:
        for tenor_measure in pitch_sequences["tenor"]:
            duos_to_check = (
                (
                    bassus_measure,
                    tenor_measure,
                    (rules.is_lowest_duo_good,),
                    rules.lower_voice_consonances,
                ),
            )
            if not are_pitch_columns_valid(duos_to_check):
                continue
            for contratenor_measure in pitch_sequences["contratenor"]:
                duos_to_check = (
                    (
                        bassus_measure,
                        contratenor_measure,
                        tuple(),
                        rules.lower_voice_consonances,
                    ),
                    (
                        tenor_measure,
                        contratenor_measure,
                        (rules.is_upper_duo_good,),
                        rules.upper_voice_consonances,
                    ),
                )
                if not are_pitch_columns_valid(duos_to_check):
                    continue
                if not has_valid_fourths(
                    bassus_measure, tenor_measure, contratenor_measure
                ):
                    continue
                for superius_measure in pitch_sequences["superius"]:
                    duos_to_check = (
                        (
                            bassus_measure,
                            superius_measure,
                            tuple(),
                            rules.lower_voice_consonances,
                        ),
                        (
                            tenor_measure,
                            superius_measure,
                            tuple(),
                            rules.upper_voice_consonances,
                        ),
                        (
                            contratenor_measure,
                            superius_measure,
                            (rules.is_upper_duo_good,),
                            rules.upper_voice_consonances,
                        ),
                    )
                    if not are_pitch_columns_valid(duos_to_check):
                        continue
                    if not has_valid_fourths(
                        bassus_measure, tenor_measure, superius_measure
                    ):
                        continue
                    if not has_valid_fourths(
                        bassus_measure, contratenor_measure, superius_measure
                    ):
                        continue
                    possible_measure_stack = (
                        bassus_measure,
                        tenor_measure,
                        contratenor_measure,
                        superius_measure,
                    )
                    whole_note_count = count_whole_notes(possible_measure_stack)
                    if whole_note_count == 0:
                        measure_stack_groups["no_whole_notes"].append(
                            possible_measure_stack
                        )
                    elif whole_note_count == 4:
                        measure_stack_groups["all_whole_notes"].append(
                            possible_measure_stack
                        )
                    else:
                        measure_stack_groups["some_whole_notes"].append(
                            possible_measure_stack
                        )
    return measure_stack_groups


def are_pitch_columns_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        additional_tests,
        consonant_ids,
    ) in duo_measure_tests:
        previous_lower_note = lower_voice_measure[0]
        previous_upper_note = upper_voice_measure[0]

        if not rules.is_duo_consonant(
            previous_lower_note.specific_pitch,
            previous_upper_note.specific_pitch,
            consonant_ids,
        ):
            return False
        duo_iter = get_note_duo(lower_voice_measure, upper_voice_measure)
        for current_lower_note, current_upper_note in duo_iter:
            for additional_test in additional_tests:
                if not additional_test(
                    current_lower_note.specific_pitch,
                    current_upper_note.specific_pitch,
                ):
                    return False

            if not rules.is_duo_motion_valid(
                previous_lower_note,
                previous_upper_note,
                current_lower_note,
                current_upper_note,
                consonant_ids,
                True,
            ):
                return False

            previous_lower_note = current_lower_note
            previous_upper_note = current_upper_note
    return True


def get_note_duo(
    lower_voice_measure: theory.MelodicSequence,
    upper_voice_measure: theory.MelodicSequence,
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


def has_valid_fourths(
    lowest_voice_measure: theory.MelodicSequence,
    middle_voice_measure: theory.MelodicSequence,
    highest_voice_measure: theory.MelodicSequence,
) -> bool:
    trio_iter = get_pitch_trio(
        lowest_voice_measure, middle_voice_measure, highest_voice_measure
    )
    previous_lowest_pitch = lowest_voice_measure[0].specific_pitch
    previous_middle_pitch = middle_voice_measure[0].specific_pitch
    previous_highest_pitch = highest_voice_measure[0].specific_pitch

    if not rules.is_perfect_fourth_consonant(
        previous_lowest_pitch, previous_middle_pitch, previous_highest_pitch
    ):
        return False

    for current_lowest_pitch, current_middle_pitch, current_highest_pitch in trio_iter:
        if not rules.is_trio_motion_valid(
            previous_lowest_pitch,
            previous_middle_pitch,
            previous_highest_pitch,
            current_lowest_pitch,
            current_middle_pitch,
            current_highest_pitch,
            True,
        ):
            return False

        previous_lowest_pitch = current_lowest_pitch
        previous_middle_pitch = current_middle_pitch
        previous_highest_pitch = current_highest_pitch

    return True


def get_pitch_trio(
    lowest_voice_measure: theory.MelodicSequence,
    middle_voice_measure: theory.MelodicSequence,
    highest_voice_measure: theory.MelodicSequence,
) -> Iterator[tuple[theory.SpecificPitch, theory.SpecificPitch, theory.SpecificPitch]]:
    lowest_voice_iter = iter(lowest_voice_measure)
    middle_voice_iter = iter(middle_voice_measure)
    highest_voice_iter = iter(highest_voice_measure)

    lowest_voice_note = next(lowest_voice_iter)
    middle_voice_note = next(middle_voice_iter)
    highest_voice_note = next(highest_voice_iter)
    lowest_voice_duration = lowest_voice_note.duration
    middle_voice_duration = middle_voice_note.duration
    highest_voice_duration = highest_voice_note.duration

    while True:
        result = (
            lowest_voice_note.specific_pitch,
            middle_voice_note.specific_pitch,
            highest_voice_note.specific_pitch,
        )
        yield result

        intersect_duration = min(
            lowest_voice_duration, middle_voice_duration, highest_voice_duration
        )
        lowest_voice_duration -= intersect_duration
        middle_voice_duration -= intersect_duration
        highest_voice_duration -= intersect_duration

        try:
            if not lowest_voice_duration:
                lowest_voice_note = next(lowest_voice_iter)
                lowest_voice_duration = lowest_voice_note.duration
            if not middle_voice_duration:
                middle_voice_note = next(middle_voice_iter)
                middle_voice_duration = middle_voice_note.duration
            if not highest_voice_duration:
                highest_voice_note = next(highest_voice_iter)
                highest_voice_duration = highest_voice_note.duration
        except StopIteration:
            break


def get_sequence_prospects(
    measure_stack_groups: dict[str, list[theory.MeasureStack]]
) -> list[list[theory.MeasureStack]]:
    sequence_prospects: list[list[theory.MeasureStack]] = [[] for _ in range(12)]
    for measure_stack in measure_stack_groups["all_whole_notes"]:
        for current_index in (4, 5, 10, 11):
            sequence_prospects[current_index].append(measure_stack)

    for measure_stack in measure_stack_groups["some_whole_notes"]:
        for current_index in (4, 5, 10):
            sequence_prospects[current_index].append(measure_stack)

    for measure_stack in measure_stack_groups["no_whole_notes"]:
        for current_index in range(11):
            sequence_prospects[current_index].append(measure_stack)
    return sequence_prospects
