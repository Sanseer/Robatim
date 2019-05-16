from voice import Voice
import idioms as idms

class KBMelody(Voice):

	def __init__(self):
		self.real_notes = Voice.soprano_pitches
		self.sheet_notes = []
		self.lily_notes = []