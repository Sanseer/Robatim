from generate.voices.voice import Voice
from generate.idioms import basics as idms_b

class VoiceLeadMixin():

	def is_voice_lead(self, t_pitch, a_pitch, s_pitch):
		"""Checks counterpoint and voice leading"""
		
		b_pitch = Voice.bass_pitches[self.note_index]
		if not b_pitch <= t_pitch <= a_pitch <= s_pitch:
			return False
		elif (a_pitch - t_pitch) > 12 or (s_pitch - a_pitch) > 12:
			# print("Keep adjacent upper voices within an octave")
			return False

		full_scale_combo = ((self.make_scale_pitch(b_pitch), 
		self.make_scale_pitch(t_pitch),
		self.make_scale_pitch(a_pitch), self.make_scale_pitch(s_pitch)))
		if len(set(full_scale_combo)) == 1:
			return False
		elif (full_scale_combo.count(11) >= 2 and 
		  Voice.chromatics[self.note_index] not in {"2Dom", "2Dim"}):
			# print("Don't repeat leading tone except modulation", end=" ")
			return False
		elif (self.is_seventh_chord() and 
		  full_scale_combo.count(self.chord_degree_to_pitch(3, 0)) >= 2):
			# print("Don't repeat chordal 7th", end=" ")
			return False
		elif self.chord_degree_to_pitch(0) not in full_scale_combo:
			return False
		elif self.chord_degree_to_pitch(1) not in full_scale_combo:
			return False
		elif self.is_seventh_chord() and (len(set(full_scale_combo)) < 3 or
		  self.chord_degree_to_pitch(3) not in full_scale_combo):
			return False

		bass_soprano_intervals = self.bass_soprano_intervals[:]
		bass_soprano_intervals.append(self.get_interval(b_pitch, s_pitch))
		if (self.note_index == 0 and 
		  bass_soprano_intervals[-1] not in {"P5", "P8", "M3", "m3"}):
			return False

		current_chord = self.get_chord()
		if (self.chord_degree_to_pitch(2) not in full_scale_combo and 
		  current_chord != idms_b.V7 and 
		  current_chord not in Voice.idms_mode.consonant_triads): 
			return False
		if self.note_index == 0:
			return True
		elif current_chord == idms_b.I64 and full_scale_combo.count(2) >= 2:
			return False

		tenor_motion = Voice.tenor_motion[:]
		alto_motion = Voice.alto_motion[:]
		soprano_motion = Voice.soprano_motion[:]

		self.add_voice_motion(soprano_motion, 2, s_pitch)
		self.add_voice_motion(alto_motion, 1, a_pitch)
		self.add_voice_motion(tenor_motion, 0, t_pitch)

		composite_motion = [tenor_motion, alto_motion, soprano_motion]
		previous_chord = self.get_chord(-1)
		for voice_index, new_pitch in enumerate((t_pitch, a_pitch, s_pitch)):
			old_pitch = self.pitch_amounts[self.note_index - 1][voice_index]
			old_scale_pitch = self.make_scale_pitch(old_pitch)
			new_scale_pitch = self.make_scale_pitch(new_pitch)
			if abs(new_pitch - old_pitch) > 12:
				# print("Leap too wide", end=" ")
				return False
			elif (old_scale_pitch == 11 and 
			  new_scale_pitch not in {11, 0} and
			  not Voice.chromatics[self.note_index] not in {"2Dom", "2Dim"} and 
			  not Voice.chromatics[self.note_index - 1] not in {"2Dom", "2Dim"}):
				if previous_chord not in {idms_b.V, idms_b.V7}:
					return False
				elif previous_chord == idms_b.V and new_scale_pitch not in {7,3,4}:
					return False
				elif previous_chord == idms_b.V7 and new_scale_pitch != 7:
					return False
			if (self.note_index > 1 and
			  abs(old_pitch - self.pitch_amounts[self.note_index - 2][voice_index]) > 5 
			  and (abs(new_pitch - old_pitch) > 2 or 
			  composite_motion[voice_index][-1] == 
			  composite_motion[voice_index][-2])):
				# print("Leaps must be followed by contrary steps")
				return False
			elif (new_scale_pitch in {8,11} and old_scale_pitch in {8,11}
			and new_pitch != old_pitch and self.mode == "aeolian" 
			and not Voice.chromatics[self.note_index]
			and not Voice.chromatics[self.note_index - 1]):
			# No melodic augmented 2nd
				return False
			if (self.is_seventh_chord(-1) and 
			  old_scale_pitch == self.chord_degree_to_pitch(3, -1)):
				inversion = self.is_chord_inversion(current_chord, previous_chord)
				# the chordal 7th is always included by earlier rules
				# make variables of repeated conditionals
				pitch_change = new_pitch - old_pitch
				if (not -2 <= pitch_change < 0 and not inversion and
				  (current_chord != idms_b.VII6 or not 
				  self.is_chord_inversion(idms_b.V7, previous_chord)) and
				  (previous_chord != idms_b.V43 or current_chord != idms_b.I6)):
					return False
				elif (0 < pitch_change <= 2 and not inversion and
				  (current_chord != idms_b.VII6 or not
				  self.is_chord_inversion(idms_b.V7, previous_chord)) and
				  (previous_chord != idms_b.V43 or current_chord != idms_b.I6)):
					return False
			if (previous_chord == idms_b.I64 and old_scale_pitch == 0 
			  and new_scale_pitch != 11):
				return False 

		if (self.is_chord_inversion(current_chord, previous_chord) and 
		  composite_motion[0][-1] == composite_motion[1][-1] == 
		  composite_motion[2][-1] == 0 and 
		  (not self.is_seventh_chord()  or not self.is_seventh_chord(-1))):
			return False

		bass_soprano_motion = self.bass_soprano_motion[:]
		self.add_motion_type(Voice.bass_motion, soprano_motion, 
			bass_soprano_motion, bass_soprano_intervals)
		old_soprano_note = self.pitch_amounts[self.note_index - 1][2]

		# third to last note of cadence should not be huge leap (greater than perfect 5th?)
		if ((self.note_index == len(self.pitch_amounts) - 1) and 
		  (bass_soprano_motion[-1] != "Contrary" or 
		  bass_soprano_intervals[-1] != "P8" or
		  abs(s_pitch - old_soprano_note) > 2)):
			# print("Must end with contrary motion and tonic by step")
			return False
		elif (bass_soprano_intervals[-1] == "P8" and
		self.note_index not in {Voice.idea1_length + Voice.idea2_length - 1, 
			Voice.idea1_length + Voice.idea2_length, len(self.pitch_amounts) - 1}):
			# print("Avoiding premature unison")
			return False
		elif ("P" in bass_soprano_intervals[-1] and 
		  "P" in bass_soprano_intervals[-2]):
			# print("Double perfects")
			return False
		elif (bass_soprano_motion[-1] == "Similar" and 
		  "P8" in bass_soprano_intervals[-1] and 
		  abs(s_pitch - old_soprano_note) > 2):
			# print("No hidden octaves except soprano moving by step")
			return False
		elif (self.note_index == Voice.idea1_length + Voice.idea2_length - 1 and
		  abs(s_pitch - old_soprano_note) > 4):
			return False

		bass_tenor_motion = self.bass_tenor_motion[:]
		bass_alto_motion = self.bass_alto_motion[:]
		tenor_alto_motion = self.tenor_alto_motion[:]
		tenor_soprano_motion = self.tenor_soprano_motion[:]
		alto_soprano_motion = self.alto_soprano_motion[:]

		bass_tenor_intervals = self.bass_tenor_intervals[:]
		bass_alto_intervals = self.bass_alto_intervals[:]
		tenor_alto_intervals = self.tenor_alto_intervals[:]
		tenor_soprano_intervals = self.tenor_soprano_intervals[:]
		alto_soprano_intervals = self.alto_soprano_intervals[:]

		tenor_alto_intervals.append(self.get_interval(t_pitch, a_pitch))
		tenor_soprano_intervals.append(self.get_interval(t_pitch, s_pitch))
		alto_soprano_intervals.append(self.get_interval(a_pitch, s_pitch))
		bass_tenor_intervals.append(self.get_interval(b_pitch, t_pitch))
		bass_alto_intervals.append(self.get_interval(b_pitch, a_pitch))

		self.add_motion_type(Voice.bass_motion, tenor_motion, 
			bass_tenor_motion, bass_tenor_intervals)
		self.add_motion_type(Voice.bass_motion, alto_motion, 
			bass_alto_motion, bass_alto_intervals)
		self.add_motion_type(tenor_motion, alto_motion,
			tenor_alto_motion, tenor_alto_intervals)
		self.add_motion_type(tenor_motion, soprano_motion,
			tenor_soprano_motion, tenor_soprano_intervals),
		self.add_motion_type(alto_motion, soprano_motion,
			alto_soprano_motion, alto_soprano_intervals)

		composite_intervals = [bass_tenor_intervals, bass_alto_intervals, 
			bass_soprano_intervals, tenor_alto_intervals, 
			tenor_soprano_intervals,alto_soprano_intervals]
		composite_movements = [bass_tenor_motion, bass_alto_motion, 
			bass_soprano_motion, tenor_alto_motion, tenor_soprano_motion,
			alto_soprano_motion]

		for interval_list, motion_list in zip(
		composite_intervals, composite_movements):
			if (interval_list[-1] in {"P5","P8"} and 
			  motion_list[-1] == "Parallel"):
				return False
			# seventh chord inversions can delay resolution. double neighbor
			elif (interval_list[-2] == "A4" and 
			  interval_list[-1] not in {"M6", "m6"}):
				if (previous_chord not in 
				  {idms_b.VII6, idms_b.V43, idms_b.II, idms_b.II6}):
					return False
				elif (previous_chord in {idms_b.VII6, idms_b.V43} and 
				  (current_chord not in {idms_b.I, idms_b.I6} or 
				  interval_list[-1] != "P4")):
					return False
				elif (previous_chord in {idms_b.II, idms_b.II6} and 
				  (current_chord not in {idms_b.V, idms_b.V7} or 
				  interval_list[-1] != "P5" or self.mode == "ionian")):
					return False
			if (interval_list[-2] == "d5" and 
			  interval_list[-1] not in {"M3", "m3"}):
				if (previous_chord not in 
				  {idms_b.VII6, idms_b.V43, idms_b.II, idms_b.II6}):
					return False
				elif (previous_chord in {idms_b.VII6, idms_b.V43} and 
				  (current_chord != idms_b.I6 or interval_list[-1] != "P5")):
					return False
				elif (previous_chord in {idms_b.II, idms_b.II6} and
				  (current_chord not in {idms_b.V, idms_b.V7} or
				  interval_list[-1] != "P4" or self.mode == "ionian")):
					return False
			if interval_list[-2] == "d7" and interval_list[-1] != "P5":
				return False
			elif interval_list[-2] == "A2" and interval_list[-1] != "P4":
				return False
			elif (interval_list[-2] in idms_b.harmonic_dissonance and
			  interval_list[-1] in idms_b.harmonic_dissonance and 
			  interval_list[-1] != interval_list[-2]):
				return False
			elif (interval_list[-1] == "P8" and motion_list[-1] == "Similar"
			and current_chord in {idms_b.I, idms_b.I6} 
			and self.is_chord_inversion(idms_b.V7, previous_chord)):
				return False 

			# can you sustain a dissonant interval before resolving into consonance
			# seventh chords, perhaps?
		return True