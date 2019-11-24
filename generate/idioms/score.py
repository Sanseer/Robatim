import random
import collections
import logging

class Score:
	"""Overarching model of a musical piece"""

	ScoreNode = collections.namedtuple("ScoreNode", ["value", "stipulations"])

	def __init__(self):

		self.logger = logging.getLogger("score")
		score_handler = logging.FileHandler("logs/score.log", mode='w')
		score_handler.setLevel(logging.WARNING)
		score_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		score_handler.setFormatter(score_format)
		self.logger.addHandler(score_handler)

		# exclude 9/8 because of uneven divisions
		# 2/4, 3/4, 6/8, 4/4, 12/8
		# the difference between duple and quadruple meter is semantic
		self.time_sigs = ((2,2), (3,2), (2,3), (4,2), (3,2), (4,3))

		# 0 = rhythm1
		# 1 = rhythm2 etc.
		# -1 = sustain
		# -2 = pickup
		# duplicate patterns are used to alter selected pattern probability
		self.rhythm_patterns = (
			((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1)), 
			(
				(0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0 , 2, -1), 
				(0, 2, 0, -1), (0, 1, 2, -1), (0, 2, 1, -1), (0, 0, -1, -1), 
				(0, 1, -1, -1), (0, 2, -1, -1), (0, 0, -1, -1), (0, 1, -1, -1), 
				(0, 2, -1, -1), (0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
				(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2), (0, 0, -1, -2), 
				(0, 1, -1, -2), (0, 2, -1, -2), (0, 0, -1, -2), (0, 1, -1, -2), 
				(0, 2, -1, -2), (0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
			), (
				(0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0, 2, -1), 
				(0, 2, 0, -1), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), 
				(0, 0, 2, 0), (0, 2, 0, 0), (0, 1, 2, -1), (0, 1, 2, 0), 
				(0, 2, 1, -1), (0, 2, 1, 0),
			), ((0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1))
		)

		# save memory
		empty_tuple = tuple()
		from_root_tonic = lambda: self.previous_chord == "0I"
		major_mode_only = lambda: self.mode == "ionian"
		minor_mode_only = lambda: self.mode == "aeolian"
		
		# can't store unhashable type (set) in hashable type tuple
		# tonic can come from other tonics and dominants
		# subdoms can come from other subdoms and tonics
		# dominants can come from tonics and subtonics
		NULL_I = Score.ScoreNode(
			"0I", (lambda: self.previous_chord not in ("+V42",),)
		)
		NULL_I_MAJOR = Score.ScoreNode(
			"0I_MAJOR", (
				minor_mode_only, lambda: self.chord_index == 14, 
			)
		)
		PLUS_I6 = Score.ScoreNode(
			"+I6", (lambda: self.previous_chord in ("+VII6", "+V43", "+V42", "0I"),)
		)

		from_positive_chord = lambda: self.previous_chord[0] in ("0", "+")
		from_negative_chord = lambda: self.previous_chord[0] == "-"
		validate_minus_V7 = (
			lambda: self.previous_chord in (
				"0I", "-II", "-II7", "-II6", "-II65", "-IV", "-IV_MAJOR", 
				"-VI", "-IV6", "-IV6_MAJOR", "-IV7"
			)
		)
		validate_minus_V6 = (
			lambda: self.previous_chord in (
				"0I", "+I6", "+II", "+II6", "+IV", "-IV6", "-IV6_MAJOR", 
				"-IV65", "-IV65_MAJOR", "+II7", "+II65", "0II42", 
			)
		)
		prevent_a2_with_V6 = (
			lambda: self.mode == "ionian" or self.previous_chord not in ("-IV6", "-IV65")
		)

		not_plus_II7 = lambda: self.previous_chord != "+II7"
		not_minus_II7 = lambda: self.previous_chord != "-II7"
		not_II42 = lambda: self.previous_chord != "0II42"
		PLUS_V = Score.ScoreNode("+V", (from_positive_chord, not_plus_II7, not_II42))
		MINUS_V = Score.ScoreNode("-V", (validate_minus_V7, not_minus_II7)) 
		PLUS_V7 = Score.ScoreNode("+V7", (from_positive_chord, not_II42))
		MINUS_V7 = Score.ScoreNode("-V7", (validate_minus_V7,))
		MINUS_V6 = Score.ScoreNode("-V6", (validate_minus_V6, prevent_a2_with_V6))

		MINUS_V65 = Score.ScoreNode("-V65", (validate_minus_V6, prevent_a2_with_V6))
		PLUS_VII6 = Score.ScoreNode("+VII6", (from_positive_chord, not_II42)
		)
		PLUS_V43 = Score.ScoreNode("+V43", (from_positive_chord, not_II42)
		)
		PLUS_V42 = Score.ScoreNode("+V42", (from_positive_chord, not_II42)
		)

		proper_subdom_order = (
			lambda: self.previous_chord not in (
				"+II", "-II", "+II6", "-II6", "+II65", "-II65", "+II7", "-II7", 
				"0II42", 
			)
		)

		no_major_mode_shift = lambda: self.previous_chord[-5:] != "MAJOR"
		no_minor_mode_shift = lambda: self.previous_chord[-5:] != "MINOR"

		maintain_seventh_tension = (
			lambda: self.previous_chord[-2:] not in ("65", "43", "42"),
			lambda: self.previous_chord[-1] != "7",
		)
		PLUS_II = Score.ScoreNode(
			"+II", (
				lambda: self.mode == "ionian" or self.chord_index % 2 == 1 and 
					self.previous_chord in ("+II6", "+IV"), 
				from_positive_chord, *maintain_seventh_tension
			)
		)
		PLUS_II6 = Score.ScoreNode(
			"+II6", (from_positive_chord, *maintain_seventh_tension)
		)
		PLUS_IV = Score.ScoreNode(
			"+IV", (
				proper_subdom_order, from_positive_chord, no_minor_mode_shift,
				*maintain_seventh_tension,
			)
		)
		PLUS_IVMAJOR = Score.ScoreNode(
			"+IV_MAJOR", (
				minor_mode_only, proper_subdom_order, from_positive_chord,
				*maintain_seventh_tension, lambda: self.previous_chord != "+IV",
			)
		)
		MINUS_IVMAJOR = Score.ScoreNode(
			"-IV_MAJOR", (
				minor_mode_only, proper_subdom_order, from_negative_chord, 
				*maintain_seventh_tension, lambda: self.previous_chord != "-IV",
			)
		)
		PLUS_IVMINOR = Score.ScoreNode(
			"+IV_MINOR", (
				major_mode_only, lambda: self.previous_chord ==  "+IV",
			)
		)
		MINUS_VI = Score.ScoreNode("-VI", (from_root_tonic,))
		MINUS_II = Score.ScoreNode(
			"-II", (
				lambda: self.mode == "ionian" or self.chord_index % 2 == 1 and 
					self.previous_chord in ("-II6", "-IV"),
				from_negative_chord, *maintain_seventh_tension,
			)
		)
		MINUS_II6 = Score.ScoreNode(
			"-II6", (from_negative_chord, *maintain_seventh_tension)
		) 
		MINUS_IV = Score.ScoreNode(
			"-IV", (
				from_negative_chord, proper_subdom_order, *maintain_seventh_tension
			)
		)

		validate_IV6 = lambda: self.previous_chord in ("0I", "-VI")
		MINUS_IV6 = Score.ScoreNode("-IV6", (validate_IV6,))
		MINUS_IV6MAJOR = Score.ScoreNode(
			"-IV6_MAJOR", (minor_mode_only, validate_IV6)
		)

		PLUS_II65 = Score.ScoreNode(
			"+II65", (
				from_positive_chord, lambda: self.previous_chord != "+II6",
			)
		)
		MINUS_II65 = Score.ScoreNode(
			"-II65",(
				from_negative_chord, lambda: self.previous_chord != "-II6",
			)
		)
		PLUS_II7 = Score.ScoreNode(
			"+II7", (
				from_positive_chord, lambda: self.previous_chord != "+II",
			)
		)
		MINUS_II7 = Score.ScoreNode(
			"-II7", (
				from_negative_chord, lambda: self.previous_chord != "-II",
			)
		)
		ante_subdom_end_only = lambda: self.chord_index == 5
		NULL_II42 = Score.ScoreNode(
			"0II42", (from_positive_chord, ante_subdom_end_only)
		)
		PLUS_IV7 = Score.ScoreNode(
			"+IV7", (
				from_positive_chord, proper_subdom_order,
				lambda: self.previous_chord != "+IV", 	
			)
		)
		MINUS_IV7 = Score.ScoreNode(
			"-IV7", (
				from_negative_chord, proper_subdom_order,
				lambda: self.previous_chord != "-IV",
			)
		)
		MINUS_IV65 = Score.ScoreNode(
			"-IV65", (major_mode_only, validate_IV6, ante_subdom_end_only)
		)
		MINUS_IV65MAJOR = Score.ScoreNode(
			"-IV65_MAJOR", (minor_mode_only, validate_IV6, ante_subdom_end_only)
		)
		PLUS_I64 = Score.ScoreNode("+I64", (from_positive_chord, not_II42))

		# patterns ignore individual chord rules
		PATTERN_EXTEND5_DOUBLE01 = Score.ScoreNode(
			(MINUS_V, MINUS_V6, NULL_I), (validate_minus_V7, not_minus_II7)
		)
		PATTERN_EXTEND5_DOUBLE02 = Score.ScoreNode(
			(MINUS_V6, MINUS_V, NULL_I), (validate_minus_V6, prevent_a2_with_V6)
		)
		PATTERN_EXTEND5_DOUBLE03 = Score.ScoreNode(
			((MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), NULL_I), 
			(from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE04 = Score.ScoreNode(
			(PLUS_V43, MINUS_V65, NULL_I), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE05 = Score.ScoreNode(
			(PLUS_V, PLUS_V42, PLUS_I6), (
				from_positive_chord, not_plus_II7, not_II42
			)
		)
		PATTERN_EXTEND5_DOUBLE06 = Score.ScoreNode(
			((PLUS_VII6, PLUS_V43), PLUS_V42, PLUS_I6), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE07 = Score.ScoreNode(
			((MINUS_V6, MINUS_V65), PLUS_V42, PLUS_I6), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE08 = Score.ScoreNode(
			(PLUS_V42, MINUS_V65, NULL_I), 
			(lambda: self.previous_chord == "+I6",)
		)

		PATTERN_EXTEND5_DOUBLE10 = Score.ScoreNode(
			(PLUS_I64, PLUS_V, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE11 = Score.ScoreNode(
			(PLUS_I64, MINUS_V, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE12 = Score.ScoreNode(
			(PLUS_I64, PLUS_V42, PLUS_I6), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE13 = Score.ScoreNode(
			(PLUS_I64, PLUS_V7, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE14 = Score.ScoreNode(
			(PLUS_I64, MINUS_V7, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE15 = Score.ScoreNode(
			(PLUS_IV, PLUS_IVMINOR, NULL_I), (
				major_mode_only, no_minor_mode_shift, proper_subdom_order, 
				from_positive_chord, *maintain_seventh_tension
			)
		)

		PATTERN_EXTEND2_DOUBLE01 = Score.ScoreNode(
			(PLUS_II, PLUS_I6, PLUS_II6), (major_mode_only,)
		)
		PATTERN_EXTEND2_DOUBLE02 = Score.ScoreNode(
			(PLUS_II6, PLUS_I6, PLUS_II), (major_mode_only,)
		)
		PATTERN_EXTEND2_DOUBLE03 = Score.ScoreNode(
			(NULL_I, MINUS_VI, (MINUS_IV, MINUS_II6)), empty_tuple
		)
		PATTERN_EXTEND2_DOUBLE04 = Score.ScoreNode(
			(NULL_I, MINUS_VI, MINUS_II), (major_mode_only,)
		)
		PATTERN_EXTEND2_DOUBLE05 = Score.ScoreNode(
			(PLUS_II65, PLUS_I6, PLUS_II7), empty_tuple
		)
		PATTERN_EXTEND2_DOUBLE06 = Score.ScoreNode(
			(PLUS_II7, PLUS_I6, PLUS_II65), empty_tuple
		)

		self.tonic_chords_single = (NULL_I, PLUS_I6, NULL_I_MAJOR) 
		self.ante_ending_single = (
			PLUS_V, MINUS_V, (MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), 
			PLUS_V42,
		)
		self.dominant_extend_single = (
			(MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), PLUS_V42,
		)
		self.cons_ending_single = (
			PLUS_V, MINUS_V, PLUS_V7, MINUS_V7, PLUS_IVMINOR, PLUS_IV,
		)
		self.ante_ending_triple = (
			PATTERN_EXTEND5_DOUBLE01, PATTERN_EXTEND5_DOUBLE02,
			PATTERN_EXTEND5_DOUBLE03, PATTERN_EXTEND5_DOUBLE04,
			PATTERN_EXTEND5_DOUBLE05, PATTERN_EXTEND5_DOUBLE06,
			PATTERN_EXTEND5_DOUBLE07, PATTERN_EXTEND5_DOUBLE08
		)
		self.subdominant_single_minus1 = (
			PLUS_II, PLUS_II6, PLUS_IV, PLUS_IVMAJOR, MINUS_IVMAJOR, MINUS_VI, MINUS_II, 
			MINUS_II6, MINUS_IV, MINUS_VI, MINUS_IV6, MINUS_IV6MAJOR,
			PLUS_II7, PLUS_II65, MINUS_II7, MINUS_II65, NULL_II42,
			PLUS_IV7, MINUS_IV7, MINUS_IV65, MINUS_IV65MAJOR,
		)
		self.subdominant_single_minus2 = (
			PLUS_II, PLUS_II6, PLUS_IV, MINUS_VI, MINUS_II, MINUS_II6, MINUS_IV,
			MINUS_VI, MINUS_IV6, PLUS_II7, PLUS_II65, MINUS_II7, MINUS_II65,
		)
		self.subdominant_triple = (
			PATTERN_EXTEND2_DOUBLE01, PATTERN_EXTEND2_DOUBLE02,
			PATTERN_EXTEND2_DOUBLE03, PATTERN_EXTEND2_DOUBLE04,
			PATTERN_EXTEND2_DOUBLE05, PATTERN_EXTEND2_DOUBLE06,
		)
		self.ante_plus1_64 = (
			PATTERN_EXTEND5_DOUBLE10, PATTERN_EXTEND5_DOUBLE11, 
			PATTERN_EXTEND5_DOUBLE12,
		)
		self.cons_plus1_64 = (
			PATTERN_EXTEND5_DOUBLE10, PATTERN_EXTEND5_DOUBLE11, 
			PATTERN_EXTEND5_DOUBLE13, PATTERN_EXTEND5_DOUBLE14,
		) 
		self.cons_ending_triple = (PATTERN_EXTEND5_DOUBLE15,)

		# starting chord is based on reverse membership testing of I and I6
		self.previous_chord = None
		self.chord_index = 0
		self.mode = random.choice(("ionian", "aeolian"))

		if self.mode == "ionian":
			self.key_sigs = (
				"C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F",
			)

		elif self.mode == "aeolian":
			self.key_sigs = (
				"A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D",
			)

	def add_chord_pattern(self, chord_pattern):
		"""Generate new chord(s) for a chord progression"""

		empty_tuple = tuple()
		chord_pattern_functions = {
			"TON": self.add_one_chord, "RPT": self.repeat_chord,
			"1HC1": self.add_one_chord, "1HC2": self.add_one_chord,
			"1END_EX1": self.add_one_chord, "1EXTON1": self.add_one_chord,
			"1EXTON2": self.add_one_chord, "2HC": self.add_three_chords,
			"SDOM_AT_-1": self.add_one_chord, "SDOM_AF_-1": self.add_one_chord,
			"SDOM_AT_-2": self.add_one_chord, "3SDOM_EX1": self.add_three_chords,
			"2END_EX1": self.add_three_chords,
		}
		chord_group_select = {
			"TON": (self.tonic_chords_single,), "RPT": empty_tuple,
			"1HC1": (self.ante_ending_single,),
			"1HC2": (self.tonic_chords_single,),
			"1END_EX1": (self.cons_ending_single,),
			"1EXTON1": (self.dominant_extend_single,),
			"1EXTON2": (self.tonic_chords_single,),
			"2HC": (
				empty_tuple, self.ante_ending_single, self.tonic_chords_single, 
				self.ante_ending_triple, self.ante_plus1_64
			), "SDOM_AT_-1": (self.subdominant_single_minus1,),
			"SDOM_AF_-1": (self.subdominant_single_minus1,),
			"SDOM_AT_-2": (self.subdominant_single_minus2,),
			"3SDOM_EX1": (
				self.subdominant_single_minus1, self.tonic_chords_single, 
				self.subdominant_single_minus1, self.subdominant_triple,
			), "2END_EX1": (
				empty_tuple, self.cons_ending_single, self.tonic_chords_single,
				self.cons_ending_triple, self.cons_plus1_64
			),
		}
		chord_adder = chord_pattern_functions[chord_pattern]
		self.logger.warning(f"Chord index: {self.chord_index}")
		self.logger.warning(f"Chord adder: {chord_adder.__name__}")
		chord_args = chord_group_select[chord_pattern]
		return chord_adder(*chord_args)

	def add_one_chord(self, chord_group):
		"""Generate the next chord in a progression based on score state"""

		valid_chords = []
		for chord in chord_group:
			# account for interchangeable chords
			if not isinstance(chord, Score.ScoreNode):
				chord = random.choice(chord)
			self.logger.warning(f"Chord: {chord}")
			# prevent repeat of subdom chords
			if (all(stipulation() for stipulation in chord.stipulations)
			  and chord.value != self.previous_chord):
				valid_chords.append(chord.value)

		self.chord_index += 1
		self.logger.warning(f"Valid chords: {valid_chords}")
		self.previous_chord = random.choice(valid_chords)
		self.logger.warning(f"Chosen chord: {self.previous_chord}")
		self.logger.warning("-" * 30)
		return self.previous_chord

	def add_three_chords(
	  self, chord_singlers, chord_doublers1, chord_doublers2, *args):
		"""Generate the next three chords in a progression based on chord state"""

		all_valid_chord_sequences = []
		temp_chord_index = self.chord_index
		temp_previous_chord = self.previous_chord
		for chord_group in args:
			valid_chord_sequences = []
			for chord_sequence in chord_group:
				self.logger.warning(chord_sequence)
				if all(stipulation() for stipulation in chord_sequence.stipulations):
					valid_chord_sequences.append(chord_sequence.value)

			if valid_chord_sequences:
				all_valid_chord_sequences.append(valid_chord_sequences)

		if not all_valid_chord_sequences:
			valid_chord_sequences = []

			# II6 II6 II doesn't work in minor mode
			# also weak-to-strong repetition
			for chord_double in chord_doublers1:
				self.previous_chord = temp_previous_chord
				self.chord_index = temp_chord_index
				if not isinstance(chord_double, Score.ScoreNode):
					chord_double = random.choice(chord_double)
					self.logger.warning(chord_double)
				if all(stipulation() for stipulation in chord_double.stipulations):
					self.previous_chord = chord_double.value
					self.chord_index += 2
					for chord_single in chord_doublers2:
						self.logger.warning(chord_single)
						if all(stipulation() for stipulation in chord_single.stipulations):
							valid_chord_sequences.append(
								(chord_double, chord_double, chord_single)
							)
			self.previous_chord = temp_previous_chord
			self.chord_index = temp_chord_index
			all_valid_chord_sequences.append(valid_chord_sequences)

			if chord_singlers:
				valid_chord_sequences = []
				for chord_single in chord_singlers:
					if not isinstance(chord_single, Score.ScoreNode):
						chord_single = random.choice(chord_single)
					self.logger(chord_single)
					if all(stipulation() for stipulation in chord_single.stipulations):
						valid_chord_sequences.append(
							(chord_single, chord_single, chord_single)
						)
				all_valid_chord_sequences.append(valid_chord_sequences)

		self.logger.warning(f"Valid chord groups: {all_valid_chord_sequences}")
		chosen_chord_group = random.choice(all_valid_chord_sequences)
		chosen_chord_items = random.choice(chosen_chord_group)
		chosen_chord_sequence = []
		for chord_item in chosen_chord_items:
			if isinstance(chord_item, Score.ScoreNode):
				chosen_chord_sequence.append(chord_item.value)
			elif isinstance(chord_item, tuple):
				chosen_chord_sequence.append(random.choice(chord_item).value)

		self.chord_index += len(chosen_chord_sequence)
		self.previous_chord = chosen_chord_sequence[-1]
		self.logger.warning(f"Chosen chord sequences: {chosen_chord_sequence}")
		self.logger.warning("-" * 30)
		return chosen_chord_sequence

	def repeat_chord(self):	
		self.chord_index += 1
		return self.previous_chord

	@staticmethod
	def choose_progression_type():
		"""Choose a pattern for a full chord progression"""

		antecedent_patterns = (
			("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "2HC"),
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "2HC"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "2HC"),

			("TON", "RPT", "RPT", "RPT", "SDOM_AT_-1", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "RPT", "SDOM_AT_-1", "RPT", "2HC"),
			("TON", "RPT", "RPT", "RPT", "RPT", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "RPT", "RPT", "SDOM_AF_-1", "2HC"),
			
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "SDOM_AF_-1", "2HC"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "SDOM_AF_-1", "2HC"),
			("TON", "RPT", "RPT", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
		)
		consequent_patterns = (
			("RPT", "RPT", "RPT", "RPT", "1END_EX1", "TON", "RPT"),
			("RPT", "RPT", "RPT", "1END_EX1", "RPT", "TON", "RPT"),

			("RPT", "RPT", "RPT", "SDOM_AT_-1", "1END_EX1", "TON", "RPT"),
			("RPT", "SDOM_AT_-1", "RPT", "1END_EX1", "RPT", "TON", "RPT"),
			("RPT", "RPT", "SDOM_AF_-1", "1END_EX1", "RPT", "TON", "RPT"),
			("RPT", "3SDOM_EX1", "1END_EX1", "TON", "RPT"),
			("RPT", "RPT", "RPT", "2END_EX1", "RPT"),
			("RPT", "SDOM_AT_-1", "RPT", "2END_EX1", "RPT"),
			("RPT", "RPT", "SDOM_AF_-1", "2END_EX1", "RPT"),
			("RPT", "SDOM_AT_-2", "SDOM_AF_-1", "2END_EX1", "RPT"),
		)

		all_progression_types = {}
		for antecedent_pattern in antecedent_patterns:
			for consequent_pattern in consequent_patterns:
				full_pattern = antecedent_pattern + consequent_pattern
				if len(full_pattern) == 16 and Score.allows_truncation(full_pattern, 2, "RPT"):
					accelerate = False
				else:
					accelerate = True
				all_progression_types[full_pattern] = accelerate

		progression_type = random.choice(tuple(all_progression_types))
		print(f"Progression type: {progression_type}")
		return progression_type, all_progression_types[progression_type]

	@staticmethod
	def allows_truncation(sequence, divisor, repeat_value):
		"""Check last item equality of list dividends"""
		
		if divisor < 2:
			return False
		if len(sequence) < divisor:
			return False

		for item_num, current_item in enumerate(sequence, 1):
			if item_num % divisor == 0 and current_item != repeat_value:
				return False
		return True
