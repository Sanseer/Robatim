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


if __name__ == "__main__":
	unittest.main() 