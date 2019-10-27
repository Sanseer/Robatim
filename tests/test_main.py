import unittest
import json
import time
from fractions import Fraction

import requests

from generate.voices.voice import Voice 


class MainSongMethods(unittest.TestCase):

	def test_output_pdf(self):
		payload = {
			"version": "stable", "code": "{ c d e }", "id": ""
		}
		# AWS can't parse python dictionaries
		sheet_music_response = requests.post(
			"https://7icpm9qr6a.execute-api.us-west-2.amazonaws.com/prod/prepare_preview/stable", data=payload)
		self.assertFalse(sheet_music_response.status_code == 200)

		time.sleep(1)

		with open("payload.json", 'w') as f:
			json.dump(payload, f)
		with open("payload.json", 'rb')  as f:
			sheet_music_response = requests.post(
				"https://7icpm9qr6a.execute-api.us-west-2.amazonaws.com/prod/prepare_preview/stable", data=f)
		self.assertTrue(sheet_music_response.status_code == 200)

		time.sleep(1)

		response_id = sheet_music_response.json()["id"]
		pdf_response = requests.get(
			f"https://s3-us-west-2.amazonaws.com/lilybin-scores/{response_id}.pdf")
		self.assertTrue(pdf_response.status_code == 200)

	def test_motifs(self):
		self.assertFalse(Voice.has_cross_duplicates([]))
		self.assertFalse(Voice.has_cross_duplicates([0, 0, 0, 0, 0]))
		self.assertFalse(Voice.has_cross_duplicates([1, 2, 3, 4, 5, 6, 7]))
		self.assertFalse(Voice.has_cross_duplicates([1, 2, 2, 3, 2, 1, 1]))

		self.assertTrue(Voice.has_cross_duplicates([2, 4, 2, 4, 1, 2, 3]))
		self.assertTrue(Voice.has_cross_duplicates([2, 2, 4, 4, 2, 4, 1, 2]))
		self.assertTrue(Voice.has_cross_duplicates([1, 5, 5, 5, 1, 1, 5]))

	def test_slopes(self):
		self.assertEqual(Voice.calculate_slope(0), 0)
		self.assertEqual(Voice.calculate_slope(1), 1)
		self.assertEqual(Voice.calculate_slope(-1), -1)
		self.assertEqual(Voice.calculate_slope(5), 1)
		self.assertEqual(Voice.calculate_slope(-3), -1)

	def test_turns(self):
		self.assertEqual(Voice.get_turns([]), 0)
		self.assertEqual(Voice.get_turns([1]), 0)
		self.assertEqual(Voice.get_turns([3, 3, 3, 3, 3]), 0)
		self.assertEqual(Voice.get_turns([5, 5, 5, 5, 6]), 1)
		self.assertEqual(Voice.get_turns([6, 6, 6, 6, 5]), 1)
		
		self.assertEqual(Voice.get_turns([2, 3, 4]), 1)
		self.assertEqual(Voice.get_turns([5, 6, 5, 4]), 2)
		self.assertEqual(Voice.get_turns([2, 3, 3, 2, 1, 2]), 3)

	def test_leaps(self):
		self.assertFalse(Voice.has_proper_leaps([7, 6, 2, 1]))
		self.assertFalse(Voice.has_proper_leaps([0, 5, 6, 5]))
		self.assertFalse(Voice.has_proper_leaps([2, 6, 2, 3]))
		self.assertFalse(Voice.has_proper_leaps([4, 0, 5, 1]))
		
		self.assertFalse(Voice.has_proper_leaps([0, 5, 10, 9]))
		self.assertFalse(Voice.has_proper_leaps([9, 5, 0, 1]))

		self.assertFalse(Voice.has_proper_leaps([6, 7, 2, 2, 1]))
		self.assertFalse(Voice.has_proper_leaps([0, 5, 5, 5, 6]))
		self.assertTrue(Voice.has_proper_leaps([1, 4, 4, 3, 2]))
		self.assertTrue(Voice.has_proper_leaps([10, 6, 6, 7, 6]))

		self.assertTrue(Voice.has_proper_leaps([]))
		self.assertTrue(Voice.has_proper_leaps([1, 2, 3, 4]))
		self.assertTrue(Voice.has_proper_leaps([0, 5, 4, 3]))
		self.assertTrue(Voice.has_proper_leaps([5, 2, 3, 1]))
		self.assertTrue(Voice.has_proper_leaps([8, 6, 4, 2]))
		self.assertTrue(Voice.has_proper_leaps([1, 3, 5, 7]))

	def test_partition(self):
		simple_durations = Voice.simple_beat_durations
		compound_durations = Voice.compound_beat_durations

		self.assertEqual(Voice.partition_rhythm(simple_durations, 0), [])
		self.assertEqual(Voice.partition_rhythm(simple_durations, 4), [4])
		self.assertEqual(Voice.partition_rhythm(simple_durations, 1.5), [1.5])
		self.assertEqual(Voice.partition_rhythm(compound_durations, 2), [2])
		self.assertEqual(
			Voice.partition_rhythm(compound_durations, Fraction("2/3")),
			[Fraction("2/3")])

		self.assertEqual(
			Voice.partition_rhythm(compound_durations, Fraction("5/6")),
			[Fraction("2/3"), Fraction("1/6")])
		self.assertEqual(
			Voice.partition_rhythm(compound_durations, Fraction("5/3")),
			[Fraction("4/3"), Fraction("1/3")])
		self.assertEqual(
			Voice.partition_rhythm(compound_durations, Fraction("10/3")),
			[Fraction("8/3"), Fraction("2/3")])

	def test_list_merger(self):
		self.assertEqual(Voice.merge_lists([]), [])
		self.assertEqual(Voice.merge_lists([], [], []), [])
		self.assertEqual(Voice.merge_lists([], [0], []), [0])
		self.assertEqual(Voice.merge_lists([5], [], []), [5])
		
		self.assertEqual(Voice.merge_lists([], [], [2, 3]), [2, 3])
		self.assertEqual(Voice.merge_lists([4], [], [9, 1, 3], []), [4, 9, 1, 3])
		self.assertEqual(Voice.merge_lists([1,2], [3], [4,5]), [1,2,3,4,5])

		list1 = [-5, -4]
		list2 = [-3, -2]
		list3 = Voice.merge_lists(list1, list2)
		list3.append(0)
		self.assertFalse(list1 == [-5, -4, 0])
		self.assertFalse(list2 == [-3, -2, 0])

		list4 = Voice.merge_lists(list1, [])
		self.assertTrue(list1 is not list4)


if __name__ == "__main__":
	unittest.main()



