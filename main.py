import random
import json
import requests

from generate.midi_export import MIDIFile
from generate.voices.voice import Voice
from generate.voices.melody import Melody
import generate.voices.chorale as chorale

def make_lily_file():
	"""Generate Lilypond file from musical piece"""

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

def make_sheet_music():
	"""Generate sheet music pdf of musical piece"""
	with open("new_layout.txt", 'r') as f:
		sheet_code = f.read()

	payload = {
		"version": "stable", "code": sheet_code, "id": ""
	}
	# AWS can't parse python dictionaries for json objects
	with open("payload.json", 'w') as f:
		json.dump(payload, f)
	with open("payload.json", 'r') as f:
		sheet_music_response = requests.post(
			"https://7icpm9qr6a.execute-api.us-west-2.amazonaws.com/prod/prepare_preview/stable", data=f)

	response_id = sheet_music_response.json()["id"]

	pdf_response = requests.get(
		f"https://s3-us-west-2.amazonaws.com/lilybin-scores/{response_id}.pdf")

	with open("final_score.pdf", "wb") as f:
		f.write(pdf_response.content)

if __name__ == "__main__":
	track    = 0
	time     = 0
	channel  = 0
	tempo    = 60  # In BPM
	# volume   = 100 # 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(5, eventtime_is_ticks=True) # One track, defaults to format 1 (tempo track
	                     # automatically created)
	MyMIDI.addProgramChange(track, channel, time, 73)
	# 77, 73! 72 71 70!
	# choose instruments randomly?
	# but keep adjacent voices close in midi numbers
	MyMIDI.addProgramChange(1, 1, time, 43)
	MyMIDI.addProgramChange(2, 2, time, 42)
	MyMIDI.addProgramChange(3, 3, time, 41)
	MyMIDI.addProgramChange(4, 3, time, 40)
	# test that all selected instruments can hit the notes 
	# of that vocal range
	# create list of available instruments per voice

	Melody().make_melody()
	for new_note in Voice.midi_score[0]:
		MyMIDI.addNote(track, channel, *new_note, 100)

	chorale.Chorale().create_parts()
	chorale.Bass().create_part()
	chorale.Tenor().create_part()
	chorale.Alto().create_part()
	chorale.Soprano().create_part()

	for voice_index, part in enumerate(Voice.midi_score[1:]):
		track += 1
		channel += 1
		volume = Voice.voice_volumes[voice_index]
		for new_note in part:
			MyMIDI.addNote(track, channel, *new_note, volume)

	if Voice.mode == "aeolian":
		tempo = random.choice(range(80, 101))
	elif Voice.mode == "ionian":
		tempo = random.choice(range(80, 111))
	MyMIDI.addTempo(track,time, tempo)

	print(Voice.mode)
	print(tempo)

	with open("song0.mid", "wb")  as output_file:
		MyMIDI.writeFile(output_file)


	make_lily_file()
	make_sheet_music()









