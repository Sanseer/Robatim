import random
import pysnooper

from voice import Voice
import idioms as idms

class KBMelody(Voice):
	"""Spices up soprano with second- and third-species counterpoint"""

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		self.sheet_notes = []
		self.lily_notes = []
		self.measure_notes = []
		self.measure_rhythms = []
		self.note_index = 0
		self.measure_index = 0
		self.beat_index = 0
		self.old_note, self.new_note = 0, 0
		self.note_values = Voice.note_values[:]

	def do_stuff(self):
		# self.group_notes()
		pass

	def create_part(self):
		self.make_letters()
		self.lily_convert()


	@property
	def notes(self):
		return self.create_rests(self.real_notes[:])

	@property
	def groove(self):
		return self.note_values

		# embellish compound time sig with one note 2_1 rhythm

















			
