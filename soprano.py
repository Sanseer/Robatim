import random

from voice import *
from idioms import *

class Soprano(Voice):

	def __init__(self):
		self.note_index = 0
		self.pitch_amounts = []
		self.possible_pitches = []
		self.intervals = []
		self.real_notes = []
		self.sheet_notes = []
		self.lily_notes = []
		self.voice = "soprano"
		self.motion_with_bass = []

	def create_part(self):
		self.create_antecedent()
		self.add_notes()
		self.create_consequent()
		self.add_notes()
		# print(Voice.soprano_motion, len(Voice.soprano_motion))
		print(self.intervals, len(self.intervals))
		print(self.motion_with_bass, len(self.motion_with_bass))
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		return self.real_notes

	def create_antecedent(self):
		new_scale_degree = random.choice((0,4))
		first_pitch = self.calculate_pitch(0, new_scale_degree, 1)
		self.pitch_amounts = [first_pitch]
		# print(Voice.idea1_length, Voice.idea2_length, Voice.idea3_length)
		self.pitch_amounts.extend(("Blank",) * (Voice.idea1_length - 1 + Voice.idea2_length + Voice.idea3_length))
		self.calculate_interval(Voice.main_pitches, first_pitch,self.intervals)

		self.possible_pitches = [self.pitch_amounts[0]]
		self.possible_pitches.extend(("Blank",) * len(Voice.chord_path[1:]))
		self.populate_notes()

	def create_consequent(self):
		print("Creating consequent")
		"""Duplicate some intervals and motion from antecedent. 
		Manually enter first note to figure out type of motion from 
		previous note"""
		self.validate_note(self.pitch_amounts[0])
		# print(self.intervals)
		# # print(f"Adding intervals: {self.intervals[1:Voice.idea1_length + Voice.idea2_length]}")
		# # print(f"Adding motions: {Voice.soprano_motion[1:Voice.idea1_length + Voice.idea2_length]}")
		# print(self.intervals)
		if Voice.rhythm_sequence != ("A","A","P") and \
		Voice.rhythm_sequence != ("A","P","P") and Voice.rhythm_sequence != ("P","A","P"):	
			self.pitch_amounts.extend(self.pitch_amounts[:Voice.idea1_length + Voice.idea2_length])
			self.intervals.extend(self.intervals[1:Voice.idea1_length + Voice.idea2_length])
			Voice.soprano_motion.extend(Voice.soprano_motion[:Voice.idea1_length + Voice.idea2_length - 1])
			self.motion_with_bass.extend(self.motion_with_bass[:Voice.idea1_length +  Voice.idea2_length- 1])
		else:
			self.pitch_amounts.extend(self.pitch_amounts[:Voice.idea1_length])
			self.pitch_amounts.extend(("Blank",) * Voice.idea2_length)
			self.intervals.extend(self.intervals[1:Voice.idea1_length])
			Voice.soprano_motion.extend(Voice.soprano_motion[:Voice.idea1_length - 1])
			self.motion_with_bass.extend(self.motion_with_bass[:Voice.idea1_length - 1])
		# print("Repeating portions")
		# print(self.intervals)
		# print(Voice.soprano_motion)
		self.pitch_amounts.extend(("Blank",) * Voice.idea4_length)
		self.populate_notes()

	def add_notes(self):
		# Don't forget to apply antecedent consequent format
		"""This melody creation is naturally recursive but I modeled it 
		with iteration. You try notes until you get a good note. 
		If none of your note choices at the current position are good, 
		then your previous note is bad and should be removed. """

		self.note_index = 0
		while self.pitch_amounts[self.note_index] != "Blank": 
			self.note_index += 1

		last_pitch = self.pitch_amounts[self.note_index - 1]
		attempts = 0
		while "Blank" in self.pitch_amounts:
			attempts += 1
			if self.possible_pitches[self.note_index]:
				pitch_choice = self.choose_pitch()
				voice_lead = self.validate_note(pitch_choice)
				if (self.note_index == Voice.idea1_length + 
					Voice.idea2_length + Voice. idea3_length - 1):
					print("Ending antecedent")
				if voice_lead:
					self.pitch_amounts[self.note_index] = pitch_choice
					last_pitch = pitch_choice
					self.note_index += 1
					# print(f"\nGood choice! Move on. New index: {self.note_index}")
					if self.note_index == len(self.pitch_amounts):
						# print(f"You win: {self.pitch_amounts}")
						break
				else:
					# print(f"Bad choice. Try another {self.note_index}", end="\n")
					self.possible_pitches[self.note_index].remove(pitch_choice)
					self.intervals.pop()
					Voice.soprano_motion.pop()
					self.motion_with_bass.pop()
			else:
				# print("All roads lead to hell!")
				self.possible_pitches[self.note_index] = "Blank" 
				self.populate_notes()
				self.intervals.pop()
				Voice.soprano_motion.pop()
				self.motion_with_bass.pop()
				self.note_index -= 1
				if self.note_index == 0:
					print("You fail")
				if last_pitch in self.possible_pitches[self.note_index]:
					self.possible_pitches[self.note_index].remove(last_pitch)
		# print(f"That took {attempts} tries.")

	def calculate_pitch(self, old_scale_degree, new_scale_degree, direction):
		old_position = old_scale_degree
		old_pitch = modes[Voice.mode][old_scale_degree]

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

		return new_pitch

	def populate_notes(self):
		for index, value in enumerate(self.possible_pitches):
			if value == "Blank":
				current_chord = abs(Voice.chord_path[index])
				chord_root = (current_chord // 1000) - 1
				chord_notes = list(chord_tones[current_chord])
				chord_notes.remove(chord_root)
				self.possible_pitches[index] = self.populate_note(chord_root, chord_notes)
		self.possible_pitches[-1] = [-12,0,12]

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

	def choose_pitch(self):
		"""Sort avaialable pitches based on desirability 
		(closeness to last pitch). """
		number = random.choice(range(10))
		last_pitch = self.pitch_amounts[self.note_index - 1]
		# if last_pitch in self.possible_pitches[self.note_index] and number > 5:
		# 	self.possible_pitches[self.note_index].remove(last_pitch)
		choices = self.possible_pitches[self.note_index][:]
		pitch_leaps = []

		for new_pitch in choices:
			pitch_leaps.append(abs(last_pitch - new_pitch))
		sorted_choices = [x for _,x in sorted(zip(pitch_leaps, choices))]

		return sorted_choices[0]

	def validate_note(self, pitch_choice):
		"""Check if the vocal range exceeds a tenth (16 semitones in major)"""
		# selected_pitches = [ pitch for pitch in self.pitch_amounts 
		# if type(pitch) == int ]
		# highest_pitch = max(selected_pitches)
		# lowest_pitch = min(selected_pitches)
		# vocal_range = highest_pitch - lowest_pitch
		# print(vocal_range, end=" | ")
		# if self.note_index == len(self.possible_pitches) - 1:
		# 	print("End strongly", pitch_choice, self.possible_pitches)

		if pitch_choice < self.pitch_amounts[self.note_index - 1]:
			Voice.soprano_motion.append(-1)
		elif pitch_choice > self.pitch_amounts[self.note_index - 1]:
			Voice.soprano_motion.append(1)
		elif pitch_choice == self.pitch_amounts[self.note_index - 1]:
			Voice.soprano_motion.append(0)

		self.calculate_interval(Voice.main_pitches, pitch_choice, self.intervals)
		self.calculate_motion(Voice.bass_motion, Voice.soprano_motion, self.motion_with_bass)

		print(f"Considering note #{self.note_index + 1}")

		return self.is_counterpoint(pitch_choice)


	def is_counterpoint(self, pitch_choice):

		if "P" in self.intervals[-1] and "P" in self.intervals[-2]:
			print("Double perfects. Delete!")
			print(self.intervals)
			return False  
		elif (self.note_index > 3 and self.intervals[-1] == self.intervals[-2] 
		and self.intervals[-2] == self.intervals[-3] and 
		self.intervals[-3] == self.intervals[-4]):
			print("Quadruple identical imperfects. Delete")
			print(self.intervals)
			return False
		elif (self.note_index > 2 and 
		self.motion_with_bass[-1] == "Parallel" and 
		self.motion_with_bass[-2] == "Parallel" and 
		self.motion_with_bass[-3] == "Parallel"):
			print("Three consecutive parallels. Delete!")  
			print(self.intervals)
			print(self.motion_with_bass)
			return False
		elif (((self.pitch_amounts[self.note_index - 1] + 1) % 12 == 0) and 
		pitch_choice % 12 != 0):
			print("Leading tone must progress to tonic")
			return False
		elif self.intervals[-2] == "d5" and "3" not in self.intervals[-1]:
			print("Diminished 5th must resolve to a third. Delete!")
			print(self.intervals)
			return False
		elif (self.intervals[-2] == "A4") and ("6" not in self.intervals[-1]):
			print("Augmented 4th must resolve to a sixth. Delete!")
			print(self.intervals)
			return False
		elif ((self.note_index != len(self.possible_pitches) - 1) and 
		self.intervals[-1] == "P8"):
			print("Avoiding premature unison")
			return False
		elif (self.note_index > 3 and self.motion_with_bass[-1] != "Contrary"
		and self.motion_with_bass[-1] == self.motion_with_bass[-2] and 
		self.motion_with_bass[-2] == self.motion_with_bass[-3]):
			print(f"Triple {self.motion_with_bass[-1]}. Delete!")
			print(self.motion_with_bass)
			return False
		elif self.motion_with_bass[-1] == "No motion":
			print("No movement. Delete!")
			return False
		elif ((self.motion_with_bass[-1] == "Parallel" or
		self.motion_with_bass[-1] == "Similar") and self.intervals[-1] == "P5"):
			print(f"{self.motion_with_bass[-1]} 5th or hidden 5th")
			return False 
		elif (self.note_index > 1 and Voice.soprano_motion[-1] == 0 and 
		Voice.soprano_motion[-2] == 0):
			print("Triple repeat. Delete!")
			print(Voice.soprano_motion)
			return False
		elif ((self.note_index == len(self.possible_pitches) - 1) and 
			self.motion_with_bass[-1] != "Contrary"):
			print("Must end strong with contrary motion!")
			return False

		# Leaps higher than a 4th
		# Protect transition to consequent
		# Triple oblique infinite loop?
		return True

	def convert_notes(self):
		"""Converts notes from relative pitch magnitudes degrees to 
		absolute pitch magnitudes"""
		# self.fixed_pitches = []
		# for index, pitch in enumerate(self.pitch_amounts):
		# 	if -12 < pitch < 0:
		# 		self.fixed_pitches.append(pitch + 12)
		# 	elif 12 < pitch < 24:
		# 		self.fixed_pitches.append(pitch - 12)
		# 	elif 0 <= pitch <= 12:
		# 		self.fixed_pitches.append(pitch)
		# 	else:
		# 		self.fixed_pitches.append(f"What? {pitch}")
		# print(self.fixed_pitches)  
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.pitch_amounts]

		vocal_range = True
		for real_note in self.real_notes:
			if real_note < 59:
				vocal_range = False
				print("Perform octave transposition")
				# print(self.real_notes)
				break

		if not vocal_range:
			for index, real_note in enumerate(self.real_notes):
				self.real_notes[index] += 12
			print("Vocal range fixed")
			# print(self.real_notes)



		# for index in range(len(self.real_notes)):
		# 	# Raise seventh only for ascending
		# 	if self.mode == "aeolian" and self.fixed_pitches[index] == 11:
		# 		print("Actual RAISED SEVENTH!")
		# 	if Voice.tonic == "B":
		# 		self.real_notes[index] -= 12
