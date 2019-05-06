import random

from voice import Voice
import idioms as idms

class Bass(Voice):
	"""Creates a bass voice with an explicit chord progression"""

	def __init__(self, time_sig=(4,2), tonic="C", mode="ionian"):
		Voice.chord_path = [idms.I]
		Voice.tonic = tonic
		Voice.mode = mode
		Voice.chromatics.append(None)
		Voice.measure_length = time_sig[0]
		Voice.beat_division = time_sig[1]
		Voice.half_rest_ending = random.choice((True,False))
		Voice.consequent_rhythm_change = random.choice((True,False))
		self.chord_style1 = None
		self.chord_style2 = None
		self.chord_style3 = None
		self.chord_style4 = None
		self.pitch_amounts = [0]
		self.real_notes = []
		self.sheet_notes = []
		if mode == "ionian":
			Voice.accidental = idms.major_accidentals[tonic]
		elif mode == "aeolian":
			Voice.accidental = idms.minor_accidentals[tonic]
		self.voice = "bass"
		self.lily_notes = []
		self.old_chord = Voice.chord_path[-1]

	def create_part(self):
		"""Creates the bass portion of the song"""
		print(f"Song in {Voice.tonic} {Voice.mode} with {Voice.accidental}'s")
		print(f"Time signature: {Voice.measure_length} {Voice.beat_division}")
		self.create_chord_progression()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		return self.real_notes

	def create_chord_progression(self):
		"""Creates the chord progression"""
		self.create_antecedent()
		print("Change consequent?",Voice.consequent_rhythm_change)
		self.create_consequent()
		raise Exception("Stop")

	def create_antecedent(self):
		if Voice.measure_length == 2:
			self.tonic_rhythms = idms.bi1_rhythms_of_2
		elif Voice.measure_length == 3:
			self.tonic_rhythms = idms.bi1_rhythms_of_3
		elif Voice.measure_length == 4:
			self.tonic_rhythms = idms.bi1_rhythms_of_4
		self.chord_style1 = random.choice(tuple(self.tonic_rhythms.keys()))
		self.basic_idea1_rhythm = self.tonic_rhythms[self.chord_style1]
		Voice.note_values.extend(self.basic_idea1_rhythm)
		self.add_chords(self.chord_style1)
		print(Voice.note_values, len(Voice.note_values))
		print(self.chord_style1)
		Voice.idea1_length = len(Voice.note_values)
		if self.chord_style1[-1] != "TPS-I":
			print("Restart tonic")
			contrast_idea_start = "tonic"
			self.add_single_chord(idms.restart_tonic)
		else:
			print("Subdominant contrast")
			contrast_idea_start = "subdominant"
			self.add_single_chord(idms.tonic_to_subdom1)
		print(Voice.chord_path)

		contrast_idea1_rhythm = self.basic_idea1_rhythm
		# int represents note, str represents rest
		print("Half rest?", Voice.half_rest_ending)
		if Voice.half_rest_ending:
			if contrast_idea_start == "tonic":
				chord_style2 = random.choice(
					idms.ci1_from_tonic_with_rest[contrast_idea1_rhythm])
			elif contrast_idea_start == "subdominant":
				chord_style2 = random.choice(
					idms.ci1_from_subdom_with_rest[contrast_idea1_rhythm])
			contrast_idea1_rhythm = list(contrast_idea1_rhythm)
			if Voice.measure_length == 2 and contrast_idea1_rhythm[-1] == 2:
				contrast_idea1_rhythm[-1:] = [1,"1"]
			elif Voice.measure_length == 3 and contrast_idea1_rhythm[-2:] == [1,1]:
				contrast_idea1_rhythm[-2:] = ["2"]
			elif Voice.measure_length == 3 and contrast_idea1_rhythm[-1] == 2:
				contrast_idea1_rhythm[-1] = "2"
			elif Voice.measure_length == 4 and contrast_idea1_rhythm[-1] == 1:
				contrast_idea1_rhythm[-2:] = ["2"]
			elif contrast_idea1_rhythm[-1] == 1:
					contrast_idea1_rhythm[-1] = "1"
			elif contrast_idea1_rhythm[-1] == 2:
					contrast_idea1_rhythm[-1] = "2"
		else:
			if contrast_idea_start == "tonic":
				chord_style2 = random.choice(
					idms.ci1_from_tonic_no_rest[contrast_idea1_rhythm])
			elif contrast_idea_start == "subdominant":
				chord_style2 = random.choice(
					idms.ci1_from_subdom_no_rest[contrast_idea1_rhythm])
		Voice.idea2_length = len(contrast_idea1_rhythm)
		Voice.note_values.extend(contrast_idea1_rhythm)
		self.add_chords(chord_style2)
		print(Voice.note_values, len(Voice.note_values))
		print(Voice.chord_path)
		assert(len(Voice.chord_path) == len(Voice.note_values) or 
			Voice.half_rest_ending), "Chord error"
		# Voice.chord_path.append(-idms.I)
		self.add_single_chord(idms.restart_tonic)
		print(Voice.chord_path)

	def add_chords(self, chord_types):
		print("Chord types",chord_types, end=" | ")
		for chord_type in chord_types:
			chord_type = chord_type.replace("2","")
			print("Chord type:", chord_type)
			if chord_type == "PDA":
				chord_options = (idms.V, idms.V7)
			elif chord_type == "ITA":
				chord_options = (-idms.I6, -idms.III)
			elif chord_type == "VI":
				chord_options = (-idms.VI,)
			elif chord_type == "TAU":
				chord_options = (-idms.I,)
			else:
				chord_options = idms.chord_groups[chord_type][abs(self.old_chord)]
			if chord_type == "SAF":
				chord_options = list(chord_options)
				chord_options.append(I64)
			print("Chord options", chord_options) 
			chords_chosen = random.choice(chord_options)
			print(chords_chosen)
			if type(chords_chosen) == int:
				Voice.chord_path.append(chords_chosen)
			else:
				[Voice.chord_path.append(chord) for chord in chords_chosen]
			print("Chord path", Voice.chord_path)
			self.old_chord = abs(Voice.chord_path[-1])

	def add_single_chord(self, progression_type):
		chord_options = progression_type[abs(self.old_chord)]
		chord_choice = random.choice(chord_options)
		Voice.chord_path.append(chord_choice)
		self.old_chord = Voice.chord_path[-1]

	def create_consequent(self):
		self.chord_style3 = self.chord_style1
		self.basic_idea2_rhythm = self.basic_idea1_rhythm
		if Voice.consequent_rhythm_change:
			while self.basic_idea2_rhythm == self.basic_idea1_rhythm:
				print("Duplicate! Try again")
				self.chord_style3 = random.choice(tuple(self.tonic_rhythms.keys()))
				self.basic_idea2_rhythm = self.tonic_rhythms[self.chord_style3]
		Voice.note_values.extend(self.basic_idea2_rhythm)

		self.add_chords(self.chord_style3)

		if self.chord_style3[-1] != "TPS-I":
			print("Restart tonic")
			contrast_idea_start = "tonic"
			self.add_single_chord(idms.restart_tonic)
		else:
			print("Subdominant contrast")
			contrast_idea_start = "subdominant"
			self.add_single_chord(idms.tonic_to_subdom1)

		print(Voice.chord_path)

		contrast_idea2_rhythm = self.basic_idea1_rhythm

		if Voice.half_rest_ending:
			if contrast_idea_start == "tonic":
				chord_style4 = random.choice(
					idms.ci2_from_tonic_with_rest[contrast_idea2_rhythm])
			elif contrast_idea_start == "subdominant":
				chord_style4 = random.choice(
					idms.ci2_from_subdom_with_rest[contrast_idea2_rhythm])
		else:
			if contrast_idea_start == "tonic":
				chord_style4 = random.choice(
					idms.ci2_from_tonic_no_rest[contrast_idea2_rhythm])
			elif contrast_idea_start == "subdominant":
				chord_style4  = random.choice(
					idms.ci2_from_subdom_no_rest[contrast_idea2_rhythm])

		self.add_chords(chord_style4)
		Voice.note_values.extend(Voice.note_values[
			Voice.idea1_length:Voice.idea1_length + Voice.idea2_length])
		print(self.chord_style1, self.chord_style2)


	# def create_chords(self):
	# 	"""Creates the chord progression"""
	# 	# tonic_chords, tonic_note_values, old_chord, rhythm_sequence = self.create_tonic_zone()
	# 	rhythm_sequence = self.create_tonic_zone()
	# 	self.make_half_cadence(rhythm_sequence)
	# 	if rhythm_sequence == ("A","A","P") or \
	# 	rhythm_sequence == ("A","P","P") or rhythm_sequence == ("P","A","P"):
	# 		Voice.change_ending = True	
	# 	else:
	# 		Voice.change_ending = False
	# 	if not Voice.change_ending:
	# 		print("Standard ending", end=" | ")
	# 		Voice.chord_path.extend(
	# 			Voice.chord_path[:Voice.idea1_length + Voice.idea2_length])
	# 		Voice.note_values.extend(
	# 			Voice.note_values[:Voice.idea1_length + Voice.idea2_length])
	# 		self.old_chord = Voice.chord_path[-1]
	# 		Voice.chromatics.extend(
	# 			Voice.chromatics[0:Voice.idea1_length + Voice.idea2_length])
	# 	else:
	# 		print("Changing ending", end=" | ")
	# 		Voice.chord_path.extend(Voice.chord_path[:Voice.idea1_length + 1])
	# 		Voice.note_values.extend(Voice.note_values[:Voice.idea1_length + Voice.idea2_length])

	# 		self.old_chord = Voice.chord_path[-1]
	# 		chord_options = expand_tonic1[abs(self.old_chord)]
	# 		Voice.chromatics.extend(Voice.chromatics[0:Voice.idea1_length + 1])
	# 		self.create_passing_chords(chord_options)

	# 	self.make_authentic_cadence(rhythm_sequence)
	# 	# print(Voice.idea1_length, Voice.idea2_length, Voice.idea3_length, Voice.idea4_length)
	# 	Voice.rhythm_sequence = rhythm_sequence


	# def create_passing_chords(self, chord_options, nonchrom=False, amount=None):
	# 	"""Adds two chords to the current progression"""
	# 	chords_chosen = random.choice(chord_options)
	# 	[Voice.chord_path.append(chord) for chord in chords_chosen]
	# 	self.old_chord = Voice.chord_path[-1]
	# 	if nonchrom == True:
	# 		Voice.chromatics.extend(("2D",None))
	# 	elif amount == 2:
	# 		Voice.chromatics.extend((None, None, None))
	# 	else:
	# 		Voice.chromatics.extend((None, None))

	# def create_accent_chord(self,chord_options, nonchrom=False):
	# 	"""Adds a chord to the current progression"""
	# 	chord_choice = random.choice(chord_options)
	# 	Voice.chord_path.append(chord_choice)
	# 	self.old_chord = Voice.chord_path[-1]
	# 	if nonchrom == True:
	# 		Voice.chromatics.append("2D")
	# 	else:
	# 		Voice.chromatics.append(None)

	# def create_tonic_zone(self):
	# 	rhythm_sequence = random.choice(tuple(antecedent.keys()))
	# 	Voice.note_values.extend(antecedent[rhythm_sequence])
	# 	print(rhythm_sequence, end=" | ")

	# 	for rhythm in rhythm_sequence:
	# 		if "SP" in rhythm:
	# 			chord_options = expand_tonic3[abs(self.old_chord)]
	# 			self.create_passing_chords(chord_options)
	# 		elif "DP" in rhythm:
	# 			chord_options = expand_tonic2[abs(self.old_chord)]
	# 			self.create_passing_chords(chord_options, amount=2)
	# 		elif "P" in rhythm:
	# 			chord_options = expand_tonic1[abs(self.old_chord)]
	# 			self.create_passing_chords(chord_options)
	# 		elif "7A" in rhythm:
	# 			chord_options = tonic_to_subdom2[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options, True)
	# 		elif "A" in rhythm:
	# 			chord_options = accent_tonic[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options)
	# 		elif "VIV" in rhythm:
	# 			chord_options = (-VI, -IV6)
	# 			self.create_accent_chord(chord_options)

	# 	note_total = 0
	# 	for note_index, note_value in enumerate(Voice.note_values):
	# 		note_total += note_value
	# 		if note_total == 4:
	# 			stop_index = note_index
	# 			break

	# 	song_length = len(Voice.note_values)
	# 	Voice.idea1_length = len(Voice.note_values[:stop_index + 1])
	# 	Voice.idea2_length = song_length - Voice.idea1_length
	# 	return rhythm_sequence

	# def make_half_cadence(self, old_rhythm):
	# 	if (old_rhythm == ("P","A") or old_rhythm == ("SP", "VIV") or 
	# 	old_rhythm == ("P1","A")):
	# 		print("Preventing staleness", end=" | ")
	# 		rhythm_sequence = random.choice((("AS","PS","FD"), 
	# 			("AS","PS","PS","FD"), ("AS","PS","CD","FD")))
	# 	else:
	# 		rhythm_sequence = random.choice(tuple(consequent1.keys()))
	# 	print(rhythm_sequence, end=" | ")
	# 	Voice.note_values.extend(consequent1[rhythm_sequence])
	# 	Voice.idea3_length = len(Voice.note_values) - Voice.idea1_length - Voice.idea2_length
	# 	self.choose_chord(rhythm_sequence, False)

	# def choose_chord(self, rhythm_sequence, cadence):
	# 	counter = 0
	# 	for rhythm in rhythm_sequence:
	# 		counter += 1
	# 		if counter == 1:
	# 			chord_options = tonic_to_subdom[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options)
	# 		elif "AS" in rhythm:
	# 			chord_options = accent_subdom[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options)
	# 		elif rhythm == "PS":
	# 			chord_options = expand_subdom[abs(self.old_chord)]
	# 			self.create_passing_chords(chord_options)
	# 		elif rhythm == "CD":
	# 			chord_options = (I64,)
	# 			self.create_accent_chord(chord_options)
	# 		elif rhythm == "FD" and "CD" in rhythm_sequence:
	# 			# print("Optional cadence")
	# 			chord_options = accent_dom[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options)
	# 		elif rhythm == "FD" and "CD" not in rhythm_sequence:
	# 			chord_options = subdom_to_dom[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options)
	# 		elif rhythm == "AD":
	# 			# print("Mandatory cadence")
	# 			chord_options = (V, V7)
	# 			self.create_accent_chord(chord_options)
	# 		elif rhythm == "FT":
	# 			# chord_options = (I,)
	# 			chord_options = dom_to_tonic[abs(self.old_chord)]
	# 			self.create_accent_chord(chord_options)

	# def make_authentic_cadence(self, old_rhythm):
	# 	if (old_rhythm == ("P","A") or old_rhythm == ("SP", "VIV") or
	# 	old_rhythm == ("P1","A")):
	# 		print("Preventing staleness", end=" | ")
	# 		rhythm_sequence = random.choice((("AS","AS1","AD","FT"), 
	# 			("AS","CD","AD", "FT")))
	# 	else:
	# 		rhythm_sequence = random.choice(tuple(consequent2.keys()))
	# 	print(rhythm_sequence)
	# 	Voice.note_values.extend(consequent2[rhythm_sequence])
	# 	Voice.idea4_length = (len(Voice.note_values) - (Voice.idea1_length) * 2 - 
	# 		(Voice.idea2_length) * 2 - Voice.idea3_length)

	# 	self.choose_chord(rhythm_sequence, True)

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_scale_degree = 0
		old_pitch = 0
		old_position = 0
		for index, chord in enumerate(Voice.chord_path[1:]):
			new_scale_degree = int(bass_notes[abs(chord)])
			# if Voice.chromatics[index + 1]:
			# 	print("New scale degree", new_scale_degree)
			# 	print("Chord", chord)

			# Deciding between regular and inverted chord
			# (e.g., III to V6 going downward)
			# Created additional condition to have proper number in bass motion list
			if (chord > 0 and Voice.chord_path[index] < 0 and 
				old_scale_degree > new_scale_degree):
				old_position -= 7
				shift = new_scale_degree - old_scale_degree + 7
				new_position = old_position + shift
				new_pitch = modes[Voice.mode][new_position]

			elif chord > 0 or (chord < 0 and old_scale_degree > new_scale_degree):
				shift = new_scale_degree - old_scale_degree
				new_position = old_position + shift
				new_pitch = modes[Voice.mode][new_position]

			elif chord < 0 and new_scale_degree > old_scale_degree:
				old_position += 7
				shift = new_scale_degree - old_scale_degree - 7
				new_position = old_position + shift
				new_pitch = old_pitch + modes[Voice.mode][new_position] - \
					modes[Voice.mode][old_position]

			Voice.bass_motion.append(shift)
			pitch_change = new_pitch - old_pitch
			self.pitch_amounts.append(new_pitch)
			# if Voice.chromatics[index] == "2D":
			# 	print(self.pitch_amounts) 
			old_pitch = new_pitch
			old_position = new_scale_degree
			old_scale_degree = new_scale_degree

			# Raised seventh
			if 1 in chord_tones[abs(chord)] and 6 in chord_tones[abs(chord)] and \
			2 not in chord_tones[abs(chord)] and (new_pitch + 2) % 12 == 0:
				self.pitch_amounts[-1] += 1

		# Shift down an octave for IV6 and VI until tonic
		descents = (index for index, chord in enumerate(Voice.chord_path) 
			if abs(chord) in (IV6, VI))
		tonic_index = (Voice.idea1_length + Voice.idea2_length 
			+ Voice.idea3_length, len(Voice.chord_path ) - 1)
		
		for index in descents:
			index += 1
			while index not in tonic_index:
				self.pitch_amounts[index] -= 12
				index += 1

		for index, move in enumerate(Voice.bass_motion):
			Voice.bass_motion[index] = self.move_direction(move)

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.pitch_amounts]

		#alter pitches and bass motion based on secondary dominants
		for nc_index in range(len(Voice.chromatics)):
			if Voice.chromatics[nc_index] == "2D":
				self.real_notes[nc_index] += self.make_sec_dom(
					Voice.chord_path[nc_index], self.real_notes[nc_index])
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
		# print(Voice.chromatics)

		Voice.bass_pitches = self.real_notes