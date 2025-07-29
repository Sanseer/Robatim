from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
import random
from typing import Iterator, Callable

from generate import export, limits, pure, rules, screen, source, theory

idioms = source.idioms
revert_duration = export.LilypondFactory.revert_duration
lower_voice_names = ("bassus", "tenor", "contratenor")


def print_prospect_counts(sequence_prospects: limits.TwoDimensionStack) -> None:
    prospect_counts = [len(index_prospects) for index_prospects in sequence_prospects]
    print(f"Allocated available measures: {prospect_counts}")


def add_duplicates(
    sequence_prospects: limits.TwoDimensionStack,
    reference_sequence: list[theory.FullMeasureStack],
    full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    chosen_modes: list[theory.ModalScale],
) -> None:
    first_voice_measures = defaultdict(list)
    first_degrees = idioms["first_degrees"]

    for voice_name in lower_voice_names:
        allowed_first_motions = set(idioms["first_motions"][voice_name])
        allowed_start_pitches = {
            str(chosen_mode[first_degree])
            for chosen_mode in chosen_modes
            for first_degree in first_degrees[voice_name]
        }

        for voice_measure in full_voice_measures[voice_name]:
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
            first_voice_measures[voice_name].append(voice_measure)

    voice_measure_groups = [
        first_voice_measures,
        full_voice_measures,
        full_voice_measures,
    ]
    for propagate_index, selected_voice_measures in enumerate(voice_measure_groups):
        reference_superius_measure = reference_sequence[propagate_index][-1]
        modified_measure_sequences = {
            "bassus": selected_voice_measures["bassus"],
            "tenor": selected_voice_measures["tenor"],
            "contratenor": selected_voice_measures["contratenor"],
            "superius": [reference_superius_measure],
        }

        voice_measure_stacker = VoiceMeasureStacker(
            modified_measure_sequences,
            result_min_count=7_000,
            result_filter_threshold=0,
        )
        measure_stack_groups = next(iter(voice_measure_stacker))
        sequence_prospects[propagate_index].extend(
            measure_stack_groups["no_whole_notes"]
        )


def get_tempo(partial_constructor: type[limits.SequencePartial]) -> int:
    dance_name = partial_constructor.__name__[:-7]
    tempo_min, tempo_max = idioms["tempo_map"][dance_name]
    return random.randint(tempo_min, tempo_max)


half_cadence_cache: dict[str, list[theory.FullMeasureStack]] = {}


def get_branle_simple(
    clef_group: list[str],
    voice_tessituras: dict[str, theory.Tessitura],
    primary_mode: theory.ModalScale,
    all_full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
) -> limits.DanceScore:
    sequence_prospects: list[list[theory.FullMeasureStack]] = [[] for _ in range(6)]
    if is_antecedent := random.random() < 0.5:
        chosen_modes = [primary_mode]
    else:
        secondary_mode = primary_mode.random_mode_shift()
        chosen_modes = [primary_mode, secondary_mode]

    top_clef = clef_group[-1]
    max_ending_pitch = theory.SpecificPitch(
        idioms["final_max_superius_pitch"][top_clef]
    )
    min_ending_pitch = theory.SpecificPitch("C0")
    superius_ending_tessitura = theory.Tessitura(min_ending_pitch, max_ending_pitch)

    set_final_prospects(
        sequence_prospects,
        primary_mode,
        voice_tessituras,
        "final_cadances",
        superius_ending_tessitura,
    )
    modified_full_voice_measures = filter_voice_measures(
        all_full_voice_measures, *chosen_modes
    )
    sequence_prospects[0] = get_first_measure_stacks(
        modified_full_voice_measures, primary_mode, is_antecedent
    )

    voice_measure_stacker = VoiceMeasureStacker(
        modified_full_voice_measures, allow_chanson_idiom=True
    )
    measure_stack_groups = next(iter(voice_measure_stacker))
    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {
            "no_whole_notes": [3],
        },
    )

    voice_measure_stacker = VoiceMeasureStacker(modified_full_voice_measures)
    measure_stack_groups = next(iter(voice_measure_stacker))

    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {
            "no_whole_notes": [1, 2],
        },
    )

    print_prospect_counts(sequence_prospects)
    dance_partial2 = limits.BranleSimplePartial(sequence_prospects, chosen_modes)
    measure_sequence2 = dance_partial2.realize()

    sequence_prospects = [[] for _ in range(6)]
    if is_antecedent:
        print("Half cadence!")
        sequence1_modes = [primary_mode]
        if str(primary_mode) in half_cadence_cache:
            sequence_prospects[5] = half_cadence_cache[str(primary_mode)]
        else:
            sequence_prospects[5] = get_half_cadence(
                modified_full_voice_measures, primary_mode, voice_tessituras
            )
        reference_stack = measure_sequence2[0]
        filtered_prospects = []
        reference_tonic_pitch = reference_stack[-1][0].specific_pitch
        for index_prospect in sequence_prospects[5]:
            current_superius_pitch = index_prospect[-1][0].specific_pitch
            if current_superius_pitch != reference_tonic_pitch:
                continue
            filtered_prospects.append(index_prospect)
        sequence_prospects[5] = filter_by_transition(
            filtered_prospects, reference_stack, primary_mode
        )
        remaining_indices = [3, 4]
    else:
        print("Double cadence!")
        sequence1_modes = [secondary_mode]
        max_ending_pitch = theory.SpecificPitch(
            idioms["intermediate_max_superius_pitch"][top_clef]
        )
        min_ending_pitch = measure_sequence2[-1][-1][-1].specific_pitch
        superius_ending_tessitura = theory.Tessitura(min_ending_pitch, max_ending_pitch)
        set_final_prospects(
            sequence_prospects,
            secondary_mode,
            voice_tessituras,
            "intermediate_cadances",
            superius_ending_tessitura,
            False,
        )
        modified_full_voice_measures = filter_voice_measures(
            all_full_voice_measures,
            secondary_mode,
        )
        voice_measure_stacker = VoiceMeasureStacker(modified_full_voice_measures)
        measure_stack_groups = next(iter(voice_measure_stacker))

        remaining_indices = [3]

    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {
            "no_whole_notes": remaining_indices,
        },
    )
    add_duplicates(
        sequence_prospects,
        measure_sequence2,
        modified_full_voice_measures,
        chosen_modes,
    )
    print_prospect_counts(sequence_prospects)

    dance_partial1 = limits.BranleSimplePartial(
        sequence_prospects,
        sequence1_modes,
        is_antecedent=is_antecedent,
        is_intermediate_sequence=True,
    )
    measure_sequence1 = dance_partial1.realize()

    sequence_prospects = [[] for _ in range(6)]
    min_ending_pitch = theory.SpecificPitch("C0")
    max_ending_pitch = theory.SpecificPitch(
        idioms["final_max_superius_pitch"][top_clef]
    )
    superius_ending_tessitura = theory.Tessitura(min_ending_pitch, max_ending_pitch)
    if is_antecedent:
        secondary_mode = primary_mode.random_mode_shift()
    else:
        secondary_mode = secondary_mode.random_mode_shift()
    set_final_prospects(
        sequence_prospects,
        secondary_mode,
        voice_tessituras,
        "intermediate_cadances",
        superius_ending_tessitura,
    )
    modified_full_voice_measures = filter_voice_measures(
        all_full_voice_measures, secondary_mode
    )
    voice_measure_stacker = VoiceMeasureStacker(modified_full_voice_measures)
    measure_stack_groups = next(iter(voice_measure_stacker))
    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {"some_whole_notes": [0, 2], "no_whole_notes": [0, 1, 2, 3]},
    )

    print_prospect_counts(sequence_prospects)
    dance_partial3 = limits.BranleSimplePartial(
        sequence_prospects,
        [secondary_mode],
    )
    measure_sequence3 = dance_partial3.realize()

    score_sequences = [[*measure_sequence1, *measure_sequence2], measure_sequence3]
    chosen_instruemnt = theory.MidiInstrument(*random.choice(idioms["instruments"]))
    tempo = get_tempo(limits.BranleSimplePartial)

    return limits.DanceScore(
        primary_mode, clef_group, score_sequences, chosen_instruemnt, tempo
    )


def get_basse_danse(
    clef_group: list[str],
    voice_tessituras: dict[str, theory.Tessitura],
    primary_mode: theory.ModalScale,
    all_full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
) -> limits.DanceScore:
    half_measure_stacks = get_half_measure_stacks(primary_mode, voice_tessituras)

    top_clef = clef_group[-1]
    max_ending_pitch = theory.SpecificPitch(
        idioms["final_max_superius_pitch"][top_clef]
    )
    min_ending_pitch = theory.SpecificPitch("C0")
    secondary_mode = primary_mode.random_mode_shift()
    modified_full_voice_measures = filter_voice_measures(
        all_full_voice_measures, primary_mode, secondary_mode
    )
    superius_ending_tessitura = theory.Tessitura(min_ending_pitch, max_ending_pitch)

    measure_sequence2 = get_dance_sequence(
        modified_full_voice_measures,
        half_measure_stacks,
        primary_mode,
        voice_tessituras,
        "final_cadances",
        superius_ending_tessitura,
    )

    max_ending_pitch = theory.SpecificPitch(
        idioms["intermediate_max_superius_pitch"][top_clef]
    )
    min_ending_pitch = measure_sequence2[-1][-1][-1].specific_pitch
    modified_full_voice_measures = filter_voice_measures(
        all_full_voice_measures,
        secondary_mode,
    )
    superius_ending_tessitura = theory.Tessitura(min_ending_pitch, max_ending_pitch)
    measure_sequence1 = get_dance_sequence(
        modified_full_voice_measures,
        half_measure_stacks,
        secondary_mode,
        voice_tessituras,
        "intermediate_cadances",
        superius_ending_tessitura,
    )
    score_sequences = [[*measure_sequence1, *measure_sequence2]]
    chosen_instruemnt = theory.MidiInstrument(*random.choice(idioms["instruments"]))
    tempo = get_tempo(limits.BasseDansePartial)

    return limits.DanceScore(
        primary_mode, clef_group, score_sequences, chosen_instruemnt, tempo
    )


def get_dance_sequence(
    full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    half_measure_stacks: list[theory.VariantStack],
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
    cadence_id: str,
    superius_ending_tessitura: theory.Tessitura,
) -> list[theory.VariantStack]:
    sequence_prospects: list[list[theory.VariantStack]] = [[] for _ in range(6)]
    sequence_prospects[0] = half_measure_stacks

    set_final_prospects(
        sequence_prospects,
        chosen_mode,
        voice_tessituras,
        cadence_id,
        superius_ending_tessitura,
    )

    if cadence_id == "final_cadances":
        voice_measure_stacker = VoiceMeasureStacker(
            full_voice_measures, allow_chanson_idiom=True
        )
        measure_stack_groups = next(iter(voice_measure_stacker))
        fill_prospects(
            sequence_prospects,
            measure_stack_groups,
            {
                "no_whole_notes": [3],
            },
        )
        remaining_indices = [1, 2]
    else:
        remaining_indices = [1, 2, 3]

    voice_measure_stacker = VoiceMeasureStacker(full_voice_measures)
    measure_stack_groups = next(iter(voice_measure_stacker))
    fill_prospects(
        sequence_prospects,
        measure_stack_groups,
        {
            "no_whole_notes": remaining_indices,
        },
    )

    print_prospect_counts(sequence_prospects)
    dance_partial = limits.BasseDansePartial(sequence_prospects, [chosen_mode])
    return dance_partial.realize()


def get_full_measure_sequences(
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
) -> dict[str, list[theory.FullVoiceMeasure]]:
    pitch_sequences = defaultdict(list)
    concerning_vectors = {-3, 3, -4, 4}
    flattened_pitch_letter = chosen_mode.flattened_pitch.letter

    melody_packs = []
    for rhythm_id, melody_contours in idioms["rhythms"].items():
        rhythm_durations = [
            revert_duration(rhythm_repr) for rhythm_repr in rhythm_id.split()
        ]
        melody_packs.append(theory.MelodyPack(rhythm_durations, melody_contours))

    for voice_name, voice_tessitura in voice_tessituras.items():
        available_pitches = voice_tessitura.filter_pitches(
            chosen_mode.get_specific_iter()
        )

        for starting_pitch in available_pitches:
            for melody_pack in melody_packs:
                for melody_contour in melody_pack.melody_contours:
                    left_skip_count, right_skip_count = melody_pack.get_skip_counts(
                        melody_contour
                    )
                    is_skip_continuous = melody_pack.check_skip_continuity(
                        left_skip_count, right_skip_count, melody_contour
                    )
                    pitch_sequence = [
                        theory.SpecificNote(
                            starting_pitch, melody_pack.rhythm_durations[0]
                        )
                    ]
                    previous_pitch = starting_pitch
                    for rhythm_duration, vector in zip(
                        melody_pack.rhythm_durations[1:], melody_contour
                    ):
                        current_pitch = chosen_mode.scale_shift(
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
                        voice_measure = theory.FullVoiceMeasure.get(
                            pitch_sequence,
                            theory.MeasureBound(
                                melody_pack.left_rhythm_bound,
                                theory.SkipBound(left_skip_count),
                            ),
                            theory.MeasureBound(
                                melody_pack.right_rhythm_bound,
                                theory.SkipBound(right_skip_count),
                            ),
                            melody_pack.is_rhythm_continuous,
                            is_skip_continuous,
                        )
                        pitch_sequences[voice_name].append(voice_measure)

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

            for melody_pack in melody_packs:
                for melody_contour in melody_pack.melody_contours:
                    left_skip_count, right_skip_count = melody_pack.get_skip_counts(
                        melody_contour
                    )
                    is_skip_continuous = melody_pack.check_skip_continuity(
                        left_skip_count, right_skip_count, melody_contour
                    )
                    pitch_sequence = [
                        theory.SpecificNote(
                            starting_pitch, melody_pack.rhythm_durations[0]
                        )
                    ]
                    is_contour_relevant = is_first_pitch_flattened
                    is_previous_pitch_flattened = is_first_pitch_flattened
                    previous_pitch = starting_pitch

                    for rhythm_duration, vector in zip(
                        melody_pack.rhythm_durations[1:], melody_contour
                    ):
                        if is_previous_pitch_flattened and not (-3 <= vector <= 0):
                            break
                        current_pitch = chosen_mode.scale_shift(
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
                            voice_measure = theory.FullVoiceMeasure.get(
                                pitch_sequence,
                                theory.MeasureBound(
                                    melody_pack.left_rhythm_bound,
                                    theory.SkipBound(left_skip_count),
                                ),
                                theory.MeasureBound(
                                    melody_pack.right_rhythm_bound,
                                    theory.SkipBound(right_skip_count),
                                ),
                                melody_pack.is_rhythm_continuous,
                                is_skip_continuous,
                            )
                            pitch_sequences[voice_name].append(voice_measure)

    return pitch_sequences


def filter_voice_measures(
    all_full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    *chosen_modes: theory.ModalScale,
) -> dict[str, list[theory.FullVoiceMeasure]]:
    modified_full_voice_measures = defaultdict(list)
    allowed_fifth_endpoints = {str(chosen_mode[0]) for chosen_mode in chosen_modes}
    allowed_fourth_endpoints = {str(chosen_mode[4]) for chosen_mode in chosen_modes}
    allowed_fourth_endpoints |= allowed_fifth_endpoints

    for voice_name, voice_measures in all_full_voice_measures.items():
        for voice_measure in voice_measures:
            if len(voice_measure) == 2:
                first_pitch = voice_measure[0].specific_pitch
                second_pitch = voice_measure[1].specific_pitch
                voice_distance = theory.SpecificPitch.get_interval_distance(
                    first_pitch, second_pitch
                )
                current_pitch_endpoints = {
                    first_pitch.generic_pitch,
                    second_pitch.generic_pitch,
                }

                if voice_distance == 4:
                    if not current_pitch_endpoints & allowed_fifth_endpoints:
                        continue
                elif voice_distance == 3:
                    if not current_pitch_endpoints & allowed_fourth_endpoints:
                        continue
            modified_full_voice_measures[voice_name].append(voice_measure)

    return modified_full_voice_measures


HalfDuoTest = tuple[
    theory.SpecificPitch,
    theory.SpecificPitch,
    tuple[Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...],
    tuple[str, ...],
]


def get_half_measure_stacks(
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
) -> list[theory.VariantStack]:
    all_available_pitches = {}
    for voice_name, voice_tessitura in voice_tessituras.items():
        all_available_pitches[voice_name] = voice_tessitura.filter_pitches(
            chosen_mode.get_specific_iter()
        )

    half_measure_stacks: list[theory.VariantStack] = []
    half_duos_to_check: tuple[HalfDuoTest, ...]

    for bassus_pitch in all_available_pitches["bassus"]:
        bassus_measure = theory.HalfVoiceMeasure.get(bassus_pitch)
        for tenor_pitch in all_available_pitches["tenor"]:
            half_duos_to_check = (
                (
                    bassus_pitch,
                    tenor_pitch,
                    (pure.is_lowest_duo_good,),
                    pure.lower_voice_consonances,
                ),
            )
            if not are_half_duos_valid(half_duos_to_check):
                continue
            tenor_measure = theory.HalfVoiceMeasure.get(tenor_pitch)
            for contratenor_pitch in all_available_pitches["contratenor"]:
                half_duos_to_check = (
                    (
                        bassus_pitch,
                        contratenor_pitch,
                        tuple(),
                        pure.lower_voice_consonances,
                    ),
                    (
                        tenor_pitch,
                        contratenor_pitch,
                        (pure.is_upper_duo_good,),
                        pure.upper_voice_consonances,
                    ),
                )
                if not are_half_duos_valid(half_duos_to_check):
                    continue
                if not is_half_trio_valid(bassus_pitch, tenor_pitch, contratenor_pitch):
                    continue
                contratenor_measure = theory.HalfVoiceMeasure.get(contratenor_pitch)
                for superius_pitch in all_available_pitches["superius"]:
                    half_duos_to_check = (
                        (
                            bassus_pitch,
                            superius_pitch,
                            tuple(),
                            pure.lower_voice_consonances,
                        ),
                        (
                            tenor_pitch,
                            superius_pitch,
                            tuple(),
                            pure.upper_voice_consonances,
                        ),
                        (
                            contratenor_pitch,
                            superius_pitch,
                            (pure.is_upper_duo_good,),
                            pure.upper_voice_consonances,
                        ),
                    )
                    if not are_half_duos_valid(half_duos_to_check):
                        continue
                    if not is_half_trio_valid(
                        bassus_pitch, tenor_pitch, superius_pitch
                    ):
                        continue
                    if not is_half_trio_valid(
                        bassus_pitch, contratenor_pitch, superius_pitch
                    ):
                        continue
                    superius_measure = theory.HalfVoiceMeasure.get(superius_pitch)

                    half_measure_stack = theory.HalfMeasureStack.get(
                        bassus_measure,
                        tenor_measure,
                        contratenor_measure,
                        superius_measure,
                    )
                    half_measure_stacks.append(half_measure_stack)

    return half_measure_stacks


def filter_by_transition(
    index_prospects: list[theory.FullMeasureStack],
    reference_stack: theory.FullMeasureStack,
    chosen_mode: theory.ModalScale,
) -> list[theory.FullMeasureStack]:
    allowed_fifth_endpoints = {str(chosen_mode[0])}
    allowed_fourth_endpoints = {str(chosen_mode[0]), str(chosen_mode[4])}
    test_suite = (
        partial(
            rules.checked_solo_transition,
            flattened_pitch=chosen_mode.flattened_pitch,
        ),
        partial(rules.are_measure_stacks_unique),
        partial(rules.checked_dissonant_pass),
        partial(rules.checked_broken_parallels),
        partial(rules.checked_dotted_adjacent),
        partial(rules.checked_cross_measures),
        partial(rules.checked_quartet_transition),
        partial(
            rules.checked_endpoints,
            allowed_fifth_endpoints=allowed_fifth_endpoints,
            allowed_fourth_endpoints=allowed_fourth_endpoints,
        ),
        partial(
            rules.checked_duo_transition,
            allowed_downbeat_unison=True,
        ),
        partial(rules.checked_trio_transition),
    )

    filtered_prospects = []
    second_id = reference_stack.id
    for index_prospect in index_prospects:
        first_id = index_prospect.id
        if second_id in rules.absolute_failures[first_id]:
            continue
        for current_test in test_suite:
            if not current_test(index_prospect, reference_stack):
                break
        else:
            filtered_prospects.append(index_prospect)
    if not filtered_prospects:
        raise limits.CompositionError("Transition failed.")
    return filtered_prospects


DuoMeasureTest = tuple[
    theory.FullVoiceMeasure,
    theory.FullVoiceMeasure,
    tuple[Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...],
    tuple[str, ...],
]

regular_duo_successes: dict[int, set[int]] = defaultdict(set)
regular_duo_failures: dict[int, set[int]] = defaultdict(set)


def are_regular_duos_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        additional_tests,
        consonant_ids,
    ) in duo_measure_tests:
        lower_id, upper_id = lower_voice_measure.id, upper_voice_measure.id
        if upper_id in regular_duo_successes[lower_id]:
            continue
        if upper_id in regular_duo_failures[lower_id]:
            return False

        if checked_regular_duo(
            lower_voice_measure, upper_voice_measure, additional_tests, consonant_ids
        ):
            regular_duo_successes[lower_id].add(upper_id)
        else:
            regular_duo_failures[lower_id].add(upper_id)
            return False
    return True


def checked_regular_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    additional_tests: tuple[
        Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...
    ],
    consonant_ids: tuple[str, ...],
) -> bool:
    previous_lower_note = lower_voice_measure[0]
    previous_upper_note = upper_voice_measure[0]

    if not pure.is_duo_consonant(
        previous_lower_note.specific_pitch,
        previous_upper_note.specific_pitch,
        consonant_ids,
    ):
        return False

    elapsed_duration = Fraction("0")
    duo_iter = rules.get_note_duo(lower_voice_measure, upper_voice_measure)
    for current_lower_note, current_upper_note in duo_iter:
        for additional_test in additional_tests:
            if not additional_test(
                current_lower_note.specific_pitch,
                current_upper_note.specific_pitch,
            ):
                return False

        allowed_unison = (
            current_lower_note.specific_pitch == previous_lower_note.specific_pitch
            and current_upper_note.specific_pitch == previous_upper_note.specific_pitch
        )
        if elapsed_duration == Fraction("3/4"):
            attack_requires_consonance = not screen.is_dissonant_idiom(
                lower_voice_measure, upper_voice_measure
            )
        else:
            attack_requires_consonance = True
        if not pure.valid_regular_duo_motion(
            previous_lower_note,
            previous_upper_note,
            current_lower_note,
            current_upper_note,
            consonant_ids,
            attack_requires_consonance,
            allowed_unison,
        ):
            return False

        elapsed_duration += min(
            current_lower_note.duration, current_upper_note.duration
        )
        previous_lower_note = current_lower_note
        previous_upper_note = current_upper_note

    measure_validators = [
        screen.valid_quarter_parallels,
        screen.valid_diminished_duo,
        screen.valid_dotted_duo,
        screen.valid_broken_parallels,
        screen.valid_third_quarter_duo,
        screen.valid_agogic,
    ]
    for measure_validator in measure_validators:
        if not measure_validator(
            lower_voice_measure, upper_voice_measure, consonant_ids
        ):
            return False
    return True


idiom_duo_presences: dict[int, set[int]] = defaultdict(set)
idiom_duo_absences: dict[int, set[int]] = defaultdict(set)


def has_chanson_duo(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        _,
        consonant_ids,
    ) in duo_measure_tests:
        lower_id, upper_id = lower_voice_measure.id, upper_voice_measure.id
        if upper_id in idiom_duo_presences[lower_id]:
            return True
        if upper_id in idiom_duo_absences[lower_id]:
            continue

        if is_duo_idiom_present(
            lower_voice_measure, upper_voice_measure, consonant_ids
        ):
            idiom_duo_presences[lower_id].add(upper_id)
            return True
        idiom_duo_absences[lower_id].add(upper_id)
    return False


def is_duo_idiom_present(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    consonant_ids: tuple[str, ...],
) -> bool:
    lower_is_cantus = lower_voice_measure[-1].duration >= Fraction("1/2")
    upper_is_cantus = upper_voice_measure[-1].duration >= Fraction("1/2")

    if lower_is_cantus ^ upper_is_cantus:
        if lower_is_cantus:
            counter_measure = upper_voice_measure
        else:
            counter_measure = lower_voice_measure
        if len(counter_measure) != 4:
            return False

        if lower_is_cantus:
            lower_pitch = lower_voice_measure[-1].specific_pitch
            upper_pitch = counter_measure[2].specific_pitch
        else:
            lower_pitch = counter_measure[2].specific_pitch
            upper_pitch = upper_voice_measure[-1].specific_pitch
        if not pure.is_duo_consonant(lower_pitch, upper_pitch, consonant_ids):
            return pure.is_complete_descent(counter_measure)
    return False


def get_trio_id(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> str:
    lowest_id = lowest_voice_measure.id
    middle_id = middle_voice_measure.id
    highest_id = highest_voice_measure.id
    return f"{lowest_id}+{middle_id}+{highest_id}"


TrioMeasureTest = tuple[
    theory.FullVoiceMeasure, theory.FullVoiceMeasure, theory.FullVoiceMeasure
]

regular_trio_successes = set()
regular_trio_failures = set()


def are_regular_trios_valid(trio_measure_tests: tuple[TrioMeasureTest, ...]) -> bool:
    for (
        lowest_voice_measure,
        middle_voice_measure,
        highest_voice_measure,
    ) in trio_measure_tests:
        test_id = get_trio_id(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        )
        if test_id in regular_trio_successes:
            continue
        if test_id in regular_trio_failures:
            return False

        if checked_regular_trio(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        ):
            regular_trio_successes.add(test_id)
        else:
            regular_trio_failures.add(test_id)
            return False
    return True


def checked_regular_trio(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    trio_iter = get_note_trio(
        lowest_voice_measure, middle_voice_measure, highest_voice_measure
    )
    previous_lowest_pitch = lowest_voice_measure[0].specific_pitch
    previous_middle_pitch = middle_voice_measure[0].specific_pitch
    previous_highest_pitch = highest_voice_measure[0].specific_pitch

    if not pure.is_perfect_fourth_consonant(
        previous_lowest_pitch, previous_middle_pitch, previous_highest_pitch
    ):
        return False

    elapsed_duration = Fraction("0")
    for current_lowest_note, current_middle_note, current_highest_note in trio_iter:
        current_lowest_pitch = current_lowest_note.specific_pitch
        current_middle_pitch = current_middle_note.specific_pitch
        current_highest_pitch = current_highest_note.specific_pitch

        if elapsed_duration == Fraction("3/4"):
            attack_requires_consonance = not screen.is_dissonant_idiom(
                middle_voice_measure, highest_voice_measure
            )
        else:
            attack_requires_consonance = True

        if not pure.valid_regular_trio_motion(
            previous_lowest_pitch,
            previous_middle_pitch,
            previous_highest_pitch,
            current_lowest_pitch,
            current_middle_pitch,
            current_highest_pitch,
            attack_requires_consonance,
        ):
            return False

        elapsed_duration += min(
            current_lowest_note.duration,
            current_middle_note.duration,
            current_highest_note.duration,
        )
        previous_lowest_pitch = current_lowest_pitch
        previous_middle_pitch = current_middle_pitch
        previous_highest_pitch = current_highest_pitch

    measure_validators = [
        screen.valid_diminished_trio,
        screen.valid_dotted_trio,
        screen.valid_third_quarter_trio,
    ]
    for measure_validator in measure_validators:
        if not measure_validator(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        ):
            return False
    return True


idiom_trio_presences = set()
idiom_trio_absences = set()


def has_chanson_trio(trio_measure_tests: tuple[TrioMeasureTest, ...]) -> bool:
    for (
        lowest_voice_measure,
        middle_voice_measure,
        highest_voice_measure,
    ) in trio_measure_tests:
        test_id = get_trio_id(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        )
        if test_id in idiom_trio_presences:
            return True
        if test_id in idiom_trio_absences:
            continue

        if is_trio_idiom_present(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        ):
            idiom_trio_presences.add(test_id)
            return True
        idiom_trio_absences.add(test_id)
    return False


def is_trio_idiom_present(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    middle_is_cantus = middle_voice_measure[-1].duration >= Fraction("1/2")
    highest_is_cantus = highest_voice_measure[-1].duration >= Fraction("1/2")

    if middle_is_cantus ^ highest_is_cantus:
        if middle_is_cantus:
            counter_measure = highest_voice_measure
        else:
            counter_measure = middle_voice_measure
        if len(counter_measure) != 4:
            return False

        if middle_is_cantus:
            middle_pitch = middle_voice_measure[-1].specific_pitch
            highest_pitch = counter_measure[2].specific_pitch
        else:
            middle_pitch = counter_measure[2].specific_pitch
            highest_pitch = highest_voice_measure[-1].specific_pitch

        lowest_pitch = pure.find_pitch(lowest_voice_measure)
        if not pure.is_perfect_fourth_consonant(
            lowest_pitch, middle_pitch, highest_pitch
        ):
            return pure.is_complete_descent(counter_measure)
    return False


def are_half_duos_valid(half_duo_tests: tuple[HalfDuoTest, ...]) -> bool:
    for lower_pitch, upper_pitch, additional_tests, consonant_ids in half_duo_tests:
        if not pure.is_duo_consonant(lower_pitch, upper_pitch, consonant_ids):
            return False
        for additional_test in additional_tests:
            if not additional_test(lower_pitch, upper_pitch):
                return False
    return True


def is_half_trio_valid(
    lowest_pitch: theory.SpecificPitch,
    middle_pitch: theory.SpecificPitch,
    highest_pitch: theory.SpecificPitch,
) -> bool:
    return pure.is_perfect_fourth_consonant(lowest_pitch, middle_pitch, highest_pitch)


def get_note_trio(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> Iterator[tuple[theory.SpecificNote, theory.SpecificNote, theory.SpecificNote]]:
    lowest_voice_iter = iter(lowest_voice_measure)
    middle_voice_iter = iter(middle_voice_measure)
    highest_voice_iter = iter(highest_voice_measure)

    lowest_duration = Fraction("0")
    middle_duration = Fraction("0")
    highest_duration = Fraction("0")
    remaining_measure_duration = Fraction("1")

    while remaining_measure_duration:
        if not lowest_duration:
            lowest_note = next(lowest_voice_iter)
            lowest_duration = lowest_note.duration
        if not middle_duration:
            middle_note = next(middle_voice_iter)
            middle_duration = middle_note.duration
        if not highest_duration:
            highest_note = next(highest_voice_iter)
            highest_duration = highest_note.duration

        yield lowest_note, middle_note, highest_note

        intersect_duration = min(lowest_duration, middle_duration, highest_duration)
        lowest_duration -= intersect_duration
        middle_duration -= intersect_duration
        highest_duration -= intersect_duration
        remaining_measure_duration -= intersect_duration


def get_first_measure_stacks(
    full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    chosen_mode: theory.ModalScale,
    is_antecedent: bool,
) -> list[theory.FullMeasureStack]:
    first_sequences = defaultdict(list)

    first_degrees = idioms["first_degrees"]
    if is_antecedent:
        first_degrees["superius"] = [0]

    for voice_name, voice_measures in full_voice_measures.items():
        allowed_first_motions = set(idioms["first_motions"][voice_name])
        allowed_start_pitches = {
            str(chosen_mode[first_degree]) for first_degree in first_degrees[voice_name]
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
    full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
) -> list[theory.FullMeasureStack]:
    cadential_sequences = defaultdict(list)
    tonic_generic_pitch = chosen_mode[0]
    superius_tessitura = voice_tessituras["superius"]

    interval_shifts = [theory.Interval.get("m2")]
    if chosen_mode.scale_intervals[-1] == "m7":
        interval_shifts.append(theory.Interval.get("M2"))
    tonic_specific_pitches = superius_tessitura.find_equivalent_pitches(
        tonic_generic_pitch
    )

    half_duration = Fraction("1/2")
    superius_measure_bound = theory.MeasureBound(
        theory.RhythmBound(half_duration, 2), theory.SkipBound(0)
    )
    for interval_shift in interval_shifts:
        for tonic_specific_pitch in tonic_specific_pitches:
            cadence_pitch = tonic_specific_pitch - interval_shift
            if cadence_pitch in superius_tessitura:
                superius_measure = theory.FullVoiceMeasure.get(
                    [
                        theory.SpecificNote(tonic_specific_pitch, half_duration),
                        theory.SpecificNote(cadence_pitch, half_duration),
                    ],
                    superius_measure_bound,
                    superius_measure_bound,
                    True,
                    False,
                )
                cadential_sequences["superius"].append(superius_measure)

    for voice_name in lower_voice_names:
        cadential_sequences[voice_name] = [
            voice_measure
            for voice_measure in full_voice_measures[voice_name]
            if len(voice_measure) <= 2
        ]

    voice_measure_stacker = VoiceMeasureStacker(cadential_sequences)
    measure_stack_groups = next(iter(voice_measure_stacker))
    result_stacks = measure_stack_groups["no_whole_notes"]
    result_stacks.extend(measure_stack_groups["some_whole_notes"])

    half_cadence_cache[str(chosen_mode)] = result_stacks
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


class CadentialError(Exception):
    def __str__(self) -> str:
        return f"Authentic cadence failed: {self.args[0]}"


def set_final_prospects(
    sequence_prospects: limits.TwoDimensionStack,
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
    cadence_id: str,
    superius_ending_tessitura: theory.Tessitura,
    include_whole_notes: bool = True,
) -> None:
    penultimate_sequences = defaultdict(list)
    ultimate_sequences = defaultdict(list)

    modify_chordal_third = partial(
        create_picardy_third,
        chosen_mode.scale_intervals[2][0] == "m",
        chosen_mode[2].letter,
    )

    for voice_name, voice_formulae in idioms[cadence_id].items():
        voice_tessitura = voice_tessituras[voice_name]
        ultimate_formulas = set()
        penultimate_formulas = set()
        for voice_formula in voice_formulae:
            *penultimate_formula, ultimate_formula = voice_formula
            converted_formula = tuple(
                tuple(formula_part) for formula_part in penultimate_formula
            )
            penultimate_formulas.add(converted_formula)
            ultimate_formulas.add(tuple(ultimate_formula))

        for penultimate_formula in penultimate_formulas:
            voice_measures = get_penultimate_voice_measures(
                chosen_mode, penultimate_formula, voice_tessitura
            )
            penultimate_sequences[voice_name].extend(voice_measures)
        for ultimate_formula in ultimate_formulas:
            voice_measures = get_ultimate_voice_measures(
                chosen_mode, ultimate_formula, voice_tessitura, modify_chordal_third
            )
            ultimate_sequences[voice_name].extend(voice_measures)

    voice_measure_stacker = VoiceMeasureStacker(
        penultimate_sequences,
        are_cadential_duos_valid,
        are_cadential_trios_valid,
    )
    measure_stack_groups = next(iter(voice_measure_stacker))

    sequence_prospects[-2].extend(measure_stack_groups["no_whole_notes"])
    sequence_prospects[-2].extend(measure_stack_groups["some_whole_notes"])
    if include_whole_notes:
        sequence_prospects[-2].extend(measure_stack_groups["all_whole_notes"])

    voice_measure_stacker = VoiceMeasureStacker(ultimate_sequences)
    measure_stack_groups = next(iter(voice_measure_stacker))

    for index_prospect in measure_stack_groups["all_whole_notes"]:
        superius_ending_pitch = index_prospect[-1][-1].specific_pitch
        if superius_ending_pitch not in superius_ending_tessitura:
            continue
        sequence_prospects[-1].append(index_prospect)
    if not sequence_prospects[-1] and cadence_id == "final_cadances":
        raise CadentialError(
            "Not enough prospects.", str(chosen_mode), chosen_mode.type
        )


def get_penultimate_voice_measures(
    chosen_mode: theory.ModalScale,
    voice_formula: list[tuple[int, str]],
    voice_tessitura: theory.Tessitura,
) -> list[theory.FullVoiceMeasure]:
    previous_scale_degree = starting_scale_degree = voice_formula[0][0]
    starting_duration = revert_duration(voice_formula[0][1])
    pitch_sequences = []

    used_scale_degrees = [starting_scale_degree]
    rhythm_durations = [starting_duration]
    melody_contour = []

    for current_scale_degree, duration_repr in voice_formula[1:]:
        used_scale_degrees.append(current_scale_degree)
        rhythm_durations.append(revert_duration(duration_repr))
        current_vector = current_scale_degree - previous_scale_degree
        melody_contour.append(current_vector)
        previous_scale_degree = current_scale_degree

    melody_pack = theory.MelodyPack(rhythm_durations, [melody_contour])
    left_skip_count, right_skip_count = melody_pack.get_skip_counts(melody_contour)
    is_skip_continuous = melody_pack.check_skip_continuity(
        left_skip_count, right_skip_count, melody_contour
    )

    if (
        -1 in used_scale_degrees
        and chosen_mode.scale_intervals[-1][0] == "m"
        and chosen_mode.type != "phrygian"
    ):
        """the phrygian cadence uses a descending minor second in the tenorizan
        rather than the usual ascending minor second in the cantizan"""
        starting_generic_pitch = chosen_mode.get_cadential_pitch(starting_scale_degree)
        starting_specific_pitches = voice_tessitura.find_equivalent_pitches(
            starting_generic_pitch
        )
        pitch_shifter = chosen_mode.cadential_shift
    else:
        starting_generic_pitch = chosen_mode[starting_scale_degree]
        starting_specific_pitches = voice_tessitura.find_equivalent_pitches(
            starting_generic_pitch
        )
        pitch_shifter = chosen_mode.scale_shift

    for starting_specific_pitch in starting_specific_pitches:
        pitch_sequence = [
            theory.SpecificNote(starting_specific_pitch, starting_duration)
        ]
        previous_scale_degree = starting_scale_degree
        previous_specific_pitch = starting_specific_pitch

        for current_scale_degree, current_duration in zip(
            used_scale_degrees[1:], rhythm_durations[1:]
        ):
            current_specific_pitch = pitch_shifter(
                previous_specific_pitch, previous_scale_degree, current_scale_degree
            )
            if current_specific_pitch not in voice_tessitura:
                break

            pitch_sequence.append(
                theory.SpecificNote(current_specific_pitch, current_duration)
            )
            previous_scale_degree = current_scale_degree
            previous_specific_pitch = current_specific_pitch
        else:
            voice_measure = theory.FullVoiceMeasure.get(
                pitch_sequence,
                theory.MeasureBound(
                    melody_pack.left_rhythm_bound, theory.SkipBound(left_skip_count)
                ),
                theory.MeasureBound(
                    melody_pack.right_rhythm_bound,
                    theory.SkipBound(right_skip_count),
                ),
                melody_pack.is_rhythm_continuous,
                is_skip_continuous,
            )
            pitch_sequences.append(voice_measure)

    return pitch_sequences


ultimate_duration = Fraction("1")
whole_note_bound = theory.RhythmBound(Fraction("1"), 1)
no_skip_bound = theory.SkipBound(0)


def get_ultimate_voice_measures(
    chosen_mode: theory.ModalScale,
    voice_formula: tuple[int, str],
    voice_tessitura: theory.Tessitura,
    modify_chordal_third: partial[theory.SpecificNote],
) -> list[theory.FullVoiceMeasure]:
    diatonic_generic_pitch = chosen_mode[voice_formula[0]]
    starting_specific_pitches = voice_tessitura.find_equivalent_pitches(
        diatonic_generic_pitch
    )

    pitch_sequences = []
    for starting_specific_pitch in starting_specific_pitches:
        sole_note = theory.SpecificNote(starting_specific_pitch, ultimate_duration)
        corrected_voice_measure = theory.FullVoiceMeasure.get(
            [modify_chordal_third(sole_note)],
            theory.MeasureBound(whole_note_bound, no_skip_bound),
            theory.MeasureBound(whole_note_bound, no_skip_bound),
            True,
            True,
        )
        pitch_sequences.append(corrected_voice_measure)

    return pitch_sequences


cadential_duo_successes: dict[int, set[int]] = defaultdict(set)
cadential_duo_failures: dict[int, set[int]] = defaultdict(set)


def are_cadential_duos_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        additional_tests,
        consonant_ids,
    ) in duo_measure_tests:
        lower_id, upper_id = lower_voice_measure.id, upper_voice_measure.id
        if upper_id in cadential_duo_successes[lower_id]:
            continue
        if upper_id in cadential_duo_failures[lower_id]:
            return False

        if checked_cadential_duo(
            lower_voice_measure, upper_voice_measure, additional_tests, consonant_ids
        ):
            cadential_duo_successes[lower_id].add(upper_id)
        else:
            cadential_duo_failures[lower_id].add(upper_id)
            return False
    return True


def checked_cadential_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
    additional_tests: tuple[
        Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...
    ],
    consonant_ids: tuple[str, ...],
) -> bool:
    previous_lower_note = lower_voice_measure[0]
    previous_upper_note = upper_voice_measure[0]

    if not pure.is_duo_consonant(
        previous_lower_pitch := previous_lower_note.specific_pitch,
        previous_upper_pitch := previous_upper_note.specific_pitch,
        consonant_ids,
    ):
        lower_is_whole = pure.is_measure_whole(lower_voice_measure)
        upper_is_whole = pure.is_measure_whole(upper_voice_measure)
        if lower_is_whole ^ upper_is_whole:
            if lower_is_whole:
                if previous_lower_pitch.has_interval_shift(
                    previous_upper_pitch, ("m2",)
                ):
                    return False
                agent_measure = lower_voice_measure
                patient_measure = upper_voice_measure
            else:
                if previous_lower_pitch.has_interval_shift(
                    previous_upper_pitch, ("d5",)
                ):
                    return False
                agent_measure = upper_voice_measure
                patient_measure = lower_voice_measure
        else:
            return False

        if len(patient_measure) != 2:
            return False
        if patient_measure[0].duration != Fraction("1/2"):
            return False
        resolution_vector = theory.SpecificPitch.get_interval_vector(
            patient_measure[0].specific_pitch,
            patient_measure[1].specific_pitch,
        )
        if resolution_vector != -1:
            return False
        if not pure.is_duo_consonant(
            lower_voice_measure[-1].specific_pitch,
            upper_voice_measure[-1].specific_pitch,
            consonant_ids,
        ):
            return False

    elapsed_duration = Fraction("0")
    duo_iter = rules.get_note_duo(lower_voice_measure, upper_voice_measure)
    for current_lower_note, current_upper_note in duo_iter:
        for additional_test in additional_tests:
            if not additional_test(
                current_lower_note.specific_pitch,
                current_upper_note.specific_pitch,
            ):
                return False

        if elapsed_duration == Fraction("3/4"):
            attack_requires_consonance = not screen.is_dissonant_idiom(
                lower_voice_measure, upper_voice_measure
            )
        else:
            attack_requires_consonance = True
        if not pure.valid_cadential_duo_motion(
            previous_lower_note,
            previous_upper_note,
            current_lower_note,
            current_upper_note,
            consonant_ids,
            attack_requires_consonance,
        ):
            return False

        elapsed_duration += min(
            current_lower_note.duration, current_upper_note.duration
        )
        previous_lower_note = current_lower_note
        previous_upper_note = current_upper_note

    measure_validators = [
        screen.valid_quarter_parallels,
        screen.valid_diminished_duo,
        screen.valid_dotted_duo,
        screen.valid_broken_parallels,
        # valid_third_quarter_duo does not apply because of double neigbor cadence
    ]
    for measure_validator in measure_validators:
        if not measure_validator(
            lower_voice_measure, upper_voice_measure, consonant_ids
        ):
            return False
    return True


cadential_trio_successes = set()
cadential_trio_failures = set()


def are_cadential_trios_valid(trio_measure_tests: tuple[TrioMeasureTest, ...]) -> bool:
    for (
        lowest_voice_measure,
        middle_voice_measure,
        highest_voice_measure,
    ) in trio_measure_tests:
        test_id = get_trio_id(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        )
        if test_id in cadential_trio_successes:
            continue
        if test_id in cadential_trio_failures:
            return False

        if checked_cadential_trio(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        ):
            cadential_trio_successes.add(test_id)
        else:
            cadential_trio_failures.add(test_id)
            return False
    return True


def checked_cadential_trio(
    lowest_voice_measure: theory.FullVoiceMeasure,
    middle_voice_measure: theory.FullVoiceMeasure,
    highest_voice_measure: theory.FullVoiceMeasure,
) -> bool:
    trio_iter = get_note_trio(
        lowest_voice_measure, middle_voice_measure, highest_voice_measure
    )
    previous_lowest_pitch = lowest_voice_measure[0].specific_pitch
    previous_middle_pitch = middle_voice_measure[0].specific_pitch
    previous_highest_pitch = highest_voice_measure[0].specific_pitch

    if not pure.is_perfect_fourth_consonant(
        previous_lowest_pitch, previous_middle_pitch, previous_highest_pitch
    ):
        middle_is_whole = pure.is_measure_whole(middle_voice_measure)
        highest_is_whole = pure.is_measure_whole(highest_voice_measure)
        if middle_is_whole ^ highest_is_whole:
            if middle_is_whole:
                agent_measure = middle_voice_measure
                patient_measure = highest_voice_measure
            else:
                agent_measure = highest_voice_measure
                patient_measure = middle_voice_measure
        else:
            return False

        if len(patient_measure) != 2:
            return False
        if patient_measure[0].duration != Fraction("1/2"):
            return False
        resolution_vector = theory.SpecificPitch.get_interval_vector(
            patient_measure[0].specific_pitch,
            patient_measure[1].specific_pitch,
        )
        if resolution_vector != -1:
            return False
        if not pure.is_duo_consonant(
            middle_voice_measure[-1].specific_pitch,
            highest_voice_measure[-1].specific_pitch,
            pure.lower_voice_consonances,
        ):
            return False

    elapsed_duration = Fraction("0")
    for current_lowest_note, current_middle_note, current_highest_note in trio_iter:
        current_lowest_pitch = current_lowest_note.specific_pitch
        current_middle_pitch = current_middle_note.specific_pitch
        current_highest_pitch = current_highest_note.specific_pitch

        if elapsed_duration == Fraction("3/4"):
            attack_requires_consonance = not screen.is_dissonant_idiom(
                middle_voice_measure, highest_voice_measure
            )
        else:
            attack_requires_consonance = True
        if attack_requires_consonance and not pure.valid_cadential_trio_motion(
            previous_lowest_pitch,
            previous_middle_pitch,
            previous_highest_pitch,
            current_lowest_pitch,
            current_middle_pitch,
            current_highest_pitch,
        ):
            return False

        elapsed_duration += min(
            current_lowest_note.duration,
            current_middle_note.duration,
            current_highest_note.duration,
        )
        previous_lowest_pitch = current_lowest_pitch
        previous_middle_pitch = current_middle_pitch
        previous_highest_pitch = current_highest_pitch

    measure_validators = [
        screen.valid_diminished_trio,
        screen.valid_dotted_trio,
        # valid_third_quarter_trio does not apply because of double neigbor cadence
    ]
    for measure_validator in measure_validators:
        if not measure_validator(
            lowest_voice_measure, middle_voice_measure, highest_voice_measure
        ):
            return False
    return True


def fill_prospects(
    sequence_prospects: limits.TwoDimensionStack,
    measure_stack_groups: dict[str, list[theory.FullMeasureStack]],
    stack_map: dict[str, list[int]],
) -> None:
    for group_key, prospect_indices in stack_map.items():
        for measure_stack in measure_stack_groups[group_key]:
            for prospect_index in prospect_indices:
                sequence_prospects[prospect_index].append(measure_stack)


quartet_tests: dict[str, bool] = {}


def is_quartet_valid(
    bassus_measure: theory.FullVoiceMeasure,
    tenor_measure: theory.FullVoiceMeasure,
    contratenor_measure: theory.FullVoiceMeasure,
    superius_measure: theory.FullVoiceMeasure,
) -> bool:
    measure_quartet = (
        bassus_measure,
        tenor_measure,
        contratenor_measure,
        superius_measure,
    )
    test_id = "+".join(str(voice_measure.id) for voice_measure in measure_quartet)
    if test_id in quartet_tests:
        return quartet_tests[test_id]

    measure_validators = [
        screen.valid_diminished_fourth_species,
        screen.valid_regular_fourth_species,
        screen.valid_quartet_motion,
    ]
    for measure_validator in measure_validators:
        if not measure_validator(measure_quartet):
            quartet_tests[test_id] = False
            return False
    quartet_tests[test_id] = True
    return True


DuoValidator = Callable[[tuple[DuoMeasureTest, ...]], bool]
TrioValidator = Callable[[tuple[TrioMeasureTest, ...]], bool]


@dataclass
class VoiceMeasureStacker:
    pitch_sequences: dict[str, list[theory.FullVoiceMeasure]]
    are_duos_valid: DuoValidator = are_regular_duos_valid
    are_trios_valid: TrioValidator = are_regular_trios_valid
    result_min_count: int = 7_000
    result_filter_threshold: int = 4_000
    allow_chanson_idiom: bool = False

    def __post_init__(self) -> None:
        self.bassus_measures = self.pitch_sequences["bassus"]
        self.tenor_measures = self.pitch_sequences["tenor"]
        self.contratenor_measures = self.pitch_sequences["contratenor"]
        self.superius_measures = self.pitch_sequences["superius"]

    def __iter__(self) -> Iterator[dict[str, list[theory.FullMeasureStack]]]:
        random.shuffle(self.bassus_measures)
        sub_iters = []
        for bassus_measure in self.bassus_measures:
            sub_iters.append(
                self.get_measure_stacks(
                    [bassus_measure],
                )
            )

        valid_result_count = 0
        total_result_count = 0
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

            total_result_count += 1
            if whole_note_count == 0:
                measure_stack_groups["no_whole_notes"].append(current_measure_stack)
                valid_result_count += 1
                if valid_result_count == self.result_min_count:
                    yield measure_stack_groups
                    valid_result_count = 0
                    total_result_count = 0
                    measure_stack_groups.clear()
            elif total_result_count < self.result_filter_threshold:
                if whole_note_count == 4:
                    measure_stack_groups["all_whole_notes"].append(
                        current_measure_stack
                    )
                else:
                    measure_stack_groups["some_whole_notes"].append(
                        current_measure_stack
                    )
            sample_index += 1

        yield measure_stack_groups

    @staticmethod
    def count_whole_notes(measure_stack: theory.FullMeasureStack) -> int:
        return sum(1 for voice_measure in measure_stack if len(voice_measure) == 1)

    @staticmethod
    def shuffle_iter(
        voice_measures: list[theory.FullVoiceMeasure],
    ) -> Iterator[theory.FullVoiceMeasure]:
        measure_indices = list(range(len(voice_measures)))
        random.shuffle(measure_indices)
        for measure_index in measure_indices:
            yield voice_measures[measure_index]

    def get_measure_stacks(
        self,
        bassus_measures: list[theory.FullVoiceMeasure],
    ) -> Iterator[theory.FullMeasureStack]:
        duos_to_check: tuple[DuoMeasureTest, ...]
        trios_to_check: tuple[TrioMeasureTest, ...]
        for bassus_measure in self.shuffle_iter(bassus_measures):
            for tenor_measure in self.shuffle_iter(self.tenor_measures):
                duos_to_check = (
                    (
                        bassus_measure,
                        tenor_measure,
                        (pure.is_lowest_duo_good,),
                        pure.lower_voice_consonances,
                    ),
                )
                if not self.are_duos_valid(duos_to_check):
                    continue
                if not self.allow_chanson_idiom and has_chanson_duo(duos_to_check):
                    continue
                for contratenor_measure in self.shuffle_iter(self.contratenor_measures):
                    duos_to_check = (
                        (
                            bassus_measure,
                            contratenor_measure,
                            tuple(),
                            pure.lower_voice_consonances,
                        ),
                        (
                            tenor_measure,
                            contratenor_measure,
                            (pure.is_upper_duo_good,),
                            pure.upper_voice_consonances,
                        ),
                    )
                    if not self.are_duos_valid(duos_to_check):
                        continue
                    if not self.allow_chanson_idiom and has_chanson_duo(duos_to_check):
                        continue
                    trios_to_check = (
                        (bassus_measure, tenor_measure, contratenor_measure),
                    )
                    if not self.are_trios_valid(trios_to_check):
                        continue
                    if not self.allow_chanson_idiom and has_chanson_trio(
                        trios_to_check
                    ):
                        continue
                    for superius_measure in self.shuffle_iter(self.superius_measures):
                        duos_to_check = (
                            (
                                bassus_measure,
                                superius_measure,
                                tuple(),
                                pure.lower_voice_consonances,
                            ),
                            (
                                tenor_measure,
                                superius_measure,
                                tuple(),
                                pure.upper_voice_consonances,
                            ),
                            (
                                contratenor_measure,
                                superius_measure,
                                (pure.is_upper_duo_good,),
                                pure.upper_voice_consonances,
                            ),
                        )
                        if not self.are_duos_valid(duos_to_check):
                            continue
                        if not self.allow_chanson_idiom and has_chanson_duo(
                            duos_to_check
                        ):
                            continue
                        trios_to_check = (
                            (bassus_measure, tenor_measure, superius_measure),
                            (bassus_measure, contratenor_measure, superius_measure),
                        )
                        if not self.are_trios_valid(trios_to_check):
                            continue
                        if not self.allow_chanson_idiom and has_chanson_trio(
                            trios_to_check
                        ):
                            continue
                        if all(
                            screen.get_dotted_status(
                                tenor_measure, contratenor_measure, superius_measure
                            )
                        ):
                            continue
                        if not is_quartet_valid(
                            bassus_measure,
                            tenor_measure,
                            contratenor_measure,
                            superius_measure,
                        ):
                            continue
                        possible_measure_stack = theory.FullMeasureStack.get(
                            bassus_measure,
                            tenor_measure,
                            contratenor_measure,
                            superius_measure,
                        )
                        yield possible_measure_stack
