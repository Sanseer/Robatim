import unittest

import tests.melody_frame as mf

class MakeSongMethods(unittest.TestCase):

	def test_melody(self):

		melody_rules = (
			mf.test_long_rest, mf.test_triple_repeat, mf.test_double_repeat, 
			mf.test_leaps_within_octave, mf.test_end_leap, 
			mf.test_predominant_descent, mf.test_octave_leap, mf.test_proper_leaps,
			mf.test_nested_climaxes, mf.test_late_melodic_jukes, 
			mf.test_unnested_climaxes
		)

		for melody_obj in mf.melodies:
			print(melody_obj)
			for test_melody_rule in melody_rules:
				print(test_melody_rule.__name__)
				self.assertTrue(test_melody_rule(melody_obj))


if __name__ == "__main__":
	unittest.main()



