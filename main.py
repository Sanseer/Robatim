#!/usr/bin/env python3

import random

from generate.midi_export import MIDIFile

from generate.voices.voice import Voice
from generate.voices.bass import Bass
from generate.voices.upper_voices2 import UpperVoices, Tenor, Alto
from generate.voices.soprano2 import Soprano
import generate.idioms.basics as idms_b

# write tests in keyboard and chorale style to try custom chord progressions

def random_settings(time_sig="", tonic="", mode=""):
	"""Selects a random, but practical key and time sig unless one is provided"""
	tonic, mode = random.choice((("C", "ionian"), ("A", "aeolian")))
	if not mode:
		mode = random.choice(("ionian", "aeolian"))
	if mode == "ionian" and not tonic:
		tonic =  random.choice(idms_b.major_keys)
	elif mode == "aeolian" and not tonic:
		tonic = random.choice(idms_b.minor_keys)
	if not time_sig:
		time_sig = random.choice(idms_b.time_sigs)

	return time_sig, tonic, mode

def create_song():
	"""Creates a tune with chorale style and period form"""
	voice_list = []
	# voice_list.append(Bass(*random_settings()))
	voice_list.append(Bass())
	voice_list[0].create_part()

	UpperVoices().create_parts()
	voice_list.append(Tenor())
	voice_list[-1].create_part()
	voice_list.append(Alto())
	voice_list[-1].create_part()

	voice_list.append(Soprano())
	voice_list[-1].do_stuff()
	voice_list[-1].create_part()
	make_lily_file()
	return voice_list

def create_tune():
	voice_list = []
	voice_list.append(Bass())
	voice_list[0].create_part()

	UpperVoices().create_parts()
	voice_list.append(Tenor())
	voice_list[-1].create_part()
	voice_list.append(Alto())
	voice_list[-1].create_part()
	voice_list.append(Soprano())
	voice_list[-1].create_part()
	make_lily_file()
	return voice_list
	# voice_list.append(Soprano())
	# voice_list[-1].create_part()



def make_lily_file():
	"""Creates a LilyPond sheet music file"""
	# make four clefs instead of two (add alto and tenor)
	if Voice.mode == "ionian":
		mode = "major "
	elif Voice.mode == "aeolian":
		mode = "minor "
	if Voice.beat_division == 3:
		time_sig = "/".join([str(Voice.measure_length * 3),"8"])
	elif Voice.beat_division == 2:
		time_sig = "/".join([str(Voice.measure_length),"4"])
	# Append chord symbols
	title = " ".join(("Chorale in", Voice.tonic, mode.replace(" ","")))
	with open("old_layout.txt", 'r') as f:
		new_file = f.read()

	for part in Voice.lily_parts:
		new_file = new_file.replace("PART_SLOT", "\\key " + 
			Voice.tonic.replace("#","is").replace("b","es").lower() 
			+ " \\" + mode + "\\time " + time_sig + " " + part, 1)
	new_file = new_file.replace("PART_SLOT", "")
	new_file = new_file.replace("Chorale", title)
	with open("new_layout.txt", 'w') as f:
		f.write(new_file)	


if __name__ ==  "__main__":
	voice_list = create_tune()
	track    = 0
	channel  = 0
	time     = 0   # In beats
	volume   = 100 # 0-127, as per the MIDI standard

	# make soprano louder than lower voices
	MyMIDI = MIDIFile(4) 

	# [MyMIDI.addProgramChange(track,ch,time,52) for ch in range(4)]
	MyMIDI.addProgramChange(track,0,time,42)
	MyMIDI.addProgramChange(track,1,time,41) 
	MyMIDI.addProgramChange(track,2,time,41) 
	MyMIDI.addProgramChange(track,3,time,40) 
	#42-40-41-22
	#42-40-40-41
	#42-41-41-40
 
	if Voice.mode == "aeolian":
		tempo = 110
	elif Voice.mode == "ionian":
		tempo = 120
	MyMIDI.addTempo(0,0,tempo)

	# optional slow ending except whole note on measure 7
	if Voice.measure_rhythms[-2][-1] not in {3,4}:
		if Voice.measure_length == 4:
			MyMIDI.addTempo(track, 26, tempo * .9)
		elif Voice.measure_length == 3:
			MyMIDI.addTempo(track, 20, tempo * .9)


	for part in voice_list:
		time = 0
		for pitch, duration in zip(part.notes, part.groove):
			if type(duration) == int or type(duration) == float:
				MyMIDI.addNote(track, channel, pitch, time, duration, volume)
				time = time + duration
			elif type(duration) == str:
				rest = int(duration[-1])
				time = time + rest
		channel += 1

	with open("chorale0.mid", "wb") as output_file:
	    MyMIDI.writeFile(output_file)