import random

from generate.midi_export import MIDIFile
from generate.voices.voice import Voice
from generate.voices.melody import Melody
import generate.voices.chorale as chorale


if __name__ == "__main__":
	track    = 0
	time     = 0
	channel  = 0
	tempo    = 60  # In BPM
	volume   = 100 # 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(5, eventtime_is_ticks=True) # One track, defaults to format 1 (tempo track
	                     # automatically created)
	MyMIDI.addProgramChange(track, channel, time, 73)
	# 77, 73! 72 71 70!
	MyMIDI.addProgramChange(1, 1, time, 63)
	MyMIDI.addProgramChange(2, 2, time, 63)
	MyMIDI.addProgramChange(3, 3, time, 63)

	Melody().make_melody()
	for new_note in Voice.midi_score[0]:
		MyMIDI.addNote(track, channel, *new_note, 100)

	chorale.Chorale().create_parts()
	chorale.Bass().create_part()
	chorale.Tenor().create_part()
	chorale.Alto().create_part()
	chorale.Soprano().create_part()
	for part in Voice.midi_score[1:]:
		track += 1
		channel += 1
		for new_note in part:
			MyMIDI.addNote(track, channel, *new_note, 60)

	if Voice.mode == "aeolian":
		tempo = random.choice(range(70, 101))
	elif Voice.mode == "ionian":
		tempo = random.choice(range(80, 111))
	MyMIDI.addTempo(track,time, tempo)

	print(Voice.mode)
	print(f"{Voice.measure_length} beats divided by {Voice.beat_division}")
	print(tempo)

	with open("song0.mid", "wb")  as output_file:
		MyMIDI.writeFile(output_file)

	def make_lily_file():

		if Voice.mode == "ionian":
			mode = "major"
		elif Voice.mode == "aeolian":
			mode = "minor"

		if Voice.beat_division == 3:
			time_sig = f"{Voice.measure_length * 3}/8"
		elif Voice.beat_division == 2:
			time_sig = f"{Voice.measure_length}/4"
		title = f"Medley in {Voice.tonic} {mode}"

		with open("old_layout.txt", 'r') as f:
			new_file = f.read()

		for lily_part in Voice.lily_score:
			new_file = new_file.replace(
				"PART_SLOT", " ".join(["\\key", 
				Voice.tonic.replace('#','is').replace('b',"es").lower(),
				f"\\{mode} \\time {time_sig} {lily_part}"]), 1)

		new_file = new_file.replace("PART_SLOT", "")
		new_file = new_file.replace("Medley", title)

		with open("new_layout.txt", 'w') as f:
			f.write(new_file)

	make_lily_file()









