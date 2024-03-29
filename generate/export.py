from fractions import Fraction
import math

from generate.midiutil import MIDIFile
from generate import theory


class LilypondFactory:
    duration_cache: dict[Fraction, str] = {}
    specific_pitch_cache: dict[str, str] = {}
    # Midi number 44 technically corresponds to Lilypond "hhp" but "hhc" is visually preferred.
    drum_mapping = {
        35: "bda",
        36: "bd",
        38: "sna",
        40: "sne",
        42: "hhc",
        44: "hhc",
        46: "hho",
        48: "tommh",
        47: "tomml",
        45: "toml",
        43: "tomfh",
        41: "tomfl",
        49: "cymc",
        52: "cymch",
        55: "cyms",
        57: "cymca",
    }

    @staticmethod
    def convert_generic_pitch(input_pitch: theory.GenericPitch) -> str:
        if input_pitch.accidental.value > 0:
            accidental_marker = "is"
        else:
            accidental_marker = "es"
        accidental_repr = accidental_marker * abs(input_pitch.accidental.value)

        return f"{input_pitch.letter.lower()}{accidental_repr}"

    @classmethod
    def convert_specific_pitch(cls, input_pitch: theory.SpecificPitch) -> str:
        input_repr = str(input_pitch)
        if input_repr in cls.specific_pitch_cache:
            return cls.specific_pitch_cache[input_repr]

        generic_pitch_repr = cls.convert_generic_pitch(input_pitch)

        abs_octave_shift = abs(input_pitch.octave - 3)
        if input_pitch.octave > 3:
            octave_mark = "'"
        else:
            octave_mark = ","

        octave_repr = octave_mark * abs_octave_shift
        output_repr = f"{generic_pitch_repr}{octave_repr}"
        cls.specific_pitch_cache[input_repr] = output_repr

        return output_repr

    @classmethod
    def convert_duration(cls, input_duration: Fraction) -> str:
        if input_duration in cls.duration_cache:
            return cls.duration_cache[input_duration]
        if input_duration.numerator == 1 and cls.is_power_of_two(
            input_duration.denominator
        ):
            output_repr = str(input_duration.denominator)
            cls.duration_cache[input_duration] = output_repr
            return output_repr

        halved_fraction = Fraction("1")
        if input_duration >= halved_fraction * 2:
            raise ValueError

        while True:
            if halved_fraction > input_duration:
                halved_fraction /= 2
            else:
                output_repr = str(halved_fraction.denominator)
                current_value = halved_fraction

                while current_value != input_duration:
                    halved_fraction /= 2
                    current_value += halved_fraction
                    output_repr = f"{output_repr}."
                    if current_value > input_duration:
                        raise ValueError

                cls.duration_cache[input_duration] = output_repr
                return output_repr

    @staticmethod
    def is_power_of_two(integer: int) -> bool:
        return math.log(integer, 2).is_integer()

    @classmethod
    def convert_drum_obj(
        cls, input_obj: theory.DrumNote | theory.DrumCluster | theory.RestNote
    ) -> str:
        duration_repr = cls.convert_duration(input_obj.duration)
        if isinstance(input_obj, theory.DrumNote):
            pitch_repr = cls.drum_mapping[input_obj.pitch]
            return f"{pitch_repr}{duration_repr}"
        elif isinstance(input_obj, theory.DrumCluster):
            drum_notes = [cls.drum_mapping[drum_pitch] for drum_pitch in input_obj]
            drum_notes_repr = " ".join(drum_notes)
            # a DrumCluster may have one DrumNote if you merged a DrumNote with a RestNote
            if len(drum_notes) == 1:
                return f"{drum_notes_repr}{duration_repr}"
            else:
                return f"<{drum_notes_repr}>{duration_repr}"
        elif isinstance(input_obj, theory.RestNote):
            return f"r{duration_repr}"

    @classmethod
    def convert_note_cluster(cls, input_cluster: theory.NoteCluster) -> str:
        converted_notes = [
            cls.convert_specific_pitch(input_note) for input_note in input_cluster
        ]
        converted_notes_repr = " ".join(converted_notes)
        return f"<{converted_notes_repr}>"

    @classmethod
    def convert_tonal_obj(
        cls, input_obj: theory.SpecificNote | theory.SpecificChord | theory.RestNote
    ) -> str:
        duration_repr = cls.convert_duration(input_obj.duration)
        if isinstance(input_obj, theory.SpecificNote):
            pitch_repr = cls.convert_specific_pitch(input_obj.specific_pitch)
            return f"{pitch_repr}{duration_repr}"
        elif isinstance(input_obj, theory.SpecificChord):
            note_cluster_repr = cls.convert_note_cluster(input_obj.note_cluster)
            return f"{note_cluster_repr}{duration_repr}"
        elif isinstance(input_obj, theory.RestNote):
            return f"r{duration_repr}"

    @classmethod
    def export(cls, input_score: theory.AbstractScore) -> None:
        note_str_sequences = []
        for _, score_part in input_score.tonal_parts.items():
            note_str_sequences.append(
                [cls.convert_tonal_obj(sound_obj) for sound_obj in score_part]
            )

        time_sig_repr = str(input_score.time_sig)
        drum_note_sequences = []
        for drum_part in input_score.drum_parts:
            drum_note_sequences.append(
                [cls.convert_drum_obj(drum_obj) for drum_obj in drum_part]
            )
        if time_sig_repr == "7/8":
            drum_note_sequences[0].insert(
                0, r"\set Timing.beamExceptions = #'() \set Timing.beatStructure = 3,4"
            )

        with open("logs/template.txt", "r") as sheet_file:
            output_string = sheet_file.read()
        tonic_designator = cls.convert_generic_pitch(input_score.major_scale[0])
        output_string = output_string.replace("KEY_SIG", tonic_designator)

        output_string = output_string.replace(
            "BASS_NOTES", " ".join(note_str_sequences[0])
        )
        output_string = output_string.replace(
            "CHORD_NOTES", " ".join(note_str_sequences[1])
        )
        output_string = output_string.replace(
            "DRUMS_LOWER_NOTES", " ".join(drum_note_sequences[0])
        )
        output_string = output_string.replace(
            "DRUMS_UPPER_NOTES", " ".join(drum_note_sequences[1])
        )

        output_string = output_string.replace("TIME_SIG", time_sig_repr)
        print(f"Using {input_score.time_sig} time")

        with open("logs/output.txt", "w") as sheet_file:
            sheet_file.write(output_string)

    @classmethod
    def export_score(cls, input_score: theory.AbstractScore) -> None:
        with open("logs/custom.txt", "r") as sheet_file:
            output_string = sheet_file.read()
        tonic_designator = cls.convert_generic_pitch(input_score.minor_scale[0])
        space_chr = " "
        voice_parts_markup = []

        all_part_settings = {
            0: [
                f"\\time {input_score.time_sig}",
                '\\clef "bass"',
                "\\ottava #-1",
            ],
            1: ['\\clef "alto"'],
        }
        for part_index, (_, score_part) in enumerate(input_score.tonal_parts.items()):
            part_sequence = [f"\\key {tonic_designator} \\minor"]
            part_sequence.extend(all_part_settings[part_index])
            part_sequence.extend(
                cls.convert_tonal_obj(sound_obj) for sound_obj in score_part
            )

            part_repr = " ".join(part_sequence)

            voice_part_markup = [
                f"{space_chr * 6}\\new Staff <<",
                f"{space_chr * 8}\\new Voice {{ {part_repr} }}",
                f"{space_chr * 6}>>",
            ]
            voice_parts_markup.append("\n".join(voice_part_markup))

        output_string = output_string.replace(
            "VOICE_PARTS", "\n".join(voice_parts_markup[::-1])
        )

        with open("logs/output.txt", "w") as sheet_file:
            sheet_file.write(output_string)


def export_midi(input_score: theory.AbstractScore) -> None:
    TICKS_PER_QUARTERNOTE = 960
    # Don't forget about percussion
    NUMBER_OF_TRACKS = len(input_score.tonal_parts) + 1
    new_midi = MIDIFile(
        numTracks=NUMBER_OF_TRACKS,
        ticks_per_quarternote=TICKS_PER_QUARTERNOTE,
        eventtime_is_ticks=True,
    )
    new_midi.addTempo(0, 0, input_score.tempo)
    track = 0
    channel = 0
    time = 0

    time_sig_beats = {"4/4": "1", "7/8": "1", "12/8": "2/3", "6/8": "2/3", "3/4": "1"}
    beats_per_quarter_note = Fraction(time_sig_beats[str(input_score.time_sig)])

    def get_tick_duration(metric_duration: Fraction) -> int:
        return int(metric_duration * 4 * beats_per_quarter_note * TICKS_PER_QUARTERNOTE)

    for (instrument, _), score_part in input_score.tonal_parts.items():
        new_midi.addProgramChange(track, channel, 0, instrument.number)
        for sound_obj in score_part:
            tick_duration = get_tick_duration(sound_obj.duration)

            if isinstance(sound_obj, theory.SpecificNote):
                new_midi.addNote(
                    track,
                    channel,
                    sound_obj.specific_pitch.value,
                    time,
                    tick_duration,
                    115,
                )
            elif isinstance(sound_obj, theory.SpecificChord):
                for specific_pitch in sound_obj.note_cluster:
                    new_midi.addNote(
                        track, channel, specific_pitch.value, time, tick_duration, 80
                    )
            time += tick_duration

        track += 1
        channel += 1
        time = 0

    channel = 9
    for drum_part in input_score.drum_parts:
        for drum_obj in drum_part:
            tick_duration = get_tick_duration(drum_obj.duration)
            if isinstance(drum_obj, theory.DrumNote):
                new_midi.addNote(
                    track, channel, drum_obj.pitch, time, tick_duration, 100
                )
            elif isinstance(drum_obj, theory.DrumCluster):
                for drum_pitch in drum_obj:
                    new_midi.addNote(
                        track, channel, drum_pitch, time, tick_duration, 100
                    )
            time += tick_duration
        time = 0

    try:
        with open("logs/output.mid", "wb") as output_file:
            new_midi.writeFile(output_file)
    except PermissionError:
        print("Close the midi file and try again.")
