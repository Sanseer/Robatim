import random

from generate.midi_export import MIDIFile
from generate.voices.voice import Voice
from generate.voices.melody import Melody


if __name__ == "__main__":
	track    = 0
	time     = 0
	channel  = 0
	tempo    = 60  # In BPM
	volume   = 100 # 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(5, eventtime_is_ticks=True) # One track, defaults to format 1 (tempo track
	                     # automatically created)
	MyMIDI.addTempo(track,time, tempo)
	MyMIDI.addProgramChange(track, channel, time, 73)
	# 77, 73! 72 71 70!

	for new_note in Melody().make_melody():
		MyMIDI.addNote(track, channel, *new_note, 100)

	if Voice.mode == "aeolian":
		tempo = random.choice(range(70, 101))
	elif Voice.mode == "ionian":
		tempo = random.choice(range(80, 111))
	print(Voice.mode)
	MyMIDI.addTempo(0, 0, tempo)
	print(tempo)

	with open("song0.mid", "wb")  as output_file:
		MyMIDI.writeFile(output_file)









