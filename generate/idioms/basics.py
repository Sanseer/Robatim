# exclude 9/8 because uneven divisions
# 2/4, 3/4, 6/8, 4/4, 12/8
time_sigs = ((2,2), (3,2), (2,3), (4,2), (3,2), (4,3))

chord_patterns_8 = []
tonic_antecedents = (
	("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "1HC1", "RPT"),
	("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "1HC1", "RPT"),
	("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "1HC1", "RPT"),
	("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "2HC1"),
	("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "2HC1"),
	("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "2HC1"),

	("TON", "RPT", "RPT", "RPT", "SDOM_AT_-1", "RPT", "1HC1", "RPT"),
	("TON", "RPT", "RPT", "RPT", "RPT", "SDOM_AF_-1", "1HC1", "RPT"),
	("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "SDOM_AF_-1", "1HC1", "RPT"),
	("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "SDOM_AF_-1", "1HC1", "RPT"),
	("TON", "RPT", "RPT", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "1HC1", "RPT"),

	("TON", "RPT", "RPT", "RPT", "RPT", "SDOM_AF_-1", "2HC1"),
	("TON", "RPT", "RPT", "RPT", "SDOM_AT_-1", "RPT", "2HC1"),
	("TON", "RPT", "RPT", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "2HC1"),
	("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "SDOM_AF_-1", "2HC1"),
	("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "SDOM_AF_-1", "2HC1"),
)
tonic_consequents = (
	("1HC2", "RPT", "RPT", "RPT", "RPT", "1PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "RPT", "RPT", "RPT", "1PAC_EX1", "TON", "RPT"),
	("1HC2", "RPT", "RPT", "RPT", "1PAC_EX1", "RPT", "TON", "RPT"),
	("2HC2", "RPT", "RPT", "RPT", "1PAC_EX1", "RPT", "TON", "RPT"),

	("1HC2", "RPT", "RPT", "RPT", "SDOM_AT_-1", "1PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "RPT", "RPT", "SDOM_AT_-1", "1PAC_EX1", "TON", "RPT"),
	("1HC2", "RPT", "SDOM_AT_-1", "RPT", "1PAC_EX1", "RPT", "TON", "RPT"),
	("2HC2", "RPT", "SDOM_AT_-1", "RPT", "1PAC_EX1", "RPT", "TON", "RPT"),

	("1HC2", "RPT", "RPT", "SDOM_AF_-1", "1PAC_EX1", "RPT", "TON", "RPT"),
	("2HC2", "RPT", "RPT", "SDOM_AF_-1", "1PAC_EX1", "RPT", "TON", "RPT"),
	("1HC2", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "1PAC_EX1", "RPT", "TON", "RPT"),
	("2HC2", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "1PAC_EX1", "RPT", "TON", "RPT"),

	("1HC2", "RPT", "3SDOM_EX1", "1PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "3SDOM_EX1", "1PAC_EX1", "TON", "RPT"),

	("1HC2", "RPT", "RPT", "RPT", "2PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "RPT", "RPT", "2PAC_EX1", "TON", "RPT"),

	("1HC2", "RPT", "SDOM_AT_-1", "RPT", "2PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "SDOM_AT_-1", "RPT", "2PAC_EX1", "TON", "RPT"),
	("1HC2", "RPT", "RPT", "SDOM_AF_-1", "2PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "RPT", "SDOM_AF_-1", "2PAC_EX1", "TON", "RPT"),
	("1HC2", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "2PAC_EX1", "TON", "RPT"),
	("2HC2", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "2PAC_EX1", "TON", "RPT"),
)
def allows_truncation(sequence, divisor, repeat_value):
	"""Check last item equality of list dividends"""
	if divisor < 2:
		return False
	if len(sequence) < divisor:
		return False

	for index, current_item in enumerate(sequence):
		item_num = index + 1
		if item_num % divisor == 0 and current_item != repeat_value:
			return False
	return True

chord_patterns_16 = {}
for ante_pattern in tonic_antecedents:
	for cons_pattern in tonic_consequents:
		if ante_pattern[-1] == "2HC1" and cons_pattern[0] == "1HC2":
			continue
		if ante_pattern[-2] == "1HC1" and cons_pattern[0] == "2HC2":
			continue
		full_pattern = ante_pattern + cons_pattern
		if len(full_pattern) == 16 and allows_truncation(full_pattern, 2, "RPT"):
			accelerate = False
		else:
			accelerate = True
		chord_patterns_16[full_pattern] = accelerate

# 0 = rhythm1
# 1 = rhythm2 etc.
# -1 = sustain
# -2 = pickup
# duplicate patterns are used to alter selected pattern probability
rhythm_patterns = (
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1)), 
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0 , 2, -1), (0, 2, 0, -1), 
		(0, 1, 2, -1), (0, 2, 1, -1), (0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
		(0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
		(0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2),
		(0, 0, -1, -2), (0, 1, -1, -2), (0, 2, -1, -2)),
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0, 2, -1), (0, 2, 0, -1),
		(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 2, 0), (0, 2, 0, 0), 
		(0, 1, 2, -1), (0, 1, 2, 0), (0, 2, 1, -1), (0, 2, 1, 0)),
	((0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1))
)





