import itertools
import random
import pysnooper

from voice import Voice
import idioms as idms

class KBUpperVoices(Voice):
	"""Creates chords using bass notes for a keyboard style tune"""

	def __init__(self):
		self.note_index = 0
		self.pitch_amounts = []
		self.possible_pitches = []
		self.pitch_amounts.extend(("Blank",) * 
			(Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length))
		self.possible_pitches.extend(("Blank",) * 
			(Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length))
		assert(len(Voice.bass_pitches) == len(self.pitch_amounts))

	def create_parts(self):
		self.populate_note(0)
		self.pitch_amounts[0] = self.possible_pitches[0][0]
		print(self.pitch_amounts)
		self.add_notes()
		self.split_notes()

	def populate_note(self, index):
		print(self.pitch_amounts, index)
		current_chord = abs(Voice.chord_path[index])
		chord_root = idms.chord_tones[current_chord][0]
		chord_length = len(idms.chord_tones[current_chord])
		all_pitches = self.create_chord_pitches(index,chord_length, chord_root)
		print(all_pitches)
		if Voice.chromatics[index] == "2D":
			all_pitches = self.add_chromatics(index, all_pitches)
		for value in all_pitches[:]:
			if (value < Voice.bass_pitches[index]) or (value > 66):
				all_pitches.remove(value)

		pitch_combos = self.create_pitch_combos(index, all_pitches)
		# print(pitch_combos)
		self.possible_pitches[index] = self.arrange_pitch_combos(
			index, pitch_combos)

	def create_chord_pitches(self, index, chord_length, chord_root):
		all_pitches = []
		high_point = 66
		low_point = Voice.bass_pitches[index]

		root_pitch = idms.modes[Voice.mode][chord_root] + idms.tonics[Voice.tonic]
		chord_pitches = [0]
		new_position = chord_root + 2
		for _ in range(chord_length - 1):
			chord_pitches.append((idms.modes[Voice.mode][new_position] - 
				idms.modes[Voice.mode][chord_root]))
			new_position += 2

		if Voice.mode == "aeolian" and chord_root == 4:
			chord_pitches[1] += 1
		elif Voice.mode == "aeolian" and chord_root == 6:
			chord_pitches[0] += 1

		chord_slot = 0
		current_pitch = root_pitch

		while current_pitch < low_point:
			if (chord_length - 1) >= chord_slot:
				chord_slot += 1
			if (chord_length - 1) < chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_pitches[chord_slot]
			print("Shifting pitch", end=" ")

		while current_pitch <= high_point:
			if (chord_length - 1) >= chord_slot:
				all_pitches.append(current_pitch)
				chord_slot += 1
			if (chord_length - 1) < chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_pitches[chord_slot]
			print("Adding pitch", end=" ")

		return all_pitches

	def add_chromatics(self, nc_index, all_pitches):
		for index, pitch in enumerate(all_pitches[:]):
			all_pitches[index] += self.make_sec_dom(
				Voice.chord_path[nc_index], pitch) 
		return all_pitches

	def create_pitch_combos(self, index, all_pitches):
		pitch_combos = list(itertools.combinations_with_replacement(
			all_pitches, 3))
		for (value1, value2, value3) in pitch_combos[:]:
			if ((value1 == value2 == value3) or 
				(Voice.bass_pitches[index] == value1 == value2) or
				max(value1, value2, value3) - min(value1, value2, value3) > 12 or 
				Voice.bass_pitches[index] == value1 == value2 - 12 == value3 - 12 or
				Voice.bass_pitches[index] == value1 - 12 == value2 - 24 == value3 - 24 or
				Voice.bass_pitches[index] == value1 - 12 == value2 - 12 == value3 - 24):
				pitch_combos.remove((value1, value2, value3))
		return pitch_combos

	# @pysnooper.snoop()
	def arrange_pitch_combos(self, index, pitch_combos):
		"""Arrange chords by completeness and smoothest motion"""
		complete_rank = []
		scale_pitches_list = []

		for notes in pitch_combos:
			scale_pitches = []
			scale_pitches.append(self.make_scale_pitch(Voice.bass_pitches[index]))
			scale_pitches.append(self.make_scale_pitch(notes[0]))
			scale_pitches.append(self.make_scale_pitch(notes[1]))
			scale_pitches.append(self.make_scale_pitch(notes[2]))
			if len(set(scale_pitches)) == 1: 
				print(Voice.bass_pitches[index], notes[0], notes[1], notes[2])
			scale_pitches_list.append(scale_pitches)
			complete_rank.append(len(set(scale_pitches)))

		complete_chord_sort = [x for _,x in sorted(zip(
			complete_rank, pitch_combos), reverse=True)]
		# print(complete_chord_sort)

		if index == 0:
			return complete_chord_sort

		complete_rank = sorted(complete_rank, reverse=True)
		chord_index_dividers = []
		chord_types = sorted(list(set(complete_rank)), reverse=True)
		for chord_type in chord_types[1:]:
			chord_index_dividers.append(complete_rank.index(chord_type))

		# print(chord_index_dividers)
		smooth_chord_sort = []
		for slot in range(len(chord_index_dividers) - 1):
			start = chord_index_dividers[slot]
			stop = chord_index_dividers[slot + 1]
			chord_group = complete_chord_sort[start:stop]
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, chord_group))

		if len(chord_index_dividers) > 1:
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, complete_chord_sort[stop:]))
		elif len(chord_index_dividers) == 1:
			divider = chord_index_dividers[0]
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, complete_chord_sort[:divider]))
			smooth_chord_sort.extend(self.arrange_chord_motion(
				index, complete_chord_sort[divider:]))
		else:
			return complete_chord_sort

		return smooth_chord_sort

	def arrange_chord_motion(self, index, chord_group):
		chord_motions = []
		old_tenor_note = self.pitch_amounts[index - 1][0]
		old_alto_note = self.pitch_amounts[index - 1][1]
		old_soprano_note = self.pitch_amounts[index - 1][2]
		for chord in chord_group:
			new_tenor_note = chord[0] 
			new_alto_note = chord[1]
			new_soprano_note = chord[2]
			movement = abs(new_tenor_note - old_tenor_note)
			movement += abs(new_alto_note - old_alto_note)
			movement += abs(new_soprano_note - old_soprano_note)
			chord_motions.append(int(movement))
		motion_sort = [x for _,x in sorted(zip(chord_motions, chord_group))]

		return motion_sort

	def add_notes(self):
		"""Fills up a blank template with notes for soprano, alto, and tenor"""
		self.note_index = 0
		while self.pitch_amounts[self.note_index] != "Blank":
			self.note_index += 1
		self.populate_note(self.note_index)
		last_combo = self.pitch_amounts[self.note_index - 1]
		attempts = 0

		"""This melody creation is naturally recursive but I modeled it 
		with iteration. You try notes until you get a good note combo. 
		If all of your note choices at the current position are bad, 
		then your previous note combo is bad and should be removed."""
		while "Blank" in self.pitch_amounts:
			attempts += 1
			# Prevent CPU overload
			assert(attempts < 2000), f"You ran out of tries"
			if self.possible_pitches[self.note_index]:
				combo_choice = self.choose_combo()
				if self.validate_notes(combo_choice):
					self.pitch_amounts[self.note_index] = combo_choice
					last_combo = combo_choice
					print("Good", end=" ~ ")
					self.note_index += 1
					if self.note_index < len(self.pitch_amounts):
						self.populate_note(self.note_index)
				else:
					print("Bad", end=" ~ ")
					self.possible_pitches[self.note_index].remove(combo_choice)
			else:
				self.possible_pitches[self.note_index] = "Blank"
				self.populate_note(self.note_index)
				assert(self.note_index != 0), "You fail"

				self.note_index -= 1
				print(f"Go back to index {self.note_index}")
				self.possible_pitches[self.note_index].remove(last_combo)
				self.pitch_amounts[self.note_index] = "Blank"
				last_combo = self.pitch_amounts[self.note_index - 1]

	def choose_combo(self):
		"""Picks the fullest and smoothest chord from remaining options"""
		return self.possible_pitches[self.note_index][0]

	def validate_notes(self, combo_choice):
		return True

	def split_notes(self):
		for index, (value1, value2, value3) in enumerate(self.pitch_amounts):
			Voice.tenor_pitches.append(value1)
			Voice.alto_pitches.append(value2)
			Voice.soprano_pitches.append(value3)

class KBSoprano(Voice):

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		self.sheet_notes = []
		self.lily_notes = []

class KBTenor(Voice):

	def __init__(self):
		self.real_notes = Voice.tenor_pitches
		self.sheet_notes = []
		self.lily_notes = []

class KBAlto(Voice):

	def __init__(self):
		self.real_notes = Voice.alto_pitches
		self.sheet_notes = []
		self.lily_notes = []

