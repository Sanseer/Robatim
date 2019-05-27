import random

from voice import Voice
import idioms as idms

class Bass(Voice):
	"""Creates a bass voice with an explicit chord progression. 
	Initializes settings for the entire song."""

	def __init__(self, time_sig=(4,2), tonic="C", mode="ionian"):
		Voice.chord_path = [idms.I]
		self.old_chord = Voice.chord_path[-1]
		Voice.tonic = tonic
		Voice.mode = mode
		Voice.chromatics = [None]
		Voice.measure_length = time_sig[0]
		Voice.beat_division = time_sig[1]
		if Voice.measure_length == 4:
			Voice.half_rest_ending = random.choice((True,False))
		Voice.consequent_rhythm_change = random.choice((True,False))
		if mode == "ionian":
			Voice.accidental = idms.major_accidentals[tonic]
		elif mode == "aeolian":
			Voice.accidental = idms.minor_accidentals[tonic]

		self.chord_style1 = None
		self.chord_style2 = None
		self.chord_style3 = None
		self.chord_style4 = None
		self.basic_idea1_rhythm = None
		self.basic_idea2_rhythm = None
		self.pitch_amounts = [0]
		self.real_notes = []
		self.sheet_notes = []
		self.lily_notes = []

	def create_part(self):
		"""Creates the bass portion of the tune"""
		print(f"Song in {Voice.tonic} {Voice.mode} with {Voice.accidental}'s")
		print(f"{Voice.measure_length} beats divided in {Voice.beat_division}")
		self.create_chord_progression()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		return self.create_rests(self.real_notes[:])

	def create_chord_progression(self):
		"""Creates the chord progression, the basis for all notes 
		with antecedent and consequent sections."""
		print("="*20)
		print("Creating antecedent")
		self.create_antecedent()
		print("="*20)
		print("Creating consequent")
		print("Rhythm change?",Voice.consequent_rhythm_change)
		self.create_consequent()

		# Now that you've applied the optional rests you can align the 
		# rhythm to the actual notes
		if Voice.half_rest_ending:
			Voice.idea2_length -= 1
			Voice.idea4_length -= 1

	def create_antecedent(self):
		"""Creates the antecedent section of the tune"""
		if Voice.measure_length == 3:
			self.tonic_rhythms = idms.bi1_rhythms_of_3
		elif Voice.measure_length == 4:
			self.tonic_rhythms = idms.bi1_rhythms_of_4
		self.chord_style1 = random.choice(tuple(self.tonic_rhythms.keys()))
		self.basic_idea1_rhythm = self.tonic_rhythms[self.chord_style1]
		Voice.note_values.extend(self.basic_idea1_rhythm)
		self.add_chords(self.chord_style1)

		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		Voice.idea1_length = len(Voice.note_values)
		contrast_idea_start = self.transition_idea(self.chord_style1)

		contrast_idea1_rhythm = self.basic_idea1_rhythm
		# [2,2,2,2,2,2,2,2] should always use half rest?
		if self.basic_idea1_rhythm == (2,2,2,2):
			print("Changing rhythm!")
			Voice.half_rest_ending = True
		print("Half rest?", Voice.half_rest_ending)
		if Voice.half_rest_ending:
			if contrast_idea_start == "tonic":
				self.chord_style2 = random.choice(
					idms.ci1_from_tonic_with_rest[contrast_idea1_rhythm])
			elif contrast_idea_start == "subdominant":
				self.chord_style2 = random.choice(
					idms.ci1_from_subdom_with_rest[contrast_idea1_rhythm])
			contrast_idea1_rhythm = list(contrast_idea1_rhythm)
			if contrast_idea1_rhythm[-2:] == [1,1]:
				contrast_idea1_rhythm[-2:] = ["2"]
			elif contrast_idea1_rhythm[-1] == 2:
				contrast_idea1_rhythm[-1] = "2"
			elif contrast_idea1_rhythm[-1] == 1:
				contrast_idea1_rhythm[-1] = "1"
		else:
			if contrast_idea_start == "tonic":
				self.chord_style2 = random.choice(
					idms.ci1_from_tonic_no_rest[contrast_idea1_rhythm])
			elif contrast_idea_start == "subdominant":
				self.chord_style2 = random.choice(
					idms.ci1_from_subdom_no_rest[contrast_idea1_rhythm])
				
		Voice.idea2_length = len(contrast_idea1_rhythm)
		Voice.note_values.extend(contrast_idea1_rhythm)
		self.add_chords(self.chord_style2)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		assert(len(Voice.chord_path) == len(Voice.note_values) or 
			Voice.half_rest_ending), "Chord error"

	def add_chords(self, chord_types):
		"""Adds chord(s) to growing chord progression. Some chord sequences 
		will fail either because I have yet to implement all the techniques 
		or because such a sequence doesn't exist in the common practice 
		period style."""
		# Don't repeat chord from weak to strong beat
		# Old chord should have property decorator
		print("Chord types:",chord_types)
		for chord_type in chord_types:
			print("Chord type:", chord_type)
			chord_type = chord_type.replace("2","")
		# explicit if statements prevent redundant dicts with same destination 
			if chord_type == "PDA":
				chord_options = (idms.V,)
			elif chord_type == "PDAX":
				chord_options = (idms.V, idms.V7)
			elif chord_type == "ITA":
				chord_options = (-idms.I6, -idms.III)
			elif chord_type == "VI":
				chord_options = (-idms.VI,)
			elif chord_type == "TAU":
				chord_options = (-idms.I,)
			else:
				chord_options = idms.chord_groups[chord_type][abs(self.old_chord)]
			if chord_type == "SAU":
				chord_options = list(chord_options)
				print(chord_options)
				chord_options.extend((idms.I64,) * 2)
				print(chord_options)
			chords_chosen = random.choice(chord_options)
			if type(chords_chosen) == int:
				chords_chosen = (chords_chosen,)
			[Voice.chord_path.append(chord) for chord in chords_chosen]
			for chord in chords_chosen:
				if abs(chord) // 10000 in (8, 9):
					Voice.chromatics.append("2Dim")
				elif abs(chord) % 10 != 1:
					Voice.chromatics.append("2Dom")
				else:
					Voice.chromatics.append(None)
			# [Voice.chromatics.append("2Dom") if abs(chord) % 10 != 1 else 
			# 	Voice.chromatics.append(None) for chord in chords_chosen]
			self.old_chord = abs(Voice.chord_path[-1])

	def add_single_chord(self, progression_type):
		"""Add single chord to progression, usually at transition points"""
		chord_options = progression_type[abs(self.old_chord)]
		chord_choice = random.choice(chord_options)
		if abs(chord_choice) // 10000 in (8, 9):
			Voice.chromatics.append("2Dim")
		elif abs(chord_choice) % 10 != 1:
			Voice.chromatics.append("2Dom")
		else:
			Voice.chromatics.append(None)
		Voice.chord_path.append(chord_choice)
		self.old_chord = Voice.chord_path[-1]

	def transition_idea(self, chord_types):
		"""Transitions from basic idea to contrasting idea of period form"""
		print("-"*20)
		if chord_types[-1] == "TPS-I":
			print("Subdominant contrast. Adding first CI note")
			contrast_idea_start = "subdominant"
			self.add_single_chord(idms.tonic_to_subdom1)
		else:
			print("Restart tonic. Adding first CI note")
			contrast_idea_start = "tonic"
			self.add_single_chord(idms.restart_tonic)

		return contrast_idea_start

	def create_consequent(self):
		"""Create the consequent section of the tune"""
		self.add_single_chord(idms.restart_tonic)
		self.chord_style3 = self.chord_style1
		self.basic_idea2_rhythm = self.basic_idea1_rhythm
		if Voice.consequent_rhythm_change:
			while self.basic_idea2_rhythm == self.basic_idea1_rhythm:
				print("Duplicate! Try again")
				self.chord_style3 = random.choice(tuple(self.tonic_rhythms.keys()))
				self.basic_idea2_rhythm = self.tonic_rhythms[self.chord_style3]
		Voice.idea3_length = len(self.basic_idea2_rhythm)
		Voice.note_values.extend(self.basic_idea2_rhythm)
		
		self.add_chords(self.chord_style3)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		contrast_idea_start = self.transition_idea(self.chord_style3)

		contrast_idea2_rhythm = self.basic_idea1_rhythm
		if Voice.half_rest_ending:
			if contrast_idea_start == "tonic":
				self.chord_style4 = random.choice(
					idms.ci2_from_tonic_with_rest[contrast_idea2_rhythm])
			elif contrast_idea_start == "subdominant":
				self.chord_style4 = random.choice(
					idms.ci2_from_subdom_with_rest[contrast_idea2_rhythm])
		else:
			if contrast_idea_start == "tonic":
				self.chord_style4 = random.choice(
					idms.ci2_from_tonic_no_rest[contrast_idea2_rhythm])
			elif contrast_idea_start == "subdominant":
				self.chord_style4  = random.choice(
					idms.ci2_from_subdom_no_rest[contrast_idea2_rhythm])
		
		Voice.note_values.extend(Voice.note_values[
			Voice.idea1_length:Voice.idea1_length + Voice.idea2_length])
		Voice.idea4_length = Voice.idea2_length

		self.add_chords(self.chord_style4)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))


	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_scale_degree = 0
		old_pitch = 0
		old_position = 0
		for index, chord in enumerate(Voice.chord_path[1:]):
			new_scale_degree = int(idms.bass_notes[abs(chord)])

			# Deciding between regular and inverted chord
			# (e.g., III to V6 going downward)
			# Created additional condition to have proper number in bass motion list
			if (chord > 0 and Voice.chord_path[index] < 0 and 
				old_scale_degree > new_scale_degree):
				old_position -= 7
				shift = new_scale_degree - old_scale_degree + 7
				new_position = old_position + shift
				new_pitch = idms.modes[Voice.mode][new_position]

			elif chord > 0 or (chord < 0 and old_scale_degree > new_scale_degree):
				shift = new_scale_degree - old_scale_degree
				new_position = old_position + shift
				new_pitch = idms.modes[Voice.mode][new_position]

			elif chord < 0 and new_scale_degree > old_scale_degree:
				old_position += 7
				shift = new_scale_degree - old_scale_degree - 7
				new_position = old_position + shift
				new_pitch = old_pitch + idms.modes[Voice.mode][new_position] - \
					idms.modes[Voice.mode][old_position]

			Voice.bass_motion.append(shift)
			pitch_change = new_pitch - old_pitch
			self.pitch_amounts.append(new_pitch) 
			old_pitch = new_pitch
			old_position = new_scale_degree
			old_scale_degree = new_scale_degree

			# Raised seventh
			if (1 in idms.chord_tones[abs(chord)] and 
				6 in idms.chord_tones[abs(chord)] and
				2 not in idms.chord_tones[abs(chord)] and 
				(new_pitch + 2) % 12 == 0):
				self.pitch_amounts[-1] += 1

		# Shift down an octave for IV6 and VI until tonic
		# Add feature when changing between basic and contrast ideas 
		# to prevent octave shift
		descents = (index for index, chord in enumerate(Voice.chord_path) 
			if chord in (-idms.IV6, -idms.VI, -idms.DIM7_DOWN_OF_VI, 
				-idms.DIM7_UP_OF_VI, -idms.V43_OF_VI))
		# tonic_index = (Voice.idea1_length + Voice.idea2_length, 
		# 	len(Voice.chord_path ) - 1)
		tonic_indices = [index for index, chord in enumerate(Voice.chord_path)
			if abs(chord) == idms.I]
		print(self.chord_path)
		print(tonic_indices)
		
		past_index = -1
		# Detect neighbor indect for nonchromatic chords
		for index in descents:
			if index == past_index + 1:
				continue
			past_index = index
			index += 1
			while index not in tonic_indices:
				self.pitch_amounts[index] -= 12
				index += 1

		for index, move in enumerate(Voice.bass_motion[:]):
			Voice.bass_motion[index] = self.move_direction(move)

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		self.real_notes = [note + 60 + idms.tonics[Voice.tonic] 
		for note in self.pitch_amounts]
		print(self.chromatics)
		print(self.chord_path)
		print(self.real_notes)

		#alter pitches and bass motion based on secondary dominants
		for nc_index in range(len(Voice.chromatics)):
			if Voice.chromatics[nc_index] == "2Dom":
				self.real_notes[nc_index] += self.convert_sec_dom(
					abs(Voice.chord_path[nc_index]), self.real_notes[nc_index])
			elif Voice.chromatics[nc_index] == "2Dim":
				self.real_notes[nc_index] += self.convert_sec_dim(
					abs(Voice.chord_path[nc_index]), self.real_notes[nc_index])
				old_note = self.real_notes[nc_index - 1]
				current_note = self.real_notes[nc_index]
				next_note = self.real_notes[nc_index + 1]
				move = current_note - old_note
				Voice.bass_motion[nc_index - 1] = self.move_direction(move)
				move = next_note - current_note
				Voice.bass_motion[nc_index] = self.move_direction(move)


		for index in range(len(self.real_notes)):
			if Voice.tonic == "C":
				self.real_notes[index] -= 12
			else:
				self.real_notes[index] -= 24

		Voice.bass_pitches = self.real_notes
		print(self.real_notes, len(self.real_notes))
