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
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, -1)), "B#")
		new_pitch = robatim.Pitch("B##")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, 0)), "B##")
		new_pitch = robatim.Pitch("E#")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, 1)), "F")

		new_pitch = robatim.Pitch("Fbb")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, -1)), "Eb")
		new_pitch = robatim.Pitch("G#")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, 1)), "Ab")
		new_pitch = robatim.Pitch("Db")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, -1)), "C#")

		new_pitch = robatim.Pitch("A#")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, 2)), "Cbb")
		new_pitch = robatim.Pitch("Fb")
		self.assertEqual(str(new_pitch.change_pitch_letter(new_pitch, -3)), "C####")

	def test_pitch_accidental_change(self):

		new_pitch = robatim.Pitch("D#")
		self.assertEqual(str(new_pitch.change_pitch_accidental(new_pitch, -2)), "Db")
		new_pitch = robatim.Pitch("A")
		self.assertEqual(str(new_pitch.change_pitch_accidental(new_pitch, 0)), "A")
		new_pitch = robatim.Pitch("Fb")
		self.assertEqual(str(new_pitch.change_pitch_accidental(new_pitch, 3)), "F##")
		new_pitch = robatim.Pitch("B#")
		self.assertEqual(str(new_pitch.change_pitch_accidental(new_pitch, -1)), "B")

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
		self.assertEqual(str(new_pitch.shift(0, -2)), "C")
		new_pitch = robatim.Pitch("Ab")
		self.assertEqual(str(new_pitch.shift(-1, 0)), "G#")

	def test_scale_pitches(self):
		chosen_scale_obj = robatim.Scale("Ab") 
		scale_sequence = ("Ab", "Bb", "C", "Db", "Eb", "F", "G")

		def analyze_scale_members(chosen_scale_obj, scale_sequence):
			for scale_pitch in chosen_scale_obj.scale_pitches:
				self.assertIn(str(scale_pitch), scale_sequence)

		analyze_scale_members(chosen_scale_obj, scale_sequence)

		scale_members = {
			("G", "ionian"): ("G", "A", "B", "C", "D", "E", "F#"), 
			("C", "aeolian"): ("C", "D", "Eb", "F", "G", "Ab", "Bb"),
			("D", "dorian"): ("D", "E", "F", "G", "A", "B", "C"),
			("G#", "ionian"): ("G#", "A#", "B#", "C#", "D#", "E#", "F##"),
		}
		for scale_parameters, scale_sequence in scale_members.items():
			analyze_scale_members(robatim.Scale(*scale_parameters), scale_sequence)


if __name__ == "__main__":
	unittest.main() 