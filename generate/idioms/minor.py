from generate.idioms import default_chords as df

key_sigs = ("A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D")

df.subdom_accent_1["0I"].append("+IV_MAJOR")
df.subdom_accent_1["+I6"].append("+IV_MAJOR")
df.subdom_noaccent_1["0I"].append("+IV_MAJOR")
df.subdom_noaccent_1["+I6"].append("+IV_MAJOR")

df.extend_subdom_3_1["0I"].append(("+I6", "+I6", "+IV_MAJOR"))
df.extend_subdom_3_1["+I6"].append(("0I", "0I", "+IV_MAJOR"))

chord_ids = {
	"1HC1": df.x1_half_cadence1, "1HC2": df.x1_half_cadence2, 
	"2HC1": df.x2_half_cadence1, "2HC2": df.x2_half_cadence2,
	"1PAC_EX1": df.x1_perfect_auth_cadence1, 
	"2PAC_EX1": df.x2_perfect_auth_cadence1,
	"SDOM_AT_-2": df.subdom_accent_2, "SDOM_AT_-1": df.subdom_accent_1, 
	"SDOM_AF_-1": df.subdom_noaccent_1,
	"1EXTON1": df.extend_tonic_1_1, "1EXTON2": df.extend_tonic_1_2,
	"3SDOM_EX1": df.extend_subdom_3_1,
}