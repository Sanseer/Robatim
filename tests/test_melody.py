import unittest

import tests.melody_frame as mf

class MelodyTester(unittest.TestCase):

	def test_long_rest(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_long_rest(melody_obj))

	def test_halfway_pause(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_halfway_pause(melody_obj))

	def test_move_from_tonic(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_move_from_tonic(melody_obj))

	def test_leaps_within_octave(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_leaps_within_octave(melody_obj))

	def test_end_leap(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_end_leap(melody_obj))

	def test_predominant_descent(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_predominant_descent(melody_obj))

	def test_octave_leap(self):
		for melody_obj in mf.melodies:
			self.assertTrue(mf.test_octave_leap(melody_obj))


if __name__ == "__main__":
	unittest.main()