from generate.idioms import basics as idms_b

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
		self.create_groove()
		self.make_letters()
		self.lily_convert()
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
		return len(idms_b.chord_members[chord]) == 4

	def is_chord_inversion(self, chord1, chord2):
		# check for triad versus seventh
		if (chord1 // 10000 == chord2 // 10000 and chord1 % 10 == chord2 % 10 
		  and len(idms_b.chord_members[chord1]) == 
		  len(idms_b.chord_members[chord2])):
			return True
		return False

	def make_scale_pitch(self, pitch):
		return (pitch - idms_b.tonics[Voice.tonic]) % 12

	def get_diatonic_scale_degree(self, pitch):
		if not 0 <= pitch <= 11:
			pitch = self.make_scale_pitch(pitch)
		if self.mode == "ionian":
			return idms_b.major_scale_degrees[pitch]
		elif self.mode == "aeolian":
			return idms_b.minor_scale_degrees[pitch]

	def center_scale_degree(self, scale_degree):
		if not 0 <= scale_degree <= 6:
			scale_degree %= 7
		return scale_degree

	def is_diatonic(self, pitch):
		pitch = self.make_scale_pitch(pitch)
		if pitch in idms_b.modes[self.mode] or pitch == 11:
			return True
		return False

	def get_interval(self, old_pitch, new_pitch):
		# try:
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
			elif self.chromatics[self.note_index] in idms_b.modes.keys():
				# chord_shift = 0
				# make current chord a property?
				chord_shift = self.get_chord() % 10 - 1
				convert_func = self.convert_mode
			old_pitch_degree = self.revert_pitch_to_degree(
				old_pitch, chord_shift, convert_func)
			new_pitch_degree = self.revert_pitch_to_degree(
				new_pitch, chord_shift, convert_func)
		elif self.chromatics[self.note_index] is None:
			old_pitch = self.make_scale_pitch(old_pitch)
			new_pitch = self.make_scale_pitch(new_pitch)
			old_pitch_degree = self.get_diatonic_scale_degree(old_pitch)
			new_pitch_degree = self.get_diatonic_scale_degree(new_pitch)

		generic_interval = new_pitch_degree - old_pitch_degree
		if generic_interval < 0:
			generic_interval += 7
		return idms_b.interval_names[(leap, generic_interval)]
		# except:
		# 	print(self.mode)
		# 	print(self.chromatics[self.note_index])
		# 	print(self.get_chord())
		# 	print(old_pitch, new_pitch)
		# 	print(self.make_scale_pitch(old_pitch), 
		# 		self.make_scale_pitch(new_pitch))
		# 	with pysnooper.snoop(depth=3):

	def revert_pitch_to_degree(self, pitch, chord_shift, convert_func):
		chord = self.get_chord()
		chord_degrees = idms_b.chord_members[chord]
		root_degree = idms_b.chord_members[chord][0]
		chord_pitches = []
		for degree in chord_degrees:
			chord_pitches.append(idms_b.modes[Voice.mode][degree])
		if not 0 <= pitch <= 11:
			pitch = self.make_scale_pitch(pitch)
		if (10 in chord_pitches and root_degree in {4, 6} 
		  and Voice.chromatics[self.note_index] not in {"2Dom", "2Dim"}):
			chord_pitches[chord_pitches.index(10)] += 1

		for index, base_pitch in enumerate(chord_pitches[:]):
			chord_pitches[index] += convert_func(chord, base_pitch)
			if not 0 <= chord_pitches[index] <= 11:
				chord_pitches[index] %= 12
		for index in range(len(chord_pitches)):
			if chord_pitches[index] == pitch:
				degree_index = index
				break

		note_degree = idms_b.chord_members[chord][degree_index]
		final_position = chord_shift + note_degree - root_degree
		final_position = self.center_scale_degree(final_position)

		return final_position

	def convert_sec_dom(self, chord, main_note):
		if not 0 <= main_note <= 11:
			main_note = self.make_scale_pitch(main_note)
		scale_degree = self.get_diatonic_scale_degree(main_note)

		position = idms_b.chord_members[chord].index(scale_degree)
		root_degree = idms_b.chord_members[chord][0]
		if Voice.mode == "ionian":
			shift = idms_b.sec_doms_in_major[root_degree][position]
		elif Voice.mode == "aeolian":
			shift = idms_b.sec_doms_in_minor[root_degree][position]

		return shift

	def convert_sec_dim(self, chord, main_note):
		if not 0 <= main_note <= 11:
			main_note = self.make_scale_pitch(main_note)
		scale_degree = self.get_diatonic_scale_degree(main_note)

		position = idms_b.chord_members[chord].index(scale_degree)
		root_degree = idms_b.chord_members[chord][0]

		if chord // 10000 == 70:
			direction = "up"
		elif chord // 10000 == 11:
			direction = "down"

		shift = idms_b.sec_dims[(direction, self.mode)][root_degree][position]

		return shift

	def convert_mode(self, chord, main_note):
		if not 0 <= main_note <= 11:
			main_note = self.make_scale_pitch(main_note)
		scale_degree = self.get_diatonic_scale_degree(main_note)

		new_mode = Voice.chromatics[self.note_index]
		new_note = idms_b.modes[new_mode][scale_degree]

		if (new_mode == "aeolian" and new_note == 10 and 
		idms_b.chord_members[chord][0] in (4,6)):
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
		elif (old_move == new_move and intervals[-1] != intervals[-2]):
			movements.append("Similar")
		elif ((old_move == 0 or new_move == 0) and 
		  (old_move != 0 or new_move != 0)):
			movements.append("Oblique")
		else:
			movements.append("Blank")

		# use "Blank" to assert proper assignment

	def make_letter(self, real_note):
		"""Converts pitch magnitudes into standard note names"""
		scale_note = self.make_scale_pitch(real_note)

		if self.chromatics[self.note_index]:
			if self.chromatics[self.note_index] == "2Dom":
				chord_shift = 4
				convert_func = self.convert_sec_dom
			elif self.chromatics[self.note_index] == "2Dim":
				chord_shift = 6 
				convert_func = self.convert_sec_dim
			elif self.chromatics[self.note_index] in idms_b.modes.keys():
				chord_shift = self.get_chord() % 10 - 1
				convert_func = self.convert_mode
			scale_degree = self.revert_pitch_to_degree(
				scale_note, chord_shift, convert_func)
		else:
			scale_degree = self.get_diatonic_scale_degree(scale_note)

		pitch_index = (self.tonic_index + scale_degree) % 7
		pitch_letter = idms_b.scale_sequence[pitch_index]
		letter_choices = idms_b.all_notes[(real_note % 12)]
		for pitch_name in letter_choices: 
			if pitch_letter in pitch_name:
				notation = pitch_name

		octave = real_note // 12 - 1
		note_symbol = f"{notation}{octave}"
		return note_symbol


	def make_letters(self):
		# if self.voice_type = "soprano"
		self.note_index = 0
		tonic_letter = Voice.tonic.replace("#","").replace("b","")
		self.tonic_index = idms_b.scale_sequence.index(tonic_letter)
		for final_note in self.final_notes:
			if type(final_note) == int: 
				self.sheet_notes.append(self.make_letter(final_note))
				self.note_index += 1
			elif type(final_note) == str:
				self.sheet_notes.append(final_note)
		print(self.sheet_notes, len(self.sheet_notes))

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
				chord = " ".join([idms_b.chord_names[root2], chord])
			elif (chord[-1] == "1" and chord_flavor != 11):
				chord = chord[:-1]
			else:
				reference = idms_b.chord_names[chord[-1]]
				chord = chord[:-1]
				chord = " of ".join([chord, reference])
			correct_name = chord.replace(root, idms_b.chord_names[root],1)
			correct_name = correct_name.replace(position, idms_b.chord_names[position])
			new_chords_names.append(correct_name)
		return new_chords_names

	def lily_convert(self):
		# add figured bass + roman numeral below chord
		# add lead-sheet symbols above chord
		self.lily_notes = []
		self.rhythm = self.invert_note_values()
		index = 0
		self.create_rests(self.sheet_notes)

		assert(len(self.rhythm) == len(self.sheet_notes))

		# C is where octave starts
		# try {a' b' bis' c'' d''} in Lilypond


		for index, sheet_note in enumerate(self.sheet_notes):
			if "r" in sheet_note:
				self.lily_notes.append(sheet_note) 
				continue
			new_symbol = ""
			octave_mark = ""
			letter = sheet_note[0].lower()
			register_shift = 0
			# edge case that realigns pitch magnitude with register
			# B# is technically in the octave above (starting from C).
			# Cb is technically below the current octave (starting from C). 
			if sheet_note.startswith(("B#","B##")):
				register_shift = -1
			elif sheet_note.startswith(("Cb","Cbb")):
				register_shift = 1
			octave = int(sheet_note[-1]) + register_shift
			if octave < 3:
				shift = 3 - octave
				octave_mark =  str(shift * ",")
			elif octave > 3:
				shift = octave - 3 
				octave_mark = str(shift * "'")
			if "#" in sheet_note or "b" in sheet_note:
				level = sheet_note.count("#")
				level += sheet_note.count("b")
				old_symbol = sheet_note[1]
				if old_symbol == "#":
					new_symbol = "is" * level
				elif old_symbol == "b":
					new_symbol = "es" * level
			current_rhythm = self.rhythm[index]
			if "FIX" not in current_rhythm:
				lily_note = "".join((letter, new_symbol, octave_mark, 
					self.rhythm[index]))
			# elif current_rhythm == "3C":
			# 	lily_note = "".join((letter, new_symbol, octave_mark, "2.~ ", 
			# 		letter, new_symbol, octave_mark, "4."))
			elif current_rhythm == "FIX":
				# deals with weird rhythms in compound time 
				# that need ties and irregular beams
				beat_partitions = []
				remaining_beat = self.final_rhythm[index]
				for current_beat in self.triple_beat_durations.keys():
					if self.truncate_float(current_beat, 2) <= remaining_beat:
						beat_partitions.append(current_beat)
						remaining_beat -= current_beat
				lily_note = ""
				for valid_beat in beat_partitions[:-1]:
					lily_note = "".join((
						lily_note, " ", letter, new_symbol, octave_mark, 
						self.triple_beat_durations[valid_beat], "~"))
				lily_note = "".join((
					lily_note, " ", letter, new_symbol, octave_mark,
					self.triple_beat_durations[beat_partitions[-1]]))


			self.lily_notes.append(lily_note)

		lily_string = " ".join(note for note in self.lily_notes)
		Voice.lily_parts.append(lily_string)

	def truncate_float(self, number, precision):
		"""Converts float to another float with less precision"""
		if number % 1 == 0:
			return number
		result = 0
		str_number = str(number)
		decimal_index = str_number.index(".")
		magnitude = 1
		current_index = decimal_index - 1
		if (str_number[current_index] != "0" or 
		  len(str_number[0:decimal_index]) >= 2):
			for _ in range(0, decimal_index):
				digit_multiplier = int(str_number[current_index])
				result += digit_multiplier * magnitude
				current_index -= 1
				magnitude *= 10

		magnitudes = [(1 / 10 ** multiplier) for multiplier in range(1,5)]
		current_index = decimal_index + 1
		counter = 0
		magnitude = magnitudes[counter]
		for _ in range(decimal_index + 1, len(str_number)):
			digit_multiplier = int(str_number[current_index])
			result += digit_multiplier * magnitude
			current_index += 1
			counter += 1
			if counter == precision:
				break
			magnitude = magnitudes[counter]

		return result



	def invert_note_values(self):
		if Voice.beat_division == 2:
			correct_durations = {
				1:"4", 4:"1", 2:"2", 3:"2.", "2":"r2", "1":"r4",
				0.5:"8", 1.5:"4.", 0.75:"8.", 0.25: "16", 0.125: "32", 
				0.375: "16.",}
		# create tie in lily_convert for compound time
		elif Voice.beat_division == 3:
			correct_durations = {
				0.5: "8.", 1:"4.", 2:"2.", 3:"FIX", 4:"1.", "2":"r2.", "1":"r4.",
				1.5: "FIX", 0.5 *  idms_b.THIRD: "16", 1 * idms_b.THIRD: "8", 
				1.5 * idms_b.THIRD: "FIX", 2 * idms_b.THIRD:"4", 
				2.5 * idms_b.THIRD: "FIX", 3 * idms_b.THIRD:"4.", 
				4 * idms_b.THIRD:"2", 5 * idms_b.THIRD: "FIX", 
				6 * idms_b.THIRD:"2.", 7.5 * idms_b.THIRD: "FIX", 
				8 * idms_b.THIRD:"1", 10 * idms_b.THIRD: "FIX" 
			}
			self.triple_beat_durations = {
				4:"1.", 2:"2.", 4 * idms_b.THIRD:"2", 1:"4.",   
				2 * idms_b.THIRD:"4", 0.5: "8.", 1 * idms_b.THIRD: "8", 
				0.5 * idms_b.THIRD: "16"  
			}
		fixed_durations = []
		for index in range(len(self.final_rhythm)):
			time = self.final_rhythm[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations

	def create_rests(self, sequence):
		# rest_indices = []
		for lily_index, item in enumerate(self.final_rhythm):
			if type(item) == str:
				sequence[lily_index] = self.rhythm[lily_index]
				# rest_indices.append(lily_index)
		# reverse insertion to prevent moving target
		# for lily_index in rest_indices:
		# 	sequence[lily_index] = self.rhythm[lily_index]
		return sequence

	def chord_degree_to_pitch(self, chord_position, index_shift=0):
		chord = self.get_chord(index_shift)
		scale_degree = idms_b.chord_members[chord][chord_position]
		pitch = idms_b.modes[Voice.mode][scale_degree]
		root_degree = idms_b.chord_members[chord][0]
		if (Voice.mode == "aeolian" and 
		  (root_degree == 4 or root_degree == 6) and pitch == 10 and
		  Voice.chromatics[self.note_index + index_shift] not in 
		  ("2Dom", "2Dim")):
			pitch += 1
		if self.chromatics[self.note_index + index_shift] == "2Dom":
			pitch += self.convert_sec_dom(chord, pitch)
		elif self.chromatics[self.note_index + index_shift] == "2Dim":
			pitch += self.convert_sec_dim(chord, pitch)
		elif (self.chromatics[self.note_index + index_shift] in 
		  idms_b.modes.keys()):
			pitch += self.convert_mode(chord, pitch)
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
		for m_index, chosen_measure in enumerate(
				Voice.rhythm_styles[start:stop]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				if rhythm_style == "Waltz2":
					self.final_rhythm[m_index + start].extend(("1",1))
				elif rhythm_style == "Waltz3":
					self.final_rhythm[m_index + start].extend(("1",1,1))
				elif rhythm_style == "Waltz4":
					self.final_rhythm[m_index + start].extend(("1",1,"1",1))
				else:
					self.final_rhythm[m_index + start].append(
						Voice.measure_rhythms[m_index + start][r_index])

	def spread_notes(self, start, stop):
		for m_index, chosen_measure in enumerate(
				Voice.rhythm_styles[start:stop]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				main_note = self.measure_notes[m_index + start][r_index]
				if rhythm_style == "Waltz2":
					self.final_notes[m_index + start].extend(
						("REST", main_note))
				elif rhythm_style == "Waltz3":
					self.final_notes[m_index + start].extend(
						("REST", main_note, main_note))
				elif rhythm_style == "Waltz4":
					self.final_notes[m_index + start].extend(
						("REST", main_note, "REST", main_note))
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




