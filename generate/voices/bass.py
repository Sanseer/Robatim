import random

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b

class Bass(Voice):
	"""Creates a bass voice with an explicit chord progression. 
	Initializes settings for the entire song."""

	def __init__(self, time_sig=(4,2), tonic="C", mode="ionian"):
		Voice.chord_path = [idms_b.I]
		Voice.tonic = tonic
		Voice.mode = mode
		Voice.chromatics = [None]
		Voice.measure_length = time_sig[0]
		Voice.beat_division = time_sig[1]
		Voice.half_rest_ending = random.choice((True, False))
		# Voice.consequent_rhythm_change = random.choice((True, False))
		if mode == "ionian":
			import generate.idioms.major
			Voice.idms_mode = generate.idioms.major
		elif mode == "aeolian":
			import generate.idioms.minor
			Voice.idms_mode = generate.idioms.minor

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
		self.sheet_notes = []
		self.lily_notes = []

		Voice.rhythm_styles = [ [] for _ in range(8)]
		self.final_rhythm = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]

	@property
	def old_chord(self):
		return abs(Voice.chord_path[-1])

	def create_part(self):
		"""Creates the bass portion of the tune"""
		print(f"Song in {Voice.tonic} {Voice.mode}")
		print(f"{Voice.measure_length} beats divided in {Voice.beat_division}")
		self.create_chord_progression()
		self.add_notes()
		self.convert_notes()
		self.create_groove()
		self.make_letters()
		self.lily_convert()
		# return self.create_rests(self.real_notes[:])

	def create_chord_progression(self):
		"""Creates the chord progression, the basis for all notes 
		with antecedent and consequent sections."""
		print("="*20)
		print("Creating antecedent")
		self.create_antecedent()
		print("="*20)
		print("Creating consequent")
		print("Rhythm change?", Voice.consequent_rhythm_change)
		self.create_consequent()

		# Now that you've applied the optional rests you can align the 
		# rhythm to the actual notes
		if Voice.half_rest_ending:
			Voice.idea2_length -= 1

	def create_antecedent(self):
		"""Creates the antecedent of the period using basic/contrast ideas"""
		if Voice.measure_length == 3:
			antecedent_rhythms = idms_b.bi1_rhythms_of_3
		elif Voice.measure_length == 4:
			antecedent_rhythms = idms_b.bi1_rhythms_of_4
		self.chord_style1 = random.choice(tuple(antecedent_rhythms.keys()))
		self.basic_idea1_rhythm = antecedent_rhythms[self.chord_style1]
		Voice.note_values.extend(self.basic_idea1_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		self.add_chord_sequence(self.chord_style1)

		Voice.idea1_length = len(Voice.note_values)
		self.declare_transition(self.chord_style1)
		if random.choice((True,False)):
			contrast_idea1_rhythm = self.basic_idea1_rhythm
		else:
			contrast_idea1_rhythm = random.choice(
				idms_b.ci1_response_rhythms[self.basic_idea1_rhythm])
		if contrast_idea1_rhythm in {(2,2,2,2), (2,1,2,1)}:
			Voice.half_rest_ending = True

		print("Half rest?", Voice.half_rest_ending)
		if Voice.half_rest_ending:
			if self.contrast_idea_start == "tonic":
				self.chord_style2 = random.choice(
					idms_b.ci1_tonic_with_rest[contrast_idea1_rhythm])
			elif self.contrast_idea_start == "subdominant":
				self.chord_style2 = random.choice(
					idms_b.ci1_subdom_with_rest[contrast_idea1_rhythm])
			contrast_idea1_rhythm = list(contrast_idea1_rhythm)
			self.add_rest_rhythm(contrast_idea1_rhythm)
		else:
			if self.contrast_idea_start == "tonic":
				self.chord_style2 = random.choice(
					idms_b.ci1_tonic_no_rest[contrast_idea1_rhythm])
			elif self.contrast_idea_start == "subdominant":
				self.chord_style2 = random.choice(
					idms_b.ci1_subdom_no_rest[contrast_idea1_rhythm])
				
		Voice.idea2_length = len(contrast_idea1_rhythm)
		Voice.note_values.extend(contrast_idea1_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		self.add_transition_chord(self.chord_style2)
		self.add_chord_sequence(self.chord_style2)
		assert(len(Voice.chord_path) == len(Voice.note_values) or 
			Voice.half_rest_ending), "Chord error"

	def add_chord_sequence(self, chord_types):
		"""Adds chord(s) to growing chord progression. Some chord sequences 
		will fail"""
		# Don't repeat chord from weak to strong beat
		print("Chord types:",chord_types)
		for chord_type in chord_types:
			print("Chord type:", chord_type)
			chord_type = chord_type.replace("*","")
			chord_options = self.idms_mode.chord_sequences[chord_type][self.old_chord]
			chords_chosen = random.choice(chord_options)
			if type(chords_chosen) == int:
				chords_chosen = (chords_chosen,)
			[Voice.chord_path.append(chord) for chord in chords_chosen]
			for chord in chords_chosen:
				self.add_chromatic(chord)

	def add_single_chord(self, progression_type):
		"""Add single chord to progression"""
		chord_options = progression_type[abs(self.old_chord)]
		chord_choice = random.choice(chord_options)
		self.add_chromatic(chord_choice)
		Voice.chord_path.append(chord_choice)

	def add_chromatic(self, chord):
		"""Marks chords for mode mixture and modulation"""
		chord = abs(chord)
		chord_flavor = chord // 10000
		chord_stem = chord % 10
		if chord_flavor == 11 or (chord_flavor == 70 and chord_stem != 1):
			Voice.chromatics.append("2Dim")
		elif chord_flavor % 10 == 0 and chord_stem != 1:
			Voice.chromatics.append("2Dom")
		elif 21 <= chord_flavor <= 26:
			if (chord_flavor == 21 and (self.mode == "aeolian" or 
			  chord_stem in {7,2,4})):
				Voice.chromatics.append("lydian")
			elif chord_flavor == 22 and self.mode == "aeolian":
				Voice.chromatics.append("ionian")
			elif (chord_flavor == 23 and (self.mode == "aeolian" or 
			  chord_stem in {3,5,7})):
				Voice.chromatics.append("mixo")
			elif (chord_flavor == 24 and (self.mode == "ionian" or 
			  chord_stem in {2,4,6})): 
				Voice.chromatics.append("dorian")
			elif chord_flavor == 25 and self.mode == "ionian":
				Voice.chromatics.append("aeolian")
			elif (chord_flavor == 26 and (self.mode == "ionian" or 
			  chord_stem in {5,7,2})):
				Voice.chromatics.append("phryg")
		else:
			Voice.chromatics.append(None)

	def declare_transition(self, chord_types):
		"""Decides transition type from basic idea to contrasting idea"""
		print("-"*20)
		if (chord_types[-1] == "TA" and random.choice((True, True, False)) 
		  and not self.basic_idea2_rhythm and self.basic_idea1_rhythm[-1] in {3,4} 
		  and self.old_chord != idms_b.VI):
			print("Restart tonic. Adding first CI note")
			self.contrast_idea_start = "tonic"
		elif chord_types[-1] == "TA" and not self.basic_idea2_rhythm:
			print("Subdominant contrast. Adding first CI note")
			self.contrast_idea_start = "subdominant"
		elif chord_types[-1] in {"TA","SA2+M"} and self.basic_idea2_rhythm:
			print("Subdominant contrast. Adding first CI note")
			self.contrast_idea_start = "subdominant"
		elif chord_types == ("SA1+M",) and self.basic_idea2_rhythm:
			self.contrast_idea_start = "dominant"
			print("Dominant contrast. Adding first CI note")

	def add_transition_chord(self, next_chord_style):
		"""Adds transition chord for the next 2 measures"""
		if self.contrast_idea_start == "tonic":
			self.add_single_chord(idms_b.restart_tonic)
		elif self.contrast_idea_start == "subdominant":
			if next_chord_style[0] in {"SA1-M","SA1+M"}:
				self.add_single_chord(idms_b.to_subdom2_strong)
			elif next_chord_style[0] in {"HC1","IAC2","PAC2"}:
				self.add_single_chord(idms_b.to_subdom1_strong)
		elif self.contrast_idea_start == "dominant":
			self.add_single_chord(idms_b.restart_dom)

	def add_rest_rhythm(self, rhythm):
		"""Modifies end of rhythm to include rest"""
		if rhythm[-1] == 2:
			rhythm[-1] = "2"
		elif rhythm[-1] == 1:
			rhythm[-1] = "1"
		elif rhythm[-1] == 3:
			rhythm[-1:] = [2,"1"]
		elif rhythm[-1] == 4:
			rhythm[-1:] = [2,"2"]

	def create_consequent(self):
		"""Creates the consequent of the period using basic/contrast ideas"""
		# Replicate melody?
		self.add_single_chord(idms_b.restart_tonic)
		if Voice.measure_length == 3:
			consequent_rhythms = idms_b.ci1_rhythms_of_3
		elif Voice.measure_length == 4:
			consequent_rhythms = idms_b.ci1_rhythms_of_4
		self.chord_style3 = random.choice(tuple(consequent_rhythms.keys()))
		self.basic_idea2_rhythm = consequent_rhythms[self.chord_style3]
		Voice.idea3_length = len(self.basic_idea2_rhythm)
		Voice.note_values.extend(self.basic_idea2_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		
		self.add_chord_sequence(self.chord_style3)
		self.declare_transition(self.chord_style3)
		if self.contrast_idea_start == "dominant":
			if Voice.measure_length == 4:
				contrast_idea2_rhythm = (4,4)
			elif Voice.measure_length == 3:
				contrast_idea2_rhythm = (3,3)
		else:
			contrast_idea2_rhythm = random.choice(
				idms_b.ci2_response_rhythms[self.basic_idea2_rhythm])
		Voice.idea4_length = len(contrast_idea2_rhythm)

		if Voice.half_rest_ending:
			if self.contrast_idea_start == "tonic":
				self.chord_style4 = random.choice(
					idms_b.ci2_tonic_with_rest[contrast_idea2_rhythm])
			elif self.contrast_idea_start == "subdominant":
				self.chord_style4 = random.choice(
					idms_b.ci2_subdom_with_rest[contrast_idea2_rhythm])
			elif self.contrast_idea_start == "dominant":
				self.chord_style4 = ("PAC1",)
			contrast_idea2_rhythm = list(contrast_idea2_rhythm)
			self.add_rest_rhythm(contrast_idea2_rhythm)
		else:
			if self.contrast_idea_start == "tonic":
				self.chord_style4 = random.choice(
					idms_b.ci2_tonic_no_rest[contrast_idea2_rhythm])
			elif self.contrast_idea_start == "subdominant":
				self.chord_style4  = random.choice(
					idms_b.ci2_subdom_no_rest[contrast_idea2_rhythm])
			elif self.contrast_idea_start == "dominant":
				self.chord_style4 = ("PAC1",)
		
		Voice.note_values.extend(contrast_idea2_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		self.add_transition_chord(self.chord_style4)
		self.add_chord_sequence(self.chord_style4)

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_pitch = 0
		old_scale_degree = 0
		tonic_indices = {Voice.idea1_length + Voice.idea2_length, 
			Voice.idea1_length + Voice.idea2_length + Voice.idea3_length + 
			Voice.idea4_length - 1}
		for n_index, chord in enumerate(Voice.chord_path[1:]):
			new_scale_degree = idms_b.bass_notes[abs(chord)]
			new_pitch = idms_b.modes[self.mode][new_scale_degree]
			# You don't need to raise diatonic leading tone if modulation
			if (Voice.chromatics[n_index + 1] not in {"2Dom", "2Dim"} and 
			  self.mode == "aeolian" and idms_b.bass_notes[abs(chord)] == 6 
			  and abs(chord) in {idms_b.V6, idms_b.V65}):
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

			if (n_index + 1) in tonic_indices and new_pitch < 0:
				shift = 1
				new_pitch += 12
			else:
				shift = new_pitch - old_pitch
			self.pitch_amounts.append(new_pitch)
			old_pitch = new_pitch
			old_scale_degree = new_scale_degree
			Voice.bass_motion.append(shift)

		Voice.chord_symbols = self.create_chord_names()
		print(Voice.chord_symbols)

		for index, move in enumerate(Voice.bass_motion[:]):
			Voice.bass_motion[index] = self.move_direction(move)

	def convert_notes(self):
		"""Converts notes from reference scale pitches to pitch magnitudes"""
		# tie notes optionally if bass is stationary within a measure
		self.real_notes = [note + 48 + idms_b.tonics[Voice.tonic] 
			for note in self.pitch_amounts]
		print(self.chromatics, end="\n\n")
		if max(self.real_notes) > 62:
			self.real_notes = [note - 12 for note in self.real_notes]

		for nc_index, chrom in enumerate(Voice.chromatics):
			if chrom:
				self.note_index = nc_index
				nc_chord = abs(Voice.chord_path[nc_index])
				# make a method for this (create_chromatic_pitch)?
				# used in chord_degree_to_pitch
				if chrom == "2Dom":
					self.real_notes[nc_index] += self.convert_sec_dom(
						nc_chord, self.real_notes[nc_index])
				elif chrom == "2Dim":
					self.real_notes[nc_index] += self.convert_sec_dim(
						nc_chord, self.real_notes[nc_index])
				elif chrom in idms_b.modes.keys():
					self.real_notes[nc_index] += self.convert_mode(
						nc_chord, self.real_notes[nc_index])
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

		self.create_rhythm(0, 3)
		self.create_rhythm(4,7)

		print(self.final_rhythm)
		print(Voice.rhythm_styles)

		self.spread_notes(0, 3)
		self.spread_notes(4, 7)

		self.finalize_part()

		print(self.final_rhythm, len(self.final_rhythm))
		print(self.final_notes, len(self.final_notes))


	def create_rhythm(self, start, stop):
		# Don't use on secondary dominants or diminished preparation or resolution
		for m_index, chosen_measure in enumerate(
				Voice.measure_rhythms[start:stop]):
			for beat in chosen_measure:
				# if beat == 2 and chosen_measure:
				# 	self.final_rhythm[m_index + start].extend((1,"1"))
				# 	Voice.rhythm_styles[m_index + start].append("Waltz2")
				# elif beat == 3:
				# 	self.final_rhythm[m_index + start].extend((1,"1","1"))
				# 	Voice.rhythm_styles[m_index + start].append("Waltz3")
				# elif beat == 4:
				# 	self.final_rhythm[m_index + start].extend((1,"1",1,"1"))
				# 	Voice.rhythm_styles[m_index + start].append("Waltz4")
				if True:
					self.final_rhythm[m_index + start].append(beat)
					Voice.rhythm_styles[m_index + start].append(None)

	def spread_notes(self, start, stop):
		for m_index, chosen_measure in enumerate(
				Voice.rhythm_styles[start:stop]):
			for r_index, rhythm_style in enumerate(chosen_measure):
				main_note = self.measure_notes[m_index + start][r_index]
				if rhythm_style == "Waltz2":
					self.final_notes[m_index + start].extend(
						(main_note, "REST"))
				elif rhythm_style == "Waltz3":
					self.final_notes[m_index + start].extend(
						(main_note, "REST", "REST"))
				elif rhythm_style == "Waltz4":
					self.final_notes[m_index + start].extend(
						(main_note, "REST", main_note, "REST"))
				elif rhythm_style is None:
					self.final_notes[m_index + start].append(main_note)
