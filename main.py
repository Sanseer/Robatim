import random

class Note:

	def __init__(self, midi_pitch: int) -> None:
		self.midi_pitch = midi_pitch


class Measure:

	def __init__(self):
		self.notes = []

	def imprint_chord(self) -> None:
		pass


class Phrase:

	def __init__(self, num_measures: int = 8) -> None:
		self.measures = []
		for _ in range(num_measures):
			self.measures.append(Measure())

	def identify_measure(self, time_marker: int) -> int:
		pass

	def imprint_progression(self) -> None:
		progression_pattern = random.choice(self.progression_patterns)
		chosen_progression = progression_pattern.realize()
		time_marker = 0
		for current_chord in chosen_progression:
			measure_index = self.identify_measure(time_marker)
			self.measures[measure_index].imprint_chord(current_chord)
			time_marker += current_chord.duration 


class MiniPeriod(Phrase): 

	def __init__(self, num_measures: int = 4) -> None:
		super().__init__(num_measures)
		self.progression_patterns = [] 

	def add_melody_notes(self) -> None:
		pass


class Score:

	def __init__(self):
		self.phrases = []

	def create_theme(self) -> None:
		new_phrase = MiniPeriod()
		new_phrase.imprint_progression()
		new_phrase.add_melody_notes()
		self.phrases.append(new_phrase)

	def export_score(self) -> None:
		pass

my_score = Score()
my_score.create_theme()
my_score.export_score()
		