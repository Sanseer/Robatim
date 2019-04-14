class Voice:

	mode = ""
	tonic = ""
	accidental = ""
	chord_path = []
	note_values = [2] #don't forget to add 4 as last item whole note
	chord_types = []
	bass_notes = []
	soprano_notes = []
	alto_notes = []
	tenor_notes = []
	lily_parts = []
	chord_symbols = []

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
		# print(self.sheet_notes)

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
		print(chord_symbols)
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
				octave_mark = str(shift * "")
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
		correct_durations = {1:4, 4:1, 2:2}
		fixed_durations = []
		for index in range(len(Voice.note_values)):
			time = Voice.note_values[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations


class Bass(Voice):
	"""The first voice to create in a song"""

	def __init__(self, tonic="D", mode="ionian"):
		Voice.chord_path = [I]
		Voice.tonic = tonic
		self.scale_notes = [0]
		Voice.mode = self.mode = mode
		self.real_notes = []
		self.sheet_notes = []
		if mode == "ionian":
			Voice.accidental = major_scales[tonic]
		elif mode == "aeolian":
			Voice.accidental = minor_scales[tonic]
		self.voice = "bass"
		self.lily_notes = []
		self.old_chord = Voice.chord_path[-1]

	def create_chords(self):
		"""Creates full chord progression"""
		tonic_chords, tonic_note_values, old_chord = self.create_tonic_zone()
		self.make_half_cadence()
		Voice.note_values.extend(tonic_note_values)
		Voice.chord_path.extend(tonic_chords)
		self.old_chord = old_chord
		self.make_authentic_cadence()

	def create_passing_chords(self, chord_options):
		chords_chosen = random.choice(chord_options)
		[Voice.chord_path.append(chord) for chord in chords_chosen]
		self.old_chord = Voice.chord_path[-1]

	def create_accent_chord(self,chord_options):
		chord_choice = random.choice(chord_options)
		Voice.chord_path.append(chord_choice)
		self.old_chord = Voice.chord_path[-1]

	def create_tonic_zone(self):
		rhythm_sequence = random.choice(tuple(antecedent.keys()))
		Voice.note_values.extend(antecedent[rhythm_sequence])
		print(Voice.note_values)
		print(rhythm_sequence)
		for rhythm in rhythm_sequence:
			if rhythm == "P":
				chord_options = expand_tonic[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "A":
				chord_options = accent_tonic[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
		return Voice.chord_path[:], Voice.note_values[:], self.old_chord

	def make_half_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent1.keys()))
		Voice.note_values.extend(consequent1[rhythm_sequence])
		print(Voice.note_values)
		print(rhythm_sequence)
		self.choose_chord(rhythm_sequence)

	def choose_chord(self, rhythm_sequence):
		counter = 0
		for rhythm in rhythm_sequence:
			counter += 1
			if counter == 1:
				chord_options = tonic_to_subdom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif "AS" in rhythm:
				chord_options = accent_subdom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "AD":
				chord_options = (V, V7)
				self.create_accent_chord(chord_options)
			elif rhythm == "PS":
				chord_options = expand_subdom[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "FD":
				chord_options = (V, V7)
				self.create_accent_chord(chord_options)
			elif rhythm == "FT":
				chord_options = (I,)
				self.create_accent_chord(chord_options)

	def make_authentic_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent2.keys()))
		Voice.note_values.extend(consequent2[rhythm_sequence])
		print(Voice.note_values)
		print(rhythm_sequence)
		self.choose_chord(rhythm_sequence)

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_scale_degree = 0
		old_pitch = 0
		old_position = 0
		for chord in Voice.chord_path[1:]:
			new_scale_degree = int(bass_notes[abs(chord)])

			# Deciding between regular and inverted chord
			if chord > 0 or chord < 0 and old_scale_degree > new_scale_degree:
				shift = new_scale_degree - old_scale_degree
				new_position = old_position + shift
				new_pitch = modes[self.mode][new_position]

			elif chord < 0 and new_scale_degree > old_scale_degree:
				old_position += 7
				shift = new_scale_degree - old_scale_degree - 7
				new_position = old_position + shift
				new_pitch = old_pitch + modes[self.mode][new_position] - \
					modes[self.mode][old_position]

			pitch_change = new_pitch - old_pitch
			self.scale_notes.append(new_pitch)
			old_pitch = new_pitch
			old_position = new_scale_degree
			old_scale_degree = new_scale_degree

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.scale_notes]
		copy_notes = self.real_notes[:]
		for index in range(len(self.real_notes)):
			# Raise seventh only for ascending
			if self.mode == "aeolian" and bass_notes[abs(Voice.chord_path[index])] == 6:
				print("RAISED SEVENTH!")
				self.real_notes[index] += 1
			if Voice.tonic == "C":
				self.real_notes[index] -= 12
			else:
				self.real_notes[index] -= 24

	def create_part(self):
		"""Creates the bass portion of the song"""
		print(f"Song in {Voice.tonic} {self.mode} with {Voice.accidental}'s")
		self.create_chords()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		return self.real_notes
