import random
import json
import requests
import time

from generate.midi_export import MIDIFile
from generate.voices.voice import Voice
from generate.voices.melody import Melody
import generate.voices.chorale as chorale

def make_lily_file():
	"""Generate Lilypond file from musical sequence"""

	if Voice.mode == "ionian":
		mode = "major"
	elif Voice.mode == "aeolian":
		mode = "minor"

	if Voice.beat_division == 3:
		time_sig = f"{Voice.measure_length * 3}/8"
	elif Voice.beat_division == 2:
		time_sig = f"{Voice.measure_length}/4"
	title = f"Medley in {Voice.tonic} {mode}"

	with open("logs/old_layout.txt", 'r') as f:
		sheet_code = f.read()

	for lily_part in Voice.lily_score:
		sheet_code = sheet_code.replace(
			"PART_SLOT", " ".join(["\\key", 
			Voice.tonic.replace('#','is').replace('b',"es").lower(),
			f"\\{mode} \\time {time_sig} {lily_part}"]), 1)

	sheet_code = sheet_code.replace("PART_SLOT", "")
	sheet_code = sheet_code.replace("Medley", title)

	with open("logs/new_layout.txt", 'w') as f:
		f.write(sheet_code)

	try:
		make_score_pdf(sheet_code)
	except PermissionError:
		print("You must close out the previous pdf to overwrite it.")
	except requests.exceptions.ConnectionError:
		print("Must be connected to internet to create pdf.")

def make_score_pdf(sheet_code):
	"""Generate sheet music pdf from lilyPond format"""

	payload = {
		"version": "stable", "code": sheet_code, "id": ""
	}
	# AWS can't parse python dictionaries
	with open("payload.json", 'w') as f:
		json.dump(payload, f)
	with open("payload.json", 'rb') as f:
		sheet_music_response = requests.post(
			"https://7icpm9qr6a.execute-api.us-west-2.amazonaws.com/prod/prepare_preview/stable", data=f)

	time.sleep(1)
	response_id = sheet_music_response.json()["id"]

	pdf_response = requests.get(
		f"https://s3-us-west-2.amazonaws.com/lilybin-scores/{response_id}.pdf")

	with open("final_score.pdf", "wb") as f:
		f.write(pdf_response.content)

def reset_score_settings():
	"""Reset parameters to allow new score generation"""
	Voice.chord_sequence = []
	Voice.all_midi_pitches = []
	Voice.midi_score = []
	Voice.lily_score = []
	Voice.chorale_scale_degrees = []

	Voice.pickup = False
	Voice.pickup_duration = 0
	Voice.bass_motion = []
	Voice.tenor_motion = []
	Voice.alto_motion = []
	Voice.soprano_motion = []


if __name__ == "__main__":
	track = 0
	current_time = 0
	channel = 0
	tempo = 60  # In BPM
	# volume 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(5, eventtime_is_ticks=True) 
	# defaults to format 1 (tempo track automatically created)

	MyMIDI.addProgramChange(track, channel, current_time, 73)
	MyMIDI.addProgramChange(1, 1, current_time, 32)
	MyMIDI.addProgramChange(2, 2, current_time, 32)
	MyMIDI.addProgramChange(3, 3, current_time, 32)
	MyMIDI.addProgramChange(4, 3, current_time, 32)

	while True:
		try:
			reset_score_settings()
			Melody().make_melody()
			chorale.Chorale().create_parts()
			chorale.Bass().create_part()
			chorale.Tenor().create_part()
			chorale.Alto().create_part()
			chorale.Soprano().create_part()
			break
		except AssertionError:
			print("Restarting...\n")
			continue
			
	for new_note in Voice.midi_score[0]:
		if isinstance(new_note.pitch, int):
			MyMIDI.addNote(track, channel, *new_note, 100)


	strum_ending = random.choice((True, True, False))
	print(f"Strum ending: {strum_ending}")
	if strum_ending:
		time_shift = 0
		for voice_index, part in enumerate(Voice.midi_score[2:], 2):
			time_shift += 90
			old_midi_obj = Voice.midi_score[voice_index][-2]
			new_midi_obj = Voice.Note(
				old_midi_obj.pitch, old_midi_obj.time + time_shift, 
				old_midi_obj.duration)
			Voice.midi_score[voice_index][-2] = new_midi_obj

	for voice_index, part in enumerate(Voice.midi_score[1:]):
		track += 1
		channel += 1
		volume = Voice.voice_volumes[voice_index]
		for new_note in part:
			if isinstance(new_note.pitch, int): 
				MyMIDI.addNote(track, channel, *new_note, volume)

	if Voice.mode == "aeolian":
		tempo = random.choice(range(85, 101))
	elif Voice.mode == "ionian":
		tempo = random.choice(range(85, 111))
	MyMIDI.addTempo(track, current_time, tempo)

	slow_ending = random.choice((True, False))
	if slow_ending:
		if Voice.repeat_ending:
			measure_mark = 16
		else:
			measure_mark = 13
		MyMIDI.addTempo(
			0, Voice.pickup_duration + Voice.max_note_duration * measure_mark, tempo * 0.93)
	print(f"Slow ending? {slow_ending}")
	print(f"Tempo: {tempo}")

	try:
		with open("song0.mid", "wb")  as output_file:
			MyMIDI.writeFile(output_file)
	except PermissionError:
		print("You must close the previous midi file to overwrite it.")

	make_lily_file()









