import idioms.basics as bsc

consonant_triads = {bsc.I, bsc.III, bsc.IV, bsc.V, bsc.VI, bsc.I_MAJOR}

expand_tonic1 = bsc.expand_tonic1
accent_tonic = bsc.accent_tonic
to_subdom2_strong = bsc.to_subdom2_strong

to_subdom1_strong = bsc.to_subdom1_strong
to_subdom1_strong[bsc.I] = (bsc.IV, bsc.IV_MAJOR, bsc.II6)
to_subdom1_weak = bsc.to_subdom1_weak
to_subdom1_weak[bsc.I] = (bsc.IV, bsc.IV_MAJOR, bsc.II6, -bsc.VI, -bsc.IV6)


half_cadence1 = bsc.half_cadence1
half_cadence1[bsc.IV_MAJOR] = (
	bsc.V, -bsc.V6, -bsc.V65, -bsc.VII6, -bsc.V43, bsc.V42)
imperfect_auth_cadence2 = bsc.imperfect_auth_cadence2
imperfect_auth_cadence2[bsc.IV_MAJOR] = (
	-bsc.V6, -bsc.V65, -bsc.VII6, -bsc.V43, bsc.V42)

imperfect_auth_cadence1 = bsc.imperfect_auth_cadence1
perfect_auth_cadence2 = bsc.perfect_auth_cadence2
perfect_auth_cadence2[bsc.IV_MAJOR] = (bsc.V, bsc.V7)

perfect_auth_cadence1 = bsc.perfect_auth_cadence1
perfect_auth_cadence1[bsc.V] = (-bsc.I, -bsc.I_MAJOR)
perfect_auth_cadence1[bsc.V7] = (-bsc.I, -bsc.I_MAJOR)

chord_sequences = {
	"TP": expand_tonic1, "TA":accent_tonic, "SA1-M": to_subdom1_weak,
	"SA1+M": to_subdom1_strong, "SA2+M": to_subdom2_strong, "HC1": half_cadence1,
	"IAC2": imperfect_auth_cadence2, "IAC1": imperfect_auth_cadence1, 
	"PAC2": perfect_auth_cadence2, "PAC1":perfect_auth_cadence1
}