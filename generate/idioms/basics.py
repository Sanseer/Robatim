# 2/4, 3/4, 6/8, 9/8
# exclude quadruple time b/c it behaves similarly to duple time
# may readd later
time_sigs = ((2,2), (3,2), (2,3), (3,3))

chord_patterns_8 = []
chord_patterns_16 = [
	["TON"] + ["RPT"] * 5 + ["HC", "RPT"] + ["TON"] * 5 + ["PAC1", "PAC2", "RPT"],
	["TON"] + ["RPT"] * 5 + ["HC", "RPT"] + ["TON"] * 4 + ["PAC1", "RPT", "PAC2", "RPT"]
]

# I I I I / I I V V
# I I I I / V V I I

# 0 = rhythm1
# 1 = rhythm2 etc.
# -1 = sustain
rhythm_patterns = (
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1)), 
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0 , 2, -1), (0, 2, 0, -1), 
		(0, 1, 2, -1), (0, 2, 1, -1)),
	((0, 0, 0, -1), (0, 0, 1, -1), (0, 1, 0, -1), (0, 0, 2, -1), (0, 2, 0, -1),
		(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 2, 0), (0, 2, 0, 0), 
		(0, 1, 2, -1), (0, 1, 2, 0), (0, 2, 1, -1), (0, 2, 1, 0)),
	((0, 0, -1, -1), (0, 1, -1, -1), (0, 2, -1, -1))
)




