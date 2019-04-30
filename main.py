import random

from midiutil import MIDIFile

from voice import *
from bass import *
from soprano import *
from alto_tenor import *
from idioms import *

def random_key(tonic="", mode=""):
	"""Selects a random but practical key unless one is provided"""
	if not mode:
		mode = random.choice(["ionian", "aeolian"])
	if mode == "ionian" and (not tonic):
		tonic =  random.choice(tuple(major_scales.keys()))
	elif mode == "aeolian" and (not tonic):
		tonic = random.choice(tuple(minor_scales.keys()))
	return tonic, mode


def create_song(parts=4):
	"""Creates a basic antecedent/consequent phrase"""
	song_notes = []
	if parts >= 1:
		song_notes.append(Bass(*random_key()).create_part())
	if parts >= 2:
		song_notes.append(Soprano().create_part())
	if parts >= 3:
		MiddleVoices().create_parts()
		song_notes.append(Alto().create_part())
	if parts >= 4:
		song_notes.append(Tenor().create_part())
	print(Voice.chord_symbols)
	make_lily_file()
	return song_notes

def make_lily_file():
	"""Creates a lilyPond file"""
	if Voice.mode == "ionian":
		mode = "major "
	elif Voice.mode == "aeolian":
		mode = "minor "
	title = " ".join(["Cantus in", Voice.tonic, mode.replace(" ","")])
	with open("old_layout.txt", 'r') as f:
		new_file = f.read()

	for part in Voice.lily_parts:
		new_file = new_file.replace("PART_SLOT", "\\key " + 
			Voice.tonic.replace("#","is").replace("b","es").lower() 
			+ " \\" + mode + part, 1)
	new_file = new_file.replace("PART_SLOT", "")
	new_file = new_file.replace("Symphony", title)
	with open("new_layout.txt", 'w') as f:
		f.write(new_file)	


if __name__ ==  "__main__":
	song_degrees = create_song(4)
	program = 48
	track    = 0
	channel  = 0
	time     = 0   # In beats
	volume   = 100 # 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(4) # One track, defaults to format 1 (tempo track
	                     # automatically created)

	for ch in range(4):
		MyMIDI.addProgramChange(track, ch, time, program)

	if Voice.mode == "aeolian":
		tempo = 110
	elif Voice.mode == "ionian":
		tempo = 120
	MyMIDI.addTempo(0,0,tempo)

	# optional slow ending
	if random.choice((0,1)) == 1:
		MyMIDI.addTempo(track, 26, tempo * .9)

	index = 0
	for part in song_degrees:
		time = 0
		index = 0
		for pitch, duration in zip(part, Voice.note_values):
		    MyMIDI.addNote(track, channel, pitch, time, duration, volume)
		    time = time + (Voice.note_values[index]) 
		    index += 1
		channel += 1

	with open("my_song0.mid", "wb") as output_file:
	    MyMIDI.writeFile(output_file)