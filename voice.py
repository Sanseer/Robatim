import idioms as idms
import pysnooper

class Voice(object):

	mode = ""
	tonic = ""
	accidental = ""
	idea1_length = 0
	idea2_length = 0
	idea3_length = 0
	idea4_length = 0
	chord_path = []
	note_values = [] 

	measure_length = 4
	beat_division = 2
	half_rest_ending = True
	consequent_rhythm_change = False
	bass_pitches = []
	bass_motion = []
	soprano_pitches = []
	soprano_motion = []
	soprano_jumps = [0]
	soprano_slope = []
	alto_pitches = []
	alto_motion = []
	tenor_pitches = []
	tenor_motion = []
	lily_parts = []
	chord_symbols = []
	chromatics = []

	def calculate_interval(self, old_pitches, pitch_choice, intervals):
		main_pitch = old_pitches[self.note_index]
		main_pitch = (main_pitch - idms.tonics[Voice.tonic]) % 12
		new_pitch = pitch_choice % 12

		if Voice.chromatics[self.note_index] == "2D": 
			main_pitch = self.center_sec_dom(main_pitch)
			new_pitch = self.center_sec_dom(new_pitch)

		intervals.append(self.make_specific_interval(main_pitch, new_pitch))

	def calculate_leap(self, pitch_choice):
		old_pitch = self.pitch_amounts[self.note_index - 1]
		pitch_change = pitch_choice - old_pitch

		# if abs(pitch_change) > 12: 
		# 	return False
		return abs(pitch_change)

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
			old_pitch_degree = idms.major_scale_degrees[old_pitch]
			new_pitch_degree = idms.major_scale_degrees[new_pitch]
		elif Voice.mode == "aeolian":
			old_pitch_degree = idms.minor_scale_degrees[old_pitch]
			new_pitch_degree = idms.minor_scale_degrees[new_pitch]

		leap = new_pitch - old_pitch
		generic_interval = new_pitch_degree - old_pitch_degree

		if leap < 0:
			leap += 12
			generic_interval += 7

		return idms.interval_names[(leap, generic_interval)]

	def append_slope(self, part_slope, part_motion, new_pitch):
		if (self.note_index > 1 and part_motion[-1] != 0 and 
			part_motion[-1] == -part_motion[-2]):
			part_slope.append(self.pitch_amounts[self.note_index - 1])

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

		for letter, num in idms.tonics.items():
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
			position = chord[-4:-1]
			if chord[-1] == "1":
				chord = chord[:-1]
			else:
				reference = idms.chord_names[chord[-1]]
				chord = chord[:-1]
				chord = " of ".join([chord, reference])
			correct_name = chord.replace(root, idms.chord_names[root],1)
			correct_name = correct_name.replace(position, idms.chord_names[position])
			new_chords_names.append(correct_name)
		return new_chords_names

	def lily_convert(self):
		self.lily_notes = []
		Voice.rhythm = self.invert_note_values()
		print(Voice.rhythm, len(Voice.rhythm))
		Voice.chord_symbols = self.convert_chords()
		print(Voice.chord_symbols)
		index = 0
		# rest_indices = []
		# for lily_index, item in enumerate(Voice.note_values):
		# 	if type(item) == str:
		# 		rest_indices.append(lily_index)
		# # print(rest_indices)
		# # print(self.sheet_notes)
		# for lily_index in rest_indices[::-1]:
		# 	self.sheet_notes.insert(lily_index, rhythm[lily_index])
		# # print(self.sheet_notes)
		Voice.create_rests(self.sheet_notes)
		print(self.sheet_notes)

		assert(len(Voice.rhythm) == len(self.sheet_notes))

		for index, sheet_note in enumerate(self.sheet_notes):
		# for lily_index, item in enumerate(rhythm):
			# if lily_index in rest_indices:
			# 	self.lily_notes.append(item)
			# 	continue
			if "r" in sheet_note:
				self.lily_notes.append(sheet_note) 
				# index += 1
				continue
			# print(self.sheet_notes)
			new_symbol = ""
			octave_mark = ""
			letter = sheet_note[0].lower()
			# letter = self.sheet_notes[lily_index][0].lower()
			# print("Letter:", letter, end=" | ")
			octave = int(sheet_note[-1])
			# octave = int(self.sheet_notes[lily_index][-1])
			# print("Octave:", octave, end=" | ")
			if octave < 3:
				shift = 3 - octave
				octave_mark =  str(shift * ",")
			elif octave > 3:
				shift = octave - 3
				octave_mark = str(shift * "'")
			# print("Octave mark:", octave_mark, end=" | ")
			if "#" in sheet_note or "b" in sheet_note:
			# if ("#" in self.sheet_notes[lily_index] 
			# 	or "b" in self.sheet_notes[lily_index]):
				old_symbol = sheet_note[1]
				# old_symbol = self.sheet_notes[lily_index][1]
				if old_symbol == "#":
					new_symbol = "is"
				elif old_symbol == "b":
					new_symbol = "es"
			# print("New symbol:", new_symbol)
			lily_note = letter + new_symbol + octave_mark + str(Voice.rhythm[index]) + " "
			# lily_note = letter + new_symbol + octave_mark + str(item) + " "
			self.lily_notes.append(lily_note)
			# index += 1

		lily_string = ""

		print(self.lily_notes, len(self.lily_notes))
		for note in self.lily_notes:
			lily_string += note
		Voice.lily_parts.append(lily_string)

	def invert_note_values(self):
		correct_durations = {1:4, 4:1, 2:2, 3:"2.", "2":"r2 ", "1":"r4 "}
		fixed_durations = []
		for index in range(len(Voice.note_values)):
			time = Voice.note_values[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations

	@staticmethod
	def create_rests(sequence):
		rest_indices = []
		for lily_index, item in enumerate(Voice.note_values):
			if type(item) == str:
				rest_indices.append(lily_index)
		for lily_index in rest_indices[::-1]:
			sequence.insert(lily_index, Voice.rhythm[lily_index])

	def create_part(self):
		self.make_letters()
		self.lily_convert()
		return self.real_notes

	def make_scale_pitch(self, pitch):
		natural_pitch = pitch - idms.tonics[Voice.tonic]
		corrected_pitch = natural_pitch % 12
		return corrected_pitch

	def make_sec_dom(self, chord, real_note):
		chord = abs(chord)
		main_note = self.make_scale_pitch(real_note)
		if Voice.mode == "ionian":
			scale_degree = idms.major_scale_degrees[main_note]
		elif Voice.mode == "aeolian":
			scale_degree = idms.minor_scale_degrees[main_note]

		position = idms.chord_tones[chord].index(scale_degree)
		root_degree = idms.chord_tones[chord][0]
		if Voice.mode == "ionian":
			shift = idms.sec_doms_in_major[root_degree][position]
		elif Voice.mode == "aeolian":
			shift = idms.sec_doms_in_minor[root_degree][position]

		return shift

	def move_direction(self, move):
		if move < 0:
			return int(move / -move)
		elif move > 0:
			return int(move / move)
		else:
			return 0

	def center_sec_dom(self, pitch, index_shift=0):
		chord = abs(Voice.chord_path[self.note_index + index_shift])
		root_degree = idms.chord_tones[chord][0]
		chord_degrees = idms.chord_tones[chord]
		chord_pitches = []
		for degree in chord_degrees:
			chord_pitches.append(idms.modes[Voice.mode][degree])
		pitch = pitch % 12
		accidentals = [pitch, pitch - 1, pitch + 1]

		for index in range(len(chord_pitches)):
			if chord_pitches[index] in accidentals:
				degree_index = index
		note_degree = idms.chord_tones[chord][degree_index]
		final_position = 4 + note_degree - root_degree
		if final_position > 7 or final_position < 0:
			final_position %= 7

		return idms.modes[Voice.mode][final_position]



