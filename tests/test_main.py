import unittest
import json
import time

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

		self.assertEqual(Voice.get_turns([]), 0)
		self.assertEqual(Voice.get_turns([1]), 0)
		self.assertEqual(Voice.get_turns([3, 3, 3, 3, 3]), 0)
		self.assertEqual(Voice.get_turns([5, 5, 5, 5, 6]), 1)
		self.assertEqual(Voice.get_turns([6, 6, 6, 6, 5]), 1)
		
		self.assertEqual(Voice.get_turns([2, 3, 4]), 1)
		self.assertEqual(Voice.get_turns([5, 6, 5, 4]), 2)
		self.assertEqual(Voice.get_turns([2, 3, 3, 2, 1, 2]), 3)


if __name__ == "__main__":
	unittest.main()



