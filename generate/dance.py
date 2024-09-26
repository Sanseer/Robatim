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

    possible_measure_combos = get_measure_combos(pitch_sequences)
    print(f"Generated {len(possible_measure_combos)} measures")
    sequence_prospects = [possible_measure_combos[:] for _ in range(12)]

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


def get_measure_combos(
    pitch_sequences: dict[str, list[theory.MelodicSequence]]
) -> list[theory.MeasureStack]:
    combos_to_check: tuple[DuoMeasureTest, ...]
    possible_measure_combos = []
    for bassus_measure in pitch_sequences["bassus"]:
        for tenor_measure in pitch_sequences["tenor"]:
            combos_to_check = (
                (
                    bassus_measure,
                    tenor_measure,
                    (rules.is_lowest_duo_good,),
                    rules.lower_voice_consonances,
                ),
            )
            if not are_pitch_columns_valid(combos_to_check):
                continue
            for contratenor_measure in pitch_sequences["contratenor"]:
                combos_to_check = (
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
                if not are_pitch_columns_valid(combos_to_check):
                    continue
                for superius_measure in pitch_sequences["superius"]:
                    combos_to_check = (
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
                    if not are_pitch_columns_valid(combos_to_check):
                        continue
                    possible_measure_combos.append(
                        (
                            bassus_measure,
                            tenor_measure,
                            contratenor_measure,
                            superius_measure,
                        )
                    )
    return possible_measure_combos


def are_pitch_columns_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        additional_tests,
        consonant_ids,
    ) in duo_measure_tests:
        previous_lower_pitch = lower_voice_measure[0].specific_pitch
        previous_upper_pitch = upper_voice_measure[0].specific_pitch

        if not rules.is_duo_consonant(
            previous_lower_pitch, previous_upper_pitch, consonant_ids
        ):
            return False
        duo_iter = get_pitch_pairs(lower_voice_measure, upper_voice_measure)
        for current_lower_pitch, current_upper_pitch in duo_iter:
            for additional_test in additional_tests:
                if not additional_test(current_lower_pitch, current_upper_pitch):
                    return False

            if not rules.is_duo_motion_valid(
                previous_lower_pitch,
                previous_upper_pitch,
                current_lower_pitch,
                current_upper_pitch,
                consonant_ids,
                True,
            ):
                return False

            previous_lower_pitch = current_lower_pitch
            previous_upper_pitch = current_upper_pitch
    return True


def get_pitch_pairs(
    lower_voice_measure: theory.MelodicSequence,
    upper_voice_measure: theory.MelodicSequence,
) -> Iterator[tuple[theory.SpecificPitch, theory.SpecificPitch]]:
    lower_voice_iter = iter(lower_voice_measure)
    upper_voice_iter = iter(upper_voice_measure)

    lower_voice_note = next(lower_voice_iter)
    upper_voice_note = next(upper_voice_iter)
    lower_voice_duration = lower_voice_note.duration
    upper_voice_duration = upper_voice_note.duration

    while True:
        yield lower_voice_note.specific_pitch, upper_voice_note.specific_pitch

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
