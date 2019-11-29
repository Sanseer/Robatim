from generate.voices.voice import Voice

class MelodyFrame:

	def __init__(self, nested_scale_degrees, pickup=False):
		self.pickup = pickup
		self.nested_scale_degrees = nested_scale_degrees
		self.unnested_scale_degrees = unnest_sequence(self.nested_scale_degrees)
		self.chosen_scale_degrees = make_base_melody(self.nested_scale_degrees)
		self.melodic_mvmt = make_melodic_ramp(
			self.chosen_scale_degrees, self.pickup
		)
		self.chosen_figurations = set_melodic_figures(self.nested_scale_degrees)
		self.relevant_melodic_mvmt = self.melodic_mvmt[1:]
		self.repeat_intro = self.nested_scale_degrees[0:4] == self.nested_scale_degrees[8:12]

	def __repr__(self):
		return str(self.nested_scale_degrees)


def make_base_melody(nested_scale_degrees):
	chosen_scale_degrees = []
	for scale_group in nested_scale_degrees:
		chosen_scale_degrees.append(scale_group[0])

	return chosen_scale_degrees


def make_melodic_ramp(chosen_scale_degrees, pickup):
	melodic_mvmt = []
	if pickup:
		melodic_mvmt.append('>')
	else:
		melodic_mvmt.append('_')

	for current_degree, next_degree in zip(
		chosen_scale_degrees, chosen_scale_degrees[1:]):
		if next_degree > current_degree:
			melodic_mvmt.append('>')
		elif next_degree < current_degree:
			melodic_mvmt.append('<')
		else:
			melodic_mvmt.append('_')

	return ''.join(melodic_mvmt)

def set_melodic_figures(nested_scale_degrees):
	chosen_figurations = []
	melodic_figures = {
		(2, (1,)): "IPT", (0, (2, 1)): "DCN", (2, (-1, 1)): "OPT", 
		(0, (-1,)): "CN", (1, (-1,)): "PIN", (1, (2,)): "CIN",
		(1, (-2, -1)): "OPT", (4, (2,)): "IPT", (3, (4,)): "CIN",
		(3, (1,)): "IPT", (1, (0,)): "RET", (2, (2,)): "ANT",
		(3, (2,)): "IPT", (3, (1, 3)): "IPT", (2, (2, 3)): "OPT",
		(4, (1, 2)): "IPT", (1, (-2,)): "OPT", (1, (-1, 0)): "OPT",
		(3, (1, 2)): "IPT", (5, (3,)): "5PT", (0, (1,)): "CN",
		(1, (1,)): "ANT"
	}
	chord_index = 0
	for previous_melody_group, current_melody_group in zip(
	  nested_scale_degrees, nested_scale_degrees[1:]):
		chord_index += 1
		figure_group = []
		main_pitch_diff = current_melody_group[0] - previous_melody_group[0]
		main_pitch_direction = Voice.calculate_slope(main_pitch_diff)
		main_pitch_diff = abs(main_pitch_diff)
		embellish_degrees = previous_melody_group[1:]
		if not embellish_degrees:
			chosen_figurations.append(None)
			continue
		for previous_melody_note in embellish_degrees:
			pitch_diff = previous_melody_note - previous_melody_group[0]
			pitch_direction = Voice.calculate_slope(pitch_diff)
			if pitch_direction == 0:
				reference_direction = 0
			if 0 != main_pitch_direction == pitch_direction:
				reference_direction = 1 * abs(pitch_diff)
			elif 0 != main_pitch_direction != pitch_direction:
				reference_direction = -1 * abs(pitch_diff)
			elif main_pitch_direction == 0:
				reference_direction = pitch_diff
			figure_group.append(reference_direction)
		figure_group = tuple(figure_group)
		if chord_index == 8:
			modifier = "PICK_"
		else:
			modifier = ""
		chosen_figurations.append(
			modifier + melodic_figures[(main_pitch_diff, figure_group)]
		)
	print(chosen_figurations)
	return chosen_figurations



def unnest_sequence(sequence):
	unnested_sequence = []
	for group in sequence:
		for item in group:
			unnested_sequence.append(item)

	return unnested_sequence


def test_long_rest(obj):
	if "_" * 3 in obj.melodic_mvmt:
		return False
	return True


def test_triple_repeat(obj):
	all_rest_indices = set()
	start_index = 0
	while True:
		rest_index = obj.melodic_mvmt.find("__", start_index)
		if rest_index == -1:
			break
		all_rest_indices.add(rest_index)
		start_index = rest_index + 1
		# index 6 is only allowed if rhythm symbol -1 on index 6
		# not common enough to make a rule for your implementation
	if all_rest_indices - {3, 7}:
		return False
	return True


def test_double_repeat(obj):
	# same thing with index 6
	bad_single_rest_indices = {6, 10, 14}
	start_index = 0
	while True:
		rest_index = obj.melodic_mvmt.find("_", start_index)
		if rest_index in bad_single_rest_indices:
			return False
		if rest_index == -1:
			break
		start_index = rest_index + 1
	return True


def test_leaps_within_octave(obj):
	for current_degree, next_degree in zip(
	  obj.unnested_scale_degrees, obj.unnested_scale_degrees[1:]):
		if abs(current_degree - next_degree) > 7:
			return False
	return True


def test_end_leap(obj):
	last_degree = obj.chosen_scale_degrees[-2]
	penultimate_degree = obj.chosen_scale_degrees[-3]
	if abs(penultimate_degree - last_degree) > 4:
		return False
	return True


def test_predominant_descent(obj):
	if obj.relevant_melodic_mvmt.count('>') > obj.relevant_melodic_mvmt.count('<'):
		return False
	return True


def test_large_leap_nested(obj):
	chord_index = 1
	for current_degree, next_degree in zip(
	  obj.chosen_scale_degrees, obj.chosen_scale_degrees[1:]):
		if (abs(next_degree - current_degree) > 4 and 
		  chord_index not in {4, 8}):
			return False
		chord_index += 1
	return True


def test_large_leap_unnested(obj):
	previous_melody_note = obj.nested_scale_degrees[0][0]
	for chord_index, melody_group in enumerate(obj.nested_scale_degrees):
		for fig_index, current_melody_note in enumerate(melody_group):
			if (abs(current_melody_note - previous_melody_note) > 4 and 
			  (fig_index != 0 or chord_index not in {4, 8})):
				return False
			previous_melody_note = current_melody_note
	return True


def test_proper_leaps(obj):
	# breaking this rule is too advanced for you
	unnested_antecedent = Voice.merge_lists(*obj.nested_scale_degrees[:8])
	unnested_consequent = Voice.merge_lists(*obj.nested_scale_degrees[8:])
	proper_antecedent_leaps = Voice.has_proper_leaps(unnested_antecedent)
	proper_consequent_leaps = Voice.has_proper_leaps(unnested_consequent)
	return proper_antecedent_leaps and proper_consequent_leaps


def test_nested_climaxes(obj):

	section1_scale_degrees = obj.chosen_scale_degrees[0:4]
	section2_scale_degrees = obj.chosen_scale_degrees[4:8]
	section3_scale_degrees = obj.chosen_scale_degrees[8:12]
	section4_scale_degrees = obj.chosen_scale_degrees[12:]

	relevant_sections = (
		section1_scale_degrees, section2_scale_degrees, 
		section3_scale_degrees
	)

	for section_scale_degrees in relevant_sections:
		section_max_degree = max(section_scale_degrees)
		if section_scale_degrees.count(section_max_degree) > 2:
			return False
		if section_scale_degrees.count(section_max_degree) == 2:
			for scale_degree0, scale_degree1 in zip(
			  section_scale_degrees, section_scale_degrees[1:]):
				if (scale_degree0 == section_max_degree and 
				  scale_degree0 == scale_degree1):
					break
			else:
				return False

	if max(section1_scale_degrees) == max(section2_scale_degrees):
		return False
	if max(section3_scale_degrees) <= max(section4_scale_degrees):
		return False

	return True


def test_late_melodic_jukes(obj):
	quick_turn_indices = {2, 5, 6, 9, 10, 13}
	for chord_index, melodic_move in enumerate(obj.relevant_melodic_mvmt):
		move_group = obj.relevant_melodic_mvmt[chord_index:chord_index + 1]
		if (move_group in {"><>", "<><"} 
		  and chord_index not in quick_turn_indices):
			return False
	return True

# def test_turns(obj):
# 	return Voice.get_turns(obj.chosen_scale_degrees) <= 8

# def test_halfway_pause(obj):
# 	if obj.chosen_scale_degrees[6] != obj.chosen_scale_degrees[7]:
# 		return False
# 	return True

# def test_move_from_tonic(obj):
# 	if obj.chosen_scale_degrees[0] == obj.chosen_scale_degrees[1]:
# 		return False
# 	return True

# think of a way to handle these cross_duplicates
# def test_cross_duplicates(obj):
# 	return not Voice.has_cross_duplicates(obj.chosen_scale_degrees)

# def test_unnested_cross_duplicates(obj):
# 	return not Voice.has_cross_duplicates(obj.unnested_scale_degrees)

# def test_true_climax(obj):
# 	return max(obj.unnested_scale_degrees) >= 6

def test_unnested_climaxes(obj):
	section1 = Voice.merge_lists(*obj.nested_scale_degrees[:4])
	section2 = Voice.merge_lists(*obj.nested_scale_degrees[4:8])
	section3 = Voice.merge_lists(*obj.nested_scale_degrees[8:12])
	section4 = Voice.merge_lists(*obj.nested_scale_degrees[12:])

	if max(section1) == max(section2):
		return False
	if max(section3) <= max(section4):
		return False
	return True

def test_bounds(obj):
	if min(obj.unnested_scale_degrees) < -3:
		return False
	if max(obj.unnested_scale_degrees) > 7:
		return False
	if max(obj.unnested_scale_degrees) < 5:
		return False
	section1 = Voice.merge_lists(*obj.nested_scale_degrees[:3])
	if min(section1) < 0:
		return False
	return True

def test_still_figures(obj):
	num_still_figures = obj.chosen_figurations.count("CN")
	num_still_figures += obj.chosen_figurations.count("DN")
	num_still_figures += obj.chosen_figurations.count("DCN")

	return num_still_figures <= 2

def test_irregular_figures(obj):
	if obj.chosen_figurations.count("OPT") > 4:
		return False
	if obj.chosen_figurations.count("OPT") > 2 and not obj.repeat_intro:
		return False
	return True 

melodies = [
	MelodyFrame([
		[0, 1], [2, 3], [4, 6, 5], [4], 
		[4, 5], [6, 7, 5], [4, 3], [4], 
		[5, 6], [4, 2], [3, 5, 4], [2, 0],
		[1, -1], [-3, 1], [0], [0]
	], False), MelodyFrame([
		[0, 1], [2, 4], [3, 2], [0], 
		[7, 7], [6, 4], [4], [4],
		[7, 6], [4, 2], [3, 2], [0, -1],
		[0, 0], [-1, -1], [0], [0]
	], True), MelodyFrame([
		[0, 2], [3, 2], [3, 2, 0], [0, 2],
		[3, 4], [6, 4, 3], [4], [4, 3],
		[4, 6], [7, 6], [4, 3, 2], [0, -1],
		[0, 2], [-1, -1], [0], [0],
	], True), MelodyFrame([
		[2, 3], [4, 5, 4], [3, 1], [-1, 0, 1], 
		[2, 0], [0, -1, 0], [1, -1], [-3, 0], 
		[2, 3], [4, 5, 4], [3, 1], [-1, 0, 1],
		[2, 1, 0], [-1, -2, -1], [0], [0] 
	], True), MelodyFrame([
		[0, 1], [2, 3], [4], [4, 4], 
		[3, 4], [5, 3], [4], [4, 4],
		[3, 4], [5, 3], [4, 5, 4], [3, 2],
		[1, 2], [1, 0], [0], [0]
	], True)
]

# MelodyFrame([
# 		[0, 0], [4, 4], [1, 2, 1], [0],
# 		[7, 6], [4, 5, 3], [4,], [4],
# 		[7, 7], [6, 4], [4, 3, 2], [1],
# 		[3, 2], [1, 0, -1], [0,], [0]
# 	], False)