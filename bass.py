import random

from voice import *
from idioms import *

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
		print(Voice.note_values, len(Voice.note_values))
		self.lily_convert()
		return self.real_notes

	def create_chords(self):
		"""Creates full chord progression"""
		tonic_chords, tonic_note_values, old_chord, rhythm_sequence = self.create_tonic_zone()
		self.make_half_cadence()
		# print(f"Add Idea #3 of {Voice.idea3_length} length: {Voice.note_values}")
		if rhythm_sequence != ("A","A","P") and \
		rhythm_sequence != ("A","P","P") and rhythm_sequence != ("P","A","P"):	
			print("Standard ending")
			# print(Voice.note_values)
			# print(Voice.chord_path)
			Voice.chord_path.extend(tonic_chords)
			Voice.note_values.extend(tonic_note_values)
			# print(Voice.note_values)
			# self.old_chord = old_chord
			self.old_chord = Voice.chord_path[-1]
		else:
			print("Changing ending")
			# print(Voice.note_values)
			Voice.chord_path.extend(tonic_chords[:-2])
			Voice.note_values.extend(tonic_note_values)
			# print(Voice.note_values)
			self.old_chord = Voice.chord_path[-1]
			chord_options = expand_tonic1[abs(self.old_chord)]
			self.create_passing_chords(chord_options)
		# self.old_chord = Voice.chord_path[-1]
		self.make_authentic_cadence()
		# print(Voice.idea1_length, Voice.idea2_length, Voice.idea3_length, Voice.idea4_length)
		# print(f"Add Idea #4 of {Voice.idea4_length} length: {Voice.note_values} {len(Voice.note_values)}")
		Voice.rhythm_sequence = rhythm_sequence

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
			if rhythm == "DP":
				chord_options = expand_tonic2[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "P":
				chord_options = expand_tonic1[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "A":
				chord_options = accent_tonic[abs(self.old_chord)]
				self.create_accent_chord(chord_options)

		note_total = 0
		for note_index, note_value in enumerate(Voice.note_values):
			note_total += note_value
			if note_total == 4:
				stop_index = note_index
				break

		song_length = len(Voice.note_values)
		Voice.idea1_length = len(Voice.note_values[:stop_index + 1])
		Voice.idea2_length = song_length - Voice.idea1_length
		return Voice.chord_path[:], Voice.note_values[:], self.old_chord, rhythm_sequence

	def make_half_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent1.keys()))
		Voice.note_values.extend(consequent1[rhythm_sequence])
		Voice.idea3_length = len(Voice.note_values) - Voice.idea1_length - Voice.idea2_length
		self.choose_chord(rhythm_sequence, False)

	def choose_chord(self, rhythm_sequence, cadence):
		counter = 0
		for rhythm in rhythm_sequence:
			counter += 1
			if counter == 1:
				chord_options = tonic_to_subdom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif "AS" in rhythm:
				chord_options = accent_subdom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "PS":
				chord_options = expand_subdom[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "CD":
				chord_options = (I64,)
				self.create_accent_chord(chord_options)
			elif rhythm == "FD" and "CD" in rhythm_sequence:
				# print("Optional cadence")
				chord_options = accent_dom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "FD" and "CD" not in rhythm_sequence:
				chord_options = subdom_to_dom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "AD":
				# print("Mandatory cadence")
				chord_options = (V, V7)
				self.create_accent_chord(chord_options)
			elif rhythm == "FT":
				# chord_options = (I,)
				chord_options = dom_to_tonic[abs(self.old_chord)]
				self.create_accent_chord(chord_options)

	def make_authentic_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent2.keys()))
		Voice.note_values.extend(consequent2[rhythm_sequence])
		Voice.idea4_length = (len(Voice.note_values) - (Voice.idea1_length) * 2 - 
			(Voice.idea2_length) * 2 - Voice.idea3_length)
		# print(Voice.note_values)
		# print(rhythm_sequence)
		self.choose_chord(rhythm_sequence, True)

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_scale_degree = 0
		old_pitch = 0
		old_position = 0
		for index, chord in enumerate(Voice.chord_path[1:]):
			new_scale_degree = int(bass_notes[abs(chord)])

			# Deciding between regular and inverted chord
			# (e.g., III to V6 going downward)
			if chord > 0 and Voice.chord_path[index] < 0 and old_scale_degree > new_scale_degree:
				old_position -= 7
				shift = new_scale_degree - old_scale_degree + 7
				new_position = old_position + shift
				new_pitch = modes[self.mode][new_position]

			elif chord > 0 or (chord < 0 and old_scale_degree > new_scale_degree):
				shift = new_scale_degree - old_scale_degree
				new_position = old_position + shift
				new_pitch = modes[self.mode][new_position]

			elif chord < 0 and new_scale_degree > old_scale_degree:
				old_position += 7
				shift = new_scale_degree - old_scale_degree - 7
				new_position = old_position + shift
				new_pitch = old_pitch + modes[self.mode][new_position] - \
					modes[self.mode][old_position]

			Voice.bass_motion.append(shift)
			pitch_change = new_pitch - old_pitch
			self.pitch_amounts.append(new_pitch)
			old_pitch = new_pitch
			old_position = new_scale_degree
			old_scale_degree = new_scale_degree

			if 1 in chord_tones[abs(chord)] and 6 in chord_tones[abs(chord)] and \
			(new_pitch + 2) % 12 == 0:
				self.pitch_amounts[-1] += 1
				# print("Raised seventh")  
		# print(self.pitch_amounts)
		# print(Voice.bass_motion)
		for index, move in enumerate(Voice.bass_motion):
			if move < 0:
				Voice.bass_motion[index] = int(move / -move)
			elif move > 0:
				Voice.bass_motion[index] = int(move / move)

		# print(Voice.bass_motion, len(Voice.bass_motion))

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		Voice.main_pitches = self.pitch_amounts
		# print(Voice.bass_pitches)
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.pitch_amounts]
		for index in range(len(self.real_notes)):
			# Raise seventh only for ascending
			if self.mode == "aeolian" and bass_notes[abs(Voice.chord_path[index])] == 6:
				pass
				# print("RAISED SEVENTH!")
				# self.real_notes[index] += 1
			if Voice.tonic == "C":
				self.real_notes[index] -= 12
			else:
				self.real_notes[index] -= 24
		Voice.bass_pitches = self.real_notes