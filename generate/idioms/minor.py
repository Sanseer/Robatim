import generate.idioms.basics as bsc

consonant_triads = {bsc.I, bsc.III, bsc.IV, bsc.V, bsc.VI, bsc.I_MAJOR}
key_sigs = ("A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D")
pitches_to_degrees = { 0:0, 2:1, 3:2, 5:3, 7:4, 8:5, 9:5, 10:6, 11:6}
# includes melodic minor

expand_tonic1 = bsc.expand_tonic1
expand_tonic2 = bsc.expand_tonic2
accent_tonic = bsc.accent_tonic

pass_to_tonic = bsc.pass_to_tonic
pass_to_subdom = bsc.pass_to_subdom

# any motion that allows movement to minor IV also allows major IV?
strong_to_subdom2_strong = bsc.strong_to_subdom2_strong
strong_to_subdom2_strong[bsc.I] = (bsc.II6, bsc.IV, bsc.IV_MAJOR, -bsc.IV6, -bsc.IV6_MAJOR, -bsc.VI)
strong_to_subdom2_strong[bsc.I6] = (bsc.II6, bsc.IV, bsc.IV_MAJOR)
strong_to_subdom2_strong[bsc.VI] = (-bsc.II6, -bsc.IV, -bsc.IV_MAJOR, bsc.IV6, bsc.IV6_MAJOR)

strong_to_subdom1_strong = bsc.strong_to_subdom1_strong
strong_to_subdom1_strong[bsc.I] = (bsc.II6, bsc.IV, bsc.IV_MAJOR, bsc.I64, 
	-bsc.IV6, -bsc.IV6_MAJOR, -bsc.VI)
strong_to_subdom1_strong[bsc.I6] = (bsc.II6, bsc.IV, bsc.IV_MAJOR, bsc.I64)
strong_to_subdom1_strong[bsc.IV_MAJOR] = (-bsc.II_MAJOR, -bsc.II6_MAJOR, bsc.I64,)
strong_to_subdom1_strong[bsc.IV6_MAJOR] = (-bsc.IV_MAJOR, -bsc.I64,)

strong_to_subdom1_weak = bsc.strong_to_subdom1_weak
strong_to_subdom1_weak[bsc.I] = (bsc.II6, bsc.IV, bsc.IV_MAJOR, -bsc.IV6, 
	-bsc.IV6_MAJOR, -bsc.VI)
strong_to_subdom1_weak[bsc.I6] = (bsc.II6, bsc.IV, bsc.IV_MAJOR)
strong_to_subdom1_weak[bsc.IV_MAJOR] = (-bsc.II_MAJOR, bsc.II6_MAJOR)
strong_to_subdom1_weak[bsc.IV6_MAJOR] = (-bsc.II_MAJOR, -bsc.II6_MAJOR, -bsc.IV_MAJOR)

weak_to_subdom2_strong = bsc.weak_to_subdom2_strong
weak_to_subdom1_strong = bsc.weak_to_subdom1_strong
weak_to_subdom1_strong[bsc.I] = (bsc.II6, bsc.IV, bsc.I64, -bsc.IV6, -bsc.VI)
weak_to_subdom1_strong[bsc.I6] = (bsc.II6, bsc.IV, bsc.I64)
weak_to_subdom1_strong[bsc.VI] = (-bsc.II6, -bsc.IV, -bsc.I64)
weak_to_subdom1_strong[bsc.IV6] = (-bsc.II6, -bsc.IV, -bsc.I64)
weak_to_subdom1_strong[bsc.IV6_MAJOR] = (-bsc.II6, -bsc.IV, -bsc.I64)

half_cadence1 = bsc.half_cadence1
half_cadence1[bsc.II_MAJOR] = (bsc.V,)
half_cadence1[bsc.II6_MAJOR] = (bsc.V,)
half_cadence1[bsc.IV_MAJOR] = (bsc.V,)
half_cadence1[bsc.IV6_MAJOR] = (-bsc.V,)

half_cadence2 = bsc.half_cadence2
half_cadence2[bsc.II_MAJOR] = (
	bsc.V, -bsc.V6, -bsc.V65, bsc.VII6, bsc.V43, bsc.V42)
half_cadence2[bsc.II6_MAJOR] = (
	bsc.V, -bsc.V6, -bsc.V65, -bsc.VII6, -bsc.V43, bsc.V42)
half_cadence2[bsc.IV_MAJOR] = (
	bsc.V, -bsc.V6, -bsc.V65, -bsc.VII6, -bsc.V43, bsc.V42)
half_cadence1[bsc.IV6_MAJOR] = (-bsc.V, -bsc.V6, -bsc.V65)

imperfect_auth_cadence2 = bsc.imperfect_auth_cadence2
imperfect_auth_cadence2[bsc.IV_MAJOR] = (
	-bsc.V6, -bsc.V65, -bsc.VII6, -bsc.V43, bsc.V42)
imperfect_auth_cadence2[bsc.IV6_MAJOR] = (bsc.V6, bsc.V65)
imperfect_auth_cadence1 = bsc.imperfect_auth_cadence1

perfect_auth_cadence2 = bsc.perfect_auth_cadence2
perfect_auth_cadence2[bsc.II_MAJOR] = (bsc.V, bsc.V7)
perfect_auth_cadence2[bsc.II6_MAJOR] = (bsc.V, bsc.V7)
perfect_auth_cadence2[bsc.IV_MAJOR] = (bsc.V, bsc.V7)
perfect_auth_cadence2[bsc.IV6_MAJOR] = (-bsc.V, -bsc.V7)

perfect_auth_cadence1 = bsc.perfect_auth_cadence1
perfect_auth_cadence1[bsc.V] = (-bsc.I, bsc.I, -bsc.I_MAJOR, bsc.I_MAJOR)
perfect_auth_cadence1[bsc.V7] = (-bsc.I, bsc.I,-bsc.I_MAJOR, bsc.I_MAJOR)

chord_sequences = {
	"TP": expand_tonic1, "TA":accent_tonic, "TDN": expand_tonic2, 
	"TPT-I": pass_to_tonic, "TPS-I": pass_to_subdom, 
	"M+SA1-M": strong_to_subdom1_weak, "M-SA2+M": weak_to_subdom2_strong, 
	"M+SA1+M": strong_to_subdom1_strong, "M-SA1+M": weak_to_subdom1_strong,  
	"M+SA2+M": strong_to_subdom2_strong, "HC1": half_cadence1, 
	"HC2": half_cadence1,"IAC2": imperfect_auth_cadence2, 
	"IAC1": imperfect_auth_cadence1, "PAC2": perfect_auth_cadence2, 
	"PAC1":perfect_auth_cadence1
}