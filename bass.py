import random
import pysnooper

from voice import Voice
import idioms as idms

class Bass(Voice):
	"""Creates a bass voice with an explicit chord progression. 
	Initializes settings for the entire song."""

	def __init__(self, time_sig=(4,2), tonic="C", mode="ionian"):
		Voice.chord_path = [idms.I]
		Voice.tonic = tonic
		Voice.mode = mode
		Voice.chromatics = [None]
		Voice.measure_length = time_sig[0]
		Voice.beat_division = time_sig[1]
		if Voice.measure_length == 4:
			Voice.half_rest_ending = random.choice((True, False))
		Voice.consequent_rhythm_change = random.choice((True, False))
		if mode == "ionian":
			Voice.accidental = idms.major_accidentals[tonic]
		elif mode == "aeolian":
			Voice.accidental = idms.minor_accidentals[tonic]

		self.note_index = 0
		self.chord_style1 = None
		self.chord_style2 = None
		self.chord_style3 = None
		self.chord_style4 = None
		self.basic_idea1_rhythm = None
		self.basic_idea2_rhythm = None

		self.measure_notes = []
		self.pitch_amounts = [0]
		self.real_notes = []
		self.final_notes = []
		self.sheet_notes = []
		self.lily_notes = []

	@property
	def old_chord(self):
		return abs(Voice.chord_path[-1])

	def create_part(self):
		"""Creates the bass portion of the tune"""
		print(f"Song in {Voice.tonic} {Voice.mode} with {Voice.accidental}'s")
		print(f"{Voice.measure_length} beats divided in {Voice.beat_division}")
		self.create_chord_progression()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		self.create_groove()
		# return self.create_rests(self.real_notes[:])

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

		for index, full_chord in enumerate(Voice.chord_path[:]):
			if (Voice.chromatics[index] is None and 
			21 <= abs(full_chord) // 10000 <= 26):
				if full_chord > 0:
					sign = 1
				elif full_chord < 0:
					sign = -1
				chord = abs(full_chord)
				inversion = chord // 10 % 1000
				root = chord % 10
				print("Before", Voice.chord_path[index])
				Voice.chord_path[index] = sign * (root * 100000 + inversion * 10 + 1)
				print("After", Voice.chord_path[index])



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
		if self.basic_idea1_rhythm in ((2,2,2,2), (2,1,1,2,2)):
			print("Changing rhythm!")
			Voice.half_rest_ending = True
		elif (self.basic_idea1_rhythm[-1] in (3,4) or 
		self.basic_idea1_rhythm in ((4,2,2), (3,2,1))):
			Voice.half_rest_ending = False
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
		will fail"""
		# Don't repeat chord from weak to strong beat
		print("Chord types:",chord_types)
		for chord_type in chord_types:
			print("Chord type:", chord_type)
			chord_type = chord_type.replace("2","")
		# explicit if statements prevent redundant dict keys with same values 
			if chord_type == "ITA":
				chord_options = (-idms.I6,)
			elif chord_type == "VI":
				chord_options = (-idms.VI,)
			elif chord_type == "TAU":
				chord_options = (-idms.I, -idms.I_MAJOR)
			else:
				chord_options = idms.chord_sequences[chord_type][self.old_chord]
			if chord_type == "SAU":
				chord_options = list(chord_options)
				chord_options.extend((idms.I64,) * 2)
			chords_chosen = random.choice(chord_options)
			if type(chords_chosen) == int:
				chords_chosen = (chords_chosen,)
			[Voice.chord_path.append(chord) for chord in chords_chosen]
			for chord in chords_chosen:
				self.add_chromatic(chord)

	def add_chromatic(self, chord):
		chord = abs(chord)
		chord_flavor = chord // 10000
		chord_stem = chord % 10
		if chord_flavor == 11 or (chord_flavor == 70 and chord_stem != 1):
			Voice.chromatics.append("2Dim")
		elif chord_flavor % 10 == 0 and chord_stem != 1:
			Voice.chromatics.append("2Dom")
		elif 21 <= chord_flavor <= 26:
			if (chord_flavor == 21 and (self.mode == "aeolian" or 
			chord_stem in (7,2,4))):
				Voice.chromatics.append("lydian")
			elif chord_flavor == 22 and self.mode == "aeolian":
				Voice.chromatics.append("ionian")
			elif (chord_flavor == 23 and (self.mode == "aeolian" or 
			chord_stem in (3,5,7))):
				Voice.chromatics.append("mixo")
			elif (chord_flavor == 24 and (self.mode == "ionian" or 
			chord_stem in (2,4,6))): 
				Voice.chromatics.append("dorian")
			elif chord_flavor == 25 and self.mode == "ionian":
				Voice.chromatics.append("aeolian")
			elif (chord_flavor == 26 and (self.mode == "ionian" or 
			chord_stem in (5,7,2))):
				Voice.chromatics.append("phryg")
			else:
				Voice.chromatics.append(None)
		else:
			Voice.chromatics.append(None)

	def add_single_chord(self, progression_type):
		"""Add single chord to progression, usually at transition points"""
		chord_options = progression_type[abs(self.old_chord)]
		chord_choice = random.choice(chord_options)
		self.add_chromatic(chord_choice)
		Voice.chord_path.append(chord_choice)

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
		# Replicate melody?
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

		# change half cadence and full cadence ending from 2,1 to 1,2

		self.add_chords(self.chord_style4)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_pitch = 0
		old_scale_degree = 0
		for n_index, chord in enumerate(Voice.chord_path[1:]):
			new_scale_degree = idms.bass_notes[abs(chord)]
			new_pitch = idms.modes[self.mode][new_scale_degree]
			# You don't need to raise diatonic leading tone if modulation
			if Voice.chromatics[n_index + 1] not in ("2Dom", "2Dim"):
				if self.mode == "aeolian" and idms.bass_notes[abs(chord)] == 6:
					new_pitch += 1
			if old_scale_degree == new_scale_degree:
				new_pitch = old_pitch
			elif chord > 0 and old_pitch >= 0 and new_pitch > old_pitch:
				pass
			elif chord < 0 and old_pitch >= 0 and new_pitch < old_pitch:
				pass
			elif chord < 0 and old_pitch >= 0 and new_pitch > old_pitch:
				new_pitch -= 12
			elif chord > 0 and old_pitch < 0 and (new_pitch - 12) > old_pitch:
				new_pitch -= 12
			elif chord < 0 and old_pitch < 0 and (new_pitch - 12) < old_pitch:
				new_pitch -= 12
			elif chord > 0 and old_pitch < 0 and (new_pitch - 12) < old_pitch:
				pass

		# correct for half and auth cadence

			shift = new_pitch - old_pitch
			self.pitch_amounts.append(new_pitch)
			old_pitch = new_pitch
			old_scale_degree = new_scale_degree


			Voice.bass_motion.append(shift)

		tonic_index = Voice.idea1_length + Voice.idea2_length
		print(tonic_index)
		print(self.pitch_amounts)
		print(Voice.bass_motion)
		if (set(Voice.chord_path[:tonic_index]) & {-idms.VI, idms.IV6, 
		-idms.DIM7_DOWN_OF_VI, -idms.VII7_OF_VI, -idms.V43_OF_VI} 
		and self.pitch_amounts[tonic_index] < 0):
			print("Shifting pitches upward")
			self.bass_motion[tonic_index - 1] = 1
			for index in range(tonic_index, tonic_index + 
				len(self.pitch_amounts[tonic_index:])):
				self.pitch_amounts[index] += 12

		Voice.chord_symbols = self.create_chord_names()
		print(Voice.chord_symbols)
		print(self.pitch_amounts)
		print(Voice.bass_motion)

		for index, move in enumerate(Voice.bass_motion[:]):
			Voice.bass_motion[index] = self.move_direction(move)
		print(Voice.bass_motion)

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		self.real_notes = [note + 48 + idms.tonics[Voice.tonic] 
		for note in self.pitch_amounts]
		print(self.chromatics, end="\n\n")
		if max(self.real_notes) > 62:
			for index, note in enumerate(self.real_notes[:]):
				self.real_notes[index] -= 12

		#alter pitches and bass motion based on secondary dominants
		for nc_index in range(len(Voice.chromatics)):
			if Voice.chromatics[nc_index]:
				self.note_index = nc_index
				if Voice.chromatics[nc_index] == "2Dom":
					self.real_notes[nc_index] += self.convert_sec_dom(
						abs(Voice.chord_path[nc_index]), self.real_notes[nc_index])
				elif Voice.chromatics[nc_index] == "2Dim":
					self.real_notes[nc_index] += self.convert_sec_dim(
						abs(Voice.chord_path[nc_index]), self.real_notes[nc_index])
				elif Voice.chromatics[nc_index] in idms.modes.keys():
					self.real_notes[nc_index] += self.convert_mode(
						abs(Voice.chord_path[nc_index]), self.real_notes[nc_index])
				old_note = self.real_notes[nc_index - 1]
				current_note = self.real_notes[nc_index]
				move = current_note - old_note
				Voice.bass_motion[nc_index - 1] = self.move_direction(move)
				if nc_index < len(self.real_notes) - 1:
					next_note = self.real_notes[nc_index + 1]
					move = next_note - current_note
					Voice.bass_motion[nc_index] = self.move_direction(move)

		Voice.bass_pitches = self.real_notes

	def group_rhythm(self):

		self.note_index = 0
		for _ in range(8):
			array = []
			while sum(array) < Voice.measure_length:
				array.append(int(self.note_values[self.note_index]))
				self.note_index += 1
			Voice.measure_rhythms.append(array)

		if Voice.half_rest_ending:
			Voice.measure_rhythms[3][-1] = str(Voice.measure_rhythms[3][-1])
			Voice.measure_rhythms[7][-1] = str(Voice.measure_rhythms[3][-1])
		self.note_index = 0

	def create_groove(self):
		self.group_rhythm()
		self.group_notes()

		Voice.rhythm_styles = [ [] for _ in range(8)]
		self.final_rhythm = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]

		for m_index, chosen_measure in enumerate(Voice.measure_rhythms[:3]):
			for beat in chosen_measure:
				if beat == 2 and chosen_measure:
					self.final_rhythm[m_index].extend((1,"1"))
					Voice.rhythm_styles[m_index].append("Waltz2")
				elif beat == 3:
					self.final_rhythm[m_index].extend((1,"1","1"))
					Voice.rhythm_styles[m_index].append("Waltz3")
				elif beat == 4:
					self.final_rhythm[m_index].extend((1,"1",1,"1"))
					Voice.rhythm_styles[m_index].append("Waltz4")
				else:
					self.final_rhythm[m_index].append(beat)
					Voice.rhythm_styles[m_index].append(None)

		for m_index, chosen_measure in enumerate(Voice.measure_rhythms[4:7]):
			for beat in chosen_measure:
				if beat == 2:
					self.final_rhythm[m_index + 4].extend((1,"1"))
					Voice.rhythm_styles[m_index + 4].append("Waltz2")
				elif beat == 3:
					self.final_rhythm[m_index + 4].extend((1,"1","1"))
					Voice.rhythm_styles[m_index + 4].append("Waltz3")
				elif beat == 4:
					self.final_rhythm[m_index + 4].extend((1,"1",1,"1"))
					Voice.rhythm_styles[m_index + 4].append("Waltz4")
				else:
					self.final_rhythm[m_index + 4].append(beat)
					Voice.rhythm_styles[m_index + 4].append(None)

		self.final_rhythm[3] = Voice.measure_rhythms[3]
		self.final_rhythm[7] = Voice.measure_rhythms[7]

		print(self.final_rhythm)
		print(Voice.rhythm_styles)

		for m_index, chosen_measure in enumerate(Voice.rhythm_styles[:3]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				main_note = self.measure_notes[m_index][r_index]
				if rhythm_style == "Waltz2":
					self.final_notes[m_index].extend((main_note, "REST"))
				elif rhythm_style == "Waltz3":
					self.final_notes[m_index].extend((main_note, "REST", "REST"))
				elif rhythm_style == "Waltz4":
					self.final_notes[m_index].extend((main_note, "REST", main_note, "REST"))
				elif rhythm_style is None:
					self.final_notes[m_index].append(main_note)


		for m_index, chosen_measure in enumerate(Voice.rhythm_styles[4:7]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				main_note = self.measure_notes[m_index + 4][r_index]
				if rhythm_style == "Waltz2":
					self.final_notes[m_index + 4].extend((main_note, "REST"))
				elif rhythm_style == "Waltz3":
					self.final_notes[m_index + 4].extend((main_note, "REST", "REST"))
				elif rhythm_style == "Waltz4":
					self.final_notes[m_index + 4].extend((main_note, "REST", main_note, "REST"))
				elif rhythm_style is None:
					self.final_notes[m_index + 4].append(main_note)

		self.final_notes[3] = self.measure_notes[3]
		self.final_notes[7] = self.measure_notes[7]
		if Voice.half_rest_ending:
			self.final_notes[3].append("REST")
			self.final_notes[7].append("REST")

		print(self.final_notes)
		self.final_rhythm = self.flatten_sequence(self.final_rhythm)
		self.final_notes = self.flatten_sequence(self.final_notes)
		print(self.final_rhythm, len(self.final_rhythm))
		print(self.final_notes, len(self.final_notes))


	@property
	def notes(self):
		return self.final_notes

	@property
	def groove(self):
		return self.final_rhythm