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
		print(f"\n{self.intervals} {len(self.intervals)}")
		# print(self.motion_with_bass, len(self.motion_with_bass))
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		return self.real_notes

	def create_antecedent(self):
		new_scale_degree = random.choice((0,4))
		first_pitch = self.calculate_pitch(0, new_scale_degree, 1)
		self.pitch_amounts = [first_pitch]
		self.pitch_amounts.extend(("Blank",) * (Voice.idea1_length - 1 + Voice.idea2_length + Voice.idea3_length))
		self.calculate_interval(Voice.bass_pitches, first_pitch, self.intervals)

		self.possible_pitches = [self.pitch_amounts[0]]
		self.possible_pitches.extend(("Blank",) * len(Voice.chord_path[1:]))
		self.populate_notes()

	def create_consequent(self):
		print("Creating consequent")
		"""Duplicate some intervals and motion from antecedent. 
		Manually enter first note to figure out type of motion from 
		previous note"""
		self.validate_note(self.pitch_amounts[0])

		# if Voice.rhythm_sequence != ("A","A","P") and \
		# Voice.rhythm_sequence != ("A","P","P") and Voice.rhythm_sequence != ("P","A","P"):	
		if not Voice.change_ending:
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
			assert(attempts < 2000), f"You ran out of tries! {self.possible_pitches}"
			if self.possible_pitches[self.note_index]:
				pitch_choice = self.choose_pitch()
				voice_lead = self.validate_note(pitch_choice)
				if voice_lead:
					self.pitch_amounts[self.note_index] = pitch_choice
					last_pitch = pitch_choice
					print(f"Good", end=" ~ ")
					self.note_index += 1
					# print(f"\nGood choice! Move on. New index: {self.note_index}")
					# if self.note_index == len(self.pitch_amounts):
					# 	# print(f"You win: {self.pitch_amounts}")
					# 	break
				else:
					print(f"Bad", end=" ~ ")
					self.possible_pitches[self.note_index].remove(pitch_choice)
					self.erase_last_note()
			else:
				# print("All roads lead to hell!")
				self.possible_pitches[self.note_index] = "Blank" 
				self.populate_notes()
				assert(self.note_index != 0), "You fail"
				self.erase_last_note()

				self.note_index -= 1
				print(f"Go back to index {self.note_index}")
				self.possible_pitches[self.note_index].remove(last_pitch)
				self.pitch_amounts[self.note_index] = "Blank"
				last_pitch = self.pitch_amounts[self.note_index - 1]
		print(f"That took {attempts} tries.")

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

		if Voice.chromatics[self.note_index] == "2D":
			new_scale_degree %= 7
			# print(f"Implemeting soprano: {new_pitch} to", end=" | ")
			chord = abs(Voice.chord_path[self.note_index])
			root_degree = chord_tones[chord][0]
			# print("New scale degree", new_scale_degree, end= " | ")
			alt_index = chord_tones[chord].index(new_scale_degree)
			if Voice.mode == "ionian":
				new_pitch += sec_dom_in_major[root_degree][alt_index] 
			elif Voice.mode == "aeolian":
				new_pitch += sec_dom_in_minor[root_degree][alt_index]
			# print(new_pitch)

		return new_pitch

	def populate_notes(self):
		temp_index = self.note_index
		for index, value in enumerate(self.possible_pitches):
			if value == "Blank":
				self.note_index = index
				current_chord = abs(Voice.chord_path[index])
				chord_root = chord_tones[current_chord][0]
				chord_notes = list(chord_tones[current_chord])
				chord_notes.remove(chord_root)
				self.possible_pitches[index] = self.populate_note(chord_root, chord_notes)
		self.possible_pitches[-1] = [-12,0,12]
		self.note_index = temp_index

	def populate_note(self, chord_root, chord_notes):
		pitches = [self.calculate_pitch(0, chord_root, 1)]
		for note in chord_notes:
			if Voice.mode == "aeolian" and note == 6 and 1 in chord_notes and 2 not in chord_notes:
				pitches.append(self.calculate_pitch(chord_root, note, 1) + 1)
				pitches.append(self.calculate_pitch(chord_root, note, 1) + 13)
				pitches.append(self.calculate_pitch(chord_root, note, -1) + 1)
				pitches.append(self.calculate_pitch(chord_root, note, -1) - 11)
			else:
				pitches.append(self.calculate_pitch(chord_root, note, 1))
				pitches.append(self.calculate_pitch(chord_root, note, 1) + 12)
				pitches.append(self.calculate_pitch(chord_root, note, -1))
				pitches.append(self.calculate_pitch(chord_root, note, -1) - 12)
		pitches.append(self.calculate_pitch(0, chord_root, 1) + 12)
		pitches.append(self.calculate_pitch(0, chord_root, 1) - 12)

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
		# sorting one list using another
		sorted_choices = [x for _,x in sorted(zip(pitch_leaps, choices))]

		return sorted_choices[0]

	def validate_note(self, pitch_choice):
		"""Checks if note choice is valid"""

		if pitch_choice < self.pitch_amounts[self.note_index - 1]:
			Voice.soprano_motion.append(-1)
		elif pitch_choice > self.pitch_amounts[self.note_index - 1]:
			Voice.soprano_motion.append(1)
		elif pitch_choice == self.pitch_amounts[self.note_index - 1]:
			Voice.soprano_motion.append(0)

		self.calculate_interval(Voice.bass_pitches, pitch_choice, self.intervals)
		self.calculate_motion(Voice.bass_motion, Voice.soprano_motion, self.motion_with_bass)

		return self.is_counterpoint(pitch_choice)


	def is_counterpoint(self, pitch_choice):

		# Some rules depend on a previous note and won't work for the first note
		# Short circuit evaluation

		if not self.is_voice_range():
			return False
		elif not self.validate_leap(pitch_choice):
			# print("Leap too wide!")
			return False
		elif "P" in self.intervals[-1] and "P" in self.intervals[-2]:
			# print("Double perfects. Delete!")
			return False  
		elif (self.note_index > 3 and self.intervals[-1] == self.intervals[-2] 
		and self.intervals[-2] == self.intervals[-3] and 
		self.intervals[-3] == self.intervals[-4]):
			# print("Quadruple identical imperfects. Delete")
			return False
		elif (self.note_index > 2 and 
		self.motion_with_bass[-1] == "Parallel" and 
		self.motion_with_bass[-2] == "Parallel" and 
		self.motion_with_bass[-3] == "Parallel"):
			# print("Three consecutive parallels. Delete!")  
			return False
		elif (((self.pitch_amounts[self.note_index - 1] + 1) % 12 == 0) and 
		pitch_choice % 12 != 0):
			# print("Leading tone must progress to tonic") EXCEPT SECONDARY DOMINANTS
			return False
		# elif self.intervals[-2] == "d5" and "3" not in self.intervals[-1]:
		# 	# print("Diminished 5th must resolve to a third. Delete!")
		# 	return False
		# elif (self.intervals[-2] == "A4") and ("6" not in self.intervals[-1]):
		# 	# print("Augmented 4th must resolve to a sixth. Delete!")
		# 	return False
		elif ((self.note_index != len(self.possible_pitches) - 1) and 
		self.intervals[-1] == "P8"):
			# print("Avoiding premature unison")
			return False
		elif (self.note_index > 2 and self.motion_with_bass[-1] != "Contrary" 
		and self.motion_with_bass[-1] != "Oblique" 
		and self.motion_with_bass[-1] == self.motion_with_bass[-2] and 
		self.motion_with_bass[-2] == self.motion_with_bass[-3]):
			# print(f"Triple {self.motion_with_bass[-1]}. Delete!")
			return False
		elif self.motion_with_bass[-1] == "No motion":
			return False
		elif ((self.motion_with_bass[-1] == "Parallel" or
		self.motion_with_bass[-1] == "Similar") and self.intervals[-1] == "P5"):
			# print(f"{self.motion_with_bass[-1]} 5th or hidden 5th")
			return False 
		elif (self.note_index > 1 and Voice.soprano_motion[-1] == 0 and 
		Voice.soprano_motion[-2] == 0):
			# print("Triple repeat. Delete!")
			return False
		elif self.intervals[-1] in harmonic_dissonance:
			return False
		elif ((self.note_index == len(self.possible_pitches) - 1) and 
			self.motion_with_bass[-1] != "Contrary"):
			# print("Must end strong with contrary motion!")
			return False


		return True

	def erase_last_note(self):
		self.intervals.pop()
		Voice.soprano_motion.pop()
		self.motion_with_bass.pop()

	def convert_notes(self):
		"""Converts notes from relative pitch magnitudes degrees to 
		absolute pitch magnitudes""" 

		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.pitch_amounts]
		vocal_range = True
		for real_note in self.real_notes:
			if real_note < 59:
				vocal_range = False
				print("Perform octave transposition")
				break

		if not vocal_range:
			for index, real_note in enumerate(self.real_notes):
				self.real_notes[index] += 12
			print("Vocal range fixed")

		Voice.soprano_pitches = self.real_notes

