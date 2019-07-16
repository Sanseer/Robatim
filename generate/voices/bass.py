import random

from generate.voices.voice import Voice
from generate.idioms import basics as idms_b

import pysnooper

class Bass(Voice):
	"""Creates a bass voice with an explicit chord progression. 
	Initializes settings for the entire song."""

	def __init__(self):
		Voice.chord_path = [(idms_b.I,)]
		self.chord_options = Voice.chord_path[:]

		Voice.mode = random.choice(("ionian", "aeolian"))
		Voice.chromatics = [None]
		time_sig = random.choice(idms_b.time_sigs)
		Voice.measure_length = time_sig[0]
		Voice.beat_division = time_sig[1]
		Voice.half_rest_ending = random.choice((True, False))
		Voice.consequent_rhythm_change = random.choice((True, False))

		if Voice.mode == "ionian":
			import generate.idioms.major
			Voice.idms_mode = generate.idioms.major
		elif Voice.mode == "aeolian":
			import generate.idioms.minor
			Voice.idms_mode = generate.idioms.minor
		Voice.tonic = random.choice(self.idms_mode.key_sigs)

		self.note_index = 0
		self.chord_descent = False
		self.chord_style1 = None
		self.chord_style2 = None
		self.chord_style3 = None
		self.chord_style4 = None

		self.basic_idea1_rhythm = None
		self.basic_idea2_rhythm = None
		self.contrast_idea1_rhythm = None
		self.contrast_idea2_rhythm = None

		self.measure_notes = []
		self.pitch_amounts = [0]
		self.real_notes = []
		self.sheet_notes = []
		self.lily_notes = []

		Voice.rhythm_styles = [ [] for _ in range(8)]
		self.final_rhythm = [ [] for _ in range(8)]
		self.final_notes = [ [] for _ in range(8)]

		self.volume = 100

	@property
	def old_chord(self):
		return abs(Voice.chord_path[-1][-1])

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
			Voice.idea4_length -= 1

	def create_antecedent(self):
		self.add_basic_idea1()
		self.add_transition_idea1()
		self.add_chord_sequence(self.chord_style2)
		Voice.note_values.append(self.contrast_idea1_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))

	def add_basic_idea1(self):
		if Voice.measure_length == 3:
			antecedent_rhythms = idms_b.bi1_rhythms_of_3
		elif Voice.measure_length == 4:
			antecedent_rhythms = idms_b.bi1_rhythms_of_4

		self.chord_style1 = random.choice(tuple(antecedent_rhythms.keys()))
		self.add_chord_sequence(self.chord_style1)
		self.basic_idea1_rhythm = antecedent_rhythms[self.chord_style1]
		Voice.note_values.append(self.basic_idea1_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))

	def add_transition_idea1(self):
		self.declare_transition(self.chord_style1)
		if random.choice((True,False)):
			self.contrast_idea1_rhythm = self.basic_idea1_rhythm
		else:
			self.contrast_idea1_rhythm = random.choice(
				idms_b.ci1_response_rhythms[self.basic_idea1_rhythm])
		if self.contrast_idea1_rhythm in {(2,2,2,2), (2,1,2,1)}:
			Voice.half_rest_ending = True

		print("Half rest?", Voice.half_rest_ending)
		if Voice.half_rest_ending:
			if self.contrast_idea_start == "tonic":
				# self.chord_style2 = random.choice(
				# 	idms_b.ci1_tonic_with_rest[self.contrast_idea1_rhythm])
				style_options = idms_b.ci1_tonic_with_rest[self.contrast_idea1_rhythm]
			elif self.contrast_idea_start == "subdominant":
				# self.chord_style2 = random.choice(
				# 	idms_b.ci1_subdom_with_rest[self.contrast_idea1_rhythm])
				style_options = idms_b.ci1_subdom_with_rest[self.contrast_idea1_rhythm]
		else:
			if self.contrast_idea_start == "tonic":
				# self.chord_style2 = random.choice(
				# 	idms_b.ci1_tonic_no_rest[self.contrast_idea1_rhythm])
				style_options = idms_b.ci1_tonic_no_rest[self.contrast_idea1_rhythm]
			elif self.contrast_idea_start == "subdominant":
				# self.chord_style2 = random.choice(
				# 	idms_b.ci1_subdom_no_rest[self.contrast_idea1_rhythm])
				style_options = idms_b.ci1_subdom_no_rest[self.contrast_idea1_rhythm]

		self.chord_style2 = self.pick_chord_style(style_options)
		self.add_transition_chord(self.chord_style2)

	def pick_chord_style(self, style_options):
		style_options = list(style_options)
		if ("IAC2", "IAC1") in style_options and self.chord_descent:
			style_options.remove(("IAC2", "IAC1"))
		return random.choice(style_options) 

	def replace_bad_chords(self):
		self.chord_options[-1].remove(Voice.chord_path[-1])
		Voice.chromatics = Voice.chromatics[:0 - len(Voice.chord_path[-1])]
		Voice.chord_path.pop()

		new_chords_chosen = random.choice(self.chord_options[-1])
		if type(new_chords_chosen) == int:
			self.add_chromatic(new_chords_chosen)
			new_chords_chosen = (new_chords_chosen,)
		elif type(new_chords_chosen) == tuple:
			[self.add_chromatic(chord) for chord in new_chords_chosen]
		Voice.chord_path.append(new_chords_chosen)
		self.check_descent()

	def are_valid_chords(self, chords_chosen):
		if (self.old_chord in {idms_b.II, idms_b.II6, idms_b.IV} and
		   chords_chosen[0] in {-idms_b.V6, -idms_b.V65} and self.chord_descent):
			print("Double descent")
			return False
		elif chords_chosen[0] in {-idms_b.I, -idms_b.I_MAJOR} and self.chord_descent:
			print("Return to tonic double descent")
			return False
		elif chords_chosen[0] in {idms_b.I, idms_b.I_MAJOR} and not self.chord_descent:
			print("Return to tonic double ascent")
			return False
		return True

	def add_chord_sequence(self, chord_types):
		print("Chord types:", chord_types)
		for chord_type in chord_types:
			possible_chords = None
			chords_chosen = None
			print("Chord type:", chord_type)
			print("Old chord:", self.old_chord)
			chord_seq = chord_type.replace("*","")
			while possible_chords is None:
				try:
					possible_chords = self.idms_mode.chord_sequences[chord_seq][self.old_chord]
				except KeyError:
					print("Before")
					self.display_error()
					self.replace_bad_chords()
					print("After")
					self.display_error()
			self.chord_options.append(list(possible_chords))
			print("Full chord options:", self.chord_options)
			while chords_chosen is None:
				chords_chosen = random.choice(self.chord_options[-1])
				print("Chords chosen:", chords_chosen)
				if type(chords_chosen) == int:
					chord_pack = (chords_chosen,)
				elif type(chords_chosen) == tuple:
					chord_pack = chords_chosen
				if not self.are_valid_chords(chord_pack):
					self.display_error()
					self.chord_options[-1].remove(chords_chosen)
					chords_chosen = None
					self.display_error()
			Voice.chord_path.append(chord_pack)
			print("New chord sequence:", Voice.chord_path)
			self.check_descent()
			[self.add_chromatic(chord) for chord in chord_pack]

	def add_single_chord(self, progression_type):
		"""Add single chord to progression"""
		possible_chords = None
		chord_choice = None
		while possible_chords is None:
			try:
				possible_chords = progression_type[abs(self.old_chord)]
			except KeyError:
				print("Before")
				self.display_error()
				self.replace_bad_chords()
				print("After")
				self.display_error()
		self.chord_options.append(list(possible_chords))
		print("Full chord options:", self.chord_options)
		while chord_choice is None:
			chord_choice = random.choice(self.chord_options[-1])
			if not self.are_valid_chords((chord_choice,)):
				self.display_error()
				self.chord_options[-1].remove(chord_choice)
				chord_choice = None
				self.display_error()
		self.add_chromatic(chord_choice)
		Voice.chord_path.append((chord_choice,))
		print("New chord sequence:", Voice.chord_path)
		self.check_descent()

	def display_error(self):
		print("="*40)
		print(Voice.chord_path)
		print(Voice.chromatics)
		print(self.chord_options)

	def check_descent(self):
		print("Checking descent:", self.chord_descent)
		if (Voice.chord_path[-1][0] in {-idms_b.VI, -idms_b.IV6, -idms_b.IV6_MAJOR} and 
		  abs(Voice.chord_path[-2][-1]) == idms_b.I):
			self.chord_descent = True
		elif self.old_chord == idms_b.I:
			self.chord_descent = False
		print("New descent:", self.chord_descent)

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
		  and self.old_chord not in {idms_b.VI, idms_b.IV6, idms_b.IV6_MAJOR}):
			print("Restart tonic. Adding first CI note")
			self.contrast_idea_start = "tonic"
		elif chord_types[-1] == "TA" and not self.basic_idea2_rhythm:
			print("Subdominant contrast. Adding first CI note")
			self.contrast_idea_start = "subdominant"
		elif chord_types[-1] in {"TA","M+SA2+M", "M-SA2+M"} and self.basic_idea2_rhythm:
			print("Subdominant contrast. Adding first CI note")
			self.contrast_idea_start = "subdominant"
		elif chord_types[-1] in {"M+SA1+M", "M-SA1+M"} and self.basic_idea2_rhythm:
			self.contrast_idea_start = "dominant"
			print("Dominant contrast. Adding first CI note")

	def add_transition_chord(self, next_chord_style):
		"""Adds transition chord for the next 2 measures"""
		print(next_chord_style)
		if self.contrast_idea_start == "tonic":
			self.add_single_chord(idms_b.restart_tonic)
		elif self.contrast_idea_start == "subdominant":
			if (next_chord_style[0] in {"M+SA1-M","M+SA1+M"} and 
			  Voice.note_values[-1][-1] in {3,4}):
				print("strong_to_subdom2_strong")
				self.add_single_chord(Voice.idms_mode.strong_to_subdom2_strong)
			elif (next_chord_style[0] in {"HC1","HC2","IAC2","PAC2"} and
			  Voice.note_values[-1][-1] in {3,4}):
				print("strong_to_subdom1_strong")
				self.add_single_chord(Voice.idms_mode.strong_to_subdom1_strong)
			elif next_chord_style[0] in {"M+SA1-M","M+SA1+M"}:
				print("weak_to_subdom2_strong")
				self.add_single_chord(Voice.idms_mode.weak_to_subdom2_strong)
			elif next_chord_style[0] in {"HC1","HC2","IAC2","PAC2"}:
				print("weak_to_subdom1_strong")
				self.add_single_chord(Voice.idms_mode.weak_to_subdom1_strong)
			else:
				raise ValueError("Invalid chords")
		elif self.contrast_idea_start == "dominant":
			print("restart_dom")
			self.add_single_chord(idms_b.restart_dom)

	def add_rest_rhythm(self, rhythm):
		"""Modifies end of rhythm to include rest"""
		# rest can be 2, "2" or 3, "1" i simple time
		if rhythm[-1] == 2:
			rhythm[-1] = "2"
		elif rhythm[-1] == 1:
			rhythm[-1] = "1"
		elif rhythm[-1] == 3:
			rhythm[-1:] = [2,"1"]
		elif rhythm[-1] == 4:
			rhythm[-1:] = [2,"2"]

	def create_consequent(self):
		self.add_single_chord(idms_b.restart_tonic)
		self.add_basic_idea2()
		self.add_transition_idea2()
		self.add_chord_sequence(self.chord_style4)
		Voice.note_values.append(self.contrast_idea2_rhythm)

		print("Rhythm:",Voice.note_values, len(Voice.note_values))
		print(Voice.chord_path)

		if Voice.half_rest_ending:
			Voice.note_values[1] = list(Voice.note_values[1])
			Voice.note_values[3] = list(Voice.note_values[3])
			self.add_rest_rhythm(Voice.note_values[1])
			self.add_rest_rhythm(Voice.note_values[3])

		print("Rhythm:", Voice.note_values, len(Voice.note_values))
		Voice.idea1_length = len(Voice.note_values[0])
		Voice.idea2_length = len(Voice.note_values[1])
		Voice.idea3_length = len(Voice.note_values[2])
		Voice.idea4_length = len(Voice.note_values[3])

		Voice.note_values = self.flatten_sequence(Voice.note_values)
		Voice.chord_path = self.flatten_sequence(Voice.chord_path)

	def add_basic_idea2(self):
		if Voice.measure_length == 3:
			consequent_rhythms = idms_b.ci1_rhythms_of_3
		elif Voice.measure_length == 4:
			consequent_rhythms = idms_b.ci1_rhythms_of_4
		self.chord_style3 = random.choice(tuple(consequent_rhythms.keys()))
		self.add_chord_sequence(self.chord_style3)

		self.basic_idea2_rhythm = consequent_rhythms[self.chord_style3]
		Voice.note_values.append(self.basic_idea2_rhythm)
		print("Rhythm:",Voice.note_values, len(Voice.note_values))

	def add_transition_idea2(self):
		self.declare_transition(self.chord_style3)
		if self.contrast_idea_start == "dominant":
			if Voice.measure_length == 4:
				self.contrast_idea2_rhythm = (4,4)
			elif Voice.measure_length == 3:
				self.contrast_idea2_rhythm = (3,3)
		else:
			self.contrast_idea2_rhythm = random.choice(
				idms_b.ci2_response_rhythms[self.basic_idea2_rhythm])

		print("Half rest?", Voice.half_rest_ending)
		if Voice.half_rest_ending:
			if self.contrast_idea_start == "tonic":
				# self.chord_style4 = random.choice(
				# 	idms_b.ci2_tonic_with_rest[self.contrast_idea2_rhythm])
				style_options = idms_b.ci2_tonic_with_rest[self.contrast_idea2_rhythm]
			elif self.contrast_idea_start == "subdominant":
				# self.chord_style4 = random.choice(
				# 	idms_b.ci2_subdom_with_rest[self.contrast_idea2_rhythm])
				style_options = idms_b.ci2_subdom_with_rest[self.contrast_idea2_rhythm]
			elif self.contrast_idea_start == "dominant":
				self.chord_style4 = ("PAC1",)
		else:
			if self.contrast_idea_start == "tonic":
				# self.chord_style4 = random.choice(
				# 	idms_b.ci2_tonic_no_rest[self.contrast_idea2_rhythm])
				style_options = idms_b.ci2_tonic_no_rest[self.contrast_idea2_rhythm]
			elif self.contrast_idea_start == "subdominant":
				# self.chord_style4  = random.choice(
				# 	idms_b.ci2_subdom_no_rest[self.contrast_idea2_rhythm])
				style_options = idms_b.ci2_subdom_no_rest[self.contrast_idea2_rhythm]
			elif self.contrast_idea_start == "dominant":
				self.chord_style4 = ("PAC1",)

		if self.chord_style4 is None:
			self.chord_style4 = self.pick_chord_style(style_options)
		self.add_transition_chord(self.chord_style4)

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

			# if (n_index + 1) in tonic_indices and new_pitch < 0:
			# 	shift = 1
			# 	new_pitch += 12
			# else:
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
			Voice.measure_rhythms[7][-1] = str(Voice.measure_rhythms[7][-1])
		self.note_index = 0

	def create_groove(self):
		self.group_rhythm()
		self.group_notes()
		self.finalize_unflavored_part()

		# self.create_rhythm(0, 3)
		# self.create_rhythm(4,7)

		# print(self.final_rhythm)
		# print(Voice.rhythm_styles)

		# self.spread_notes(0, 3)
		# self.spread_notes(4, 7)

		# self.finalize_part()




	# def create_rhythm(self, start, stop):
	# 	# Don't use on secondary dominants or diminished preparation or resolution
	# 	for m_index, chosen_measure in enumerate(
	# 			Voice.measure_rhythms[start:stop]):
	# 		for beat in chosen_measure:
	# 			# if beat == 2 and chosen_measure:
	# 			# 	self.final_rhythm[m_index + start].extend((1,"1"))
	# 			# 	Voice.rhythm_styles[m_index + start].append("Waltz2")
	# 			# elif beat == 3:
	# 			# 	self.final_rhythm[m_index + start].extend((1,"1","1"))
	# 			# 	Voice.rhythm_styles[m_index + start].append("Waltz3")
	# 			# elif beat == 4:
	# 			# 	self.final_rhythm[m_index + start].extend((1,"1",1,"1"))
	# 			# 	Voice.rhythm_styles[m_index + start].append("Waltz4")
	# 			if True:
	# 				self.final_rhythm[m_index + start].append(beat)
	# 				Voice.rhythm_styles[m_index + start].append(None)

	# def spread_notes(self, start, stop):
	# 	for m_index, chosen_measure in enumerate(
	# 			Voice.rhythm_styles[start:stop]):
	# 		for r_index, rhythm_style in enumerate(chosen_measure):
	# 			main_note = self.measure_notes[m_index + start][r_index]
	# 			if rhythm_style == "Waltz2":
	# 				self.final_notes[m_index + start].extend(
	# 					(main_note, "REST"))
	# 			elif rhythm_style == "Waltz3":
	# 				self.final_notes[m_index + start].extend(
	# 					(main_note, "REST", "REST"))
	# 			elif rhythm_style == "Waltz4":
	# 				self.final_notes[m_index + start].extend(
	# 					(main_note, "REST", main_note, "REST"))
	# 			elif rhythm_style is None:
	# 				self.final_notes[m_index + start].append(main_note)
