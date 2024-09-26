from generate import export, dance


if __name__ == "__main__":
    dance_score = dance.get_new_score()
    export.LilypondFactory.export_dance_score(dance_score)
    export.export_dance_midi(dance_score)
