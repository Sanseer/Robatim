import itertools
import random

from voice import Voice
import idioms as idms

class MiddleVoices(Voice):

	def __init__(self):
		self.note_index = 0
		self.pitch_amounts = []
		self.possible_pitches = []
		self.pitch_amounts.extend(("Blank",) * 
			((Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length)))
		self.possible_pitches.extend(("Blank",) * 
			((Voice.idea1_length + Voice.idea2_length + 
			Voice.idea3_length + Voice.idea4_length)))
		print(len(Voice.chord_path), len(self.possible_pitches), "WTF")

	def create_parts(self):
		self.populate_note(0)
		self.pitch_amounts[0] = random.choice(self.possible_pitches[0])
		self.add_notes()
		print(self.pitch_amounts)
		self.split_notes()

	def populate_note(self, index):
		current_chord = abs(Voice.chord_path[index])
		chord_root = idms.chord_tones[current_chord][0]
		chord_length = len(idms.chord_tones[current_chord]) - 1
		all_pitches = self.create_chord_pitches(index, chord_length, chord_root)
		if Voice.chromatics[index] == "2D":
			all_pitches = self.add_chromatics(index, all_pitches)

		for value in all_pitches[:]:
			if (value < 48) or (value > 73):
				all_pitches.remove(value)

		pitch_combos = self.create_pitch_combos(all_pitches)
		correct_combos = self.arrange_pitch_combos(index, pitch_combos)
		self.possible_pitches[index] = correct_combos

	def create_chord_pitches(self, index, chord_length, chord_root):
		all_pitches = []
		high_point = Voice.soprano_pitches[index]
		low_point = Voice.bass_pitches[index]

		root_pitch = idms.modes[Voice.mode][chord_root] + idms.tonics[Voice.tonic]
		
		chord_pitches = [0]
		new_position = chord_root + 2
		for _ in range(chord_length):
			chord_pitches.append(idms.modes[Voice.mode][new_position] - idms.modes[Voice.mode][chord_root])
			new_position += 2

		if Voice.mode == "aeolian" and chord_root == 4:
			print(f"Index {index}", end=" ")
			print("Raising seventh as upper")
			chord_pitches[1] += 1
		elif Voice.mode == "aeolian" and chord_root == 6:
			print(f"Index: {index}", end=" ")
			print("Raising seventh as bass")
			chord_pitches[0] += 1

		chord_slot = 0
		current_pitch = root_pitch

		while current_pitch < low_point:
			if chord_length >= chord_slot:
				chord_slot += 1
			if chord_length < chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_pitches[chord_slot]

		while current_pitch <= high_point:
			if chord_length >= chord_slot:
				all_pitches.append(current_pitch)
				chord_slot += 1
			if chord_length < chord_slot:
				chord_slot = 0
				root_pitch += 12
			current_pitch = root_pitch + chord_pitches[chord_slot]

		return all_pitches

	def create_pitch_combos(self, all_pitches):
		pitch_combos = list(itertools.combinations_with_replacement(
			all_pitches, 2))
		for (value1, value2) in pitch_combos[:]:
			if (value1 < 54 and value2 < 54) or (value1 > 68 and value2 > 68):
				pitch_combos.remove((value1, value2))
		return pitch_combos

	def arrange_pitch_combos(self, index, pitch_combos):
		# Arrange by complete chords
		complete_rank = []
		scale_degrees = []
		# print(f"Index: {index}")
		# print(pitch_combos)
		for notes in pitch_combos:
			# print(notes, end=" ")
			scale_degrees.append(self.make_scale_pitch(notes[0]))
			scale_degrees.append(self.make_scale_pitch(notes[1]))
			scale_degrees.append(self.make_scale_pitch(Voice.soprano_pitches[index]))
			scale_degrees.append(self.make_scale_pitch(Voice.bass_pitches[index]))
			complete_rank.append(len(set(scale_degrees)))
			# print(scale_degrees, end=" ")
			scale_degrees = []
		# print(complete_rank)
		# Sorting one list using another
		complete_sort = [x for _,x in sorted(zip(complete_rank, pitch_combos), reverse=True)]
		# print(complete_sort, len(complete_sort))

		if index == 0:
			return complete_sort

		complete_rank = sorted(complete_rank, reverse=True)
		# print(complete_rank)
		complete_parts = []
		set_rank = sorted(list(set(complete_rank)), reverse=True)
		# print(set_rank)
		for chord_type in set_rank[1:]:
			complete_parts.append(complete_rank.index(chord_type))

		pitches_full_sort = []
		# print("Complete parts",complete_parts)


		for chord_type_index in range(len(complete_parts) - 1):
			start = complete_parts[chord_type_index]
			stop = complete_parts[chord_type_index + 1]
			chord_group = complete_sort[start:stop]
			pitches_full_sort.extend(self.arrange_chord_motion(index, chord_group))

		if len(complete_parts) > 1:
			pitches_full_sort.extend(self.arrange_chord_motion(index, complete_sort[stop:]))
			# print(pitches_full_sort)
		elif len(complete_parts) == 1:
			divider = complete_parts[0]
			pitches_full_sort.extend(self.arrange_chord_motion(index, complete_sort[:divider]))
			# print(pitches_full_sort)
			pitches_full_sort.extend(self.arrange_chord_motion(index, complete_sort[divider:]))
		else:
			return complete_sort

		return pitches_full_sort

	def arrange_chord_motion(self, index, chord_group):
		chord_motions = []
		old_tenor_note = self.pitch_amounts[index - 1][0]
		old_alto_note = self.pitch_amounts[index - 1][1]
		for chord in chord_group:
			new_tenor_note = chord[0] 
			new_alto_note = chord[1]
			movement = abs(new_tenor_note - old_tenor_note)
			movement += abs(new_alto_note - old_alto_note)
			chord_motions.append(int(movement))
		motion_sort = [x for _,x in sorted(zip(chord_motions, chord_group))]

		return motion_sort

	def add_chromatics(self, nc_index, all_pitches):
		for index, pitch in enumerate(all_pitches[:]):
			all_pitches[index] += self.make_sec_dom(
				Voice.chord_path[nc_index], pitch)
		return all_pitches

	def add_notes(self):
		"""This melody creation is naturally recursive but I modeled it 
		with iteration. You try notes until you get a good note. 
		If all of your note choices at the current position are bad, 
		then your previous note is bad and should be removed as well."""

		self.note_index = 0
		while self.pitch_amounts[self.note_index] != "Blank":
			self.note_index += 1
		self.populate_note(self.note_index)

		last_combo = self.pitch_amounts[self.note_index - 1]
		attempts = 0
		while "Blank" in self.pitch_amounts:
			attempts += 1
			# Prevent CPU overload
			assert(attempts < 2000), f"You ran out of tries"
			if self.possible_pitches[self.note_index]:
				combo_choice = self.choose_combo()
				# voice_lead = self.validate_notes(combo_choice)
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
		return self.possible_pitches[self.note_index][0]

	def validate_notes(self, combo_choice):
		for voice_index in range(len(combo_choice)):
			if self.note_index != 0 and not self.validate_leap(
				self.pitch_amounts[self.note_index - 1][voice_index], 
				combo_choice[voice_index]):
				# print("Leap too wide")
				return False
			if (self.note_index > 0 and voice_index == 0 and 
			Voice.bass_pitches[self.note_index] == combo_choice[voice_index] and 
			Voice.bass_pitches[self.note_index - 1] == 
			self.pitch_amounts[self.note_index - 1][voice_index]):
				# print("No more than two consecutive unisons between voices")
				return False
			elif (self.note_index > 0 and voice_index == 1 and 
			Voice.soprano_pitches[self.note_index] == combo_choice[voice_index] and 
			Voice.soprano_pitches[self.note_index - 1] == 
			self.pitch_amounts[self.note_index - 1][voice_index]):
				# print("No more than two consecutive unisons between voices")
				return False

		# No more than two consecutive unisons between soprano/alto or bass/tenor
		# Remove duplicate leading tones, including with secondary dominants
		# leading tone of secondary dominant and regular chord must progress to tonic
		# Prevent using only two notes of a seventh chord
		return True

	def validate_leap(self, old_pitch, new_pitch):
		# for index in range(len(combo_choice)):
			# old_pitch = self.pitch_amounts[self.note_index - 1][index]
		pitch_change = new_pitch - old_pitch
		if abs(pitch_change) > 4: 
			return False
		return True

	def split_notes(self):
		for index, (value1, value2) in enumerate(self.pitch_amounts):
			Voice.tenor_pitches.append(value1)
			Voice.alto_pitches.append(value2)


class Tenor(Voice):

	def __init__(self):
		self.real_notes = Voice.tenor_pitches
		self.sheet_notes = []
		self.lily_notes = []

class Alto(Voice):

	def __init__(self):
		self.real_notes = Voice.alto_pitches
		self.sheet_notes = []
		self.lily_notes = []



