import random

from generate import export, dance, limits


if __name__ == "__main__":
    dance_constructors = [dance.get_branle_simple, dance.get_basse_danse]
    dance_constructor = random.choice(dance_constructors)
    print(f"Using {dance_constructor.__name__}")
    while True:
        try:
            dance_score = dance_constructor()
            break
        except limits.CompositionError as err:
            print(f"{err} Reattempting.\n")
    export.LilypondFactory.export_dance_score(dance_score)
    export.export_dance_midi(dance_score)
