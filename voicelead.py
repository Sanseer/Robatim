from voice import Voice

class VoiceLeadMixin():

	def is_voice_lead(self, t_pitch, a_pitch, s_pitch):

		b_pitch = Voice.bass_pitches[self.note_index]
		full_scale_combo = ((self.make_scale_pitch(b_pitch), 
		self.make_scale_pitch(t_pitch),
		self.make_scale_pitch(a_pitch), self.make_scale_pitch(s_pitch)))

		bass_soprano_intervals = self.bass_soprano_intervals[:]
		bass_soprano_intervals.append(self.get_interval(b_pitch, s_pitch))

		if len(set(full_scale_combo)) == 1:
			return False
		elif (a_pitch - t_pitch) > 12 or (s_pitch - a_pitch) > 12:
			# print("Keep adjacent upper voices within an octave")
			return False
		if self.note_index == 0:
			return True

		tenor_motion = Voice.tenor_motion[:]
		alto_motion = Voice.alto_motion[:]
		soprano_motion = Voice.soprano_motion[:]

		self.add_voice_motion(soprano_motion, 2, s_pitch)
		self.add_voice_motion(alto_motion, 1, a_pitch)
		self.add_voice_motion(tenor_motion, 0, t_pitch)

		for voice_index, new_pitch in enumerate((t_pitch, a_pitch, s_pitch)):
			old_pitch = self.pitch_amounts[self.note_index - 1][voice_index]
			if abs(new_pitch - old_pitch) > 12:
				# print("Leap too wide", end=" ")
				return False

		bass_soprano_motion = self.bass_soprano_motion[:]
		self.add_motion_type(Voice.bass_motion, soprano_motion, 
			bass_soprano_motion, bass_soprano_intervals)
		old_soprano_note = self.pitch_amounts[self.note_index - 1][2]

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
			if (interval_list[-1] in ("P5","P8") and 
			  motion_list[-1] == "Parallel"):
				return False

		return True