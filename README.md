# Robatim

Robatim is a deterministic music generator that uses recursive depth-first search and breadth-first search. [Video Demonstration](https://youtu.be/EYrInLi0P-Q). The style of music is based on Renaissance dance books I found on IMSLP (e.g., Terpsichore, Musarum Aoniarum and Danceries, Livre 2). I also consulted a secondary literature reference on the topic (Peter Schubert's Modal Counterpoint). 


## Requirements

- Python 3.10+

## Setup (User)

Because this repository is a script rather than a package, it must be cloned/downloaded rather than installed. 

```
git clone https://github.com/Sanseer/Robatim
```

Download [dance.json](https://gist.github.com/Sanseer/58f838bab2bedb8a311a86fe65a65c56) and put it in the main directory.

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
- Dave Smith et al.: for inventing MIDI  