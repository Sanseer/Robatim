import random
from collections import deque
import itertools
from fractions import Fraction
from typing import Callable

from generate import theory, implement

time_sigs = [
    theory.TimeSignature(*time_sig) for time_sig in implement.idioms["time_sigs"]
]
instruments_bass = [
    theory.MidiInstrument(*instrument)
    for instrument in implement.idioms["instruments_bass"]
]
instruments_accompaniment = [
    theory.MidiInstrument(*instrument)
    for instrument in implement.idioms["instruments_accompaniment"]
]


class FolkBuilder:
    progression_presets: list[list[list[str]]] = implement.idioms["progression_presets"]
    chord_labels: dict[str, list[str]] = implement.idioms["chord_labels"]
    drum_mapping = {"BD": (35, 36), "SN": (38, 40), "HHC": (42, 44), "HHO": (46,)}

    def __init__(self) -> None:
        self._score = theory.AbstractScore()
        chosen_time_sig = random.choice(time_sigs)
        self._score.time_sig = chosen_time_sig
        self.time_keeper: implement.TimeKeeper
        self.chords: list[theory.GenericChord]

        self.index_repeats: dict[int, set[int]]
        self.subsequences: dict[int, tuple[tuple[int, ...], str]]
        self.get_bass_range: Callable[
            [deque[theory.SpecificPitch]],
            tuple[theory.SpecificPitch, theory.SpecificPitch],
        ]

    @staticmethod
    def find_subsequences(
        symbol_sequence: list[str],
        delimiter: str,
        max_search_length: int,
        valid_composites: dict[str, list[str]],
    ) -> dict[int, tuple[tuple[int, ...], str]]:
        """Given a sequence of strings, finds all indices that are part
        of specified subsequences of strings, which have a known max length.
        A subsequence is identified as a composite string with a delimiter."""

        result = {}
        sequence_indices = list(range(len(symbol_sequence)))

        for start_index in sequence_indices:
            stop_index = start_index + max_search_length
            attempted_subsequence = symbol_sequence[start_index:stop_index]

            while len(attempted_subsequence) > 1:
                attempted_composite = delimiter.join(attempted_subsequence)

                if attempted_composite in valid_composites:
                    index_references = tuple(sequence_indices[start_index:stop_index])
                    for composite_index in index_references:
                        result[composite_index] = (
                            index_references,
                            attempted_composite,
                        )
                    break

                stop_index -= 1
                attempted_subsequence = symbol_sequence[start_index:stop_index]

            # Beware of elision: two or more subsequences might overlap

        return result

    def write_chord_progression(self) -> None:
        self._score.set_tempo()
        print("Tempo:", self._score.tempo)

        progression_preset = random.choice(self.progression_presets)
        self.time_keeper = implement.TimeKeeper(progression_preset)
        self.time_keeper.print_formatted()
        self.index_repeats = self.time_keeper.symbol_parent_repeats

        symbol_sequence = self.time_keeper.symbol_sequence
        self.subsequences = self.find_subsequences(
            symbol_sequence, "|", 4, self.chord_labels
        )

        # The prospective chords will be modified when the wave function collapses.
        # This requires list copying to prevent side effects
        sequence_prospects = [
            self.chord_labels[symbol][:] for symbol in symbol_sequence
        ]
        new_progression = theory.WaveFunction(
            sequence_prospects, self.has_chord_propagated
        )
        chord_symbols = next(iter(new_progression))
        print("")
        self.time_keeper.print_corresponding_sequence(chord_symbols)

        self.chords = [
            self._score.scale.get_chord(chord_symbol) for chord_symbol in chord_symbols
        ]

    def has_chord_propagated(
        self,
        chord_sequence_prospects: list[list[str]],
        propagate_index: int,
        chord_sequence: list[str | None],
        chosen_chord: str,
    ) -> bool:
        if propagate_index != 0:
            previous_chord = chord_sequence[propagate_index - 1]
            if chosen_chord == previous_chord:
                return False

        if propagate_index != len(chord_sequence) - 1:
            next_chord = chord_sequence[propagate_index + 1]
            if chosen_chord == next_chord:
                return False

        for duplicate_index in self.index_repeats[propagate_index]:
            chord_sequence_prospects[duplicate_index] = [chosen_chord]

        if propagate_index in self.subsequences:
            index_references, sequence_id = self.subsequences[propagate_index]
            valid_subsequence_prospects: list[set[str]] = [
                set() for _ in index_references
            ]

            for composite_option in self.chord_labels[sequence_id]:
                valid_subsequence = composite_option.split("|")
                for sequence_index, chord_group in zip(
                    index_references, valid_subsequence
                ):
                    chord_equivalents = chord_group.split("=")
                    current_chord = chord_sequence[sequence_index]
                    if (
                        current_chord is not None
                        and current_chord not in chord_equivalents
                    ):
                        break
                else:
                    for proofread_index, chord_group in enumerate(valid_subsequence):
                        for valid_chord in chord_group.split("="):
                            valid_subsequence_prospects[proofread_index].add(
                                valid_chord
                            )

            validator = zip(index_references, valid_subsequence_prospects)
            for sequence_index, valid_index_prospects in validator:
                current_index_prospects = chord_sequence_prospects[sequence_index]
                filtered_prospects = [
                    index_prospect
                    for index_prospect in current_index_prospects
                    if index_prospect in valid_index_prospects
                ]
                if not filtered_prospects:
                    return False
                current_index_prospects[:] = filtered_prospects

        return True

    def write_bassline(self) -> None:
        chosen_instrument = random.choice(instruments_bass)
        print("Chosen bass instrument:", chosen_instrument)
        lowest_pitch = theory.SpecificPitch.get_pitch_from_value(
            chosen_instrument.lower_bound
        )
        highest_pitch = theory.SpecificPitch.get_pitch_from_value(
            chosen_instrument.upper_bound
        )
        bass_tessitura = theory.Tessitura(lowest_pitch, highest_pitch)

        bass_root_prospects = []
        for chord in self.chords:
            lowest_chord_root = theory.SpecificPitch(f"{chord[0]}0")
            root_iter = lowest_chord_root.create_iterator(["P8"])
            bass_root_prospects.append(deque(bass_tessitura.filter_pitches(root_iter)))

        bass_range_options = [self.surround_single_tonic, self.within_double_tonic]
        random.shuffle(bass_range_options)
        for bass_range_option in bass_range_options:
            self.get_bass_range = bass_range_option
            possible_bassline_scaffolds = theory.WaveFunction(
                bass_root_prospects, self.has_bass_rooted
            )

            for bassline_scaffold in possible_bassline_scaffolds:
                print(f"Attempting {bassline_scaffold}")
                bass_walker_prospects = []
                for bass_root_note, current_chord, symbol_parent in zip(
                    bassline_scaffold, self.chords, self.time_keeper.symbol_parents
                ):
                    bass_paths = self.get_bass_paths(
                        bass_root_note, current_chord, symbol_parent.groove_units
                    )
                    index_prospects = []
                    for bass_path in bass_paths:
                        for bass_note in bass_path:
                            if bass_note not in bass_tessitura:
                                break
                        else:
                            index_prospects.append(bass_path)
                    bass_walker_prospects.append(index_prospects)

                try:
                    bass_walker = next(
                        iter(
                            theory.WaveFunction(
                                bass_walker_prospects, self.has_bass_walked
                            )
                        )
                    )
                    break
                except StopIteration:
                    continue
            else:
                continue
            break
        else:
            raise ValueError

        groove_iter = itertools.cycle(
            [
                Fraction(groove_value)
                for groove_value in self._score.time_sig.groove_pattern
            ]
        )
        for pitch_group in bass_walker:
            for bass_pitch in pitch_group:
                strum_duration = next(groove_iter)
                self._score.tonal_parts[(chosen_instrument, 1)].append(
                    theory.SpecificNote(bass_pitch, strum_duration)
                )

        final_bass_note = bassline_scaffold[-1]
        self._score.tonal_parts[(chosen_instrument, 1)][-2:] = [
            theory.SpecificNote(final_bass_note, next(groove_iter)),
            theory.RestNote(next(groove_iter)),
        ]

    def has_bass_rooted(
        self,
        bass_sequence_prospects: list[deque[theory.SpecificPitch]],
        propagate_index: int,
        bass_sequence: list[theory.SpecificPitch | None],
        chosen_bass_note: theory.SpecificPitch,
    ) -> bool:
        global_tessitura = theory.Tessitura(
            *self.get_bass_range(deque([chosen_bass_note]))
        )
        local_tessituras = []
        for index_prospects in bass_sequence_prospects:
            local_tessitura = theory.Tessitura(index_prospects[0], index_prospects[-1])
            local_tessituras.append(local_tessitura)
            global_tessitura.has_contracted(*self.get_bass_range(index_prospects))

        sequence_size = len(bass_sequence)
        for sequence_index in range(sequence_size):
            index_prospects = bass_sequence_prospects[sequence_index]
            if index_prospects[0].generic_pitch == chosen_bass_note.generic_pitch:
                if (
                    self.get_bass_range == self.surround_single_tonic
                    or chosen_bass_note.generic_pitch != self._score.scale
                ):
                    index_prospects.clear()
                    index_prospects.append(chosen_bass_note)

        def has_global_reset(sequence_index: int) -> bool:
            min_pitch = index_prospects[0]
            max_pitch = index_prospects[-1]
            local_tessituras[sequence_index] = theory.Tessitura(min_pitch, max_pitch)
            global_delta = global_tessitura.has_contracted(
                *self.get_bass_range(index_prospects)
            )

            return global_delta

        queue = deque(range(sequence_size))
        queue_set = set(queue)
        while queue:
            primary_index = queue.popleft()
            index_prospects = bass_sequence_prospects[primary_index]
            previous_options_count = len(index_prospects)
            global_tessitura.filter(index_prospects)
            current_options_count = len(index_prospects)

            if previous_options_count != current_options_count:
                if not index_prospects:
                    return False

                if has_global_reset(primary_index):
                    for secondary_index in range(sequence_size):
                        if secondary_index not in queue_set:
                            local_tessitura = local_tessituras[secondary_index]
                            if local_tessitura not in global_tessitura:
                                queue.append(secondary_index)
                                queue_set.add(secondary_index)

            queue_set.remove(primary_index)

        return True

    def surround_single_tonic(
        self, specific_pitches: deque[theory.SpecificPitch]
    ) -> tuple[theory.SpecificPitch, theory.SpecificPitch]:
        if specific_pitches[0].generic_pitch == self._score.scale:
            up_shift = theory.Interval.get("P5")
            down_shift = theory.Interval.get("P4")
        else:
            up_shift = down_shift = theory.Interval.get("P8")

        pitch_min = specific_pitches[0] - down_shift
        pitch_max = specific_pitches[-1] + up_shift

        return pitch_min, pitch_max

    def within_double_tonic(
        self, specific_pitches: deque[theory.SpecificPitch]
    ) -> tuple[theory.SpecificPitch, theory.SpecificPitch]:
        up_shift = down_shift = theory.Interval.get("P8")
        pitch_min = specific_pitches[0] - down_shift
        pitch_max = specific_pitches[-1] + up_shift

        return pitch_min, pitch_max

    @staticmethod
    def get_bass_paths(
        bass_root_note: theory.SpecificPitch,
        chosen_chord: theory.GenericChord,
        groove_units: int,
    ) -> list[list[theory.SpecificPitch]]:
        third_interval = chosen_chord.get_interval(1)
        fifth_interval = chosen_chord.get_interval(2)
        if groove_units == 1:
            return [[bass_root_note]]
        elif groove_units % 2 == 0:
            multiplier = groove_units // 2
            # duplicated prospects reduce the probability of non-duplicated prospects
            prospects = [
                [bass_root_note, bass_root_note] * multiplier,
                [bass_root_note, bass_root_note + third_interval] * multiplier,
                [bass_root_note, bass_root_note + third_interval] * multiplier,
                [bass_root_note, bass_root_note - theory.Interval.get("m3")]
                * multiplier,
                [bass_root_note, bass_root_note - theory.Interval.get("m3")]
                * multiplier,
            ]
            if fifth_interval != "d5":
                prospects.extend(
                    [
                        [bass_root_note, bass_root_note + fifth_interval] * multiplier,
                        [bass_root_note, bass_root_note + fifth_interval] * multiplier,
                        [bass_root_note, bass_root_note - (~fifth_interval)]
                        * multiplier,
                        [bass_root_note, bass_root_note - (~fifth_interval)]
                        * multiplier,
                    ]
                )
                if groove_units == 4:
                    additional_walks = [
                        [
                            bass_root_note,
                            bass_root_note + third_interval,
                            bass_root_note + fifth_interval,
                            bass_root_note,
                        ],
                        [
                            bass_root_note,
                            bass_root_note + third_interval,
                            bass_root_note + fifth_interval,
                            bass_root_note + fifth_interval,
                        ],
                        [
                            bass_root_note,
                            bass_root_note + theory.Interval.get("M2"),
                            bass_root_note + third_interval,
                            bass_root_note + fifth_interval,
                        ],
                        [
                            bass_root_note,
                            bass_root_note - (~fifth_interval),
                            bass_root_note - (~third_interval),
                            bass_root_note - (~fifth_interval),
                        ],
                        [
                            bass_root_note,
                            bass_root_note - theory.Interval.get("M2"),
                            bass_root_note - theory.Interval.get("M3"),
                            bass_root_note - (~fifth_interval),
                        ],
                    ]
                    prospects.extend(additional_walks)
            return prospects
        elif groove_units == 3:
            prospects = [
                [bass_root_note, bass_root_note, bass_root_note],
                [bass_root_note, bass_root_note + third_interval, bass_root_note],
                [bass_root_note, bass_root_note + third_interval, bass_root_note],
                [
                    bass_root_note,
                    bass_root_note - theory.Interval.get("m3"),
                    bass_root_note,
                ],
                [
                    bass_root_note,
                    bass_root_note - theory.Interval.get("m3"),
                    bass_root_note,
                ],
            ]
            if fifth_interval != "d5":
                prospects.extend(
                    [
                        [
                            bass_root_note,
                            bass_root_note + fifth_interval,
                            bass_root_note,
                        ],
                        [
                            bass_root_note,
                            bass_root_note + fifth_interval,
                            bass_root_note,
                        ],
                        [
                            bass_root_note,
                            bass_root_note - (~fifth_interval),
                            bass_root_note,
                        ],
                        [
                            bass_root_note,
                            bass_root_note - (~fifth_interval),
                            bass_root_note,
                        ],
                        [
                            bass_root_note,
                            bass_root_note,
                            bass_root_note + fifth_interval,
                        ],
                        [
                            bass_root_note,
                            bass_root_note,
                            bass_root_note - (~fifth_interval),
                        ],
                    ]
                )
            return prospects
        else:
            raise ValueError

    def has_bass_walked(
        self,
        bass_walker_prospects: list[list[list[theory.SpecificPitch]]],
        propagate_index: int,
        bass_walker: list[list[theory.SpecificPitch] | None],
        chosen_bass_move: list[theory.SpecificPitch],
    ) -> bool:
        if propagate_index != len(bass_walker) - 1:
            last_bass_note = chosen_bass_move[-1]
            next_bass_note = bass_walker_prospects[propagate_index + 1][0][0]
            transition_leap = abs(chosen_bass_move[-1].value - next_bass_note.value)
            if transition_leap > 7:
                return False

            undesirable_pitches = [
                (last_bass_note + theory.Interval.get("d4")).generic_pitch,
                (last_bass_note + theory.Interval.get("A5")).generic_pitch,
            ]
            if repr(next_bass_note.generic_pitch) in repr(undesirable_pitches):
                return False

        for duplicate_index in self.index_repeats[propagate_index]:
            if len(bass_walker_prospects[duplicate_index][0]) == len(chosen_bass_move):
                bass_walker_prospects[duplicate_index] = [chosen_bass_move]

        return True

    def write_percussion(self) -> None:
        instrument_mapping = {}
        note_loops: list[list[theory.DrumSequence]] = []

        time_sig_repr = str(self._score.time_sig)
        possible_drum_grooves = implement.idioms["drum_grooves"][time_sig_repr]
        chosen_drum_groove = random.choice(possible_drum_grooves)

        for drum_part in chosen_drum_groove:
            note_loops.append([])
            for drum_snippet in drum_part.split("||"):
                drum_sequence = theory.DrumSequence([])
                for drum_item in drum_snippet.split():
                    instrument_id, str_duration = drum_item.split(":")
                    if instrument_id not in instrument_mapping:
                        drum_pitch = random.choice(self.drum_mapping[instrument_id])
                        instrument_mapping[instrument_id] = drum_pitch
                    else:
                        drum_pitch = instrument_mapping[instrument_id]
                    drum_sequence.append(
                        theory.DrumNote(drum_pitch, Fraction(str_duration))
                    )

                note_loops[-1].append(drum_sequence)

        nested_drum_parts: list[list[theory.DrumSequence]] = []
        for note_loop in note_loops:
            nested_drum_parts.append([])
            sequence_iter = itertools.cycle(note_loop)
            for _ in self.time_keeper.structural_nodes:
                current_drum_sequence = next(sequence_iter)
                nested_drum_parts[-1].append(current_drum_sequence)

        groove_duration = self._score.time_sig.groove_duration

        drums_lower_ending = theory.DrumSequence([])
        drums_lower_ending.append(
            theory.DrumNote(instrument_mapping["BD"], groove_duration)
        )
        drums_upper_ending = theory.DrumSequence([f"CYM:{groove_duration}"])

        nested_drum_parts[0][-1] = drums_lower_ending
        nested_drum_parts[1][-1] = drums_upper_ending

        for node_index, structural_node in enumerate(self.time_keeper.structural_nodes):
            if structural_node.modifier == "DRUM_FILL":
                affected_drum_sequence = nested_drum_parts[0][node_index]
                chosen_fill_sequence = theory.DrumSequence(
                    random.choice(implement.idioms["fill_sequences"][time_sig_repr])
                )
                altered_drum_sequence = affected_drum_sequence + chosen_fill_sequence
                nested_drum_parts[0][node_index] = altered_drum_sequence
            elif structural_node.modifier == "CYM_CRASH":
                affected_drum_sequence = nested_drum_parts[1][node_index]
                chosen_crash_sequence = theory.DrumSequence(
                    implement.idioms["crash_sequences"][time_sig_repr]
                )
                altered_drum_sequence = affected_drum_sequence + chosen_crash_sequence
                nested_drum_parts[1][node_index] = altered_drum_sequence

        for nested_drum_part in nested_drum_parts:
            self._score.drum_parts.append([])
            for drum_sequence in nested_drum_part:
                for drum_note in drum_sequence:
                    self._score.drum_parts[-1].append(drum_note)

    def write_accompaniment(self) -> None:
        chosen_instrument = random.choice(instruments_accompaniment)
        print("Chosen chord instrument:", chosen_instrument)
        lowest_pitch = theory.SpecificPitch.get_pitch_from_value(
            max(
                implement.idioms["ACCOMPANIMENT_MIN_PITCH"],
                chosen_instrument.lower_bound,
            )
        )
        highest_pitch = theory.SpecificPitch.get_pitch_from_value(
            min(
                implement.idioms["ACCOMPANIMENT_MAX_PITCH"],
                chosen_instrument.upper_bound,
            )
        )
        instrument_tessitura = theory.Tessitura(lowest_pitch, highest_pitch)

        prospects_cache = {}
        sequence_prospects = []
        for generic_chord in self.chords:
            chord_repr = str(generic_chord)
            if chord_repr not in prospects_cache:
                index_prospects = instrument_tessitura.find_closed_voicings(
                    generic_chord
                )
                prospects_cache[chord_repr] = index_prospects
                sequence_prospects.append(index_prospects.copy())
            else:
                index_prospects = prospects_cache[chord_repr]
                sequence_prospects.append(index_prospects.copy())

        voicing_possibilities = theory.WaveFunction(
            sequence_prospects, self.has_voicing_propagated
        )
        chord_notes = next(iter(voicing_possibilities))

        regular_strum_duration = self._score.time_sig.groove_duration
        half_strum_iter = itertools.cycle(
            [
                Fraction(str_duration)
                for str_duration in self._score.time_sig.groove_pattern
            ]
        )
        for note_cluster, symbol_parent in zip(
            chord_notes, self.time_keeper.symbol_parents
        ):
            for symbol_child in symbol_parent:
                if symbol_child.groove_units == 2:
                    self._score.tonal_parts[(chosen_instrument, 1)].append(
                        theory.SpecificChord(note_cluster, regular_strum_duration)
                    )
                elif symbol_child.groove_units == 1:
                    self._score.tonal_parts[(chosen_instrument, 1)].append(
                        theory.SpecificChord(note_cluster, next(half_strum_iter))
                    )

    @staticmethod
    def has_voicing_propagated(
        voicing_sequence_prospects: list[deque[theory.NoteCluster]],
        propagate_index: int,
        voicing_sequence: list[theory.NoteCluster | None],
        chosen_voicing: theory.NoteCluster,
    ) -> bool:
        accompaniment_range = theory.Interval.get("M9")
        # arbitrary starting point
        global_tessitura = theory.Tessitura(
            theory.SpecificPitch("C0"), theory.SpecificPitch("C15")
        )
        local_tessituras = [global_tessitura for _ in voicing_sequence]

        def has_global_reset(sequence_index: int) -> bool:
            min_pitch = index_prospects[0][0]
            max_pitch = index_prospects[-1][-1]
            local_tessituras[sequence_index] = theory.Tessitura(min_pitch, max_pitch)

            min_bound = index_prospects[0][-1] - accompaniment_range
            max_bound = index_prospects[-1][0] + accompaniment_range
            global_delta = global_tessitura.has_contracted(min_bound, max_bound)

            return global_delta

        sequence_size = len(voicing_sequence)
        for sequence_index in range(sequence_size):
            index_prospects = voicing_sequence_prospects[sequence_index]
            if index_prospects[0].generic_chord == chosen_voicing.generic_chord:
                index_prospects.clear()
                index_prospects.append(chosen_voicing)
            has_global_reset(sequence_index)

        queue = deque(range(sequence_size))
        queue_set = set(queue)

        while queue:
            primary_index = queue.popleft()
            index_prospects = voicing_sequence_prospects[primary_index]
            previous_options_count = len(index_prospects)
            global_tessitura.filter(index_prospects)
            current_options_count = len(index_prospects)

            if previous_options_count != current_options_count:
                if not index_prospects:
                    return False

                if has_global_reset(primary_index):
                    for secondary_index in range(sequence_size):
                        if secondary_index not in queue_set:
                            local_tessitura = local_tessituras[secondary_index]
                            if local_tessitura not in global_tessitura:
                                queue.append(secondary_index)
                                queue_set.add(secondary_index)

            queue_set.remove(primary_index)

        return True
