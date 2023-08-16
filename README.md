# Robatim

Robatim is a deterministic music generator based on wave function collapse. [Video Demonstration](https://www.youtube.com/watch?v=eQ8Ll_BAHo0).

## Requirements

- Python 3.10+

## Setup (User)

Because this repository is a script rather than a package, it must be cloned rather than installed. 

```
git clone https://github.com/Sanseer/Robatim
```

Download [idioms.json](https://gist.github.com/Sanseer/6e9c06cdffb8bc630cbd42b4fb89cb82) and put it in the main directory.

## Usage 

```
python main.py
```

1. Running the main file generates two files within the logs directory: output.mid and output.txt
2. output.mid: This is the audio file  
3. output.txt: This is Lilypond code that can be used to generate a pdf of the sheet music 

## Setup (Developer)

If you wish to modify the repository, additional steps are recommended. After setting up the user environment, perform the following actions to setup the developer environment:

```
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

## Credits

- [MidiUtil](https://github.com/MarkCWirt/MIDIUtil): Midi file creation in Python
- [Lilypond](https://github.com/lilypond/lilypond): Music engraving from text input
- [MidiEditor](https://github.com/markusschwenk/midieditor): for helping me understand how MIDI works
- [Martin Donald](https://www.youtube.com/watch?v=2SuvO4Gi7uY): for the inspiration for the wave function collapse algorithm
- [Trevor0402](https://www.doomworld.com/forum/topic/118828-trevor0402s-sc-55-soundfont/): Midi soundfont used in video demonstration
- Dave Smith et al.: for inventing MIDI  