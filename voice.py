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
	idea5_length = 0
	chord_path = []
	
	note_values = []
	rhythm_styles = []
	measure_rhythms = []
	measure_length = 4
	beat_division = 2
	half_rest_ending = True
	consequent_rhythm_change = False
	
	bass_pitches = []
	bass_motion = []
	soprano_pitches = []
	bass_soprano_intervals = []
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

	def __init__(self):
		self.note_index = 0
		self.measure_notes = []
		self.sheet_notes = []
		self.lily_notes = []
		self.note_values = Voice.note_values[:]

	def create_part(self):
		self.make_letters()
		self.lily_convert()
		self.create_groove()
		# return self.create_rests(self.real_notes[:])

	# @property
	# def notes(self):
	# 	return self.create_rests(self.real_notes[:])

	# @property
	# def groove(self):
	# 	return self.note_values

	@property
	def notes(self):
		return self.final_notes

	@property
	def groove(self):
		return self.final_rhythm

	def get_chord(self, index_shift=0):
		return abs(Voice.chord_path[self.note_index + index_shift])

	def is_seventh_chord(self, index_shift=0):
		chord = self.get_chord(index_shift) 
		return len(idms.chord_tones[chord]) == 4

	def make_scale_pitch(self, pitch):
		return (pitch - idms.tonics[Voice.tonic]) % 12

	def make_scale_degree(self, pitch, scale_pitch=True):
		if not scale_pitch:
			pitch = self.make_scale_pitch(pitch)
		if self.mode == "ionian":
			return idms.major_scale_degrees[pitch]
		elif self.mode == "aeolian":
			return idms.minor_scale_degrees[pitch]

	def center_scale_degree(self, scale_degree):
		if not 0 <= scale_degree <= 6:
			scale_degree %= 7
		return scale_degree

	def get_root_degree(self, index_shift=0):
		chord = self.get_chord(index_shift)
		return idms.chord_tones[chord][0]

	def is_diatonic(self, pitch):
		pitch = self.make_scale_pitch(pitch)
		if pitch in idms.modes[self.mode] or pitch == 11:
			return True
		return False

	def get_interval(self, old_pitch, new_pitch):
		try:
			leap = new_pitch - old_pitch
			if not 0 <= leap <= 11:
				leap %= 12 
			if self.chromatics[self.note_index]:
				if self.chromatics[self.note_index] == "2Dom":
					chord_shift = 4
					convert_func = self.convert_sec_dom
				elif self.chromatics[self.note_index] == "2Dim":
					chord_shift = 6 
					convert_func = self.convert_sec_dim
				elif self.chromatics[self.note_index] in idms.modes.keys():
					chord_shift = 0
					convert_func = self.convert_mode
				old_pitch_degree = self.revert_pitch_to_degree(
					old_pitch, chord_shift, convert_func)
				new_pitch_degree = self.revert_pitch_to_degree(
					new_pitch, chord_shift, convert_func)
			elif self.chromatics[self.note_index] is None:
				old_pitch = self.make_scale_pitch(old_pitch)
				new_pitch = self.make_scale_pitch(new_pitch)
				old_pitch_degree = self.make_scale_degree(old_pitch)
				new_pitch_degree = self.make_scale_degree(new_pitch)

			generic_interval = new_pitch_degree - old_pitch_degree
			if generic_interval < 0:
				generic_interval += 7
			return idms.interval_names[(leap, generic_interval)]
		except:
			print(self.mode)
			print(self.chromatics[self.note_index])
			print(self.get_chord())
			print(old_pitch, new_pitch)
			print(self.make_scale_pitch(old_pitch), 
				self.make_scale_pitch(new_pitch))
			with pysnooper.snoop(depth=3):
				leap = new_pitch - old_pitch
				if not 0 <= leap <= 11:
					leap %= 12 
				if self.chromatics[self.note_index]:
					if self.chromatics[self.note_index] == "2Dom":
						chord_shift = 4
						convert_func = self.convert_sec_dom
					elif self.chromatics[self.note_index] == "2Dim":
						chord_shift = 6 
						convert_func = self.convert_sec_dim
					elif self.chromatics[self.note_index] in idms.modes.keys():
						chord_shift = 0
						convert_func = self.convert_mode
					old_pitch_degree = self.revert_pitch_to_degree(
						old_pitch, chord_shift, convert_func)
					new_pitch_degree = self.revert_pitch_to_degree(
						new_pitch, chord_shift, convert_func)
				elif self.chromatics[self.note_index] is None:
					old_pitch = self.make_scale_pitch(old_pitch)
					new_pitch = self.make_scale_pitch(new_pitch)
					old_pitch_degree = self.make_scale_degree(old_pitch)
					new_pitch_degree = self.make_scale_degree(new_pitch)

				generic_interval = new_pitch_degree - old_pitch_degree
				if generic_interval < 0:
					generic_interval += 7
				return idms.interval_names[(leap, generic_interval)]


	def revert_pitch_to_degree(self, pitch, chord_shift, convert_func, scale_pitch=False):
		chord = self.get_chord()
		chord_degrees = idms.chord_tones[chord]
		root_degree = idms.chord_tones[chord][0]
		chord_pitches = []
		for degree in chord_degrees:
			chord_pitches.append(idms.modes[Voice.mode][degree])
		if not scale_pitch:
			pitch = self.make_scale_pitch(pitch)
		if (10 in chord_pitches and root_degree in (4, 6) 
		and Voice.chromatics[self.note_index] not in ("2Dom", "2Dim")):
			chord_pitches[chord_pitches.index(10)] += 1

		for index, base_pitch in enumerate(chord_pitches[:]):
			chord_pitches[index] += convert_func(
				self.get_chord(), base_pitch, True)
			if not 0 <= chord_pitches[index] <= 11:
				chord_pitches[index] %= 12
		for index in range(len(chord_pitches)):
			if chord_pitches[index] == pitch:
				degree_index = index
				break

		note_degree = idms.chord_tones[chord][degree_index]
		final_position = chord_shift + note_degree - root_degree
		final_position = self.center_scale_degree(final_position)

		return final_position

	def convert_sec_dom(self, chord, main_note, scale_pitch=False):
		if not scale_pitch:
			main_note = self.make_scale_pitch(main_note)
		scale_degree = self.make_scale_degree(main_note)

		position = idms.chord_tones[chord].index(scale_degree)
		root_degree = idms.chord_tones[chord][0]
		if Voice.mode == "ionian":
			shift = idms.sec_doms_in_major[root_degree][position]
		elif Voice.mode == "aeolian":
			shift = idms.sec_doms_in_minor[root_degree][position]

		return shift

	def convert_sec_dim(self, chord, main_note, scale_pitch=False):
		if not scale_pitch:
			main_note = self.make_scale_pitch(main_note)
		scale_degree = self.make_scale_degree(main_note)

		position = idms.chord_tones[chord].index(scale_degree)
		root_degree = idms.chord_tones[chord][0]

		if chord // 10000 == 70:
			direction = "up"
		elif chord // 10000 == 11:
			direction = "down"

		shift = idms.sec_dims[(direction, self.mode)][root_degree][position]

		return shift

	def convert_mode(self, chord, main_note, scale_pitch=False):
		if not scale_pitch:
			main_note = self.make_scale_pitch(main_note)
		scale_degree = self.make_scale_degree(main_note)

		new_mode = Voice.chromatics[self.note_index]
		new_note = idms.modes[new_mode][scale_degree]

		if (new_mode == "aeolian" and new_note == 10 and 
		idms.chord_tones[chord][0] in (4,6)):
			new_note += 1

		return new_note - main_note

	def move_direction(self, move):
		if move < 0:
			return int(move / -move)
		elif move > 0:
			return int(move / move)
		else:
			return 0

	def add_motion_type(self, old_motion, new_motion, movements, intervals):
		# Bass motion list already created
		old_move = old_motion[self.note_index - 1]
		new_move = new_motion[-1]
		if (old_move == new_move and old_move != 0 and 
		intervals[-1] == intervals[-2]):
			movements.append("Parallel")
		elif old_move == new_move and old_move == 0:
			movements.append("No motion")
		elif old_move == -(new_move) and old_move != 0:
			movements.append("Contrary")
		elif (old_move == new_move and 
		intervals[-1] != intervals[-2]):
			movements.append("Similar")
		elif ((old_move == 0 or new_move == 0) and 
		(old_move != 0 or new_move != 0)):
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

	def create_chord_names(self):
		new_chords_names = []
		for chord in Voice.chord_path:
			chord_flavor = abs(chord) // 10000
			chord = str(abs(chord))
			root = chord[:2]
			position = chord[-4:-1]
			if 21 <= chord_flavor <= 26:
				root2 = "".join([chord[-1], "0"])
				chord = chord[:-1]
				chord = " ".join([idms.chord_names[root2], chord])
			elif (chord[-1] == "1" and chord_flavor != 11):
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
		self.rhythm = self.invert_note_values()
		index = 0
		self.create_rests(self.sheet_notes)

		assert(len(self.rhythm) == len(self.sheet_notes))

		for index, sheet_note in enumerate(self.sheet_notes):
			if "r" in sheet_note:
				self.lily_notes.append(sheet_note) 
				# index += 1
				continue
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
			lily_note = letter + new_symbol + octave_mark + str(self.rhythm[index])
			self.lily_notes.append(lily_note)

		lily_string = " ".join(note for note in self.lily_notes)
		Voice.lily_parts.append(lily_string)

	def invert_note_values(self):
		if Voice.beat_division == 2:
			correct_durations = {
				1:"4", 4:"1", 2:"2", 3:"2.", "2":"r2", "1":"r4",
				0.5:"8", 1.5:"4.", .75:"8."}
		# create tie in lily_convert for compound time
		elif Voice.beat_division == 3:
			correct_durations = {
				1:"4.", 4:"1.", 2:"2.", 3:"2.FIX", "2":"r2.", "1":"r4.",
				1*idms.THIRD:"8", 2*idms.THIRD:"4", 5*idms.THIRD:"1.FIX"}
		fixed_durations = []
		for index in range(len(self.note_values)):
			time = self.note_values[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations

	def create_rests(self, sequence):
		rest_indices = []
		for lily_index, item in enumerate(self.note_values):
			if type(item) == str:
				rest_indices.append(lily_index)
		# reverse insertion to prevent moving target
		for lily_index in rest_indices[::-1]:
			sequence.insert(lily_index, self.rhythm[lily_index])
		return sequence

	def chord_degree_to_pitch(self, chord_position, index_shift=0):
		chord = self.get_chord(index_shift)
		scale_degree = idms.chord_tones[chord][chord_position]
		pitch = idms.modes[Voice.mode][scale_degree]
		root_degree = idms.chord_tones[chord][0]
		if (Voice.mode == "aeolian" and 
		(root_degree == 4 or root_degree == 6) and pitch == 10 and
		Voice.chromatics[self.note_index + index_shift] not in ("2Dom", "2Dim")):
			pitch += 1
		if self.chromatics[self.note_index + index_shift] == "2Dom":
			pitch += self.convert_sec_dom(chord, pitch, True)
		elif self.chromatics[self.note_index + index_shift] == "2Dim":
			pitch += self.convert_sec_dim(chord, pitch, True)
		elif self.chromatics[self.note_index + index_shift] in idms.modes.keys():
			pitch += self.convert_mode(chord, pitch, True)
		return pitch

	def is_voice_range(self, voice_index):
		selected_pitches = [ combo[voice_index] for combo in self.pitch_amounts 
		if type(combo) == tuple ]
		highest_pitch = max(selected_pitches)
		lowest_pitch = min(selected_pitches)
		vocal_range = highest_pitch - lowest_pitch

		if vocal_range > 16:
			return False
		return True

	def group_notes(self):
		for rhythm in Voice.measure_rhythms:
			array = []
			for item in rhythm:
				if type(item) == int:
					array.append(self.real_notes[self.note_index])
					self.note_index += 1
			self.measure_notes.append(array)

		print(self.measure_notes)
		print(Voice.measure_rhythms)
		print(self.note_values)

		self.note_index = 0

	def flatten_sequence(self, old_sequence):
		new_list = []
		for nested_sequence in old_sequence:
			for item in nested_sequence:
				new_list.append(item)

		return new_list

	def create_groove(self):
		self.group_notes()

		self.final_rhythm = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]

		self.create_rhythm(0, 3)
		self.create_rhythm(4, 7)

		self.spread_notes(0, 3)
		self.spread_notes(4, 7)

		self.finalize_part()

	def create_rhythm(self, start, stop):
		for m_index, chosen_measure in enumerate(Voice.rhythm_styles[start:stop]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				if rhythm_style == "Waltz2":
					self.final_rhythm[m_index + start].extend(("1",1))
				elif rhythm_style == "Waltz3":
					self.final_rhythm[m_index + start].extend(("1",1,1))
				elif rhythm_style == "Waltz4":
					self.final_rhythm[m_index + start].extend(("1",1,"1",1))
				else:
					self.final_rhythm[m_index + start].append(Voice.measure_rhythms[m_index + start][r_index])

	def spread_notes(self, start, stop):
		for m_index, chosen_measure in enumerate(Voice.rhythm_styles[start:stop]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				main_note = self.measure_notes[m_index + start][r_index]
				if rhythm_style == "Waltz2":
					self.final_notes[m_index + start].extend(("REST", main_note))
				elif rhythm_style == "Waltz3":
					self.final_notes[m_index + start].extend(("REST", main_note, main_note))
				elif rhythm_style == "Waltz4":
					self.final_notes[m_index + start].extend(("REST", main_note, "REST", main_note))
				elif rhythm_style is None:
					self.final_notes[m_index + start].append(main_note)

	def finalize_part(self):
		self.final_notes[3] = self.measure_notes[3]
		self.final_notes[7] = self.measure_notes[7]
		self.final_rhythm[3] = Voice.measure_rhythms[3]
		self.final_rhythm[7] = Voice.measure_rhythms[7]

		if Voice.half_rest_ending:
			self.final_notes[3].append("REST")
			self.final_notes[7].append("REST")

		self.final_rhythm = self.flatten_sequence(self.final_rhythm)
		self.final_notes = self.flatten_sequence(self.final_notes)




