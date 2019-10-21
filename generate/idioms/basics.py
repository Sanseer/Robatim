# exclude 9/8 because uneven divisions
# 2/4, 3/4, 6/8, 4/4, 12/8
time_sigs = ((2,2), (3,2), (2,3), (4,2), (3,2), (4,3))

chord_patterns_8 = []
tonic_antecedents = (
	("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "HC1", "RPT"),
	("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "HC1", "RPT"),
	("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "HC1", "RPT")
)
tonic_consequents = (
	("HC2", "RPT", "RPT", "RPT", "RPT", "PAC1", "TON", "RPT"),
	("HC2", "RPT", "RPT", "RPT", "PAC1", "RPT", "TON", "RPT"),
	)
def is_divisble_by(sequence, divisor):
	if divisor < 2:
		return True

	count_index = 0
	for current_item in sequence:
		if count_index % divisor == 0 and current_item != "RPT":
			return False
		count_index += 1
	return True

chord_patterns_16 = {}
for ant_pattern in tonic_antecedents:
	for cons_pattern in tonic_consequents:
		full_pattern = ant_pattern + cons_pattern
		if is_divisble_by(full_pattern, 2):
			accelerate = True
		else:
			accelerate = False
		chord_patterns_16[full_pattern] = accelerate

# 0 = rhythm1
# 1 = rhythm2 etc.
# -1 = sustain
rhythm_patterns = (
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1)), 
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0 , 2, -1), (0, 2, 0, -1), 
		(0, 1, 2, -1), (0, 2, 1, -1), (0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
		(0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2)),
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0, 2, -1), (0, 2, 0, -1),
		(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 2, 0), (0, 2, 0, 0), 
		(0, 1, 2, -1), (0, 1, 2, 0), (0, 2, 1, -1), (0, 2, 1, 0)),
	((0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1))
)





