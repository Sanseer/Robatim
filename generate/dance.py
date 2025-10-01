from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from functools import partial
import random
from typing import Any, Callable, Iterator, Literal

from generate import export, limits, pure, rules, screen, source, theory

idioms = source.idioms
revert_duration = export.LilypondFactory.revert_duration


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
        for melody_pack in melody_packs:
            for melody_contour in melody_pack.melody_contours:
                left_skip_count, right_skip_count = melody_pack.get_skip_counts(
                    melody_contour
                )
                is_skip_continuous = melody_pack.check_skip_continuity(
                    left_skip_count, right_skip_count, melody_contour
                )
                for starting_pitch in available_pitches:
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
                        if (
                            vector in concerning_vectors
                            and previous_pitch.has_interval_shift(
                                current_pitch, ("A4", "d5")
                            )
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
                        if (
                            vector in concerning_vectors
                            and previous_pitch.has_interval_shift(
                                current_pitch, ("A4", "d5")
                            )
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


SequenceEnding = Literal[
    "final_cadences",
    "intermediate_cadences",
    "mixed_cadences",
    "forward_antecedent",
    "backward_antecedent",
]


@dataclass
class PartialConfig:
    ending: SequenceEnding
    mode_shift: int = 0
    no_whole_notes: list[int] = field(default_factory=list)
    some_whole_notes: list[int] = field(default_factory=list)
    all_whole_notes: list[int] = field(default_factory=list)
    duplicate: dict[str, Any] | None = None
    is_section_start: bool = False


def get_config_sections(dance_name: str) -> list[list[PartialConfig]]:
    config_sections = []
    for partial_spec in random.choice(idioms["form"][dance_name]):
        partial_config = PartialConfig(**partial_spec)
        if partial_config.is_section_start:
            config_sections.append([partial_config])
        else:
            config_sections[-1].append(partial_config)
    return config_sections


@dataclass
class GlobalSpec:
    dance_name: str
    clef_group: list[str]
    voice_tessituras: dict[str, theory.Tessitura]
    all_full_voice_measures: dict[str, list[theory.FullVoiceMeasure]]
    dance_type: type[limits.SequencePartial] = field(init=False)
    final_ending_tessitura: theory.Tessitura = field(init=False)
    sequence_builders = {
        "BasseDanse": limits.BasseDansePartial,
        "BranleSimple": limits.BranleSimplePartial,
        "BranleGaySemel": limits.BranleGaySemelPartial,
    }

    def __post_init__(self) -> None:
        self.dance_type = self.sequence_builders[self.dance_name]
        min_ending_pitch = theory.SpecificPitch("C0")
        max_ending_pitch = theory.SpecificPitch(
            idioms["final_max_superius_pitch"][self.clef_group[-1]]
        )
        self.final_ending_tessitura = theory.Tessitura(
            min_ending_pitch, max_ending_pitch
        )

    @property
    def top_clef(self) -> str:
        return self.clef_group[-1]


@dataclass
class DuplicateMarker:
    global_index: int = 0
    local_indices: list[int] = field(default_factory=list)


class SolutionSpec:
    def __init__(
        self,
        primary_mode: theory.ModalScale,
        config_sections: list[list[PartialConfig]],
    ) -> None:
        self.primary_mode = primary_mode
        second_mode = primary_mode.random_mode_shift()
        third_mode = second_mode.random_mode_shift()
        all_modes = (primary_mode, second_mode, third_mode)

        self.result: list[limits.TwoDimensionStack] = []
        self.sections = []
        null_marker = DuplicateMarker()
        accumulated_modes: list[theory.ModalScale]

        for section_index, config_section in enumerate(config_sections):
            self.result.append([])
            sequence_specs = []
            accumulated_modes = []

            for sequence_index, sequence_config in enumerate(config_section):
                current_mode = all_modes[sequence_config.mode_shift]
                current_modes = [current_mode]
                for accumulated_mode in accumulated_modes:
                    if accumulated_mode != current_mode:
                        current_modes.append(accumulated_mode)
                if current_mode not in accumulated_modes:
                    accumulated_modes.append(current_mode)

                sequence_rhythms = defaultdict(set)
                for partial_index in sequence_config.no_whole_notes:
                    sequence_rhythms[partial_index].add("no_whole_notes")
                for partial_index in sequence_config.some_whole_notes:
                    sequence_rhythms[partial_index].add("some_whole_notes")
                for partial_index in sequence_config.all_whole_notes:
                    sequence_rhythms[partial_index].add("all_whole_notes")

                if sequence_config.duplicate is None:
                    duplicate_marker = null_marker
                else:
                    duplicate_marker = DuplicateMarker(**sequence_config.duplicate)

                self.result[-1].append([])
                sequence_specs.append(
                    SequenceSpec(
                        section_index,
                        sequence_index,
                        current_modes,
                        sequence_rhythms,
                        sequence_config.ending,
                        duplicate_marker,
                    )
                )
            self.sections.append(
                SectionSpec(section_index, sequence_specs, accumulated_modes)
            )

    def __getitem__(self, index: int) -> SectionSpec:
        return self.sections[index]

    def get_superius_duplicate(
        self, global_index: int, local_index: int
    ) -> theory.BaseVoiceMeasure:
        flattened_index = 0
        for section_result in self.result:
            for sequence_result in section_result:
                if flattened_index == global_index:
                    return sequence_result[local_index][-1]
                flattened_index += 1
        raise IndexError


class SectionSpec:
    def __init__(
        self,
        index: int,
        display_order: list[SequenceSpec],
        modes: list[theory.ModalScale],
    ) -> None:
        self.display_order = display_order
        self.solve_order = display_order
        self.modes = modes

        if len(display_order) == 2:
            first_spec, second_spec = display_order
            solve_in_reverse = (
                "antecedent" in first_spec.ending
                or second_spec.ending == "final_cadences"
                or ("cadences" in second_spec.ending and index == 0)
            )
            if solve_in_reverse:
                self.solve_order = self.solve_order[::-1]

    def __getitem__(self, index: int) -> SequenceSpec:
        return self.display_order[index]

    def __len__(self) -> int:
        return len(self.display_order)


class ImpossibleError(Exception):
    def __str__(self) -> str:
        return f"Solution not possible: {self.args[0]}"


def filter_duplicates(
    all_voice_measures: list[theory.FullVoiceMeasure],
    reference_measure: theory.BaseVoiceMeasure,
    partial_match: bool = False,
) -> list[theory.FullVoiceMeasure]:
    if partial_match:
        reference_starting_pitch = reference_measure[0].specific_pitch
        filtered_voice_measures = [
            voice_measure
            for voice_measure in all_voice_measures
            if voice_measure[0].specific_pitch == reference_starting_pitch
        ]
    else:
        filtered_voice_measures = [
            voice_measure
            for voice_measure in all_voice_measures
            if voice_measure == reference_measure
        ]
    return filtered_voice_measures


HalfDuoTest = tuple[
    theory.SpecificPitch,
    theory.SpecificPitch,
    tuple[Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...],
    tuple[str, ...],
]


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


def get_basse_danse_start(
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
) -> list[theory.VariantStack]:
    all_available_pitches = {}
    for voice_name, voice_tessitura in voice_tessituras.items():
        all_available_pitches[voice_name] = voice_tessitura.filter_pitches(
            chosen_mode.get_specific_iter()
        )
    first_stacks: list[theory.VariantStack] = []
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
                    first_stacks.append(half_measure_stack)
    return first_stacks


def get_branle_simple_start(
    full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    chosen_modes: list[theory.ModalScale],
    section_start_is_antecedent: bool,
    current_superius_duplicate: theory.BaseVoiceMeasure | None,
) -> list[theory.VariantStack]:
    first_sequences = defaultdict(list)
    for voice_name, voice_measures in full_voice_measures.items():
        if voice_name == "superius":
            if current_superius_duplicate is not None:
                for voice_measure in filter_duplicates(
                    voice_measures,
                    current_superius_duplicate,
                ):
                    if len(voice_measure) != 1:
                        first_sequences[voice_name].append(voice_measure)
                continue
            if section_start_is_antecedent:
                allowed_start_degrees = [0]
            else:
                allowed_start_degrees = idioms["first_degrees"][voice_name]
        else:
            allowed_start_degrees = idioms["first_degrees"][voice_name]

        allowed_first_motions = set(idioms["first_motions"][voice_name])
        allowed_start_pitches = {
            str(chosen_mode[start_degree])
            for chosen_mode in chosen_modes
            for start_degree in allowed_start_degrees
        }
        for voice_measure in voice_measures:
            if len(voice_measure) == 1:
                continue
            if voice_measure[0].duration == Fraction("3/4"):
                continue
            first_specific_pitch = voice_measure[0].specific_pitch
            if first_specific_pitch.generic_pitch not in allowed_start_pitches:
                continue

            second_specific_pitch = voice_measure[1].specific_pitch
            interval_vector = theory.SpecificPitch.get_interval_vector(
                first_specific_pitch, second_specific_pitch
            )
            if interval_vector in allowed_first_motions:
                first_sequences[voice_name].append(voice_measure)
    voice_measure_stacker = VoiceMeasureStacker(first_sequences, {"no_whole_notes"})
    return next(iter(voice_measure_stacker))


first_motions = {
    "bassus": {-3, 3, -1, 1, 0},
    "tenor": {-2, 2, -1, 1, 0},
    "contratenor": {-2, 2, -1, 1, 0},
    "superius": {-2, -1, 1, 0},
}


def get_branle_gay_start(
    full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    chosen_modes: list[theory.ModalScale],
    allowed_rhythms: set[str],
    current_superius_duplicate: theory.BaseVoiceMeasure | None,
) -> list[theory.VariantStack]:
    first_sequences = defaultdict(list)
    for voice_name, voice_measures in full_voice_measures.items():
        if voice_name == "superius" and current_superius_duplicate is not None:
            first_sequences[voice_name] = filter_duplicates(
                voice_measures,
                current_superius_duplicate,
            )
        else:
            allowed_start_degrees = idioms["first_degrees"][voice_name]
            allowed_start_pitches = {
                str(chosen_mode[start_degree])
                for chosen_mode in chosen_modes
                for start_degree in allowed_start_degrees
            }
            for voice_measure in voice_measures:
                if len(voice_measure) > 2 and voice_name != "superius":
                    continue
                if voice_measure[0].duration == Fraction("3/4"):
                    continue

                first_specific_pitch = voice_measure[0].specific_pitch
                if first_specific_pitch.generic_pitch not in allowed_start_pitches:
                    continue
                if len(voice_measure) > 1:
                    second_specific_pitch = voice_measure[1].specific_pitch
                    interval_vector = theory.SpecificPitch.get_interval_vector(
                        first_specific_pitch, second_specific_pitch
                    )
                    if interval_vector not in first_motions[voice_name]:
                        continue
                first_sequences[voice_name].append(voice_measure)
    voice_measure_stacker = VoiceMeasureStacker(first_sequences, allowed_rhythms)
    return next(iter(voice_measure_stacker))


def get_antecedent_ending(
    current_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    chosen_mode: theory.ModalScale,
    voice_tessituras: dict[str, theory.Tessitura],
    is_backward: bool,
    reference_stack: theory.VariantStack,
) -> list[theory.VariantStack]:
    last_sequences = defaultdict(list)
    tonic_generic_pitch = chosen_mode[0]
    flattened_pitch = chosen_mode.flattened_pitch
    superius_tessitura = voice_tessituras["superius"]

    interval_shifts = [theory.Interval.get("m2")]
    if chosen_mode.scale_intervals[-1] == "m7":
        interval_shifts.append(theory.Interval.get("M2"))
    tonic_specific_pitches = superius_tessitura.find_equivalent_pitches(
        tonic_generic_pitch
    )

    superius_measure_bound = theory.MeasureBound(
        theory.RhythmBound(theory.half_duration, 2), theory.SkipBound(0)
    )
    voice_can_transition = partial(
        rules.checked_solo_motion,
        second_voice_measure=reference_stack[-1],
        flattened_pitch=flattened_pitch,
    )
    for interval_shift in interval_shifts:
        for tonic_specific_pitch in tonic_specific_pitches:
            cadence_pitch = tonic_specific_pitch - interval_shift
            if cadence_pitch not in superius_tessitura:
                continue
            measure_sequence = [
                theory.SpecificNote(tonic_specific_pitch, theory.half_duration),
                theory.SpecificNote(cadence_pitch, theory.half_duration),
            ]
            if is_backward:
                measure_sequence = measure_sequence[::-1]
            superius_measure = theory.FullVoiceMeasure.get(
                measure_sequence,
                superius_measure_bound,
                superius_measure_bound,
                True,
                False,
            )
            if voice_can_transition(superius_measure):
                last_sequences["superius"].append(superius_measure)

    lower_voice_vectors = {
        "bassus": {0, -1, -3, -4},
        "tenor": {0, -1, 1},
        "contratenor": {0, -1, 1},
    }
    for voice_index, (voice_name, allowed_vectors) in enumerate(
        lower_voice_vectors.items()
    ):
        voice_can_transition = partial(
            rules.checked_solo_motion,
            second_voice_measure=reference_stack[voice_index],
            flattened_pitch=flattened_pitch,
        )
        for voice_measure in current_voice_measures[voice_name]:
            if len(voice_measure) > 2:
                continue

            first_pitch = voice_measure[0].specific_pitch
            second_pitch = voice_measure[-1].specific_pitch
            current_vector = theory.SpecificPitch.get_interval_vector(
                first_pitch, second_pitch
            )
            if current_vector not in allowed_vectors:
                continue
            if voice_can_transition(voice_measure):
                last_sequences[voice_name].append(voice_measure)
    voice_measure_stacker = VoiceMeasureStacker(
        last_sequences, {"no_whole_notes", "some_whole_notes"}
    )
    return next(iter(voice_measure_stacker))


def get_penultimate_voice_measures(
    chosen_mode: theory.ModalScale,
    voice_formula: tuple[tuple[int, str], ...],
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
whole_note_bound = theory.MeasureBound(
    theory.RhythmBound(ultimate_duration, 1), theory.SkipBound(0)
)


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
            whole_note_bound,
            whole_note_bound,
            True,
            True,
        )
        pitch_sequences.append(corrected_voice_measure)
    return pitch_sequences


def filter_transition(
    prospect_stacks: list[theory.VariantStack],
    reference_stack: theory.VariantStack,
    chosen_modes: list[theory.ModalScale],
) -> list[theory.VariantStack]:
    allowed_fifth_endpoints = {str(chosen_mode[0]) for chosen_mode in chosen_modes}
    allowed_fourth_endpoints = {str(chosen_mode[4]) for chosen_mode in chosen_modes}
    allowed_fourth_endpoints |= allowed_fifth_endpoints
    test_suite = (
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
    for prospect_stack in prospect_stacks:
        first_id = prospect_stack.id
        if second_id in rules.absolute_failures[first_id]:
            continue
        for current_test in test_suite:
            if not current_test(prospect_stack, reference_stack):
                break
        else:
            filtered_prospects.append(prospect_stack)
    if not filtered_prospects:
        raise limits.CompositionError("Transition failed.")
    return filtered_prospects


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


@dataclass
class SequenceSpec:
    section_index: int
    sequence_index: int
    modes: list[theory.ModalScale]
    rhythms: defaultdict[int, set[str]]
    ending: SequenceEnding
    duplicate: DuplicateMarker

    def __post_init__(self) -> None:
        if "cadences" in self.ending:
            self.realize_prospects = self.solve_cadence
        elif "antecedent" in self.ending:
            self.realize_prospects = self.solve_antecedent
        else:
            raise ValueError
        self.sequence_prospects: limits.TwoDimensionStack
        self.unfilled_prospect_indices: set[int]
        self.unfilled_duplicate_indices: set[int]

    @property
    def mode(self) -> theory.ModalScale:
        return self.modes[0]

    def setup_solution(
        self, global_spec: GlobalSpec, solution_spec: SolutionSpec
    ) -> SectionSpec:
        self.sequence_prospects = [[] for _ in range(6)]
        self.unfilled_prospect_indices = set(range(6))
        self.unfilled_duplicate_indices = set(self.duplicate.local_indices)
        section_spec = solution_spec[self.section_index]

        section_start_is_antecedent = "antecedent" in section_spec[0].ending
        if 0 in self.unfilled_duplicate_indices:
            current_superius_duplicate = solution_spec.get_superius_duplicate(
                self.duplicate.global_index, 0
            )
        else:
            current_superius_duplicate = None

        if global_spec.dance_name == "BasseDanse":
            self.sequence_prospects[0] = get_basse_danse_start(
                self.mode, global_spec.voice_tessituras
            )
            self.unfilled_prospect_indices.remove(0)
        elif global_spec.dance_name == "BranleGaySemel":
            if section_start_is_antecedent:
                starting_modes = [section_spec.modes[0]]
            else:
                starting_modes = section_spec.modes[:]
                if solution_spec.primary_mode not in starting_modes:
                    starting_modes.append(solution_spec.primary_mode)
            self.sequence_prospects[0] = get_branle_gay_start(
                global_spec.all_full_voice_measures,
                starting_modes,
                self.rhythms[0],
                current_superius_duplicate,
            )
            if current_superius_duplicate is not None:
                self.unfilled_duplicate_indices.remove(0)
            self.unfilled_prospect_indices.remove(0)
        elif (
            global_spec.dance_name == "BranleSimple"
            and "some_whole_notes" not in self.rhythms[0]
        ):
            starting_modes = section_spec.modes[:]
            if solution_spec.primary_mode not in starting_modes:
                starting_modes.append(solution_spec.primary_mode)
            self.sequence_prospects[0] = get_branle_simple_start(
                global_spec.all_full_voice_measures,
                starting_modes,
                section_start_is_antecedent,
                current_superius_duplicate,
            )
            if current_superius_duplicate is not None:
                self.unfilled_duplicate_indices.remove(0)
            self.unfilled_prospect_indices.remove(0)
        return section_spec

    def solve(
        self, global_spec: GlobalSpec, solution_spec: SolutionSpec
    ) -> Iterator[bool]:
        print(f"Solving {self.ending} with {self.mode} {self.mode.type}")
        section_spec = self.setup_solution(global_spec, solution_spec)
        try:
            self.realize_prospects(global_spec, solution_spec, section_spec)
            self.print_prospect_counts()
            dance_partial = global_spec.dance_type(
                self.sequence_prospects,
                self.modes,
                "antecedent" in self.ending,
                self.sequence_index != len(section_spec) - 1,
            )
            solution_iter = dance_partial.realize()
            for measure_sequence in solution_iter:
                section_result = solution_spec.result[self.section_index]
                section_result[self.sequence_index] = measure_sequence
                yield True
        except limits.CompositionError as err:
            print(f"{err} Backtracking to previous sequence.")
            return

    def print_prospect_counts(self) -> None:
        prospect_counts = [
            len(prospect_stacks) for prospect_stacks in self.sequence_prospects
        ]
        print(f"Allocated available measures: {prospect_counts}")

    def filter_voice_measures(
        self,
        all_full_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
    ) -> dict[str, list[theory.FullVoiceMeasure]]:
        modified_full_voice_measures = defaultdict(list)
        allowed_fifth_endpoints = {str(mode[0]) for mode in self.modes}
        allowed_fourth_endpoints = {str(mode[4]) for mode in self.modes}
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

    def solve_antecedent(
        self,
        global_spec: GlobalSpec,
        solution_spec: SolutionSpec,
        section_spec: SectionSpec,
    ) -> None:
        allowed_voice_measures = self.filter_voice_measures(
            global_spec.all_full_voice_measures
        )
        reference_stack = solution_spec.result[self.section_index][1][0]
        self.sequence_prospects[5] = get_antecedent_ending(
            allowed_voice_measures,
            self.mode,
            global_spec.voice_tessituras,
            is_backward := "backward" in self.ending,
            reference_stack,
        )
        if is_backward:
            filtered_prospects = self.sequence_prospects[5]
        else:
            reference_tonic_pitch = reference_stack[-1][0].specific_pitch
            filtered_prospects = []
            for prospect_stack in self.sequence_prospects[5]:
                current_superius_pitch = prospect_stack[-1][0].specific_pitch
                if current_superius_pitch == reference_tonic_pitch:
                    filtered_prospects.append(prospect_stack)

        self.sequence_prospects[5] = filter_transition(
            filtered_prospects, reference_stack, section_spec.modes
        )
        self.unfilled_prospect_indices.remove(5)
        self.fill_remaining_prospects(
            allowed_voice_measures,
            solution_spec,
        )

    def solve_cadence(
        self,
        global_spec: GlobalSpec,
        solution_spec: SolutionSpec,
        section_spec: SectionSpec,
    ) -> None:
        if self.section_index == 0:
            if self.sequence_index == len(section_spec) - 1:
                final_ending_tessitura = global_spec.final_ending_tessitura
            else:
                reference_stack = solution_spec.result[self.section_index][1][-1]
                min_ending_pitch = reference_stack[-1][-1].specific_pitch
                max_ending_pitch = theory.SpecificPitch(
                    idioms["intermediate_max_superius_pitch"][global_spec.top_clef]
                )
                final_ending_tessitura = theory.Tessitura(
                    min_ending_pitch, max_ending_pitch
                )
        else:
            min_ending_pitch = theory.SpecificPitch("C0")
            max_ending_pitch = theory.SpecificPitch(
                idioms["intermediate_max_superius_pitch"][global_spec.top_clef]
            )
            final_ending_tessitura = theory.Tessitura(
                min_ending_pitch, max_ending_pitch
            )

        if 4 in self.unfilled_duplicate_indices:
            current_superius_duplicate = solution_spec.get_superius_duplicate(
                self.duplicate.global_index, 4
            )
            self.unfilled_duplicate_indices.remove(4)
        else:
            current_superius_duplicate = None
        self.fill_cadential_prospects(
            global_spec.voice_tessituras,
            final_ending_tessitura,
            current_superius_duplicate,
        )
        self.unfilled_prospect_indices -= {4, 5}

        allowed_voice_measures = self.filter_voice_measures(
            global_spec.all_full_voice_measures
        )
        self.fill_remaining_prospects(
            allowed_voice_measures,
            solution_spec,
        )

    def fill_cadential_prospects(
        self,
        voice_tessituras: dict[str, theory.Tessitura],
        superius_ending_tessitura: theory.Tessitura,
        penultimate_superius_duplicate: theory.BaseVoiceMeasure | None,
    ) -> None:
        cadence_type = self.ending
        penultimate_sequences = defaultdict(list)
        ultimate_sequences = defaultdict(list)
        mediant_pitch_letter = self.mode[2].letter

        modify_chordal_third = partial(
            create_picardy_third,
            self.mode.scale_intervals[2][0] == "m",
            mediant_pitch_letter,
        )
        penultimate_rhythms = self.rhythms[4]
        for voice_name, voice_formulas in idioms[cadence_type].items():
            voice_tessitura = voice_tessituras[voice_name]
            penultimate_formulas = set()
            ultimate_formulas = set()
            for voice_formula in voice_formulas:
                *penultimate_formula, ultimate_formula = voice_formula
                converted_formula = tuple(
                    tuple(formula_part) for formula_part in penultimate_formula
                )
                penultimate_formulas.add(converted_formula)
                ultimate_formulas.add(tuple(ultimate_formula))
            if (
                voice_name == "superius"
                and cadence_type == "final_cadences"
                and "some_whole_notes" in penultimate_rhythms
                and "all_whole_notes" not in penultimate_rhythms
            ):
                penultimate_formulas.remove(((-1, "1"),))

            for penultimate_formula in penultimate_formulas:
                voice_measures = get_penultimate_voice_measures(
                    self.mode, penultimate_formula, voice_tessitura
                )
                penultimate_sequences[voice_name].extend(voice_measures)
            for ultimate_formula in ultimate_formulas:
                voice_measures = get_ultimate_voice_measures(
                    self.mode, ultimate_formula, voice_tessitura, modify_chordal_third
                )
                ultimate_sequences[voice_name].extend(voice_measures)
        if penultimate_superius_duplicate is not None:
            penultimate_sequences["superius"] = filter_duplicates(
                penultimate_sequences["superius"],
                penultimate_superius_duplicate,
                partial_match=True,
            )

        voice_measure_stacker = VoiceMeasureStacker(
            penultimate_sequences,
            penultimate_rhythms,
            are_cadential_duos_valid,
            are_cadential_trios_valid,
        )
        leading_tone_letter = self.mode[-1].letter
        for prospect_stack in next(iter(voice_measure_stacker)):
            leading_tone_count = 0
            for voice_measure in prospect_stack:
                current_pitch_letter = voice_measure[-1].specific_pitch.letter
                if current_pitch_letter == leading_tone_letter:
                    leading_tone_count += 1
                    if leading_tone_count > 1:
                        break
            else:
                self.sequence_prospects[4].append(prospect_stack)

        voice_measure_stacker = VoiceMeasureStacker(
            ultimate_sequences, {"all_whole_notes"}
        )
        for prospect_stack in next(iter(voice_measure_stacker)):
            superius_ending_pitch = prospect_stack[-1][-1].specific_pitch
            if superius_ending_pitch not in superius_ending_tessitura:
                continue

            mediant_pitch_count = 0
            for voice_measure in prospect_stack:
                current_pitch_letter = voice_measure[-1].specific_pitch.letter
                # accounts for the picardy third
                if current_pitch_letter == mediant_pitch_letter:
                    mediant_pitch_count += 1
                    if mediant_pitch_count > 1:
                        break
            else:
                self.sequence_prospects[5].append(prospect_stack)
        if not self.sequence_prospects[5]:
            if cadence_type == "final_cadences":
                raise ImpossibleError(
                    "Authentic cadence failed.", str(self.mode), self.mode.type
                )
            raise limits.ImprobableError("Cadence failed.")

    def fill_remaining_prospects(
        self,
        allowed_voice_measures: dict[str, list[theory.FullVoiceMeasure]],
        solution_spec: SolutionSpec,
    ) -> None:
        for duplicate_index in self.unfilled_duplicate_indices:
            allow_chanson_idiom = (
                self.ending == "final_cadences" and duplicate_index == 3
            )
            current_superius_duplicate = solution_spec.get_superius_duplicate(
                self.duplicate.global_index, duplicate_index
            )
            partial_match = duplicate_index == self.duplicate.local_indices[-1]

            local_voice_measures = {
                "bassus": allowed_voice_measures["bassus"],
                "tenor": allowed_voice_measures["tenor"],
                "contratenor": allowed_voice_measures["contratenor"],
            }
            local_voice_measures["superius"] = filter_duplicates(
                allowed_voice_measures["superius"],
                current_superius_duplicate,
                partial_match,
            )
            voice_measure_stacker = VoiceMeasureStacker(
                local_voice_measures,
                self.rhythms[duplicate_index],
                allow_chanson_idiom=allow_chanson_idiom,
            )
            self.sequence_prospects[duplicate_index] = next(iter(voice_measure_stacker))
            self.unfilled_prospect_indices.remove(duplicate_index)
        self.unfilled_duplicate_indices.clear()

        if self.ending == "final_cadences" and 3 in self.unfilled_prospect_indices:
            voice_measure_stacker = VoiceMeasureStacker(
                allowed_voice_measures,
                self.rhythms[3],
                allow_chanson_idiom=True,
            )
            self.sequence_prospects[3] = next(iter(voice_measure_stacker))
            self.unfilled_prospect_indices.remove(3)
        for prospect_index in self.unfilled_prospect_indices:
            voice_measure_stacker = VoiceMeasureStacker(
                allowed_voice_measures,
                self.rhythms[prospect_index],
            )
            self.sequence_prospects[prospect_index] = next(iter(voice_measure_stacker))
        self.unfilled_prospect_indices.clear()


@dataclass
class DanceSolver:
    global_spec: GlobalSpec
    solution_spec: SolutionSpec
    number_of_sections: int = field(init=False)

    def __post_init__(self) -> None:
        self.number_of_sections = len(self.solution_spec.sections)

    def get_tempo(self) -> int:
        tempo_min, tempo_max = idioms["tempo_map"][self.global_spec.dance_name]
        return random.randint(tempo_min, tempo_max)

    def solve(self) -> limits.DanceScore:
        try:
            solution_score = next(self.advance_section(0))
        except StopIteration:
            raise limits.ImprobableError("Sample of prospects are insufficient.")
        return solution_score

    def advance_section(self, section_index: int) -> Iterator[limits.DanceScore]:
        if section_index >= self.number_of_sections:
            chosen_instrument = theory.MidiInstrument(
                *random.choice(idioms["instruments"])
            )
            score_sequences = []
            for section_result in self.solution_spec.result:
                score_sequences.append(
                    [
                        measure_stack
                        for sequence_result in section_result
                        for measure_stack in sequence_result
                    ]
                )
            if (
                self.solution_spec[-1][-1].ending != "final_cadences"
                and self.solution_spec[0][-1].ending == "final_cadences"
            ):
                if self.number_of_sections == 2 and len(self.solution_spec[-1]) > 1:
                    will_refrain = True
                elif self.number_of_sections > 2:
                    will_refrain = True
                else:
                    will_refrain = False
            else:
                will_refrain = False

            dance_score = limits.DanceScore(
                self.solution_spec.primary_mode,
                self.global_spec.clef_group,
                score_sequences,
                chosen_instrument,
                self.get_tempo(),
                will_refrain,
            )
            yield dance_score
            return

        section_solver = self.advance_sequence(
            0, self.solution_spec[section_index].solve_order
        )
        try:
            for _ in section_solver:
                yield from self.advance_section(section_index + 1)
        except limits.ImprobableError as err:
            print(f"{err} Backtracking to previous section.")
            return

    def advance_sequence(
        self, solve_index: int, sequence_specs: list[SequenceSpec]
    ) -> Iterator[bool]:
        if solve_index >= len(sequence_specs):
            yield True
            return
        sequence_spec = sequence_specs[solve_index]
        sequence_solver = sequence_spec.solve(self.global_spec, self.solution_spec)
        for _ in sequence_solver:
            yield from self.advance_sequence(solve_index + 1, sequence_specs)


DuoMeasureTest = tuple[
    theory.FullVoiceMeasure,
    theory.FullVoiceMeasure,
    tuple[Callable[[theory.SpecificPitch, theory.SpecificPitch], bool], ...],
    tuple[str, ...],
]


bass_regular_duo_successes: dict[int, set[int]] = defaultdict(set)
bass_regular_duo_failures: dict[int, set[int]] = defaultdict(set)
upper_regular_duo_successes: dict[int, set[int]] = defaultdict(set)
upper_regular_duo_failures: dict[int, set[int]] = defaultdict(set)


def are_regular_duos_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        additional_tests,
        consonant_ids,
    ) in duo_measure_tests:
        lower_id, upper_id = lower_voice_measure.id, upper_voice_measure.id
        if consonant_ids == pure.lower_voice_consonances:
            success_cache = bass_regular_duo_successes
            failure_cache = bass_regular_duo_failures
        elif consonant_ids == pure.upper_voice_consonances:
            success_cache = upper_regular_duo_successes
            failure_cache = upper_regular_duo_failures
        else:
            raise ValueError

        if upper_id in failure_cache[lower_id]:
            return False
        if upper_id not in success_cache[lower_id]:
            if checked_regular_duo(
                lower_voice_measure, upper_voice_measure, consonant_ids
            ):
                success_cache[lower_id].add(upper_id)
            else:
                failure_cache[lower_id].add(upper_id)
                return False

        duo_iter = rules.get_note_duo(lower_voice_measure, upper_voice_measure)
        for current_lower_note, current_upper_note in duo_iter:
            for additional_test in additional_tests:
                if not additional_test(
                    current_lower_note.specific_pitch,
                    current_upper_note.specific_pitch,
                ):
                    return False
    return True


def checked_regular_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
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


bass_idiom_duo_presences: dict[int, set[int]] = defaultdict(set)
bass_idiom_duo_absences: dict[int, set[int]] = defaultdict(set)
upper_idiom_duo_presences: dict[int, set[int]] = defaultdict(set)
upper_idiom_duo_absences: dict[int, set[int]] = defaultdict(set)


def has_chanson_duo(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        _,
        consonant_ids,
    ) in duo_measure_tests:
        lower_id, upper_id = lower_voice_measure.id, upper_voice_measure.id
        if consonant_ids == pure.lower_voice_consonances:
            success_cache = bass_idiom_duo_presences
            failure_cache = bass_idiom_duo_absences
        elif consonant_ids == pure.upper_voice_consonances:
            success_cache = upper_idiom_duo_presences
            failure_cache = upper_idiom_duo_absences
        else:
            raise ValueError

        if upper_id in success_cache[lower_id]:
            return True
        if upper_id in failure_cache[lower_id]:
            continue
        if is_duo_idiom_present(
            lower_voice_measure, upper_voice_measure, consonant_ids
        ):
            success_cache[lower_id].add(upper_id)
            return True
        failure_cache[lower_id].add(upper_id)
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


bass_cadential_duo_successes: dict[int, set[int]] = defaultdict(set)
bass_cadential_duo_failures: dict[int, set[int]] = defaultdict(set)
upper_cadential_duo_successes: dict[int, set[int]] = defaultdict(set)
upper_cadential_duo_failures: dict[int, set[int]] = defaultdict(set)


def are_cadential_duos_valid(duo_measure_tests: tuple[DuoMeasureTest, ...]) -> bool:
    for (
        lower_voice_measure,
        upper_voice_measure,
        additional_tests,
        consonant_ids,
    ) in duo_measure_tests:
        lower_id, upper_id = lower_voice_measure.id, upper_voice_measure.id
        if consonant_ids == pure.lower_voice_consonances:
            success_cache = bass_cadential_duo_successes
            failure_cache = bass_cadential_duo_failures
        elif consonant_ids == pure.upper_voice_consonances:
            success_cache = upper_cadential_duo_successes
            failure_cache = upper_cadential_duo_failures
        else:
            raise ValueError

        if upper_id in failure_cache[lower_id]:
            return False
        if upper_id not in success_cache[lower_id]:
            if checked_cadential_duo(
                lower_voice_measure, upper_voice_measure, consonant_ids
            ):
                success_cache[lower_id].add(upper_id)
            else:
                failure_cache[lower_id].add(upper_id)
                return False

        duo_iter = rules.get_note_duo(lower_voice_measure, upper_voice_measure)
        for current_lower_note, current_upper_note in duo_iter:
            for additional_test in additional_tests:
                if not additional_test(
                    current_lower_note.specific_pitch,
                    current_upper_note.specific_pitch,
                ):
                    return False
    return True


def checked_cadential_duo(
    lower_voice_measure: theory.FullVoiceMeasure,
    upper_voice_measure: theory.FullVoiceMeasure,
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


quartet_tests: dict[str, bool] = {}


def is_quartet_valid(
    measure_quartet: tuple[
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
        theory.FullVoiceMeasure,
    ]
) -> bool:
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
    allowed_rhythms: set[str]
    are_duos_valid: DuoValidator = are_regular_duos_valid
    are_trios_valid: TrioValidator = are_regular_trios_valid
    allow_chanson_idiom: bool = False
    result_min_count = 5_000
    some_whole_count = {1, 2, 3}

    def __post_init__(self) -> None:
        self.bassus_measures = self.pitch_sequences["bassus"]
        self.tenor_measures = self.pitch_sequences["tenor"]
        self.contratenor_measures = self.pitch_sequences["contratenor"]
        self.superius_measures = self.pitch_sequences["superius"]

    def __iter__(self) -> Iterator[list[theory.VariantStack]]:
        random.shuffle(self.bassus_measures)
        sub_iters = []
        for bassus_measure in self.bassus_measures:
            sub_iters.append(
                self.get_measure_stacks(
                    [bassus_measure],
                )
            )
        result_stacks: list[theory.VariantStack] = []
        result_count = 0
        sub_iter_count = len(sub_iters)
        sample_index = 0

        while sub_iters:
            if sample_index == sub_iter_count:
                sample_index = 0
            try:
                prospect_stack = next(sub_iters[sample_index])
            except StopIteration:
                sub_iters.pop(sample_index)
                sub_iter_count -= 1
                continue

            result_stacks.append(prospect_stack)
            sample_index += 1
            result_count += 1
            if result_count == self.result_min_count:
                yield result_stacks
                result_count = 0
                result_stacks = []
        yield result_stacks

    def shuffle_iter(
        self,
        voice_measures: list[theory.FullVoiceMeasure],
    ) -> Iterator[theory.FullVoiceMeasure]:
        measure_indices = list(range(len(voice_measures)))
        random.shuffle(measure_indices)
        for measure_index in measure_indices:
            voice_measure = voice_measures[measure_index]
            if len(voice_measure) == 1:
                if self.allowed_rhythms == {"no_whole_notes"}:
                    continue
            elif self.allowed_rhythms == {"all_whole_notes"}:
                continue
            yield voice_measure

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

                        pseudo_stack = (
                            bassus_measure,
                            tenor_measure,
                            contratenor_measure,
                            superius_measure,
                        )
                        whole_note_count = sum(
                            1
                            for voice_measure in pseudo_stack
                            if len(voice_measure) == 1
                        )
                        if (
                            whole_note_count not in self.some_whole_count
                            and self.allowed_rhythms == {"some_whole_notes"}
                        ):
                            continue
                        if not is_quartet_valid(pseudo_stack):
                            continue
                        prospect_stack = theory.FullMeasureStack.get(*pseudo_stack)
                        yield prospect_stack
