import copy
import random

from generate import dance, export, limits, source, theory


idioms = source.idioms
voice_names = ("bassus", "tenor", "contratenor", "superius")

if __name__ == "__main__":
    clef_group = random.choice(idioms["clef_groups"])
    print(f"{clef_group = }")
    voice_tessituras = {}
    idioms["mixed_cadences"] = copy.deepcopy(idioms["final_cadences"])

    for clef_name, voice_name in zip(clef_group, voice_names):
        pitch_min_str, pitch_max_str = idioms["clef_ranges"][clef_name]
        voice_tessituras[voice_name] = theory.Tessitura(
            theory.SpecificPitch(pitch_min_str),
            theory.SpecificPitch(pitch_max_str),
        )
        idioms["mixed_cadences"][voice_name].extend(
            idioms["intermediate_cadences"][voice_name]
        )

    mode_group = random.choice(idioms["available_keys"])
    tonic_pitch_str, chosen_mode_str = mode_group[0]
    proxy_mode = theory.scale_type_map[chosen_mode_str](tonic_pitch_str)
    all_full_voice_measures = dance.get_full_measure_sequences(
        proxy_mode, voice_tessituras
    )

    dance_name = random.choice(list(idioms["form"].keys()))
    print(f"{dance_name = }")
    config_sections = dance.get_config_sections(dance_name)
    for config_section in config_sections:
        for partial_config in config_section:
            print(partial_config)
        print()
    global_spec = dance.GlobalSpec(
        dance_name,
        clef_group,
        voice_tessituras,
        all_full_voice_measures,
    )

    while True:
        tonic_pitch_str, chosen_mode_str = random.choice(mode_group)
        primary_mode = theory.scale_type_map[chosen_mode_str](tonic_pitch_str)
        solution_spec = dance.SolutionSpec(primary_mode, config_sections)
        solver = dance.DanceSolver(global_spec, solution_spec)
        try:
            dance_score = solver.solve()
            break
        except limits.ImprobableError as err:
            print(f"{err} Reattempting.\n")
        except dance.ImpossibleError as err:
            print(f"{err} Reattempting.\n")
            _, tonic_pitch_str, chosen_mode_str = err.args
            mode_group.remove([tonic_pitch_str, chosen_mode_str])

    export.LilypondFactory.export_dance_score(global_spec.score_name, dance_score)
    export.export_dance_midi(dance_score)
