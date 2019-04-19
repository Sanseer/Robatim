from idioms import *

class Voice:

	mode = ""
	tonic = ""
	accidental = ""
	idea1_length = 0
	idea2_length = 0
	idea3_length = 0
	idea4_length = 0
	chord_path = []
	note_values = [] 
	chord_types = []
	main_pitches = []
	bass_pitches = []
	bass_motion = []
	soprano_pitches = []
	soprano_motion = []
	alto_pitches = []
	alto_motion = []
	tenor_pitches = []
	tenor_motion = []
	lily_parts = []
	chord_symbols = []

	def calculate_interval(self, old_pitches, pitch_choice, intervals):
		# print(old_pitches)
		# main_pitches = [(pitch - tonics[Voice.tonic]) % 12 for pitch in old_pitches]
		# new_pitches = [pitch % 12 for pitch in self.pitch_amounts if type(pitch) == int]
		main_pitch = old_pitches[self.note_index]
		# print(f"{main_pitch} and {pitch_choice}")
		while main_pitch < 0:
			main_pitch += 12
		new_pitch = pitch_choice % 12
		while new_pitch < 0:
			new_pitch += 12
		while new_pitch > 12:
			new_pitch -= 12
		# print(f"{Voice.mode} mode: {main_pitch} and {new_pitch}")
		if Voice.mode == "ionian":
			main_pitch_degree = major_scale_degrees[main_pitch]
			new_pitch_degree = major_scale_degrees[new_pitch]
		elif Voice.mode == "aeolian":
			main_pitch_degree = minor_scale_degrees[main_pitch]
			new_pitch_degree = minor_scale_degrees[new_pitch]
		# print(f"Scale degrees: {main_pitch_degree} and {new_pitch_degree}")
		leap = new_pitch - main_pitch
		generic_interval = new_pitch_degree - main_pitch_degree
		if leap < 0:
			leap += 12
			generic_interval += 7
		# print(f"{leap} semitones. Generic interval: {generic_interval}")
		# intervals.append((leap, generic_interval))
		# intervals[-1] = interval_names[(leap, generic_interval)]
		intervals.append(interval_names[(leap, generic_interval)])
		# print(self.pitch_amounts, len(self.pitch_amounts))
		# print(self.intervals, len(self.intervals), end="\n\n")

	def next_interval(self, old_pitch, pitch_choice):
		pass

	def calculate_motion(self, old_motion, new_motion, movements):
		old_move = old_motion[self.note_index - 1]
		new_move = new_motion[self.note_index - 1]
		if old_move == new_move and old_move != 0 and \
		self.intervals[-1] == self.intervals[-2]:
			movements.append("Parallel")
		elif old_move == new_move and old_move == 0:
			movements.append("No motion")
		elif old_move == -(new_move) and old_move != 0:
			movements.append("Contrary")
		elif old_move == new_move and \
		self.intervals[-1] != self.intervals[-2]:
			movements.append("Similar")
		elif (old_move == 0 or new_move == 0) and \
		(old_move != 0 or new_move != 0):
			movements.append("Oblique")
		else:
			movements.append("Blank")

	def make_letter(self, real_note):
		"""Converts pitch magnitudes into standard note names"""
		letter_choices = []
		note_number = real_note % 12

		for letter, num in tonics.items():
			if num == note_number:
				letter_choices.append(letter)
			if len(letter_choices) > 1:
				for letter in letter_choices:
					if Voice.accidental in letter:
						notation = letter
			elif len(letter_choices) == 1:
				notation = letter_choices[0]

		octave = real_note // 12 - 1
		note_symbol = notation + str(octave)
		return note_symbol

	def make_letters(self):
		for real_note in self.real_notes:
			self.sheet_notes.append(self.make_letter(real_note))

	def convert_chords(self):
		new_chords_names = []
		for chord in Voice.chord_path:
			chord = str(abs(chord))
			root = chord[0]
			position = chord[-3:]
			correct_name = chord.replace(root, names[root],1)
			correct_name = correct_name.replace(position, names[position])
			new_chords_names.append(correct_name)
		return new_chords_names

	def lily_convert(self):
		self.lily_notes = []
		rhythm = self.invert_note_values()
		chord_symbols = self.convert_chords()
		print(chord_symbols, len(chord_symbols))
		index = 0
		for sheet_note in self.sheet_notes:
			new_symbol = ""
			octave_mark = ""
			letter = sheet_note[0].lower()
			octave = int(sheet_note[-1])
			if octave < 3:
				shift = 3 - octave
				octave_mark =  str(shift * ",")
			elif octave > 3:
				shift = octave - 3
				octave_mark = str(shift * "'")
			if "#" in sheet_note or "b" in sheet_note:
				old_symbol = sheet_note[1]
				if old_symbol == "#":
					new_symbol = "is"
				elif old_symbol == "b":
					new_symbol = "es"
			lily_note = letter + new_symbol + octave_mark + str(rhythm[index]) + " "
			self.lily_notes.append(lily_note)
			index += 1
		lily_string = ""
		for note in self.lily_notes:
			lily_string += note
		# print(lily_string)
		Voice.lily_parts.append(lily_string)

	def invert_note_values(self):
		correct_durations = {1:4, 4:1, 2:2}
		fixed_durations = []
		for index in range(len(Voice.note_values)):
			time = Voice.note_values[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations









