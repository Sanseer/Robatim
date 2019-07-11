import generate.idioms.basics as bsc

consonant_triads = {bsc.I, bsc.II, bsc.III, bsc.IV, bsc.V, bsc.VI}
key_sigs = ("C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F")
pitches_to_degrees = { 0:0, 2:1, 4:2, 5:3, 7:4, 9:5, 11:6}


expand_tonic1 = bsc.expand_tonic1
accent_tonic = bsc.accent_tonic

to_subdom2_strong = bsc.to_subdom2_strong
to_subdom2_strong[bsc.I] = (bsc.IV, bsc.II6, bsc.II)
to_subdom2_strong[bsc.I6] = (bsc.IV, bsc.II6, -bsc.II)
to_subdom2_strong[bsc.VI] = (-bsc.IV, -bsc.II6, -bsc.II)

to_subdom1_strong = bsc.to_subdom1_strong
to_subdom1_strong[bsc.I] = (bsc.IV, bsc.II6, bsc.II)
to_subdom1_strong[bsc.I6] = (bsc.IV, bsc.II6, -bsc.II)
to_subdom1_strong[bsc.VI] = (-bsc.IV, -bsc.II6, -bsc.II)

to_subdom1_weak = bsc.to_subdom1_weak
to_subdom1_weak[bsc.I] = (bsc.IV, bsc.II6, bsc.II, -bsc.VI, -bsc.IV6)
to_subdom1_weak[bsc.I6] = (bsc.IV, bsc.II6, -bsc.II)
to_subdom1_weak[bsc.VI] = (-bsc.IV, -bsc.II6, bsc.IV6, -bsc.II, bsc.IV6)

half_cadence1 = bsc.half_cadence1
imperfect_auth_cadence2 = bsc.imperfect_auth_cadence2
imperfect_auth_cadence1 = bsc.imperfect_auth_cadence1
perfect_auth_cadence2 = bsc.perfect_auth_cadence2
perfect_auth_cadence1 = bsc.perfect_auth_cadence1

chord_sequences = {
	"TP": expand_tonic1, "TA":accent_tonic, "SA1-M": to_subdom1_weak,
	"SA1+M": to_subdom1_strong, "SA2+M": to_subdom2_strong, "HC1": half_cadence1,
	"IAC2": imperfect_auth_cadence2, "IAC1": imperfect_auth_cadence1, 
	"PAC2": perfect_auth_cadence2, "PAC1":perfect_auth_cadence1
}