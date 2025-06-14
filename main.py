import random

from generate import dance, export, limits, source, theory


idioms = source.idioms
voice_names = ("bassus", "tenor", "contratenor", "superius")

if __name__ == "__main__":
    clef_group = random.choice(idioms["clef_groups"])
    print(f"{clef_group = }")
    voice_tessituras = {}

    for clef_name, voice_name in zip(clef_group, voice_names):
        pitch_min_str, pitch_max_str = idioms["clef_ranges"][clef_name]
        voice_tessituras[voice_name] = theory.Tessitura(
            theory.SpecificPitch(pitch_min_str),
            theory.SpecificPitch(pitch_max_str),
        )
        idioms["intermediate_cadances"][voice_name].extend(
            idioms["final_cadances"][voice_name]
        )

    mode_group = random.choice(idioms["available_keys"])
    tonic_pitch_str, chosen_mode_str = mode_group[0]
    proxy_mode = theory.scale_type_map[chosen_mode_str](tonic_pitch_str)
    flattened_pitch = proxy_mode.flattened_pitch
    all_full_voice_measures = dance.get_full_measure_sequences(
        proxy_mode, voice_tessituras, flattened_pitch.letter
    )

    dance_constructors = [dance.get_branle_simple, dance.get_basse_danse]
    dance_constructor = random.choice(dance_constructors)
    print(f"Using {dance_constructor.__name__}")
    while True:
        try:
            tonic_pitch_str, chosen_mode_str = random.choice(mode_group)
            primary_mode = theory.scale_type_map[chosen_mode_str](tonic_pitch_str)
            dance_score = dance_constructor(
                clef_group,
                voice_tessituras,
                primary_mode,
                flattened_pitch,
                all_full_voice_measures,
            )
            break
        except limits.CompositionError as err:
            print(f"{err} Reattempting.\n")
        except dance.CadentialError as err:
            print(f"{err} Reattempting.\n")
            _, tonic_pitch_str, chosen_mode_str = err.args
            mode_group.remove([tonic_pitch_str, chosen_mode_str])

    export.LilypondFactory.export_dance_score(dance_score)
    export.export_dance_midi(dance_score)
