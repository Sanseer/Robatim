import random
import collections
import logging

from generate.idioms.score import Score

class Progression(Score):
	"""A framework for chord progressions"""

	PNode = collections.namedtuple("PNode", ["value", "stipulations"])

	def __init__(self):

		self.logger = logging.getLogger("score")
		score_handler = logging.FileHandler("logs/progression.log", mode='w')
		score_handler.setLevel(logging.WARNING)
		score_format = logging.Formatter("%(name)s %(levelname)s %(message)s")
		score_handler.setFormatter(score_format)
		self.logger.addHandler(score_handler)

		# save memory
		empty_tuple = tuple()
		from_root_tonic = lambda: self.previous_chord == "0I"
		major_mode_only = lambda: self.mode == "ionian"
		minor_mode_only = lambda: self.mode == "aeolian"
		
		# can't store unhashable type (set) in hashable type tuple
		# tonic can come from other tonics and dominants
		# subdoms can come from other subdoms and tonics
		# dominants can come from tonics and subtonics
		NULL_I = self.PNode(
			"0I", (lambda: self.previous_chord not in ("+V42", "-IV6", "-VI"),)
		)
		prevent_ending = lambda: self.chord_index != 14
		NULL_I_MAJOR = self.PNode(
			"0I_MAJOR", (
				minor_mode_only, lambda: self.chord_index == 14, 
				lambda: not self.repeat_ending
			)
		)
		PLUS_I6 = self.PNode(
			"+I6", (
				lambda: self.previous_chord in ("+VII6", "+V43", "+V42", "0I", "+IV"),
				prevent_ending,
			)
		)
		MINUS_I6 = self.PNode("-I6", (lambda: self.previous_chord in ("-IV6", "-VI"),))

		from_positive_chord = lambda: self.previous_chord[0] in ("0", "+")
		from_negative_chord = lambda: self.previous_chord[0] == "-"
		validate_minus_V7 = (
			lambda: self.previous_chord in (
				"0I", "-I6", "-II", "-II7", "-II6", "-II65", "-IV", "-IV_MAJOR", 
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
		PLUS_V = self.PNode("+V", (from_positive_chord, not_plus_II7, not_II42))
		MINUS_V = self.PNode("-V", (validate_minus_V7, not_minus_II7)) 
		PLUS_V7 = self.PNode("+V7", (from_positive_chord, not_II42))
		MINUS_V7 = self.PNode("-V7", (validate_minus_V7,))
		MINUS_V6 = self.PNode("-V6", (validate_minus_V6, prevent_a2_with_V6))

		MINUS_V65 = self.PNode("-V65", (validate_minus_V6, prevent_a2_with_V6))
		PLUS_VII6 = self.PNode("+VII6", (from_positive_chord, not_II42)
		)
		PLUS_V43 = self.PNode("+V43", (from_positive_chord, not_II42)
		)
		PLUS_V42 = self.PNode("+V42", (from_positive_chord, not_II42)
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
		validate_plus_II = 	(
			lambda: self.mode == "ionian" or self.chord_index % 2 == 1 and 
				self.previous_chord in ("+II6", "+IV")
		)
		PLUS_II = self.PNode(
			"+II", (
				validate_plus_II, from_positive_chord, 
				*maintain_seventh_tension
			)
		)
		PLUS_II6 = self.PNode(
			"+II6", (from_positive_chord, *maintain_seventh_tension)
		)
		PLUS_IV = self.PNode(
			"+IV", (
				proper_subdom_order, from_positive_chord, no_minor_mode_shift,
				*maintain_seventh_tension,
			)
		)
		PLUS_IVMAJOR = self.PNode(
			"+IV_MAJOR", (
				minor_mode_only, proper_subdom_order, from_positive_chord,
				*maintain_seventh_tension, lambda: self.previous_chord != "+IV",
			)
		)
		MINUS_IVMAJOR = self.PNode(
			"-IV_MAJOR", (
				minor_mode_only, proper_subdom_order, from_negative_chord, 
				*maintain_seventh_tension, lambda: self.previous_chord != "-IV",
			)
		)
		PLUS_IVMINOR = self.PNode(
			"+IV_MINOR", (
				major_mode_only, lambda: self.previous_chord ==  "+IV",
			)
		)
		validate_minus_VI = lambda: self.previous_chord in ("0I", "-V")
		MINUS_VI = self.PNode("-VI", (validate_minus_VI, prevent_ending))
		validate_minus_II = (				
			lambda: self.mode == "ionian" or self.chord_index % 2 == 1 and 
				self.previous_chord in ("-II6", "-IV")
		)
		MINUS_II = self.PNode(
			"-II", (
				validate_minus_II, from_negative_chord, *maintain_seventh_tension,
			)
		)
		MINUS_II6 = self.PNode(
			"-II6", (from_negative_chord, *maintain_seventh_tension)
		) 
		MINUS_IV = self.PNode(
			"-IV", (
				from_negative_chord, proper_subdom_order, *maintain_seventh_tension
			)
		)

		validate_minus_IV6 = lambda: self.previous_chord in ("0I", "-VI", "-V")
		MINUS_IV6 = self.PNode("-IV6", (validate_minus_IV6, prevent_ending))
		MINUS_IV6MAJOR = self.PNode(
			"-IV6_MAJOR", (minor_mode_only, validate_minus_IV6)
		)

		not_plus_II6 = lambda: self.previous_chord != "+II6"
		not_minus_II6 = lambda: self.previous_chord != "-II6"
		not_plus_II = lambda: self.previous_chord != "+II"
		not_minus_II = lambda: self.previous_chord != "-II"

		# II7 must go to V7 if it's the last subdom chord
		ante_section_only = lambda: self.chord_index < 8
		cons_section_only = lambda: self.chord_index >= 8
		PLUS_II65 = self.PNode(
			"+II65", (from_positive_chord, not_plus_II6)
		)
		MINUS_II65 = self.PNode(
			"-II65",(from_negative_chord, not_minus_II6)
		)
		PLUS_II7 = self.PNode(
			"+II7", (from_positive_chord, not_plus_II)
		)
		MINUS_II7 = self.PNode(
			"-II7", (from_negative_chord, not_minus_II, cons_section_only)
		)
		NULL_II42 = self.PNode(
			"0II42", (from_positive_chord, ante_section_only)
		)
		PLUS_IV7 = self.PNode(
			"+IV7", (
				from_positive_chord, proper_subdom_order,
				lambda: self.previous_chord != "+IV", 	
			)
		)
		MINUS_IV7 = self.PNode(
			"-IV7", (
				from_negative_chord, proper_subdom_order,
				lambda: self.previous_chord != "-IV",
			)
		)
		MINUS_IV65 = self.PNode(
			"-IV65", (major_mode_only, validate_minus_IV6, ante_section_only)
		)
		MINUS_IV65MAJOR = self.PNode(
			"-IV65_MAJOR", (minor_mode_only, validate_minus_IV6, ante_section_only)
		)
		PLUS_I64 = self.PNode("+I64", (from_positive_chord, not_II42))

		# patterns ignore individual chord rules
		PATTERN_EXTEND5_DOUBLE01 = self.PNode(
			(MINUS_V, MINUS_V6, NULL_I), (validate_minus_V7, not_minus_II7)
		)
		PATTERN_EXTEND5_DOUBLE02 = self.PNode(
			(MINUS_V6, MINUS_V, NULL_I), (validate_minus_V6, prevent_a2_with_V6)
		)
		PATTERN_EXTEND5_DOUBLE03 = self.PNode(
			((MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), NULL_I), 
			(from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE04 = self.PNode(
			(PLUS_V43, MINUS_V65, NULL_I), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE05 = self.PNode(
			(PLUS_V, PLUS_V42, PLUS_I6), (
				from_positive_chord, not_plus_II7, not_II42
			)
		)
		PATTERN_EXTEND5_DOUBLE06 = self.PNode(
			((PLUS_VII6, PLUS_V43), PLUS_V42, PLUS_I6), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE07 = self.PNode(
			((MINUS_V6, MINUS_V65), PLUS_V42, PLUS_I6), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE08 = self.PNode(
			(PLUS_V42, MINUS_V65, NULL_I), 
			(lambda: self.previous_chord == "+I6",)
		)

		PATTERN_EXTEND5_DOUBLE10 = self.PNode(
			(PLUS_I64, PLUS_V, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE11 = self.PNode(
			(PLUS_I64, MINUS_V, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE12 = self.PNode(
			(PLUS_I64, PLUS_V42, PLUS_I6), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE13 = self.PNode(
			(PLUS_I64, PLUS_V7, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE14 = self.PNode(
			(PLUS_I64, MINUS_V7, NULL_I), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE15 = self.PNode(
			(PLUS_IV, PLUS_IVMINOR, NULL_I), (
				major_mode_only, no_minor_mode_shift, proper_subdom_order, 
				from_positive_chord, *maintain_seventh_tension
			)
		)

		PATTERN_EXTEND5_DOUBLE20 = self.PNode(
			(PLUS_V43, NULL_I, MINUS_V6), (from_positive_chord, not_II42)
		)
		PATTERN_EXTEND5_DOUBLE21 = self.PNode(
			(MINUS_V, MINUS_IV6, (MINUS_V6, MINUS_V65)), (
				major_mode_only, validate_minus_V7, not_minus_II7
			)
		)
		PATTERN_EXTEND5_DOUBLE22 = self.PNode(
			(MINUS_V, MINUS_VI, (MINUS_V6, MINUS_V65)), (
				major_mode_only, validate_minus_V7, not_minus_II7)
		)
		PATTERN_EXTEND5_DOUBLE23 = self.PNode(
			(MINUS_V, MINUS_IV6MAJOR, (MINUS_V6, MINUS_V65)), (
				minor_mode_only, validate_minus_V7, not_minus_II7
			)
		)
		PATTERN_EXTEND5_DOUBLE24 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_IV6, MINUS_V), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE25 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_VI, MINUS_V), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE26 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_IV6MAJOR, MINUS_V), (
				minor_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE27 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_IV6, MINUS_V7), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			) 
		)
		PATTERN_EXTEND5_DOUBLE28 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_VI, MINUS_V7), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE29 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_IV6MAJOR, MINUS_V7), (
				minor_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)


		not_minus_VI = lambda: self.previous_chord != "-VI"
		not_minus_IV6 = lambda: self.previous_chord != "-IV6"
		PATTERN_EXTEND2_DOUBLE01 = self.PNode(
			(PLUS_II, PLUS_I6, PLUS_II6), (				
				validate_plus_II, from_positive_chord, 
				*maintain_seventh_tension)
		)
		PATTERN_EXTEND2_DOUBLE02 = self.PNode(
			(PLUS_II6, PLUS_I6, PLUS_II), (
				from_positive_chord, *maintain_seventh_tension
			)
		)
		PATTERN_EXTEND2_DOUBLE03 = self.PNode(
			(NULL_I, MINUS_VI, (MINUS_IV, MINUS_II6)), (
				not_minus_VI, not_minus_IV6
			)
		)
		PATTERN_EXTEND2_DOUBLE04 = self.PNode(
			(NULL_I, MINUS_VI, MINUS_II), (
				major_mode_only, not_minus_VI, not_minus_IV6
			)
		)
		PATTERN_EXTEND2_DOUBLE05 = self.PNode(
			(PLUS_II65, PLUS_I6, PLUS_II7), (from_positive_chord, not_plus_II6)
		)
		PATTERN_EXTEND2_DOUBLE06 = self.PNode(
			(PLUS_II7, PLUS_I6, PLUS_II65), (from_positive_chord, not_plus_II)
		)
		PATTERN_EXTEND2_DOUBLE07 = self.PNode(
			(MINUS_II, MINUS_I6, MINUS_II6), (
				validate_minus_II, from_negative_chord, 
				*maintain_seventh_tension
			)
		)
		PATTERN_EXTEND2_DOUBLE08 = self.PNode(
			(MINUS_II6, MINUS_I6, MINUS_II), (
				from_negative_chord, *maintain_seventh_tension
			)
		)
		PATTERN_EXTEND2_DOUBLE09 = self.PNode(
			(MINUS_II65, MINUS_I6, MINUS_II7), (
				from_negative_chord, not_minus_II6, cons_section_only 
			)
		)
		PATTERN_EXTEND2_DOUBLE10 = self.PNode(
			(MINUS_II7, MINUS_I6, MINUS_II65), (
				from_negative_chord, not_minus_II,
			)
		)

		self.tonic_chords_single = (
			NULL_I, PLUS_I6, NULL_I_MAJOR, (MINUS_VI, MINUS_IV6), MINUS_I6
		) 
		self.ante_ending_single = (
			PLUS_V, MINUS_V, (MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), 
			PLUS_V42,
		)
		self.tonic_extend_single = (
			(MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), PLUS_V42, PLUS_IV, 
			(MINUS_IV6, MINUS_VI),
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
			PATTERN_EXTEND2_DOUBLE07, PATTERN_EXTEND2_DOUBLE08,
			PATTERN_EXTEND2_DOUBLE09, PATTERN_EXTEND2_DOUBLE10,
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
		self.ante_dominant_extend_triple = (
			PATTERN_EXTEND5_DOUBLE20, PATTERN_EXTEND5_DOUBLE21, 
			PATTERN_EXTEND5_DOUBLE22, PATTERN_EXTEND5_DOUBLE23,
			PATTERN_EXTEND5_DOUBLE24, PATTERN_EXTEND5_DOUBLE25,
			PATTERN_EXTEND5_DOUBLE26,
		)
		self.cons_dominant_extend_triple = (
			PATTERN_EXTEND5_DOUBLE24, PATTERN_EXTEND5_DOUBLE25, 
			PATTERN_EXTEND5_DOUBLE26, PATTERN_EXTEND5_DOUBLE27,
			PATTERN_EXTEND5_DOUBLE28, PATTERN_EXTEND5_DOUBLE29,
		)
		# starting chord is based on reverse membership testing of I and I6
		self.previous_chord = None
		self.chord_index = 0

	def add_chord_pattern(self, chord_pattern):
		"""Generate new chord(s) for a chord progression"""

		empty_tuple = tuple()
		chord_pattern_functions = {
			"TON": self.add_one_chord, "RPT": self.repeat_chord,
			"1HC1": self.add_one_chord, "1HC2": self.add_one_chord,
			"1END_EX1": self.add_one_chord, "1EXTON1": self.add_one_chord,
			"1EXTON2": self.add_one_chord, "2HC": self.add_three_chords,
			"SDOM_AT_-1": self.add_one_chord, "SDOM_AF_-1": self.add_one_chord,
			"SDOM_AT_-2": self.add_one_chord, "3SDOM_EX": self.add_three_chords,
			"2END_EX1": self.add_three_chords, "ANTE_3DOM_EX": self.add_three_chords,
			"CONS_3DOM_EX": self.add_three_chords,
		}
		chord_group_select = {
			"TON": (self.tonic_chords_single,), "RPT": empty_tuple,
			"1HC1": (self.ante_ending_single,),
			"1HC2": (self.tonic_chords_single,),
			"1END_EX1": (self.cons_ending_single,),
			"1EXTON1": (self.tonic_extend_single,),
			"1EXTON2": (self.tonic_chords_single,),
			"2HC": (
				empty_tuple, self.ante_ending_single, self.tonic_chords_single, 
				self.ante_ending_triple, self.ante_plus1_64
			), "SDOM_AT_-1": (self.subdominant_single_minus1,),
			"SDOM_AF_-1": (self.subdominant_single_minus1,),
			"SDOM_AT_-2": (self.subdominant_single_minus2,),
			"3SDOM_EX": (
				self.subdominant_single_minus1, self.tonic_chords_single, 
				self.subdominant_single_minus1, self.subdominant_triple,
			), "2END_EX1": (
				empty_tuple, self.cons_ending_single, self.tonic_chords_single,
				self.cons_ending_triple, self.cons_plus1_64
			), "ANTE_3DOM_EX": (
				self.ante_ending_single, self.tonic_chords_single,
				self.ante_ending_single, self.ante_dominant_extend_triple
			), "CONS_3DOM_EX": (
				self.cons_ending_single, self.tonic_chords_single,
				self.ante_ending_single, self.cons_dominant_extend_triple
			)
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
			if not isinstance(chord, self.PNode):
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
				if not isinstance(chord_double, self.PNode):
					chord_double = random.choice(chord_double)
				self.logger.warning(chord_double)
				if all(stipulation() for stipulation in chord_double.stipulations):
					self.previous_chord = chord_double.value
					self.chord_index += 2
					for chord_single in chord_doublers2:
						if not isinstance(chord_single, self.PNode):
							chord_single = random.choice(chord_single)
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
					if not isinstance(chord_single, self.PNode):
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
			if isinstance(chord_item, self.PNode):
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

			("TON", "RPT", "RPT", "RPT", "ANTE_3DOM_EX", "RPT", "1HC2"),
		)
		consequent_patterns = (
			("RPT", "RPT", "RPT", "RPT", "1END_EX1", "TON", "RPT"),
			("RPT", "RPT", "RPT", "1END_EX1", "RPT", "TON", "RPT"),

			("RPT", "RPT", "RPT", "SDOM_AT_-1", "1END_EX1", "TON", "RPT"),
			("RPT", "SDOM_AT_-1", "RPT", "1END_EX1", "RPT", "TON", "RPT"),
			("RPT", "RPT", "SDOM_AF_-1", "1END_EX1", "RPT", "TON", "RPT"),
			("RPT", "3SDOM_EX", "1END_EX1", "TON", "RPT"),
			("RPT", "RPT", "RPT", "2END_EX1", "RPT"),
			("RPT", "SDOM_AT_-1", "RPT", "2END_EX1", "RPT"),
			("RPT", "RPT", "SDOM_AF_-1", "2END_EX1", "RPT"),
			("RPT", "SDOM_AT_-2", "SDOM_AF_-1", "2END_EX1", "RPT"),

			("RPT", "CONS_3DOM_EX", "RPT","TON", "RPT"),
		)

		all_progression_types = {}
		for antecedent_pattern in antecedent_patterns:
			for consequent_pattern in consequent_patterns:
				full_pattern = antecedent_pattern + consequent_pattern
				if len(full_pattern) == 16 and Progression.allows_truncation(full_pattern, 2, "RPT"):
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
