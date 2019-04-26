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
		main_pitch = old_pitches[self.note_index]
		main_pitch = (main_pitch - tonics[Voice.tonic]) % 12
		new_pitch = pitch_choice % 12

		intervals.append(self.make_specific_interval(main_pitch, new_pitch))

	def validate_leap(self, pitch_choice):
		old_pitch = self.pitch_amounts[self.note_index - 1]
		pitch_change = pitch_choice - old_pitch

		if abs(pitch_change) > 7: 
			return False
		return True

	def is_voice_range(self):
		selected_pitches = [ pitch for pitch in self.pitch_amounts 
		if type(pitch) == int ]
		highest_pitch = max(selected_pitches)
		lowest_pitch = min(selected_pitches)
		vocal_range = highest_pitch - lowest_pitch

		if vocal_range > 16:
			return False
		else:
			return True

	def make_specific_interval(self, old_pitch, new_pitch):

		if Voice.mode == "ionian":
			old_pitch_degree = major_scale_degrees[old_pitch]
			new_pitch_degree = major_scale_degrees[new_pitch]
		elif Voice.mode == "aeolian":
			old_pitch_degree = minor_scale_degrees[old_pitch]
			new_pitch_degree = minor_scale_degrees[new_pitch]

		leap = new_pitch - old_pitch
		generic_interval = new_pitch_degree - old_pitch_degree

		if leap < 0:
			leap += 12
			generic_interval += 7

		return interval_names[(leap, generic_interval)]

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
		print(self.sheet_notes)

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
		Voice.lily_parts.append(lily_string)

	def invert_note_values(self):
		correct_durations = {1:4, 4:1, 2:2, 3:"2."}
		fixed_durations = []
		for index in range(len(Voice.note_values)):
			time = Voice.note_values[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations

	def create_part(self):
		self.make_letters()
		self.lily_convert()
		return self.real_notes

	def make_scale_degree(self, pitch):
		natural_pitch = pitch - tonics[Voice.tonic]
		corrected_pitch = natural_pitch % 12
		return corrected_pitch










