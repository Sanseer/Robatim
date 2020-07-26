import unittest
import main as robatim

class TestScore(unittest.TestCase):

	def test_pitch_creation(self):

		new_pitch = robatim.Pitch("C")
		self.assertEqual(new_pitch.pitch_letter, "C")
		self.assertEqual(new_pitch.accidental_symbol, "")
		self.assertEqual(new_pitch.accidental_amount, 0)
		self.assertEqual(str(new_pitch), "C")

		new_pitch = robatim.Pitch("G#")
		self.assertEqual(new_pitch.pitch_letter, "G")
		self.assertEqual(new_pitch.accidental_symbol, "#")
		self.assertEqual(new_pitch.accidental_amount, 1)
		self.assertEqual(str(new_pitch), "G#")

		new_pitch = robatim.Pitch("Dbb")
		self.assertEqual(new_pitch.pitch_letter, "D")
		self.assertEqual(new_pitch.accidental_symbol, "bb")
		self.assertEqual(new_pitch.accidental_amount, -2)
		self.assertEqual(str(new_pitch), "Dbb")

	def test_pitch_letter_change(self):

		new_pitch = robatim.Pitch("C")
		self.assertEqual(str(new_pitch.change_pitch_letter(-1)), "B#")
		new_pitch = robatim.Pitch("B##")
		self.assertEqual(str(new_pitch.change_pitch_letter(0)), "B##")
		new_pitch = robatim.Pitch("E#")
		self.assertEqual(str(new_pitch.change_pitch_letter(1)), "F")

		new_pitch = robatim.Pitch("Fbb")
		self.assertEqual(str(new_pitch.change_pitch_letter(-1)), "Eb")
		new_pitch = robatim.Pitch("G#")
		self.assertEqual(str(new_pitch.change_pitch_letter(1)), "Ab")
		new_pitch = robatim.Pitch("Db")
		self.assertEqual(str(new_pitch.change_pitch_letter(-1)), "C#")

		new_pitch = robatim.Pitch("A#")
		self.assertEqual(str(new_pitch.change_pitch_letter(2)), "Cbb")
		new_pitch = robatim.Pitch("Fb")
		self.assertEqual(str(new_pitch.change_pitch_letter(-3)), "C####")

	def test_note_letter_change(self):

		new_note = robatim.Note("C4")
		self.assertEqual(str(new_note.change_pitch_letter(-1)), "B#3")
		new_note = robatim.Note("B##2")
		self.assertEqual(str(new_note.change_pitch_letter(0)), "B##2")
		new_note = robatim.Note("E#5")
		self.assertEqual(str(new_note.change_pitch_letter(1)), "F5")

		new_note = robatim.Note("Fbb3")
		self.assertEqual(str(new_note.change_pitch_letter(-1)), "Eb3")
		new_note = robatim.Note("G#0")
		self.assertEqual(str(new_note.change_pitch_letter(1)), "Ab0")
		new_note = robatim.Note("Db4")
		self.assertEqual(str(new_note.change_pitch_letter(-1)), "C#4")

		new_note = robatim.Note("A#6")
		self.assertEqual(str(new_note.change_pitch_letter(2)), "Cbb7")
		new_note = robatim.Note("Fb5")
		self.assertEqual(str(new_note.change_pitch_letter(-3)), "C####5")

	def test_pitch_accidental_change(self):

		new_pitch = robatim.Pitch("D#")
		self.assertEqual(str(new_pitch.change_pitch_accidental(-2)), "Db")
		new_pitch = robatim.Pitch("A")
		self.assertEqual(str(new_pitch.change_pitch_accidental(0)), "A")
		new_pitch = robatim.Pitch("Fb")
		self.assertEqual(str(new_pitch.change_pitch_accidental(3)), "F##")
		new_pitch = robatim.Pitch("B#")
		self.assertEqual(str(new_pitch.change_pitch_accidental(-1)), "B")

	def test_note_accidental_change(self):

		new_note = robatim.Note("D#4")
		self.assertEqual(str(new_note.change_pitch_accidental(-2)), "Db4")
		new_note = robatim.Note("A0")
		self.assertEqual(str(new_note.change_pitch_accidental(0)), "A0")
		new_note = robatim.Note("Fb5")
		self.assertEqual(str(new_note.change_pitch_accidental(3)), "F##5")
		new_note = robatim.Note("B#3")
		self.assertEqual(str(new_note.change_pitch_accidental(-1)), "B3")	

	def test_pitch_shift(self):

		new_pitch = robatim.Pitch("G")
		self.assertEqual(str(new_pitch.shift(1, 3)), "A#")
		new_pitch = robatim.Pitch("E")
		self.assertEqual(str(new_pitch.shift(-2, -2)), "C##")
		new_pitch = robatim.Pitch("F#")
		self.assertEqual(str(new_pitch.shift(3, 5)), "B")

		new_pitch = robatim.Pitch("Db")
		self.assertEqual(str(new_pitch.shift(0, 0)), "Db")
		new_pitch = robatim.Pitch("C##")
		self.assertEqual(str(new_pitch.shift(-2, -3)), "A##")
		new_pitch = robatim.Pitch("Ab")
		self.assertEqual(str(new_pitch.shift(-1, 0)), "G#")

	def test_note_shift(self):

		new_note = robatim.Note("G2")
		self.assertEqual(str(new_note.shift(1, 3)), "A#2")
		new_note = robatim.Note("E3")
		self.assertEqual(str(new_note.shift(-2, -2)), "C##3")
		new_note = robatim.Note("F#6")
		self.assertEqual(str(new_note.shift(3, 5)), "B6")

		new_note = robatim.Note("Db0")
		self.assertEqual(str(new_note.shift(0, 0)), "Db0")
		new_note = robatim.Note("C##4")
		self.assertEqual(str(new_note.shift(-2, -3)), "A##3")
		new_note = robatim.Note("Ab7")
		self.assertEqual(str(new_note.shift(-1, 0)), "G#7")

	def test_scale_degrees(self):
		
		chosen_scale_obj = robatim.Engraver.scale_obj = robatim.Scale("Ab") 
		scale_sequence = ("Ab", "Bb", "C", "Db", "Eb", "F", "G")

		self.assertTrue(chosen_scale_obj.is_note_diatonic(48))
		self.assertTrue(chosen_scale_obj.is_note_diatonic(68))
		self.assertTrue(chosen_scale_obj.is_note_diatonic(7))
		self.assertTrue(chosen_scale_obj.is_note_diatonic(25))

		chosen_note = robatim.Note(10)
		self.assertEqual(chosen_scale_obj.get_absolute_degree(chosen_note), 1)
		chosen_note = robatim.Note(41)
		self.assertEqual(chosen_scale_obj.get_absolute_degree(chosen_note), 5)
		chosen_note = robatim.Note(87)
		self.assertEqual(chosen_scale_obj.get_absolute_degree(chosen_note), 4)

	def test_scale_pitches(self):

		def analyze_scale_members(chosen_scale_obj, scale_sequence):
			for scale_pitch in chosen_scale_obj.scale_pitches_seq:
				self.assertIn(str(scale_pitch), scale_sequence)

		scale_members = {
			("G", "ionian"): ("G", "A", "B", "C", "D", "E", "F#"), 
			("C", "aeolian"): ("C", "D", "Eb", "F", "G", "Ab", "Bb"),
			("D", "dorian"): ("D", "E", "F", "G", "A", "B", "C"),
			("G#", "ionian"): ("G#", "A#", "B#", "C#", "D#", "E#", "F##"),
		}
		for scale_parameters, scale_sequence in scale_members.items():
			analyze_scale_members(robatim.Scale(*scale_parameters), scale_sequence)

	def test_chord_pitches(self):

		def check_chord(chord_symbol, chord_pitch_names):
			new_chord = robatim.Chord(chord_symbol, 0)
			pitch_str_sequence = []
			for chord_pitch in new_chord.pitches:
				pitch_str_sequence.append(str(chord_pitch))
			self.assertEqual(chord_pitch_names, pitch_str_sequence)

		robatim.Engraver.scale_obj = robatim.Scale("Bb", "ionian")
		check_chord("I", ["Bb", "D", "F"])
		check_chord("V7", ["F", "A", "C", "Eb"])
		check_chord("II6", ["C", "Eb", "G"])
		check_chord("VI", ["G", "Bb", "D"])

		robatim.Engraver.scale_obj = robatim.Scale("F#", "aeolian")
		check_chord("I", ["F#", "A", "C#"])
		check_chord("IV6/5", ["B", "D", "F#", "A"])
		check_chord("VII", ["E", "G#", "B"])
		check_chord("I6/4", ["F#", "A", "C#"])

	def test_scalar_shift(self):

		robatim.Engraver.scale_obj = robatim.Scale("G", "lydian")
		starting_note = robatim.Note("G4")
		self.assertEqual(str(starting_note.scalar_shift(1)), "A4")
		self.assertEqual(str(starting_note.scalar_shift(-1)), "F#4")
		self.assertEqual(str(starting_note.scalar_shift(9)), "B5")
		self.assertEqual(str(starting_note.scalar_shift(-11	)), "C#3")

		robatim.Engraver.scale_obj = robatim.Scale("F", "phrygian")
		starting_note = robatim.Note("F3")
		self.assertEqual(str(starting_note.scalar_shift(5)), "Db4")
		self.assertEqual(str(starting_note.scalar_shift(0)), "F3")
		self.assertEqual(str(starting_note.scalar_shift(-5)), "Ab2")
		self.assertEqual(str(starting_note.scalar_shift(14)), "F5")

	def test_interval_shift(self):

		new_interval = robatim.Interval("P", 0)
		altered_interval = new_interval.shift_interval_quality(1)
		self.assertEqual(str(altered_interval), "A1")
		new_interval = robatim.Interval("m", 1)
		altered_interval = new_interval.shift_interval_quality(0)
		self.assertEqual(str(altered_interval), "m2")
		new_interval = robatim.Interval("A", 6)
		altered_interval = new_interval.shift_interval_quality(-1)
		self.assertEqual(str(altered_interval), "M7")

		new_interval = robatim.Interval.create_from_symbol("A5")
		altered_interval = new_interval.shift_interval_quality(-2)
		self.assertEqual(str(altered_interval), "d5")
		new_interval = robatim.Interval.create_from_symbol("dd4")
		altered_interval = new_interval.shift_interval_quality(-1)
		self.assertEqual(str(altered_interval), "ddd4")
		new_interval = robatim.Interval.create_from_symbol("M3")
		altered_interval = new_interval.shift_interval_quality(2)
		self.assertEqual(str(altered_interval), "AA3")

	def test_interval_input(self):
		
		self.assertRaises(ValueError, robatim.Interval, "d", 0)
		self.assertRaises(ValueError, robatim.Interval, "M", 4)
		self.assertRaises(ValueError, robatim.Interval, "P", -1)

		self.assertRaises(ValueError, robatim.Interval, "MM", 15)
		self.assertRaises(ValueError, robatim.Interval, "m", -11)
		self.assertRaises(ValueError, robatim.Interval, "PP", 0)

	def test_note_subtraction(self):

		self.assertEqual(str(robatim.Note("A2") - robatim.Note("A3")), "P8")
		self.assertEqual(str(robatim.Note("Fbb1") - robatim.Note("Fbb1")), "P1")
		self.assertEqual(str(robatim.Note("B5") - robatim.Note("B#5")), "A1")
		self.assertEqual(str(robatim.Note("G#5") - robatim.Note("Gb5")), "AA1")

		self.assertEqual(str(robatim.Note("E4") - robatim.Note("C4")), "M3")
		self.assertEqual(str(robatim.Note("Db4")- robatim.Note("G3")), "d5")
		self.assertEqual(str(robatim.Note("G2") - robatim.Note("F3")), "m7")
		self.assertEqual(str(robatim.Note("Ab4") - robatim.Note("D5")), "A4")

		self.assertEqual(str(robatim.Note("Fb5") - robatim.Note("C##4")), "ddd11")
		self.assertEqual(str(robatim.Note("D1") - robatim.Note("E#2")), "A9")
		self.assertEqual(str(robatim.Note("B3") - robatim.Note("F#6")), "P19")

	def test_slope_finder(self):
		 self.assertEqual(
		 	robatim.find_slopes([0, 1, 2, 1, 0]), [[0, 1, 2], [2, 1, 0]]
		 )
		 self.assertEqual(
		 	robatim.find_slopes([-1, 2, 3, 4, 1, 0, 2, 5]),
		 	[[-1, 2, 3, 4], [4, 1, 0], [0, 2, 5]]
		 )
		 self.assertEqual(
		 	robatim.find_slopes([4, 4, 3, 3, 2, 2, 0]),
		 	[[4, 4, 3, 3, 2, 2, 0]]
		 )
		 self.assertEqual(
		 	robatim.find_slopes([4, 2, 2, 0, 1, -1, 0, 0]),
		 	[[4, 2, 2, 0], [0, 1], [1, -1], [-1, 0, 0]]
		 )


if __name__ == "__main__":
	unittest.main() 