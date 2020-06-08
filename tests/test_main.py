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

	def test_scale_degrees(self):
		chosen_scale_obj = robatim.Engraver.scale_obj = robatim.Scale("Ab") 
		scale_sequence = ("Ab", "Bb", "C", "Db", "Eb", "F", "G")

		self.assertTrue(chosen_scale_obj.is_note_diatonic(48))
		self.assertTrue(chosen_scale_obj.is_note_diatonic(68))
		self.assertTrue(chosen_scale_obj.is_note_diatonic(7))
		self.assertTrue(chosen_scale_obj.is_note_diatonic(25))

		chosen_note = robatim.Note(10)
		self.assertEqual(chosen_scale_obj.get_degree(chosen_note), 1)
		chosen_note = robatim.Note(41)
		self.assertEqual(chosen_scale_obj.get_degree(chosen_note), 5)
		chosen_note = robatim.Note(87)
		self.assertEqual(chosen_scale_obj.get_degree(chosen_note), 4)

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


if __name__ == "__main__":
	unittest.main() 