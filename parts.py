import random

from idioms import *

class Voice:

	mode = ""
	tonic = ""
	accidental = ""
	idea1_length = 0
	idea2_length = 0
	idea3_length = 0
	chord_path = []
	note_values = [2] 
	chord_types = []
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


class Bass(Voice):
	"""The first voice to create in a song"""

	def __init__(self, tonic="D", mode="ionian"):
		Voice.chord_path = [I]
		Voice.tonic = tonic
		self.pitch_amounts = [0]
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

	def create_part(self):
		"""Creates the bass portion of the song"""
		print(f"Song in {Voice.tonic} {self.mode} with {Voice.accidental}'s")
		self.create_chords()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		Voice.bass_letters = self.sheet_notes
		print(self.sheet_notes)
		self.lily_convert()
		return self.real_notes

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

		for rhythm in rhythm_sequence:
			if rhythm == "P":
				chord_options = expand_tonic[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "A":
				chord_options = accent_tonic[abs(self.old_chord)]
				self.create_accent_chord(chord_options)

		Voice.idea1_length = len(Voice.note_values)
		return Voice.chord_path[:], Voice.note_values[:], self.old_chord

	def make_half_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent1.keys()))
		Voice.note_values.extend(consequent1[rhythm_sequence])
		Voice.idea2_length = len(Voice.note_values) - Voice.idea1_length
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
				chord_options = subdom_to_dom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "PS":
				chord_options = expand_subdom[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "FD":
				chord_options = subdom_to_dom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "FT":
				chord_options = (I,)
				self.create_accent_chord(chord_options)

	def make_authentic_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent2.keys()))
		Voice.note_values.extend(consequent2[rhythm_sequence])
		Voice.idea3_length = len(Voice.note_values) - (Voice.idea1_length * 2) - (Voice.idea2_length)
		# print(Voice.note_values)
		# print(rhythm_sequence)
		self.choose_chord(rhythm_sequence)

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_scale_degree = 0
		old_pitch = 0
		old_position = 0
		for chord in Voice.chord_path[1:]:
			new_scale_degree = int(bass_notes[abs(chord)])

			# Deciding between regular and inverted chord
			# (e.g., III to V6 going downward)
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
			self.pitch_amounts.append(new_pitch)
			old_pitch = new_pitch
			old_position = new_scale_degree
			old_scale_degree = new_scale_degree
		# print(self.pitch_amounts)

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		Voice.bass_pitches = self.pitch_amounts
		print(Voice.bass_pitches)
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.pitch_amounts]
		for index in range(len(self.real_notes)):
			# Raise seventh only for ascending
			if self.mode == "aeolian" and bass_notes[abs(Voice.chord_path[index])] == 6:
				print("RAISED SEVENTH!")
				self.real_notes[index] += 1
			if Voice.tonic == "C":
				self.real_notes[index] -= 12
			else:
				self.real_notes[index] -= 24

class Soprano(Voice):

	def __init__(self):
		self.pitch_amounts = []
		self.possible_pitches = []
		self.real_notes = []
		self.sheet_notes = []
		self.lily_notes = []
		self.voice = "soprano"

	def create_part(self):
		self.create_antecedent()
		self.remove_bad_notes()
		self.add_notes()
		self.create_consequent()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		print(self.sheet_notes)
		Voice.soprano_letters = self.sheet_notes
		self.lily_convert()
		return self.real_notes

	def create_antecedent(self):
		new_scale_degree = random.choice((0,2,4))
		first_pitch = self.calculate_pitch(0, new_scale_degree, 1)
		self.pitch_amounts = [first_pitch]
		self.pitch_amounts.extend(("Blank",) * (Voice.idea1_length - 1 + Voice.idea2_length))

		self.possible_pitches = [self.pitch_amounts[0]]
		self.possible_pitches.extend(("Blank",) * len(Voice.chord_path[1:-1]))
		self.possible_pitches.append([-12,0,12])
		self.populate_notes()

	def create_consequent(self):
		self.pitch_amounts.extend(self.pitch_amounts[:Voice.idea1_length])
		self.pitch_amounts.extend(("Blank",) * (Voice.idea3_length))
		# print(self.pitch_amounts)
		self.populate_notes()

	def remove_bad_notes(self):
		"""Removes bad notes from possible choices"""
		# print(Voice.bass_pitches)

		# Remove octaves
		for index, bass_pitch in enumerate(Voice.bass_pitches[1:-1]):
			pitch_options = self.possible_pitches[index + 1][:]
			# print(pitch_options, bass_pitch)
			for new_pitch in pitch_options:
				# print(new_pitch,  (new_pitch + (12 - bass_pitch)) % 12)
				if (new_pitch + (12 - bass_pitch)) % 12 == 0:
					self.possible_pitches[index + 1].remove(new_pitch)
					# print(f"Removing {new_pitch} using {bass_pitch}")

		# Remove duplicate leading tones
		for index, chord in enumerate(Voice.chord_path):
			if 6 in chord_tones[abs(chord)] and 1 in chord_tones[abs(chord)]:
				pitch_options = self.possible_pitches[index][:]
				for pitch in pitch_options:
					if (pitch + 1) % 12 == 0 and (Voice.bass_pitches[index] + 1) % 12 == 0:
						print(pitch, self.possible_pitches[index])
						print(f"Removing leading tone! {pitch}")
						self.possible_pitches[index].remove(pitch)
						print(pitch , self.possible_pitches[index])

	def add_notes(self):
		# Don't forget to apply antecedent consequent format
		"""This melody creation is naturally recursive but I modeled it 
		with iteration. You try notes until you get a good note. 
		If none of your note choices at the current position are good, 
		then your previous note is bad and should be removed. """

		note_index = 0
		while self.pitch_amounts[note_index] != "Blank": 
			note_index += 1 

		last_pitch = self.pitch_amounts[note_index - 1]
		attempts = 0
		while "Blank" in self.pitch_amounts:
			attempts += 1
			if self.possible_pitches[note_index]:
				pitch_choice = self.choose_pitch(note_index)
				voice_lead = self.check_counterpoint(pitch_choice, note_index)
				if voice_lead:
					# print("Good choice! Move on.")
					self.pitch_amounts[note_index] = pitch_choice
					last_pitch = pitch_choice
					note_index += 1
					if note_index == len(self.pitch_amounts):
						# print(f"You win: {self.pitch_amounts}")
						break
				else:
					# print("Bad choice. Try another")
					self.possible_pitches[note_index].remove(pitch_choice)
			else:
				# print("All roads lead to hell!")
				self.possible_pitches[note_index] = "Blank" 
				self.populate_notes()
				self.remove_bad_notes()
				note_index -= 1
				if note_index == 0:
					print("You fail")
				self.possible_pitches[note_index].remove(last_pitch)
		# print(f"That took {attempts} tries.")
		# print(self.pitch_amounts)

	def calculate_pitch(self, old_scale_degree, new_scale_degree, direction):
		old_position = old_scale_degree
		old_pitch = modes[Voice.mode][old_scale_degree]
		# print(f"Old scale degree: {old_scale_degree}", end=" | ")
		# print(f"New scale degree: {new_scale_degree}", end= " | ")
		if (direction > 0 and new_scale_degree >= old_scale_degree) or \
		(direction < 0 and old_scale_degree > new_scale_degree):
			shift = new_scale_degree - old_scale_degree
			new_position = old_position + shift
			new_pitch = modes[Voice.mode][new_position]

		elif direction < 0 and old_scale_degree < new_scale_degree:
			old_position += 7
			shift = new_scale_degree - old_scale_degree - 7
			new_position = old_position + shift
			new_pitch = old_pitch + modes[Voice.mode][new_position] - \
			modes[Voice.mode][old_position]

		elif direction > 0 and new_scale_degree < old_scale_degree:
			new_scale_degree += 7
			shift = new_scale_degree - old_scale_degree
			new_position = old_position + shift
			new_pitch = modes[Voice.mode][new_position]

		# print(f"Old pitch: {old_pitch}", end=" | ")
		# print(f"New pitch: {new_pitch}")

		return new_pitch

	def populate_notes(self):
		for index, value in enumerate(self.possible_pitches):
			if value == "Blank":
				current_chord = abs(Voice.chord_path[index])
				chord_root = (current_chord // 1000) - 1
				chord_notes = list(chord_tones[current_chord])
				# print(f"Removing root from {chord_notes}")
				chord_notes.remove(chord_root)
				# print(f"\nCurrent chord: {current_chord} | Chord notes: {chord_notes} | Chord root: {chord_root}")
				self.possible_pitches[index] = self.populate_note(chord_root, chord_notes)
				# print(f"\n{self.possible_pitches}. Next chord")


	def populate_note(self, chord_root, chord_notes):
		pitches = [self.calculate_pitch(0, chord_root, 1)]
		for note in chord_notes:
			if Voice.mode == "aeolian" and note == 6 and 1 in chord_notes:
				pitches.append(self.calculate_pitch(chord_root, note, 1) + 1)
				pitches.append(self.calculate_pitch(chord_root, note, 1) + 13)
				pitches.append(self.calculate_pitch(chord_root, note, -1) + 1)
				pitches.append(self.calculate_pitch(chord_root, note, -1) - 11)
			else:
				pitches.append(self.calculate_pitch(chord_root, note, 1))
				# print(f"Add {note} above: {pitches}")
				pitches.append(self.calculate_pitch(chord_root, note, 1) + 12)
				# print(f"Add {note} above (+ octave): {pitches}")
				pitches.append(self.calculate_pitch(chord_root, note, -1))
				# print(f"Add {note} below {pitches}")
				pitches.append(self.calculate_pitch(chord_root, note, -1) - 12)
				# print(f"Add {note} below (-octave) {pitches}")
		return pitches

	def choose_pitch(self, note_index):
		"""Sort avaialable pitches based on desirability 
		(closeness to last pitch). """
		number = random.choice(range(10))
		last_pitch = self.pitch_amounts[note_index - 1]
		if last_pitch in self.possible_pitches[note_index]:
			self.possible_pitches[note_index].remove(last_pitch)
		choices = self.possible_pitches[note_index][:]
		pitch_leaps = []

		for new_pitch in choices:
			pitch_leaps.append(abs(last_pitch - new_pitch))
		sorted_choices = [x for _,x in sorted(zip(pitch_leaps, choices))]


		return sorted_choices[0]

	def check_counterpoint(self, pitch_choice, note_index):
		return random.choice((True,))

	def convert_notes(self):
		"""Converts notes from relative pitch magnitudes degrees to 
		absolute pitch magnitudes"""
		self.fixed_pitches = []
		for index, pitch in enumerate(self.pitch_amounts):
			if -12 < pitch < 0:
				self.fixed_pitches.append(pitch + 12)
			elif 12 < pitch < 24:
				self.fixed_pitches.append(pitch - 12)
			elif 0 <= pitch <= 12:
				self.fixed_pitches.append(pitch)
			else:
				self.fixed_pitches.append(f"What? {pitch}")
		# print(self.fixed_pitches)  
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.pitch_amounts]

		vocal_range = True
		for real_note in self.real_notes:
			if real_note < 59:
				vocal_range = False
				print("Perform octave transposition")
				print(self.real_notes)
				break

		if not vocal_range:
			for index, real_note in enumerate(self.real_notes):
				self.real_notes[index] += 12
			print("Vocal range fixed")
			print(self.real_notes)



		# for index in range(len(self.real_notes)):
		# 	# Raise seventh only for ascending
		# 	if self.mode == "aeolian" and self.fixed_pitches[index] == 11:
		# 		print("Actual RAISED SEVENTH!")
		# 	if Voice.tonic == "B":
		# 		self.real_notes[index] -= 12






