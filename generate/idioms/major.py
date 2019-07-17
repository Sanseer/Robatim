import generate.idioms.basics as bsc

consonant_triads = {bsc.I, bsc.II, bsc.III, bsc.IV, bsc.V, bsc.VI}
key_sigs = ("C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F")
pitches_to_degrees = { 0:0, 2:1, 4:2, 5:3, 7:4, 9:5, 11:6 }


expand_tonic1 = bsc.expand_tonic1
double_neighbor1 = bsc.double_neighbor1
accent_tonic = bsc.accent_tonic

pass_to_tonic = bsc.pass_to_tonic
pass_to_subdom = bsc.pass_to_subdom

strong_to_subdom2_strong = bsc.strong_to_subdom2_strong
strong_to_subdom2_strong[bsc.I] = (bsc.II, bsc.II6, bsc.IV, -bsc.IV6, -bsc.VI)
strong_to_subdom2_strong[bsc.I6] = (-bsc.II, bsc.II6, bsc.IV)
strong_to_subdom2_strong[bsc.VI] = (-bsc.II, -bsc.II6, -bsc.IV, bsc.IV6)

strong_to_subdom1_strong = bsc.strong_to_subdom1_strong
strong_to_subdom1_strong[bsc.I] = (bsc.II, bsc.II6, bsc.IV, bsc.I64, -bsc.IV6, -bsc.VI)
strong_to_subdom1_strong[bsc.I6] = (-bsc.II, bsc.II6, bsc.IV, bsc.I64)
strong_to_subdom1_strong[bsc.II6] = (-bsc.II, bsc.I64)
strong_to_subdom1_strong[bsc.IV] = (-bsc.II, bsc.II6, bsc.I64)
strong_to_subdom1_strong[bsc.VI] = (-bsc.II, -bsc.II6, -bsc.IV, -bsc.I64, bsc.IV6)
strong_to_subdom1_strong[bsc.IV6] = (-bsc.II, -bsc.II6, -bsc.IV, -bsc.I64)

strong_to_subdom1_weak = bsc.strong_to_subdom1_weak
strong_to_subdom1_weak[bsc.I] = (bsc.II, bsc.II6, bsc.IV, -bsc.IV6, -bsc.VI)
strong_to_subdom1_weak[bsc.I6] = (-bsc.II, bsc.II6, bsc.IV)
strong_to_subdom1_weak[bsc.II] = (bsc.II6,)
strong_to_subdom1_weak[bsc.IV6] = (-bsc.II, -bsc.II6, -bsc.IV)
strong_to_subdom1_weak[bsc.VI] = (-bsc.II, -bsc.II6, -bsc.IV, bsc.IV6)

weak_to_subdom2_strong = bsc.weak_to_subdom2_strong
weak_to_subdom1_strong = bsc.weak_to_subdom1_strong
weak_to_subdom1_strong[bsc.I] = (
	bsc.II, bsc.II6, bsc.IV, bsc.I64, -bsc.IV6, -bsc.VI)
weak_to_subdom1_strong[bsc.I6] = (-bsc.II, bsc.II6, bsc.IV, bsc.I64)
weak_to_subdom1_strong[bsc.VI] = (-bsc.II, -bsc.II6, -bsc.IV, -bsc.I64)
weak_to_subdom1_strong[bsc.IV6] = (-bsc.II, -bsc.II6, -bsc.IV, -bsc.I64)

half_cadence1 = bsc.half_cadence1
half_cadence2 = bsc.half_cadence2

imperfect_auth_cadence2 = bsc.imperfect_auth_cadence2
imperfect_auth_cadence2[bsc.VI] = (bsc.V6, bsc.V65)
imperfect_auth_cadence2[bsc.IV6] = (bsc.V6, bsc.V65)

imperfect_auth_cadence1 = bsc.imperfect_auth_cadence1
perfect_auth_cadence2 = bsc.perfect_auth_cadence2
perfect_auth_cadence1 = bsc.perfect_auth_cadence1

chord_sequences = {
	"TP": expand_tonic1, "TA":accent_tonic, "TDN1": double_neighbor1, 
	"TPT-I": pass_to_tonic, "TPS-I": pass_to_subdom, 
	"M+SA1-M": strong_to_subdom1_weak, "M-SA2+M": weak_to_subdom2_strong, 
	"M+SA1+M": strong_to_subdom1_strong, "M-SA1+M": weak_to_subdom1_strong,  
	"M+SA2+M": strong_to_subdom2_strong, "HC1": half_cadence1, 
	"HC2": half_cadence1,"IAC2": imperfect_auth_cadence2, 
	"IAC1": imperfect_auth_cadence1, "PAC2": perfect_auth_cadence2, 
	"PAC1":perfect_auth_cadence1
}