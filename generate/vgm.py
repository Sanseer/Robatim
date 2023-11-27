import json
import functools
import random
from collections import defaultdict, deque
from fractions import Fraction

from generate import theory

# Importing settings allows stylistic updates independent of codebase.
with open("idioms_vgm.json", "r") as f:
    idioms = json.load(f)

instruments_bass = [
    theory.MidiInstrument(*instrument) for instrument in idioms["instruments_bass"]
]
instruments_melody = [
    theory.MidiInstrument(*instrument) for instrument in idioms["instruments_melody"]
]
time_sigs = [theory.TimeSignature(*time_sig) for time_sig in idioms["time_sigs"]]


def filter_prospects(
    original_prospects: list, has_prospect_succeeded: functools.partial[bool]
) -> bool:
    filtered_prospects = [
        original_prospect
        for original_prospect in original_prospects
        if has_prospect_succeeded(original_prospect)
    ]

    if not filtered_prospects:
        return False
    original_prospects.clear()
    original_prospects.extend(filtered_prospects)

    return True


def checked_previous_boundary(
    previous_segment: list[str], current_segment: list[str]
) -> bool:
    return previous_segment[-1] != current_segment[0]


def checked_next_boundary(next_segment: list[str], current_segment: list[str]) -> bool:
    return current_segment[-1] != next_segment[0]


def checked_consequent_repeat(
    prospect_segment: list[str], current_segment: list[str]
) -> bool:
    first_condition = prospect_segment[0][-1] == current_segment[0][-1]
    second_condition = prospect_segment[1][-1] == current_segment[1][-1]
    return first_condition and second_condition


nonadjacent_section_pairs = ((0, 2), (2, 0))


def include_generic_pitch(
    prospect_pitch: theory.GenericPitch, target_pitch: theory.GenericPitch
) -> bool:
    return prospect_pitch == target_pitch


def checked_next_fragment_leap(
    second_melody_fragment: list[theory.SpecificPitch],
    first_melody_fragment: list[theory.SpecificPitch],
    first_chord: theory.GenericChord,
) -> bool:
    args = first_melody_fragment, second_melody_fragment, first_chord
    return checked_previous_fragment_leap(*args)


def checked_previous_fragment_leap(
    first_melody_fragment: list[theory.SpecificPitch],
    second_melody_fragment: list[theory.SpecificPitch],
    first_chord: theory.GenericChord,
) -> bool:
    penultimate_pitch = first_melody_fragment[-1]
    ultimate_pitch = second_melody_fragment[0]
    ultimate_interval_distance = theory.SpecificPitch.get_interval_distance(
        penultimate_pitch, ultimate_pitch
    )
    if ultimate_interval_distance > 3:
        return False
    if theory.GenericPitch(penultimate_pitch.generic_pitch) in first_chord:
        return True

    antepenultimate_pitch = first_melody_fragment[-2]
    if antepenultimate_pitch == ultimate_pitch:
        return False

    penultimate_interval_distance = theory.SpecificPitch.get_interval_distance(
        antepenultimate_pitch, penultimate_pitch
    )
    return penultimate_interval_distance == ultimate_interval_distance == 1


def checked_next_resolution(
    second_melody_fragment: list[theory.SpecificPitch],
    first_melody_fragment: list[theory.SpecificPitch],
) -> bool:
    return checked_previous_resolution(first_melody_fragment, second_melody_fragment)


def checked_previous_resolution(
    first_melody_fragment: list[theory.SpecificPitch],
    second_melody_fragment: list[theory.SpecificPitch],
) -> bool:
    penultimate_pitch = first_melody_fragment[-1]
    ultimate_pitch = second_melody_fragment[0]
    resolution_distance = theory.SpecificPitch.get_interval_distance(
        penultimate_pitch, ultimate_pitch
    )
    return resolution_distance <= 1


def is_fragment_valid(
    current_melody_fragment: list[theory.SpecificPitch],
    imagined_tessitura: theory.Tessitura,
) -> bool:
    return current_melody_fragment[0] in imagined_tessitura


starting_tessitura = theory.Tessitura(
    theory.SpecificPitch("C0"), theory.SpecificPitch("C8")
)


class Composer:
    def __init__(self) -> None:
        self.score = theory.AbstractScore()
        self.score.time_sig = random.choice(time_sigs)
        self.index_repeats: dict[int, set[int]] = defaultdict(set)
        self.index_repeats.update({0: {8}, 8: {0}, 1: {9}, 9: {1}})

    def fill_score(self) -> None:
        strum_duration = self.score.time_sig.groove_duration
        unnested_bass_degrees = self.write_bassline(strum_duration)
        self.write_melody(strum_duration, unnested_bass_degrees)

    def write_bassline(self, strum_duration: Fraction) -> list[str]:
        bassline_presets = idioms["bassline_presets"]
        possible_bass_degrees = theory.WaveFunction(
            bassline_presets, self.has_bass_degree_propagated
        )
        nested_bass_degrees = next(iter(possible_bass_degrees))
        print(f"{nested_bass_degrees = }")
        unnested_bass_degrees = [
            bass_degree
            for bass_degree_section in nested_bass_degrees
            for bass_degree in bass_degree_section
        ]
        unnested_bass_degrees.pop()
        bass_generic_pitches = [
            self.score.major_scale.get_pitch_from_scale_degree(bass_degree)
            for bass_degree in unnested_bass_degrees
        ]

        lowest_bass_pitch = theory.SpecificPitch.get_pitch_from_value(
            idioms["lowest_bass_pitch"]
        )
        highest_bass_pitch = theory.SpecificPitch.get_pitch_from_value(
            idioms["highest_bass_pitch"]
        )
        bass_tessitura = theory.Tessitura(lowest_bass_pitch, highest_bass_pitch)

        bass_pitch_prospects = [
            deque(bass_tessitura.find_equivalent_pitches(bass_generic_pitch))
            for bass_generic_pitch in bass_generic_pitches
        ]
        possible_basslines = theory.WaveFunction(
            bass_pitch_prospects, self.has_bassline_propagated
        )
        final_bass_pitches = next(iter(possible_basslines))

        chosen_instrument = random.choice(instruments_bass)
        current_score_part = self.score.tonal_parts[(chosen_instrument, 0)]
        current_score_part.extend(
            theory.SpecificNote(bass_pitch, strum_duration)
            for bass_pitch in final_bass_pitches
        )
        current_score_part.append(theory.RestNote(strum_duration))
        return unnested_bass_degrees

    def write_melody(
        self, strum_duration: Fraction, unnested_bass_degrees: list[str]
    ) -> None:
        rhythm_options = idioms["rhythm_options"][str(self.score.time_sig)]
        chosen_rhythms = {
            rhythm_id: random.choice(rhythm_options[rhythm_id])
            for rhythm_id in idioms["rhythm_identifiers"]
        }
        print(f"{chosen_rhythms = }")
        sustain_rhythm_id = idioms["sustain_rhythm_id"]
        chosen_rhythm_config = random.choice(idioms["possible_rhythm_configs"])
        print(f"{chosen_rhythm_config = }")
        nested_melody_rhythm = []

        chosen_rhythm_config.pop()
        for rhythm_id in chosen_rhythm_config:
            if rhythm_id == sustain_rhythm_id:
                nested_melody_rhythm.append([strum_duration])
            else:
                nested_melody_rhythm.append(
                    [Fraction(rhythm_repr) for rhythm_repr in chosen_rhythms[rhythm_id]]
                )

        degree_to_chord_symbol = idioms["degree_to_chord_symbol"]
        chosen_chord_symbols = [
            degree_to_chord_symbol[bass_degree] for bass_degree in unnested_bass_degrees
        ]
        print(f"{chosen_chord_symbols = }")
        chosen_chords = [
            self.score.major_scale.get_chord(chord_symbol)
            for chord_symbol in chosen_chord_symbols
        ]

        scaffold_prospects = [
            chosen_chord._members[:] for chosen_chord in chosen_chords
        ]
        has_prospect_succeeded = functools.partial(
            include_generic_pitch, target_pitch=self.score.minor_scale[0]
        )
        filter_prospects(scaffold_prospects[-1], has_prospect_succeeded)

        # mapping objects in json must use strings as keys
        melody_figure_options = {
            int(k): v for k, v in idioms["melody_figure_options"].items()
        }
        lowest_melody_pitch = theory.SpecificPitch.get_pitch_from_value(
            idioms["lowest_melody_pitch"]
        )
        highest_melody_pitch = theory.SpecificPitch.get_pitch_from_value(
            idioms["highest_melody_pitch"]
        )
        melody_tessitura = theory.Tessitura(lowest_melody_pitch, highest_melody_pitch)

        def get_figurations(
            chord_pitch: theory.GenericPitch,
            figure_length: int,
            chosen_chord: theory.GenericChord,
        ) -> list[list[theory.SpecificPitch]]:
            possible_starting_pitches = melody_tessitura.find_equivalent_pitches(
                chord_pitch
            )
            possible_figures = melody_figure_options[figure_length]
            figurations = []

            for possible_starting_pitch in possible_starting_pitches:
                for possible_figure in possible_figures:
                    current_figure = [possible_starting_pitch]
                    for scale_shift in possible_figure:
                        shifted_pitch = possible_starting_pitch.consonant_shift(
                            self.score.minor_scale, chosen_chord, scale_shift
                        )
                        if shifted_pitch not in melody_tessitura:
                            break
                        current_figure.append(shifted_pitch)
                    else:
                        figurations.append(current_figure)

            return figurations

        nested_melody_prospects = []
        for rhythm_group, chord_pitches, chosen_chord in zip(
            nested_melody_rhythm, scaffold_prospects, chosen_chords
        ):
            figure_length = len(rhythm_group)
            possible_melody_fragments = []
            for chord_pitch in chord_pitches:
                possible_melody_fragments.extend(
                    get_figurations(chord_pitch, figure_length, chosen_chord)
                )
            nested_melody_prospects.append(possible_melody_fragments)

        has_melody_propagated = functools.partial(
            self.has_melody_propagated, chosen_chords=chosen_chords
        )
        possible_nested_melodies = theory.WaveFunction(
            nested_melody_prospects, has_melody_propagated
        )
        chosen_nested_melody = next(iter(possible_nested_melodies))
        chosen_instrument = random.choice(instruments_melody)

        current_score_part = self.score.tonal_parts[chosen_instrument, 1]
        for rhythm_group, melody_fragment in zip(
            nested_melody_rhythm, chosen_nested_melody
        ):
            for note_duration, melody_pitch in zip(rhythm_group, melody_fragment):
                current_score_part.append(
                    theory.SpecificNote(melody_pitch, note_duration)
                )
        current_score_part.append(theory.RestNote(strum_duration))

    @staticmethod
    def has_bass_degree_propagated(
        bass_degree_prospects: list[list[list[str]]],
        propagate_index: int,
        bass_sequence: list[list[str] | None],
        current_segment: list[str],
    ) -> bool:
        if propagate_index != len(bass_sequence) - 1:
            next_prospects = bass_degree_prospects[propagate_index + 1]
            has_prospect_succeeded = functools.partial(
                checked_next_boundary, current_segment=current_segment
            )
            if not filter_prospects(next_prospects, has_prospect_succeeded):
                return False
        if propagate_index != 0:
            previous_prospects = bass_degree_prospects[propagate_index - 1]
            has_prospect_succeeded = functools.partial(
                checked_previous_boundary, current_segment=current_segment
            )
            if not filter_prospects(previous_prospects, has_prospect_succeeded):
                return False

        for first_index, second_index in nonadjacent_section_pairs:
            if propagate_index == first_index:
                nonadjacent_prospects = bass_degree_prospects[second_index]
                has_prospect_succeeded = functools.partial(
                    checked_consequent_repeat, current_segment=current_segment
                )
                if not filter_prospects(nonadjacent_prospects, has_prospect_succeeded):
                    return False

        return True

    def has_bassline_propagated(
        self,
        bass_pitch_prospects: list[deque[theory.SpecificPitch]],
        propagate_index: int,
        bassline: list[theory.SpecificPitch | None],
        chosen_bass_pitch: theory.SpecificPitch,
    ) -> bool:
        imagined_global_tessitura = self.get_bass_range(
            bass_pitch_prospects[propagate_index]
        )
        real_local_tessituras = [imagined_global_tessitura for _ in bassline]

        def has_global_reset(
            sequence_index: int, index_prospects: deque[theory.SpecificPitch]
        ) -> bool:
            real_local_tessituras[sequence_index] = theory.Tessitura(
                index_prospects[0], index_prospects[-1]
            )
            imagined_local_tessitura = self.get_bass_range(index_prospects)
            global_delta = imagined_global_tessitura.shrink(imagined_local_tessitura)

            return global_delta

        sequence_size = len(bassline)
        for sequence_index in range(sequence_size):
            index_prospects = bass_pitch_prospects[sequence_index]
            if index_prospects[0].generic_pitch == chosen_bass_pitch.generic_pitch:
                index_prospects.clear()
                index_prospects.append(chosen_bass_pitch)
            has_global_reset(sequence_index, index_prospects)

        queue = deque(range(sequence_size))
        queue_set = set(queue)
        while queue:
            primary_index = queue.popleft()
            index_prospects = bass_pitch_prospects[primary_index]
            previous_options_count = len(index_prospects)
            imagined_global_tessitura.filter(index_prospects)
            current_options_count = len(index_prospects)

            if previous_options_count != current_options_count:
                if not index_prospects:
                    return False

                if has_global_reset(primary_index, index_prospects):
                    for secondary_index in range(sequence_size):
                        if secondary_index not in queue_set:
                            real_local_tessitura = real_local_tessituras[
                                secondary_index
                            ]
                            if real_local_tessitura not in imagined_global_tessitura:
                                queue.append(secondary_index)
                                queue_set.add(secondary_index)

            queue_set.remove(primary_index)

        return True

    def get_bass_range(
        self, specific_pitches: deque[theory.SpecificPitch]
    ) -> theory.Tessitura:
        if specific_pitches[0].generic_pitch == self.score.major_scale:
            up_shift = theory.Interval.get("P1")
            down_shift = theory.Interval.get("P8")
        else:
            up_shift = down_shift = theory.Interval.get("P8")

        pitch_min = specific_pitches[0] - down_shift
        pitch_max = specific_pitches[-1] + up_shift

        return theory.Tessitura(pitch_min, pitch_max)

    def has_melody_propagated(
        self,
        nested_melody_prospects: list[list[list[theory.SpecificPitch]]],
        propagate_index: int,
        nested_melody: list[list[theory.SpecificPitch] | None],
        current_melody_fragment: list[theory.SpecificPitch],
        chosen_chords: list[theory.GenericChord],
    ) -> bool:
        for duplicate_index in self.index_repeats[propagate_index]:
            nested_melody_prospects[duplicate_index] = [current_melody_fragment]

        if propagate_index != (final_index := len(nested_melody) - 1):
            next_prospects = nested_melody_prospects[propagate_index + 1]
            prospect_validators = [
                functools.partial(
                    checked_next_fragment_leap,
                    first_melody_fragment=current_melody_fragment,
                    first_chord=chosen_chords[propagate_index],
                )
            ]
            if propagate_index == final_index - 1:
                prospect_validators.append(
                    functools.partial(
                        checked_next_resolution,
                        first_melody_fragment=current_melody_fragment,
                    )
                )
            for prospect_validator in prospect_validators:
                if not filter_prospects(next_prospects, prospect_validator):
                    return False

        if propagate_index != 0:
            previous_prospects = nested_melody_prospects[propagate_index - 1]
            prospect_validators = [
                functools.partial(
                    checked_previous_fragment_leap,
                    second_melody_fragment=current_melody_fragment,
                    first_chord=chosen_chords[propagate_index - 1],
                )
            ]
            if propagate_index == final_index:
                prospect_validators.append(
                    functools.partial(
                        checked_previous_resolution,
                        second_melody_fragment=current_melody_fragment,
                    )
                )
            for prospect_validator in prospect_validators:
                if not filter_prospects(previous_prospects, prospect_validator):
                    return False

        queue = deque([propagate_index])
        queue_set = set(queue)

        imagined_tessituras = [starting_tessitura.clone() for _ in nested_melody]
        scaffold_tessituras = [
            self.get_scaffold_tessitura(index_prospects)
            for index_prospects in nested_melody_prospects
        ]
        while queue:
            primary_index = queue.popleft()
            imagined_tessitura = imagined_tessituras[primary_index]
            current_prospects = nested_melody_prospects[primary_index]

            has_prospect_succeeded = functools.partial(
                is_fragment_valid, imagined_tessitura=imagined_tessitura
            )
            if not filter_prospects(current_prospects, has_prospect_succeeded):
                return False

            current_scaffold_tessitura = self.get_scaffold_tessitura(current_prospects)
            scaffold_tessituras[primary_index] = current_scaffold_tessitura

            adjacent_imagined_tessitura = current_scaffold_tessitura.clone()
            adjacent_imagined_tessitura.highest_pitch += theory.Interval.get("P5")
            adjacent_imagined_tessitura.lowest_pitch -= theory.Interval.get("P5")

            if primary_index != final_index:
                next_index = primary_index + 1
                next_scaffold_tessitura = scaffold_tessituras[next_index]
                imagined_tessituras[next_index].shrink(adjacent_imagined_tessitura)
                if (
                    next_index not in queue_set
                    and next_scaffold_tessitura not in adjacent_imagined_tessitura
                ):
                    queue.append(next_index)
                    queue_set.add(next_index)

            if primary_index != 0:
                previous_index = primary_index - 1
                previous_scaffold_tessitura = scaffold_tessituras[previous_index]
                imagined_tessituras[previous_index].shrink(adjacent_imagined_tessitura)
                if (
                    previous_index not in queue_set
                    and previous_scaffold_tessitura not in adjacent_imagined_tessitura
                ):
                    queue.append(previous_index)
                    queue_set.add(previous_index)

            if primary_index == final_index:
                global_imagined_tessitura = current_scaffold_tessitura.clone()
                global_imagined_tessitura.highest_pitch += theory.Interval.get("m7")
                global_imagined_tessitura.lowest_pitch -= theory.Interval.get("M3")

                for secondary_index, local_scaffold_tessitura in enumerate(
                    scaffold_tessituras
                ):
                    imagined_tessituras[secondary_index].shrink(
                        global_imagined_tessitura
                    )
                    if (
                        secondary_index not in queue_set
                        and local_scaffold_tessitura not in global_imagined_tessitura
                    ):
                        queue.append(secondary_index)
                        queue_set.add(secondary_index)
            elif primary_index == 0:
                global_imagined_tessitura = current_scaffold_tessitura.clone()
                global_imagined_tessitura.highest_pitch += theory.Interval.get("M6")
                global_imagined_tessitura.lowest_pitch -= theory.Interval.get("P5")

                for secondary_index, local_scaffold_tessitura in enumerate(
                    scaffold_tessituras
                ):
                    imagined_tessituras[secondary_index].shrink(
                        global_imagined_tessitura
                    )
                    if (
                        secondary_index not in queue_set
                        and local_scaffold_tessitura not in global_imagined_tessitura
                    ):
                        queue.append(secondary_index)
                        queue_set.add(secondary_index)

            queue_set.remove(primary_index)

        return True

    @staticmethod
    def get_scaffold_tessitura(
        current_prospects: list[list[theory.SpecificPitch]],
    ) -> theory.Tessitura:
        lowest_scaffold_pitch = min(current_prospects, key=lambda x: x[0])[0]
        highest_scaffold_pitch = max(current_prospects, key=lambda x: x[0])[0]
        return theory.Tessitura(lowest_scaffold_pitch, highest_scaffold_pitch)
