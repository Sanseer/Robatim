"""This program creates a short four-part tune using period form 
from the classical style. It creates a chord progression (bass),
picks a rhythm, and then adds the remaining voices using 
the conventions of counterpoint and voice leading. 
The rhythm is embellished, the sheet music created, and the MIDI file exported."""

import random

from midiutil import MIDIFile

from voice import Voice
from bass import Bass
from soprano import Soprano
from alto_tenor import MiddleVoices, Alto, Tenor
import idioms as idms

def random_settings(time_sig="", tonic="", mode=""):
	"""Selects a random, but practical key and time sig unless one is provided"""
	if not mode:
		mode = random.choice(["ionian", "aeolian"])
	if mode == "ionian" and not tonic:
		tonic =  random.choice(tuple(idms.major_accidentals.keys()))
	elif mode == "aeolian" and not tonic:
		tonic = random.choice(tuple(idms.minor_accidentals.keys()))
	if not time_sig:
		time_sig = random.choice(idms.time_sigs)

	return time_sig, tonic, mode


def create_song(parts=4):
	"""Creates up to four voices sequentially"""
	song_notes = []
	if parts >= 1:
		song_notes.append(Bass(*random_settings()).create_part())
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
	"""Creates a lilyPond file using a pre-defined layout"""
	if Voice.mode == "ionian":
		mode = "major "
	elif Voice.mode == "aeolian":
		mode = "minor "
	if Voice.beat_division == 3:
	# For some reason, LilyPond doesn't correspond with regular time sigs
		time_sig = "/".join([str(Voice.measure_length * 3),"12"])
	elif Voice.beat_division == 2:
		time_sig = "/".join([str(Voice.measure_length),"4"])
	title = " ".join(["Cantus in", Voice.tonic, mode.replace(" ","")])
	with open("old_layout.txt", 'r') as f:
		new_file = f.read()

	for part in Voice.lily_parts:
		new_file = new_file.replace("PART_SLOT", "\\key " + 
			Voice.tonic.replace("#","is").replace("b","es").lower() 
			+ " \\" + mode + "\\time " + time_sig + " " + part, 1)
	new_file = new_file.replace("PART_SLOT", "")
	new_file = new_file.replace("Symphony", title)
	with open("new_layout.txt", 'w') as f:
		f.write(new_file)	


if __name__ ==  "__main__":
	song_degrees = create_song(4)
	program = 73
	track    = 0
	channel  = 0
	time     = 0   # In beats
	volume   = 100 # 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(4) # One track, defaults to format 1 (tempo track
	                     # automatically created)
	# for ch in range(4):
	# 	MyMIDI.addProgramChange(track, ch, time, program)
	[MyMIDI.addProgramChange(track,ch,time,program) for ch in range(4)]

	if Voice.mode == "aeolian":
		tempo = 110
	elif Voice.mode == "ionian":
		tempo = 120
	MyMIDI.addTempo(0,0,tempo)

	# optional slow ending
	if Voice.measure_length == 4:
		MyMIDI.addTempo(track, 26, tempo * .9)
	elif Voice.measure_length == 3:
		MyMIDI.addTempo(track, 20, tempo * .9)

	# index = 0
	for part in song_degrees:
		Voice.create_rests(part)
		time = 0
		for pitch, duration in zip(part, Voice.note_values):
			if type(duration) == int:
				MyMIDI.addNote(track, channel, pitch, time, duration, volume)
				time = time + duration
			elif type(duration) == str:
				rest = int(duration[-1])
				time = time + rest
		channel += 1

	with open("my_song0.mid", "wb") as output_file:
	    MyMIDI.writeFile(output_file)