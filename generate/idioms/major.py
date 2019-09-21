key_sigs = ("C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F")

reset_tonic = {"0I": ("0I",), "+V": ("0I",)}
half_cadence = {"0I": ("+V",)}

perfect_auth_cadence1 = {"0I": ("+V",)}
perfect_auth_cadence2 = {"+V": ("0I",)}

chord_ids = {
	"TON": reset_tonic, "HC": half_cadence, "PAC1": perfect_auth_cadence1,
	"PAC2": perfect_auth_cadence2
}