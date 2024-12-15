from fractions import Fraction
from functools import partial
import json
import random
from collections import defaultdict
from typing import Iterator, Callable

from generate import theory, export, rules, limits

with open("dance.json", "r") as f:
    idioms = json.load(f)

revert_duration = export.LilypondFactory.revert_duration
voice_names = ("bassus", "tenor", "contratenor", "superius")


def get_new_score() -> limits.DanceScore:
    clef_group = random.choice(idioms["clef_groups"])
    print(f"{clef_group = }")
    voice_tessituras = {}

    for clef_name, voice_name in zip(clef_group, voice_names):
        pitch_min_str, pitch_max_str = idioms["clef_ranges"][clef_name]
        pitch_min = theory.SpecificPitch(pitch_min_str)
        pitch_max = theory.SpecificPitch(pitch_max_str)

        voice_tessituras[voice_name] = theory.Tessitura(pitch_min, pitch_max)
        idioms["intermediate_cadances"][voice_name].extend(
            idioms["final_cadances"][voice_name]
        )

    tonic_pitch_str, chosen_mode = random.choice(idioms["available_keys"])
    chosen_scale = theory.type_map[chosen_mode](tonic_pitch_str)
    flattened_pitch = chosen_scale.flattened_pitch
    all_pitch_sequences = get_all_pitch_sequences(
        chosen_scale, voice_tessituras, flattened_pitch.letter
    )

    sequence_prospects: list[list[theory.MeasureStack]] = [[] for _ in range(12)]
    sequence_prospects[0] = get_first_measure_stacks(all_pitch_sequences, chosen_scale)
    sequence_prospects[5] = get_half_cadence(
        all_pitch_sequences, chosen_scale, voice_tessituras
    )
    sequence_prospects[6] = sequence_prospects[0][:]

    set_final_prospects(
        sequence_prospects, chosen_scale, voice_tessituras, "final_cadances"
    )
    voice_measure_stacker = VoiceMeasureStacker(all_pitch_sequences)
    measure_stack_groups = next(iter(voice_measure_stacker))

    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {
            "no_whole_notes": (1, 2, 3, 4, 7, 8, 9),
        },
    )
    score_sequences = [finalize_sequence(sequence_prospects, flattened_pitch)]

    sequence_prospects = [[] for _ in range(6)]
    set_final_prospects(
        sequence_prospects,
        chosen_scale.random_mode_shift(),
        voice_tessituras,
        "intermediate_cadances",
    )
    voice_measure_stacker = VoiceMeasureStacker(all_pitch_sequences)
    measure_stack_groups = next(iter(voice_measure_stacker))
    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {"some_whole_notes": (0,), "no_whole_notes": (0, 1, 2, 3)},
    )
    score_sequences.append(finalize_sequence(sequence_prospects, flattened_pitch))
    chosen_instruemnt = theory.MidiInstrument(*random.choice(idioms["instruments"]))

    return limits.DanceScore(
        chosen_scale, clef_group, score_sequences, chosen_instruemnt
    )


def finalize_sequence(
    sequence_prospects: list[list[theory.MeasureStack]],
    flattened_pitch: theory.GenericPitch,
) -> limits.CognizantSequence:
    prospect_counts = [len(index_prospects) for index_prospects in sequence_prospects]
    print(f"Allocated available measures: {prospect_counts}")
    propagator = partial(
        rules.has_counterpoint_propagated, flattened_pitch=flattened_pitch
    )
    possible_measure_sequences = limits.WaveFunction(sequence_prospects, propagator)

    return next(iter(possible_measure_sequences))


def get_all_pitch_sequences(
    chosen_scale: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
    flattened_pitch_letter: str,
) -> dict[str, list[theory.MelodicSequence]]:
    pitch_sequences = defaultdict(list)
    concerning_vectors = {-3, 3, -4, 4}

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
                        current_pitch = chosen_scale.scale_shift(
                            previous_pitch, 0, vector
                        )
                        if current_pitch not in voice_tessitura:
                            break
                        if vector in concerning_vectors:
                            if previous_pitch.has_interval_shift(
                                current_pitch, ("A4", "d5")
                            ):
                                break
                        pitch_sequence.append(
                            theory.SpecificNote(current_pitch, rhythm_duration)
                        )
                        previous_pitch = current_pitch
                    else:
                        pitch_sequences[voice_name].append(pitch_sequence)

        for available_pitch in available_pitches:
            if available_pitch.letter == flattened_pitch_letter:
                starting_pitch = available_pitch.clone()
                starting_pitch.increment_value(-1)
                if starting_pitch not in voice_tessitura:
                    continue
                is_first_pitch_flattened = True
            else:
                starting_pitch = available_pitch
                is_first_pitch_flattened = False

            for rhythm_id, melody_contours in idioms["rhythms"].items():
                rhythm_durations = [
                    revert_duration(rhythm_repr) for rhythm_repr in rhythm_id.split()
                ]
                for melody_contour in melody_contours:
                    pitch_sequence = [
                        theory.SpecificNote(starting_pitch, rhythm_durations[0])
                    ]
                    is_contour_relevant = is_first_pitch_flattened
                    is_previous_pitch_flattened = is_first_pitch_flattened
                    previous_pitch = starting_pitch

                    for rhythm_duration, vector in zip(
                        rhythm_durations[1:], melody_contour
                    ):
                        if is_previous_pitch_flattened and not (-3 <= vector <= 0):
                            break
                        current_pitch = chosen_scale.scale_shift(
                            previous_pitch, 0, vector
                        )
                        if current_pitch.letter == flattened_pitch_letter:
                            is_contour_relevant = True
                            current_pitch.increment_value(-1)
                            is_previous_pitch_flattened = True
                        else:
                            is_previous_pitch_flattened = False

                        if current_pitch not in voice_tessitura:
                            break
                        if vector in concerning_vectors:
                            if previous_pitch.has_interval_shift(
                                current_pitch, ("A4", "d5")
                            ):
                                break
                        pitch_sequence.append(
                            theory.SpecificNote(current_pitch, rhythm_duration)
                        )
                        previous_pitch = current_pitch
                    else:
                        if is_contour_relevant:
                            pitch_sequences[voice_name].append(pitch_sequence)

    return pitch_sequences


DuoMeasureTest = tuple[
    theory.MelodicSequence,
    theory.MelodicSequence,
    tuple[Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...],
    tuple[str, ...],
]


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
        duo_iter = limits.get_note_duo(lower_voice_measure, upper_voice_measure)
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
                True,
            ):
                return False

            previous_lower_note = current_lower_note
            previous_upper_note = current_upper_note
    return True


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


def get_first_measure_stacks(
    all_pitch_sequences: dict[str, list[theory.MelodicSequence]],
    chosen_scale: theory.ModalScale,
) -> list[theory.MeasureStack]:
    first_sequences = defaultdict(list)

    for voice_name, voice_measures in all_pitch_sequences.items():
        allowed_first_motions = set(idioms["first_motions"][voice_name])
        allowed_start_pitches = {
            str(chosen_scale[first_degree])
            for first_degree in idioms["first_degrees"][voice_name]
        }
        for voice_measure in voice_measures:
            if len(voice_measure) == 1:
                continue
            first_specific_pitch = voice_measure[0].specific_pitch
            if first_specific_pitch.generic_pitch not in allowed_start_pitches:
                continue

            second_specific_pitch = voice_measure[1].specific_pitch
            interval_vector = theory.SpecificPitch.get_interval_vector(
                first_specific_pitch, second_specific_pitch
            )
            if interval_vector not in allowed_first_motions:
                continue
            first_sequences[voice_name].append(voice_measure)

    voice_measure_stacker = VoiceMeasureStacker(first_sequences)
    measure_stack_groups = next(iter(voice_measure_stacker))

    return measure_stack_groups["no_whole_notes"]


def get_half_cadence(
    all_pitch_sequences: dict[str, list[theory.MelodicSequence]],
    chosen_scale: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
) -> list[theory.MeasureStack]:
    cadential_sequences = defaultdict(list)
    tonic_generic_pitch = chosen_scale[0]
    superius_tessitura = voice_tessituras["superius"]

    interval_shifts = [theory.Interval.get("m2")]
    if chosen_scale.scale_intervals[-1] == "m7":
        interval_shifts.append(theory.Interval.get("M2"))
    tonic_specific_pitches = superius_tessitura.find_equivalent_pitches(
        tonic_generic_pitch
    )

    for interval_shift in interval_shifts:
        for tonic_specific_pitch in tonic_specific_pitches:
            cadence_pitch = tonic_specific_pitch - interval_shift
            if cadence_pitch in superius_tessitura:
                cadential_sequences["superius"].append(
                    [
                        theory.SpecificNote(tonic_specific_pitch, Fraction("1/2")),
                        theory.SpecificNote(cadence_pitch, Fraction("1/2")),
                    ]
                )

    voice_vectors = {"bassus": {-1, -3}, "tenor": {-1, 1}, "contratenor": {-1, 1}}
    for voice_name in voice_names[:-1]:
        allowed_vectors = voice_vectors[voice_name]
        for voice_measure in all_pitch_sequences[voice_name]:
            if len(voice_measure) > 2:
                continue
            if len(voice_measure) == 2:
                first_note, second_note = voice_measure
                interval_vector = theory.SpecificPitch.get_interval_vector(
                    first_note.specific_pitch, second_note.specific_pitch
                )
                if interval_vector not in allowed_vectors:
                    continue
            cadential_sequences[voice_name].append(voice_measure)

    voice_measure_stacker = VoiceMeasureStacker(cadential_sequences)
    measure_stack_groups = next(iter(voice_measure_stacker))
    result_stacks = measure_stack_groups["no_whole_notes"]
    result_stacks.extend(measure_stack_groups["some_whole_notes"])

    return result_stacks


def create_picardy_third(
    has_minor_third: bool,
    designated_letter: str,
    original_note: theory.SpecificNote,
) -> theory.SpecificNote:
    if has_minor_third:
        original_pitch = original_note.specific_pitch
        if original_pitch.letter == designated_letter:
            picardy_third = original_pitch.clone()
            picardy_third.increment_value(1)
            return theory.SpecificNote(picardy_third, original_note.duration)

    return original_note


def set_final_prospects(
    sequence_prospects: list[list[theory.MeasureStack]],
    chosen_scale: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
    cadence_id: str,
) -> None:
    penultimate_sequences = defaultdict(list)
    ultimate_sequences = defaultdict(list)

    if chosen_scale.scale_intervals[2][0] == "m":
        modify_chordal_third = partial(
            create_picardy_third, True, chosen_scale[2].letter
        )
    else:
        modify_chordal_third = partial(
            create_picardy_third, False, chosen_scale[2].letter
        )

    for voice_name, voice_formulae in idioms[cadence_id].items():
        voice_tessitura = voice_tessituras[voice_name]
        ultimate_formulae = set()
        for voice_formula in voice_formulae:
            *penultimate_formula, ultimate_formula = voice_formula
            voice_measures = get_penultimate_voice_measures(
                chosen_scale, penultimate_formula, voice_tessitura
            )
            penultimate_sequences[voice_name].extend(voice_measures)
            ultimate_formulae.add(tuple(ultimate_formula))
        for ultimate_formula in ultimate_formulae:
            voice_measures = get_ultimate_voice_measures(
                chosen_scale, ultimate_formula, voice_tessitura, modify_chordal_third
            )
            ultimate_sequences[voice_name].extend(voice_measures)

    penultimate_iter = VoiceMeasureStacker.get_measure_stacks(
        penultimate_sequences["bassus"],
        penultimate_sequences["tenor"],
        penultimate_sequences["contratenor"],
        penultimate_sequences["superius"],
        are_cadential_columns_valid,
        has_cadential_fourths,
    )
    sequence_prospects[-2].extend(penultimate_iter)
    ultimate_iter = VoiceMeasureStacker.get_measure_stacks(
        ultimate_sequences["bassus"],
        ultimate_sequences["tenor"],
        ultimate_sequences["contratenor"],
        ultimate_sequences["superius"],
        are_pitch_columns_valid,
        has_valid_fourths,
    )
    sequence_prospects[-1].extend(ultimate_iter)


def get_penultimate_voice_measures(
    chosen_scale: theory.ModalScale,
    voice_formula: list[tuple[int, str]],
    voice_tessitura: theory.Tessitura,
) -> list[theory.MelodicSequence]:
    starting_scale_degree = voice_formula[0][0]
    starting_duration = revert_duration(voice_formula[0][1])
    pitch_sequences = []

    if (
        "-1" in str(voice_formula)
        and chosen_scale.scale_intervals[-1][0] == "m"
        and chosen_scale.type != "phrygian"
    ):
        starting_generic_pitch = chosen_scale.get_cadential_pitch(starting_scale_degree)
        starting_specific_pitches = voice_tessitura.find_equivalent_pitches(
            starting_generic_pitch
        )
        pitch_shifter = chosen_scale.cadential_shift
    else:
        starting_generic_pitch = chosen_scale[starting_scale_degree]
        starting_specific_pitches = voice_tessitura.find_equivalent_pitches(
            starting_generic_pitch
        )
        pitch_shifter = chosen_scale.scale_shift

    for starting_specific_pitch in starting_specific_pitches:
        pitch_sequence = [
            theory.SpecificNote(starting_specific_pitch, starting_duration)
        ]
        previous_scale_degree = starting_scale_degree
        previous_specific_pitch = starting_specific_pitch

        for current_scale_degree, duration_repr in voice_formula[1:]:
            current_specific_pitch = pitch_shifter(
                previous_specific_pitch, previous_scale_degree, current_scale_degree
            )
            if current_specific_pitch not in voice_tessitura:
                break

            current_duration = revert_duration(duration_repr)
            pitch_sequence.append(
                theory.SpecificNote(current_specific_pitch, current_duration)
            )
            previous_scale_degree = current_scale_degree
            previous_specific_pitch = current_specific_pitch
        else:
            pitch_sequences.append(pitch_sequence)

    return pitch_sequences


def get_ultimate_voice_measures(
    chosen_scale: theory.ModalScale,
    voice_formula: tuple[int, str],
    voice_tessitura: theory.Tessitura,
    modify_chordal_third: partial[theory.SpecificNote],
) -> list[theory.MelodicSequence]:
    ultimate_duration = Fraction("1")
    diatonic_generic_pitch = chosen_scale[voice_formula[0]]
    starting_specific_pitches = voice_tessitura.find_equivalent_pitches(
        diatonic_generic_pitch
    )

    pitch_sequences = []
    for starting_specific_pitch in starting_specific_pitches:
        sole_note = theory.SpecificNote(starting_specific_pitch, ultimate_duration)
        corrected_voice_measure = [modify_chordal_third(sole_note)]
        pitch_sequences.append(corrected_voice_measure)

    return pitch_sequences


def are_cadential_columns_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
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
            if len(upper_voice_measure) != 2:
                return False
            if len(lower_voice_measure) != 1:
                return False
            if previous_upper_note.duration != Fraction("1/2"):
                return False
            resolution_vector = theory.SpecificPitch.get_interval_vector(
                previous_upper_note.specific_pitch,
                upper_voice_measure[1].specific_pitch,
            )
            if resolution_vector != -1:
                return False
        duo_iter = limits.get_note_duo(lower_voice_measure, upper_voice_measure)
        for current_lower_note, current_upper_note in duo_iter:
            for additional_test in additional_tests:
                if not additional_test(
                    current_lower_note.specific_pitch,
                    current_upper_note.specific_pitch,
                ):
                    return False

            if not rules.is_cadential_duo_valid(
                previous_lower_note,
                previous_upper_note,
                current_lower_note,
                current_upper_note,
                consonant_ids,
            ):
                return False

            previous_lower_note = current_lower_note
            previous_upper_note = current_upper_note
    return True


def has_cadential_fourths(
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
        if len(highest_voice_measure) != 2:
            return False
        if len(middle_voice_measure) != 1:
            return False
        if highest_voice_measure[0].duration != Fraction("1/2"):
            return False
        resolution_vector = theory.SpecificPitch.get_interval_vector(
            previous_highest_pitch,
            highest_voice_measure[1].specific_pitch,
        )
        if resolution_vector != -1:
            return False

    for current_lowest_pitch, current_middle_pitch, current_highest_pitch in trio_iter:
        if not rules.is_cadential_trio_valid(
            previous_lowest_pitch,
            previous_middle_pitch,
            previous_highest_pitch,
            current_lowest_pitch,
            current_middle_pitch,
            current_highest_pitch,
        ):
            return False

        previous_lowest_pitch = current_lowest_pitch
        previous_middle_pitch = current_middle_pitch
        previous_highest_pitch = current_highest_pitch

    return True


def fill_prospects(
    sequence_prospects: list[list[theory.MeasureStack]],
    measure_stack_groups: dict[str, list[theory.MeasureStack]],
    stack_map: dict[str, tuple[int, ...]],
) -> None:
    for group_key, prospect_indices in stack_map.items():
        for measure_stack in measure_stack_groups[group_key]:
            for prospect_index in prospect_indices:
                sequence_prospects[prospect_index].append(measure_stack)


class VoiceMeasureStacker:
    def __init__(
        self, pitch_sequences: dict[str, list[theory.MelodicSequence]]
    ) -> None:
        self.bassus_measures = pitch_sequences["bassus"]
        self.tenor_measures = pitch_sequences["tenor"]
        self.contratenor_measures = pitch_sequences["contratenor"]
        self.superius_measures = pitch_sequences["superius"]

    def __iter__(self) -> Iterator[dict[str, list[theory.MeasureStack]]]:
        random.shuffle(self.bassus_measures)
        sub_iters = []
        for bassus_measure in self.bassus_measures:
            sub_iters.append(
                self.get_measure_stacks(
                    [bassus_measure],
                    self.tenor_measures,
                    self.contratenor_measures,
                    self.superius_measures,
                    are_pitch_columns_valid,
                    has_valid_fourths,
                )
            )

        valid_result_count = 0
        measure_stack_groups = defaultdict(list)
        sub_iter_count = len(sub_iters)
        print(f"Generating stacks from {sub_iter_count} iterators.")
        sample_index = 0

        while sub_iters:
            if sample_index == sub_iter_count:
                sample_index = 0
            try:
                current_measure_stack = next(sub_iters[sample_index])
            except StopIteration:
                sub_iters.pop(sample_index)
                sub_iter_count -= 1
                continue
            whole_note_count = self.count_whole_notes(current_measure_stack)

            if whole_note_count == 0:
                measure_stack_groups["no_whole_notes"].append(current_measure_stack)
                valid_result_count += 1
                if valid_result_count == 3_500:
                    yield measure_stack_groups
                    valid_result_count = 0
                    measure_stack_groups.clear()
            elif whole_note_count == 4:
                measure_stack_groups["all_whole_notes"].append(current_measure_stack)
            else:
                measure_stack_groups["some_whole_notes"].append(current_measure_stack)
            sample_index += 1

        yield measure_stack_groups

    @staticmethod
    def count_whole_notes(measure_stack: theory.MeasureStack) -> int:
        return sum(1 for voice_measure in measure_stack if len(voice_measure) == 1)

    @staticmethod
    def shuffle_iter(
        voice_measures: list[theory.MelodicSequence],
    ) -> Iterator[theory.MelodicSequence]:
        measure_indices = list(range(len(voice_measures)))
        random.shuffle(measure_indices)
        for measure_index in measure_indices:
            yield voice_measures[measure_index]

    @classmethod
    def get_measure_stacks(
        cls,
        bassus_measures: list[theory.MelodicSequence],
        tenor_measures: list[theory.MelodicSequence],
        contratenor_measures: list[theory.MelodicSequence],
        superius_measures: list[theory.MelodicSequence],
        is_duo_valid: Callable[[tuple[DuoMeasureTest, ...]], bool],
        is_trio_valid: Callable[
            [theory.MelodicSequence, theory.MelodicSequence, theory.MelodicSequence],
            bool,
        ],
    ) -> Iterator[theory.MeasureStack]:
        duos_to_check: tuple[DuoMeasureTest, ...]
        for bassus_measure in cls.shuffle_iter(bassus_measures):
            for tenor_measure in cls.shuffle_iter(tenor_measures):
                duos_to_check = (
                    (
                        bassus_measure,
                        tenor_measure,
                        (rules.is_lowest_duo_good,),
                        rules.lower_voice_consonances,
                    ),
                )
                if not is_duo_valid(duos_to_check):
                    continue
                for contratenor_measure in cls.shuffle_iter(contratenor_measures):
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
                    if not is_duo_valid(duos_to_check):
                        continue
                    if not is_trio_valid(
                        bassus_measure, tenor_measure, contratenor_measure
                    ):
                        continue
                    for superius_measure in cls.shuffle_iter(superius_measures):
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
                        if not is_duo_valid(duos_to_check):
                            continue
                        if not is_trio_valid(
                            bassus_measure, tenor_measure, superius_measure
                        ):
                            continue
                        if not is_trio_valid(
                            bassus_measure, contratenor_measure, superius_measure
                        ):
                            continue
                        possible_measure_stack = (
                            bassus_measure,
                            tenor_measure,
                            contratenor_measure,
                            superius_measure,
                        )
                        yield possible_measure_stack
