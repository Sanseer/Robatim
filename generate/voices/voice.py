import collections
from fractions import Fraction

class Voice:

	chord_sequence = []
	mode = None
	idms_mode = None
	tonic = None
	all_midi_pitches = []
	Note = collections.namedtuple('Note', ["pitch", "time", "duration"])
	midi_score = []
	lily_score = []

	beat_division = []
	measure_length = []

	mode_notes = {
		"lydian": (0, 2, 4, 6, 7, 9, 11),
		"ionian": (0, 2, 4, 5, 7, 9, 11),
		"mixo": (0, 2, 4, 5, 7, 9, 10),
		"dorian": (0, 2, 3, 5, 7, 9, 10),
		"aeolian": (0, 2, 3, 5, 7, 8, 10),
		"phryg": (0, 1, 3, 5, 7, 8, 10) 
	}
	tonics = {
		"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
		"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
	}

	note_letters = ("C","D","E","F","G","A","B")

	note_names = (
		("B#","C","Dbb"), ("B##","C#", "Db"), ("C##", "D", "Ebb"), ("D#","Eb"),
		("D##","E","Fb"), ("E#","F","Gbb"), ("E##","F#", "Gb"), ("F##","G","Abb"), 
		("G#", "Ab"), ("G##","A","Bbb"), ("A#","Bb","Cbb"), ("A##","B","Cb"), 
	)

	simple_beat_durations = {
		4:"1", 3:"2.", 2:"2", 1.5:"4.", 1:"4", 0.75:"8.",
		0.5:"8", 0.375: "16.", 0.25: "16", 0.125: "32", 
	}
	compound_beat_durations = {
		4:"1.", 2:"2.", 4 * Fraction("1/3"):"2", 1:"4.",   
		2 * Fraction("1/3"):"4", 0.5: "8.", 1 * Fraction("1/3"): "8", 
		0.5 * Fraction("1/3"): "16"  
	}

	@staticmethod
	def calculate_slope(move_distance):
		if move_distance < 0:
			return -1
		elif move_distance > 0:
			return 1
		return 0

	@staticmethod
	def has_cross_duplicates(sequence):
		for item1, item2, item3, item4 in zip(
			sequence, sequence[1:], sequence[2:], sequence[3:]):
			if (item1, item2) == (item3, item4):
				return True
		return False

	def set_sheet_notes(self):
		"""Convert midi pitches into sheet music note names"""

		self.logger.warning('=' * 40)
		self.logger.warning("Creating sheet notation")

		tonic_letter = Voice.tonic.replace('#',"").replace('b',"")
		self.logger.warning(f"Tonic letter {tonic_letter}")
		tonic_index = Voice.note_letters.index(tonic_letter)
		for midi_note, scale_degree in zip(
		  self.midi_notes, self.unnested_scale_degrees):
			true_midi_pitch = midi_note.pitch
			self.logger.warning(f"True midi pitch: {true_midi_pitch}")
			scale_midi_pitch =  true_midi_pitch % 12
			possible_note_names = Voice.note_names[scale_midi_pitch]

			self.logger.warning(f"Possible note names: {possible_note_names}")
			note_letter_index = (tonic_index + scale_degree) % 7
			note_letter = Voice.note_letters[note_letter_index]
			octave = true_midi_pitch // 12 - 1

			for possible_note_name in possible_note_names:
				if note_letter in possible_note_name:
					self.sheet_notes.append(f"{possible_note_name}{octave}")
					self.logger.warning(f"Chosen note designation: {possible_note_name}{octave}")
					break

		self.logger.warning(f"Sheet notes: {self.sheet_notes}")


	def make_lily_part(self):
		"""Write sheet music text notation for voice part"""

		note_index = 0
		current_time = 0
		lily_part = []

		for midi_note, sheet_note in zip(self.midi_notes, self.sheet_notes):
			accidental_mark = ""
			octave_mark = ""
			note_letter = sheet_note[0].lower()
			register_shift = 0

			# B# is technically in the octave above (starting from C)
			# Cb is technically in the octave below
			if sheet_note.startswith(("B#","B##")):
				register_shift = -1
			elif sheet_note.startswith(("Cb","Cbb")):
				register_shift = 1
			octave = int(sheet_note[-1]) + register_shift
			if octave < 3:
				octave_shift = 3 - octave
				octave_mark = str(octave_shift * ',')
			elif octave > 3:
				octave_shift = octave - 3
				octave_mark = str(octave_shift * "'")
			if '#' in sheet_note or 'b' in sheet_note:
				accidental_amount = sheet_note.count('#')
				accidental_amount += sheet_note.count('b')
				accidental = sheet_note[1]
				if accidental == '#':
					accidental_mark = "is" * accidental_amount
				elif accidental == 'b':
					accidental_mark = "es" * accidental_amount

			if Voice.beat_division == 2:
				beat_durations = Voice.simple_beat_durations
			elif Voice.beat_division == 3:
				beat_durations = Voice.compound_beat_durations

			note_duration = Fraction(numerator=midi_note.duration, denominator=960)
			if note_duration in beat_durations:
				lily_note = "".join([
					note_letter, accidental_mark, octave_mark, 
					beat_durations[note_duration]])
			else:
				beat_partitions = []
				remaining_rhythm = note_duration
				for current_rhythm in beat_durations:
					if current_rhythm <= remaining_rhythm:
						beat_partitions.append(current_rhythm)
						remaining_rhythm -= current_rhythm
					if remaining_rhythm == 0:
						break
				lily_note = ""
				for beat_part in beat_partitions[:-1]:
					lily_note = "".join([
						lily_note, note_letter, accidental_mark, octave_mark,
						beat_durations[beat_part], "~ "])

				lily_note = "".join([
					lily_note, note_letter, accidental_mark, octave_mark, 
					beat_durations[beat_partitions[-1]]])

			lily_part.append(lily_note)

			self.logger.warning(note_index)

			if note_index < len(self.midi_notes) - 1:
				self.logger.warning("Checking rest possibility")
				self.logger.warning(f"Current time: {current_time}")
				next_note_start = self.midi_notes[note_index + 1].time
				self.logger.warning(f"Note duration: {midi_note.duration}")
				self.logger.warning(f"Next note start: {next_note_start}") 
				if current_time + midi_note.duration < next_note_start:
					unused_ticks = next_note_start - current_time - midi_note.duration
					self.logger.warning(f"Unused ticks: {unused_ticks}")
					unused_duration = Fraction(numerator=unused_ticks, denominator=960)
					if unused_duration in beat_durations:
						lily_part.append(f"r{beat_durations[unused_duration]}") 
					else:
						rest_partitions = []
						remaining_rhythm = unused_duration

						for current_rhythm in beat_durations:
							if current_rhythm <= remaining_rhythm:
								rest_partitions.append(current_rhythm)
								remaining_rhythm -= current_rhythm
							if remaining_rhythm == 0:
								break

						for rest_part in rest_partitions:
							lily_part.append(f"r{beat_durations[rest_part]}")
				current_time = next_note_start 

			note_index += 1

		lily_string = " ".join(note for note in lily_part) 
		Voice.lily_score.append(lily_string)
		self.logger.warning(f"Lily part: {lily_part}")


