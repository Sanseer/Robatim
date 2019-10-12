import itertools
import random
import logging

from generate.voices.voice import Voice

class Chorale(Voice):

	def __init__(self):
		self.chord_index = 0
		self.root_pitch = None

		self.bass_tenor_intervals = []
		self.bass_alto_intervals = []
		self.bass_soprano_intervals = []
		self.tenor_alto_intervals = []
		self.tenor_soprano_intervals = []
		self.alto_soprano_intervals = []

		self.bass_tenor_motion = []
		self.bass_alto_motion = []
		self.bass_soprano_motion = []
		self.tenor_alto_motion = []
		self.tenor_soprano_motion = []
		self.alto_soprano_motion = []

		self.composite_intervals = [self.bass_tenor_intervals, 
			self.bass_alto_intervals, self.bass_soprano_intervals, 
			self.tenor_alto_intervals, self.tenor_soprano_intervals,
			self.alto_soprano_intervals]
		self.composite_mvmts = [self.bass_tenor_motion, 
			self.bass_alto_motion, self.bass_soprano_motion, 
			self.tenor_alto_motion, self.tenor_soprano_motion,
			self.alto_soprano_motion]

		self.condensed_chords = []
		self.unique_chord_indices = set()

		self.logger = logging.getLogger("chorale")
		chorale_handler = logging.FileHandler("logs/chorale.log", mode='w')
		chorale_handler.setLevel(logging.WARNING)
		chorale_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		chorale_handler.setFormatter(chorale_format)
		self.logger.addHandler(chorale_handler)

	def create_parts(self):
		self.condense_chords()
		self.make_chord_voicings()
		self.make_accompanyment()

	def condense_chords(self):
		current_chord_obj = Voice.chord_sequence[0]
		self.condensed_chords.append(current_chord_obj)
		self.unique_chord_indices.add(0)
		previous_chord_obj = current_chord_obj

		for chord_index, current_chord_obj in enumerate(Voice.chord_sequence[1:], 1):
			if current_chord_obj != previous_chord_obj:
				self.condensed_chords.append(current_chord_obj)
				self.unique_chord_indices.add(chord_index)
			previous_chord_obj = current_chord_obj

	def make_chord_voicings(self):

		self.chosen_chord_voicings = [None for _ in self.condensed_chords]
		self.possible_chord_voicings = [None for _ in self.condensed_chords]

		self.possible_chord_voicings[self.chord_index] = self.populate_chord()

		while None in self.chosen_chord_voicings:
			self.logger.warning(f"Chord index: {self.chord_index}")
			self.combo_choice = next(
				self.possible_chord_voicings[self.chord_index], None)
			if self.combo_choice is None:
				self.possible_chord_voicings[self.chord_index] = None
				if self.chord_index <= 0:
					raise IndexError
				self.chord_index -= 1
				self.erase_last_chord()
				self.chosen_chord_voicings[self.chord_index] = None
				last_combo = self.chosen_chord_voicings[self.chord_index - 1]
			else:
				self.chosen_chord_voicings[self.chord_index] = self.combo_choice
				last_combo = self.combo_choice
				self.chord_index += 1
				if self.chord_index < len(self.chosen_chord_voicings):
					self.possible_chord_voicings[self.chord_index] = self.populate_chord()

	def erase_last_chord(self):
		if self.bass_motion:
			self.bass_motion.pop()
			self.tenor_motion.pop()
			self.alto_motion.pop()
			self.soprano_motion.pop()
			[motion_list.pop() for motion_list in self.composite_mvmts]

		[interval_list.pop() for interval_list in self.composite_intervals]

	def populate_chord(self):
		current_chord_obj = self.condensed_chords[self.chord_index]
		current_pitches_dict = current_chord_obj.pitches_to_degrees
		self.logger.warning(f"Current pitches dict: {current_pitches_dict}")

		chordal_members = current_chord_obj.scale_degrees
		unsorted_pitch_combos = self.make_pitch_combos(current_pitches_dict)
		current_chord = current_chord_obj.chord_name
		chord_direction = str(current_chord_obj)[0]
		bass_degree = current_chord_obj.bass_degree

		if self.chord_index > 0:
			previous_chord = self.condensed_chords[self.chord_index - 1].chord_name
		else:
			previous_chord = None

		# change parameters into array corresponding to chord indices
		# calculate only once
		for pitch_combo in self.arrange_pitch_combos(unsorted_pitch_combos, chordal_members,current_pitches_dict):
			if self.is_voice_lead(
			  pitch_combo, current_chord, previous_chord, chord_direction, 
			  current_pitches_dict, chordal_members, bass_degree):
				yield pitch_combo

	def make_pitch_combos(self, current_pitches_dict):
		possible_midi_pitches = [[] for _ in range(4)]
		for midi_pitch in current_pitches_dict:
			if 38 <= midi_pitch <= 62:
				possible_midi_pitches[0].append(midi_pitch)
			if 48 <= midi_pitch <= 69:
				possible_midi_pitches[1].append(midi_pitch)
			if 55 <= midi_pitch <= 74:
				possible_midi_pitches[2].append(midi_pitch)
			if 59 <= midi_pitch <= 81:
				possible_midi_pitches[3].append(midi_pitch)
			if midi_pitch > 81:
				break

		self.logger.warning(f"Possible midi pitches: {possible_midi_pitches}")

		return itertools.product(*possible_midi_pitches)

	def arrange_pitch_combos(self, unsorted_pitch_combos, chordal_members, current_pitches_dict):

		voicing_groups = [[] for _ in chordal_members]

		for pitch_combo in unsorted_pitch_combos:
			scale_degrees_used = set()
			for midi_pitch in pitch_combo:
				scale_degrees_used.add(current_pitches_dict[midi_pitch])
			scale_degree_count = len(scale_degrees_used)
			voicing_groups[scale_degree_count - 1].append(pitch_combo)

		if self.chord_index == 0:
			for voicing_group in reversed(voicing_groups):
				random.shuffle(voicing_group)
				for pitch_combo in voicing_group:
					yield pitch_combo
		else:
			for unsorted_voicing_group in reversed(voicing_groups):
				sorted_voicing_group = self.sort_voicing_group(unsorted_voicing_group)
				for pitch_combo in sorted_voicing_group:
					yield pitch_combo

	def sort_voicing_group(self, unsorted_voicing_group):

		note_mvmts = []
		for pitch_combo in unsorted_voicing_group:
			note_mvmt = 0
			for old_note, new_note in zip(
			  self.chosen_chord_voicings[self.chord_index - 1], pitch_combo):
				note_mvmt += abs(new_note - old_note) 

			note_mvmts.append(note_mvmt)

		sorted_voicing_group = [pitch_combo 
			for _, pitch_combo in sorted(zip(note_mvmts, unsorted_voicing_group))]

		return sorted_voicing_group

	@property
	def octave_above(self):
		return range(self.root_pitch, self.root_pitch + 12)

	@property 
	def octave_below(self):
		return range(self.root_pitch - 12, self.root_pitch)

	def is_voice_lead(
	  self, pitch_combo, current_chord, previous_chord, chord_direction, 
	  current_pitches_dict, chordal_members, bass_degree):
		(b_pitch, t_pitch, a_pitch, s_pitch) = pitch_combo
		if not b_pitch <= t_pitch <= a_pitch <= s_pitch:
			return False 
		if (b_pitch - t_pitch) > 24:
			return False
		if (a_pitch - t_pitch) > 12:
			return False
		if (s_pitch - a_pitch) > 12:
			return False

		degree_combo = (current_pitches_dict[b_pitch], 
			current_pitches_dict[t_pitch], 
			current_pitches_dict[a_pitch],
			current_pitches_dict[s_pitch])

		if len(set(degree_combo)) == 1:
			return False
		if chordal_members[0] not in degree_combo:
			return False
		if chordal_members[1] not in degree_combo:
			return False
		if bass_degree != degree_combo[0]:
			return False
		if current_chord in {"V", "V7", "V6"} and degree_combo.count(6) >= 2:
			return False

		bass_tenor_intervals = self.bass_tenor_intervals[:]
		bass_tenor_intervals.append(
			self.get_interval(b_pitch, t_pitch, current_pitches_dict))
		bass_alto_intervals = self.bass_alto_intervals[:]
		bass_alto_intervals.append(
			self.get_interval(b_pitch, a_pitch, current_pitches_dict))
		bass_soprano_intervals = self.bass_soprano_intervals[:]
		bass_soprano_intervals.append(
			self.get_interval(b_pitch, s_pitch, current_pitches_dict))

		tenor_alto_intervals = self.tenor_alto_intervals[:]
		tenor_alto_intervals.append(
			self.get_interval(t_pitch, a_pitch, current_pitches_dict))
		tenor_soprano_intervals = self.tenor_soprano_intervals[:]
		tenor_soprano_intervals.append(
			self.get_interval(t_pitch, s_pitch, current_pitches_dict))
		alto_soprano_intervals = self.alto_soprano_intervals[:]
		alto_soprano_intervals.append(
			self.get_interval(a_pitch, s_pitch, current_pitches_dict))

		if self.chord_index == 0:
			self.bass_tenor_intervals.append(bass_tenor_intervals[-1]) 
			self.bass_alto_intervals.append(bass_alto_intervals[-1]) 
			self.bass_soprano_intervals.append(bass_soprano_intervals[-1]) 
			self.tenor_alto_intervals.append(tenor_alto_intervals[-1]) 
			self.tenor_soprano_intervals.append(tenor_soprano_intervals[-1]) 
			self.alto_soprano_intervals.append(alto_soprano_intervals[-1])

			self.root_pitch = b_pitch 
			self.logger.warning(f"Root pitch: {self.root_pitch}")
			return True

		if chord_direction == "+" and b_pitch not in self.octave_above:
			return False
		elif chord_direction == "-" and b_pitch not in self.octave_below:
			return False
		elif chord_direction == "0" and b_pitch != self.root_pitch:
			return False

		bass_motion = self.bass_motion[:]
		tenor_motion = self.tenor_motion[:]
		alto_motion = self.alto_motion[:]
		soprano_motion = self.soprano_motion[:]

		self.add_voice_motion(bass_motion, b_pitch, 0)
		self.add_voice_motion(tenor_motion, t_pitch, 1)
		self.add_voice_motion(alto_motion, a_pitch, 2)
		self.add_voice_motion(soprano_motion, s_pitch, 3)

		composite_motion = [tenor_motion, alto_motion, soprano_motion]
		for voice_index, new_pitch in enumerate(pitch_combo[1:]):
			old_pitch = self.chosen_chord_voicings[self.chord_index - 1][voice_index + 1] 
			if abs(new_pitch - old_pitch) > 12:
				return False
			if (self.chord_index > 1 and
			  abs(old_pitch - self.chosen_chord_voicings[self.chord_index - 2][voice_index + 1]) > 5
			  and (abs(new_pitch - old_pitch) > 2 or
			  composite_motion[voice_index][-1] == 
			  composite_motion[voice_index][-2])):
				return False

		bass_tenor_motion = self.bass_tenor_motion[:]
		bass_alto_motion = self.bass_alto_motion[:]
		bass_soprano_motion = self.bass_soprano_motion[:]
		tenor_alto_motion = self.tenor_alto_motion[:]
		tenor_soprano_motion = self.tenor_soprano_motion[:]
		alto_soprano_motion = self.alto_soprano_motion[:]

		self.add_motion_type(bass_motion, 
			tenor_motion, bass_tenor_motion, bass_tenor_intervals)
		self.add_motion_type(bass_motion, 
			alto_motion, bass_alto_motion, bass_alto_intervals)
		self.add_motion_type(bass_motion, 
			soprano_motion, bass_soprano_motion, bass_soprano_intervals)

		self.add_motion_type(tenor_motion, 
			alto_motion, tenor_alto_motion, tenor_alto_intervals)
		self.add_motion_type(tenor_motion,
			soprano_motion, tenor_soprano_motion, tenor_soprano_intervals)
		self.add_motion_type(alto_motion, 
			soprano_motion, alto_soprano_motion, alto_soprano_intervals)

		composite_intervals = [bass_tenor_intervals, bass_alto_intervals, 
			bass_soprano_intervals, tenor_alto_intervals, 
			tenor_soprano_intervals, alto_soprano_intervals]
		composite_mvmts = [bass_tenor_motion, bass_alto_motion, 
			bass_soprano_motion, tenor_alto_motion, tenor_soprano_motion,
			alto_soprano_motion]

		for interval_list, motion_list in zip(
		  composite_intervals, composite_mvmts):
			if (interval_list[-1] in {"P5", "P8"} and 
			  motion_list[-1] == "Parallel"):
				return False
			if (interval_list[-2] == "A4" and 
			  interval_list[-1] not in {"M6", "m6"}): 
				if current_chord == "I" and previous_chord == "V7":
					return False
			if (interval_list[-2] == "d5" and 
			  interval_list[-1] not in {"M3", "m3"}): 
				if current_chord == "I" and previous_chord == "V7":
					return False

		# add new parameters to official sequence
		self.bass_tenor_intervals.append(bass_tenor_intervals[-1]) 
		self.bass_alto_intervals.append(bass_alto_intervals[-1]) 
		self.bass_soprano_intervals.append(bass_soprano_intervals[-1]) 
		self.tenor_alto_intervals.append(tenor_alto_intervals[-1]) 
		self.tenor_soprano_intervals.append(tenor_soprano_intervals[-1]) 
		self.alto_soprano_intervals.append(alto_soprano_intervals[-1]) 

		self.bass_motion.append(bass_motion[-1])
		self.tenor_motion.append(tenor_motion[-1])
		self.alto_motion.append(alto_motion[-1])
		self.soprano_motion.append(soprano_motion[-1])

		self.bass_tenor_motion.append(bass_tenor_motion[-1]) 
		self.bass_alto_motion.append(bass_alto_motion[-1]) 
		self.bass_soprano_motion.append(bass_soprano_motion[-1]) 
		self.tenor_alto_motion.append(tenor_alto_motion[-1]) 
		self.tenor_soprano_motion.append(tenor_soprano_motion[-1]) 
		self.alto_soprano_motion.append(alto_soprano_motion[-1]) 

		return True

	def make_accompanyment(self):

		for _ in range(4):
			Voice.midi_score.append([])
			Voice.chorale_scale_degrees.append([])
		chord_accompaniments = {
			(2,2): [
				((960,), ({0,1,2,3},)), ((960, 960), ({0}, {1,2,3})),
				((960 * 3 // 2,), ({0,1,2,3},)), ((960, 960), ({1,2,3}, {0})),
				((480, 480, 480), ({0,1,2,3}, {}, {0,1,2,3})),
				((480, 240, 480, 240, 480), ({0,1,2}, {}, {0,1,2,3}, {}, {0,1,2})),
				((480, 480, 480, 480), ({2}, {1}, {3}, {0}))
			], (2,3): [
				((960,), ({0,1,2,3},)), ((960, 960), ({0}, {1,2,3})),
				((960 * 10 // 6,), ({0,1,2,3},)), ((960, 960), ({1,2,3}, {0})),
				((960 * 2 // 3, 320, 960 * 2 // 3), ({0,1,2,3}, {}, {0,1,2,3}))
			], (3,2): [
				((960,), ({0,1,2,3},)), ((960, 960, 960), ({0}, {1,2,3}, {1,2,3})),
				((960 * 2,), ({0,1,2,3},)),
				((480, 480, 480, 480, 480), ({0,1,2,3}, {}, {0,1,2,3}, {}, {0,1,2,3}))
			], (4,2): [
				((960,), ({0,1,2,3},)), ((960, 960), ({0}, {1,2,3})),
				((960 * 3 // 2,), ({0,1,2,3},)), ((960, 960), ({1,2,3}, {0})),
				((480, 480, 480), ({0,1,2,3}, {}, {0,1,2,3})),
				((480, 240, 480, 240, 480), ({0,1,2}, {}, {0,1,2,3}, {}, {0,1,2})),
				((480, 480, 480, 480), ({2}, {1}, {3}, {0})),
				((960, 960, 960, 960), ({0}, {1,2,3}, {}, {1,2,3})),
				((960 * 2, 960 * 2), ({0,1,2,3}, {}))
			], (4,3): [
				((960,), ({0,1,2,3},)), ((960, 960), ({0}, {1,2,3})),
				((960 * 10 // 6,), ({0,1,2,3},)), ((960, 960), ({1,2,3}, {0})),
				((960 * 2 // 3, 320, 960 * 2 // 3), ({0,1,2,3}, {}, {0,1,2,3})),
				((960, 960, 960, 960), ({0}, {1,2,3}, {}, {1,2,3})),
				((960 * 2, 960 * 2), ({0,1,2,3}, {}))

			]
		}
		if Voice.time_sig == (3,2):
			raw_chord_duration = 960 * 3
		else:
			raw_chord_duration = 960 * 2
		chord_accompaniment = chord_accompaniments[Voice.time_sig]

		if Voice.time_sig[0] == 4:
			if Voice.chord_acceleration:
				chord_accompaniment.pop()

		note_durations, voices_used = random.choice(chord_accompaniment)

		chord_units_used = sum(note_durations) // raw_chord_duration
		if chord_units_used == 0:
			chord_units_used = 1
		print(f"Chord units used: {chord_units_used}")
		if chord_units_used > 1:
			all_note_durations = [] 
			all_voices_used = []
			note_index = 0
			for _ in range(chord_units_used):
				all_note_durations.append([])
				all_voices_used.append([])
				while sum(all_note_durations[-1]) < raw_chord_duration:
					all_note_durations[-1].append(note_durations[note_index])
					all_voices_used[-1].append(voices_used[note_index])
					note_index += 1
		else:
			all_note_durations = [note_durations]
			all_voices_used = [voices_used]


		print(f"All note durations: {all_note_durations}")
		print(f"All voices used: {all_voices_used}")
		if {1,2,3} in voices_used:
			Voice.waltz = True
			Voice.voice_volumes = (80, 50, 50, 50)
		print(f"Waltz? {Voice.waltz}")

		unique_chord_iter = iter(self.chosen_chord_voicings)
		current_time = 0

		for chord_index, current_chord_obj in enumerate(Voice.chord_sequence):
			pitches_to_degrees = current_chord_obj.pitches_to_degrees
			note_durations = all_note_durations[chord_index % chord_units_used]
			voices_used = all_voices_used[chord_index % chord_units_used]
			self.logger.warning(f"Note durations: {note_durations}")
			if chord_index in self.unique_chord_indices:
				current_pitch_combo = next(unique_chord_iter)
				self.logger.warning(f"Current pitch combo: {current_pitch_combo}")
				last_pitch_combo = []
				for voice_index, current_pitch in enumerate(current_pitch_combo):
					note_time = current_time
					for beat_index, note_duration in enumerate(note_durations):
						if voice_index in voices_used[beat_index]:
							Voice.midi_score[voice_index + 1].append(
								Voice.Note(current_pitch, note_time, note_duration))
							Voice.chorale_scale_degrees[voice_index].append(
								pitches_to_degrees[current_pitch])
						note_time += note_duration
					last_pitch_combo.append(current_pitch)
					self.logger.warning(
						f"Added notes: {Voice.midi_score[voice_index + 1][-len(note_durations):]}")
			else:
				self.logger.warning(f"Last pitch combo: {last_pitch_combo}")
				for voice_index, last_pitch in enumerate(last_pitch_combo):
					note_time = current_time
					for beat_index, note_duration in enumerate(note_durations):
						if voice_index in voices_used[beat_index]:
							Voice.midi_score[voice_index + 1].append(
								Voice.Note(last_pitch, note_time, note_duration))
							Voice.chorale_scale_degrees[voice_index].append(
								pitches_to_degrees[last_pitch])
						note_time += note_duration
					self.logger.warning(
						f"Added notes: {Voice.midi_score[voice_index + 1][-len(note_durations):]}")

			current_time += raw_chord_duration


class Bass(Voice):

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[0]
		self.midi_notes = Voice.midi_score[1]

		self.chordal_voice = True
		self.part_name = "bass"

		self.logger = logging.getLogger("bass")
		voice_handler = logging.FileHandler("logs/bass.log", mode='w')
		voice_handler.setLevel(logging.WARNING)
		voice_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		voice_handler.setFormatter(voice_format)
		self.logger.addHandler(voice_handler)


class Tenor(Voice):

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[1]
		self.midi_notes = Voice.midi_score[2]

		self.chordal_voice = True
		self.part_name = "tenor"

		self.logger = logging.getLogger("tenor")
		voice_handler = logging.FileHandler("logs/tenor.log", mode='w')
		voice_handler.setLevel(logging.WARNING)
		voice_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		voice_handler.setFormatter(voice_format)
		self.logger.addHandler(voice_handler)

class Alto(Voice):

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[2]
		self.midi_notes = Voice.midi_score[3]

		self.chordal_voice = True
		self.part_name = "alto"

		self.logger = logging.getLogger("alto")
		voice_handler = logging.FileHandler("logs/alto.log", mode='w')
		voice_handler.setLevel(logging.WARNING)
		voice_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		voice_handler.setFormatter(voice_format)
		self.logger.addHandler(voice_handler)

class Soprano(Voice):

	def __init__(self):
		self.sheet_notes = []
		self.unnested_scale_degrees = Voice.chorale_scale_degrees[3]
		self.midi_notes = Voice.midi_score[4]

		self.chordal_voice = True
		self.part_name = "soprano"

		self.logger = logging.getLogger("soprano")
		voice_handler = logging.FileHandler("logs/soprano.log", mode='w')
		voice_handler.setLevel(logging.WARNING)
		voice_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		voice_handler.setFormatter(voice_format)
		self.logger.addHandler(voice_handler)








