import json
import functools
import random
from collections import deque
from fractions import Fraction

from generate import theory

with open("idioms_vgm.json", "r") as f:
    idioms = json.load(f)

instruments_bass = [
    theory.MidiInstrument(*instrument) for instrument in idioms["instruments_bass"]
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


class Composer:
    def __init__(self) -> None:
        self.score = theory.AbstractScore()
        self.score.time_sig = random.choice(time_sigs)

    def fill_score(self) -> None:
        bassline_presets = idioms["bassline_presets"]
        possible_bass_degrees = theory.WaveFunction(
            bassline_presets, self.has_bass_degree_propagated
        )
        nested_bass_degrees = next(iter(possible_bass_degrees))
        print(f"{nested_bass_degrees = }")
        bass_generic_pitches = [
            self.score.scale.get_pitch_from_scale_degree(bass_degree)
            for bass_degree_section in nested_bass_degrees
            for bass_degree in bass_degree_section
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
        print(f"{final_bass_pitches = }")

        chosen_instrument = random.choice(instruments_bass)
        strum_duration = sum(
            (
                Fraction(groove_repr)
                for groove_repr in self.score.time_sig.groove_pattern
            ),
            Fraction("0"),
        )
        self.score.tonal_parts[(chosen_instrument, 0)] = [
            theory.SpecificNote(bass_pitch, strum_duration)
            for bass_pitch in final_bass_pitches
        ]

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
        if specific_pitches[0].generic_pitch == self.score.scale:
            up_shift = theory.Interval.get("P1")
            down_shift = theory.Interval.get("P8")
        else:
            up_shift = down_shift = theory.Interval.get("P8")

        pitch_min = specific_pitches[0] - down_shift
        pitch_max = specific_pitches[-1] + up_shift

        return theory.Tessitura(pitch_min, pitch_max)
