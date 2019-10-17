import unittest
import json
import time

import requests

class MainSongMethods(unittest.TestCase):

	def test_output_pdf(self):
		payload = {
			"version": "stable", "code": "{ c d e }", "id": ""
		}
		# AWS can't parse python dictionaries for json objects
		sheet_music_response = requests.post(
			"https://7icpm9qr6a.execute-api.us-west-2.amazonaws.com/prod/prepare_preview/stable", data=payload)
		self.assertFalse(sheet_music_response.status_code == 200)

		time.sleep(2)

		with open("payload.json", 'w') as f:
			json.dump(payload, f)
		with open("payload.json", 'rb')  as f:
			sheet_music_response = requests.post(
				"https://7icpm9qr6a.execute-api.us-west-2.amazonaws.com/prod/prepare_preview/stable", data=f)
		self.assertTrue(sheet_music_response.status_code == 200)

		response_id = sheet_music_response.json()["id"]
		pdf_response = requests.get(
			f"https://s3-us-west-2.amazonaws.com/lilybin-scores/{response_id}.pdf")
		self.assertTrue(pdf_response.status_code == 200)


if __name__ == "__main__":
	unittest.main()



