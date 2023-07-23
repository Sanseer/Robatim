from generate import genre, export


if __name__ == "__main__":
    builder = genre.FolkBuilder()
    builder.write_chord_progression()
    builder.write_bassline()

    builder.write_percussion()
    builder.write_accompaniment()
    export.export_midi(builder._score)
    export.LilypondFactory.export(builder._score)
