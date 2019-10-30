from generate.voices.voice import Voice

class MelodyFrame:

	def __init__(self, nested_scale_degrees, pickup=False):
		self.pickup = pickup
		self.nested_scale_degrees = nested_scale_degrees
		self.unnested_scale_degrees = unnest_sequence(self.nested_scale_degrees)
		self.chosen_scale_degrees = make_base_melody(self.nested_scale_degrees)
		self.melodic_mvmt = make_melodic_ramp(
			self.chosen_scale_degrees, self.pickup)
		self.relevant_melodic_mvmt = self.melodic_mvmt[1:]

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
		# index 6 is only allowed if rhythm symbol -1 on index 8
	if all_rest_indices - {3, 6, 7}:
		return False
	# add conditional here
	return True

def test_halfway_pause(obj):
	if obj.chosen_scale_degrees[6] != obj.chosen_scale_degrees[7]:
		return False
	return True

def test_move_from_tonic(obj):
	if obj.chosen_scale_degrees[0] == obj.chosen_scale_degrees[1]:
		return False
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

def test_octave_leap(obj):
	chord_index = 1
	for current_degree, next_degree in zip(
	  obj.chosen_scale_degrees, obj.chosen_scale_degrees[1:]):
		if (abs(next_degree - current_degree) == 7 and 
		  chord_index not in {4, 8}):
			return False
		chord_index += 1
	return True

def test_proper_leaps(obj):
	if not Voice.has_proper_leaps(obj.unnested_scale_degrees):
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
		[0, 0], [4, 4], [1, 2, 1], [0],
		[7, 6], [4, 5, 3], [4,], [4],
		[7, 7], [6, 4], [4, 3, 2], [1],
		[3, 2], [1, 0, -1], [0,], [0]
	], False), MelodyFrame([
		[0, 2], [3, 2], [3, 2], [0],
		[3, 4], [6, 4, 3], [4], [4],
		[4, 6], [7, 6], [4, 3, 2], [0, -1],
		[0, 2], [-1, -1], [0], [0],
	], True)
]

# print(melodies[2].melodic_mvmt)
