from generate.idioms import default_chords as df

key_sigs = ("C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F")

df.subdom_accent_1["0I"].append("+II")
df.subdom_accent_1["+I6"].append("+II")
df.subdom_accent_2["0I"].append("+II")
df.subdom_accent_2["+I6"].append("+II")
df.subdom_noaccent_1["0I"].append("+II")
df.subdom_noaccent_1["+I6"].append("+II")

df.extend_subdom_3_1["0I"].extend((
	("+II", "+I6", "+II6"), ("+II6", "+I6", "+II"), ("+I6", "+I6", "+II")))
df.extend_subdom_3_1["+I6"].extend((
	("+II", "+I6", "+II6"), ("+II6", "+I6", "+II"), ("0I", "0I", "+II")))

df.perfect_auth_cadence1["+IV"].append("+IV_MINOR")

chord_ids = {
	"1HC1": df.x1_half_cadence1, "1HC2": df.x1_half_cadence2, 
	"2HC1": df.x2_half_cadence1, "2HC2": df.x2_half_cadence2,
	"PAC1": df.perfect_auth_cadence1, "SDOM_AT_-2": df.subdom_accent_2,
	"SDOM_AT_-1": df.subdom_accent_1, "SDOM_AF_-1": df.subdom_noaccent_1,
	"1EXTON1": df.extend_tonic_1_1, "1EXTON2": df.extend_tonic_1_2,
	"3SDOM_EX1": df.extend_subdom_3_1, 
}

