from generate.idioms import default_chords as df

key_sigs = ("C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F")

df.subdom_accent_1["0I"].append("+II")
df.subdom_accent_1["+I6"].append("+II")
df.subdom_noaccent_1["0I"].append("+II")
df.subdom_noaccent_1["+I6"].append("+II")

df.perfect_auth_cadence1["+IV"].append("+IV_MINOR")

chord_ids = {
	"1HC1": df.x1_half_cadence1, "1HC2": df.x1_half_cadence2, 
	"2HC1": df.x2_half_cadence1, "2HC2": df.x2_half_cadence2,
	"PAC1": df.perfect_auth_cadence1,
	"SDOM_AT_-1": df.subdom_accent_1, "SDOM_AF_-1": df.subdom_noaccent_1,
	"1EXTON1": df.extend_tonic_1_1, "1EXTON2": df.extend_tonic_1_2
}

