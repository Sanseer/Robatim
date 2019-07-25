from generate.voices.voice import Voice
from generate.idioms import basics as idms_b

class VoiceLeadMixin():

	def is_voice_lead(self, t_pitch, a_pitch):
		"""Checks counterpoint and voice leading"""

		b_pitch = Voice.bass_pitches[self.note_index]
		if not b_pitch <= t_pitch <= a_pitch:
			return False

		soprano_pitch_choices = [
			pitch for pitch in self.all_pitches if pitch >= a_pitch
		]
		soprano_scale_choices = {
			self.make_scale_pitch(pitch) for pitch in soprano_pitch_choices
		}
		chord_scale_combo = (
			self.make_scale_pitch(b_pitch), self.make_scale_pitch(t_pitch),
			self.make_scale_pitch(a_pitch)
		)

		if self.chord_degree_to_pitch(0) in chord_scale_combo:
			chordal_root = True
		else:
			chordal_root = False
		if self.chord_degree_to_pitch(0) in soprano_scale_choices:
			melodic_root = True
		else:
			melodic_root = False
		if not chordal_root and not melodic_root:
			return False
		if self.chord_degree_to_pitch(1) in chord_scale_combo:
			chordal_third = True
		else:
			chordal_third = False
		if self.chord_degree_to_pitch(1) in soprano_scale_choices:
			melodic_third = True
		else:
			melodic_third = False
		if not chordal_third and not melodic_third:
			return False
		if not chordal_root and not chordal_third:
			return False
		if self.chord_degree_to_pitch(2) in chord_scale_combo:
			chordal_fifth = True
		else:
			chordal_fifth = False
		if self.chord_degree_to_pitch(2) in soprano_scale_choices:
			melodic_fifth = True
		else:
			melodic_fifth = False
		current_chord = self.get_chord()
		if self.is_seventh_chord():
			if self.chord_degree_to_pitch(3) in chord_scale_combo:
				chordal_seventh = True
			else:
				chordal_seventh = False
			if not chordal_root and not chordal_seventh:
				return False
			elif not chordal_third and not chordal_seventh:
				return False 
			if self.chord_degree_to_pitch(3) in soprano_scale_choices:
				melodic_seventh = True
			else:
				melodic_seventh = False
			if not chordal_seventh and not melodic_seventh:
				return False
			if current_chord != idms_b.V7:
				if not chordal_fifth and not melodic_fifth:
					return False
				elif not chordal_root and not chordal_fifth:
					return False
				elif not chordal_third and not chordal_fifth:
					return False
				if not chordal_fifth and not chordal_seventh:
					return False
		else:
			if current_chord not in Voice.idms_mode.consonant_triads:
				if not chordal_fifth and not melodic_fifth:
					return False
				elif not chordal_root and not chordal_fifth:
					return False
				elif not chordal_third and not chordal_fifth:
					return False

		if self.note_index == 0:
			return True
		if (self.note_index == self.sequence_length - 1 and 
		  (not melodic_root or not chordal_third)):
			return False
		elif current_chord == idms_b.I64: 
			if chord_scale_combo.count(0) >= 2:
				return False

		tenor_motion = Voice.tenor_motion[:]
		alto_motion = Voice.alto_motion[:]

		self.add_voice_motion(alto_motion, 1, a_pitch)
		self.add_voice_motion(tenor_motion, 0, t_pitch)

		composite_motion = [tenor_motion, alto_motion]

		for voice_index, new_pitch in enumerate((t_pitch, a_pitch)):
			old_pitch = self.lower_voice_pitches[self.note_index - 1][voice_index]
			old_scale_pitch = self.make_scale_pitch(old_pitch)
			new_scale_pitch = self.make_scale_pitch(new_pitch)

			if abs(new_pitch - old_pitch) > 12:
				return False
			# a leap can delay its eventual opposite motion by keeping the same pitch.
			if (self.note_index > 1 and
			  abs(old_pitch - self.lower_voice_pitches[self.note_index - 2][voice_index]) > 5 
			  and (abs(new_pitch - old_pitch) > 2 or 
			  composite_motion[voice_index][-1] == 
			  composite_motion[voice_index][-2])):
				# print("Leaps must be followed by contrary steps")
				return False
			elif (new_scale_pitch in {8,11} and old_scale_pitch in {8,11}
			and new_scale_pitch != old_scale_pitch and self.mode == "aeolian" 
			and not Voice.chromatics[self.note_index]
			and not Voice.chromatics[self.note_index - 1]):
			# No melodic augmented 2nd
				return False

		bass_tenor_motion = self.bass_tenor_motion[:]
		bass_alto_motion = self.bass_alto_motion[:]
		tenor_alto_motion = self.tenor_alto_motion[:]

		bass_tenor_intervals = self.bass_tenor_intervals[:]
		bass_alto_intervals = self.bass_alto_intervals[:]
		tenor_alto_intervals = self.tenor_alto_intervals[:]

		tenor_alto_intervals.append(self.get_interval(t_pitch, a_pitch))
		bass_tenor_intervals.append(self.get_interval(b_pitch, t_pitch))
		bass_alto_intervals.append(self.get_interval(b_pitch, a_pitch))

		self.add_motion_type(Voice.bass_motion, tenor_motion, 
			bass_tenor_motion, bass_tenor_intervals)
		self.add_motion_type(Voice.bass_motion, alto_motion, 
			bass_alto_motion, bass_alto_intervals)
		self.add_motion_type(tenor_motion, alto_motion,
			tenor_alto_motion, tenor_alto_intervals)

		composite_intervals = [bass_tenor_intervals, bass_alto_intervals, 
			tenor_alto_intervals]
		composite_movements = [bass_tenor_motion, bass_alto_motion, 
			tenor_alto_motion]

		for interval_list, motion_list in zip(
		composite_intervals, composite_movements):
			if (interval_list[-1] in {"P5","P8"} and 
			  motion_list[-1] == "Parallel"):
				return False
			elif "P" in interval_list[-1] and "P" in interval_list[-2]:
				return False

		# avoid voice overlap
		# consider resolution of chordal 7th
		# consider modal interchange
		# melodic minor
		return True