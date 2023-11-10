from generate import export, vgm


if __name__ == "__main__":
    composer = vgm.Composer()
    composer.fill_score()
    export.export_midi(composer.score)
    export.LilypondFactory.export_score(composer.score)
