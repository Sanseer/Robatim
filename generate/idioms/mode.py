class Mode():

	def __init__(self, mode):
		self.chord_ids = {
			"1HC1": {
				"0I": ("+V", "-V", "-V6", "-V65", "+VII6", "+V43", "+V42"), 
				"+I6": ("+V", "-V6", "-V65", "+VII6", "+V43", "+V42"),
				"+II": ("+V", "-V","-V6", "-V65", "+VII6", "+V43", "+V42"), 
				"+II6": ("+V", "+V42", "-V6", "-V65", "+VII6", "+V43"), 
				"+IV": ("+V", "+V42", "-V6", "-V65", "+VII6", "+V43"),
				"+IV_MAJOR": ("+V", "+VII6", "+V43", "+V42"),
				"-VI": ["-V"], "-IV6": ["-V"], "-IV6_MAJOR": ("-V", "-V6", "-V65"),
				"-II": ("-V",), "-II6": ("-V",), "-IV": ("-V",),
			}, "1HC2": {
					"+V": ("0I",), "-V": ("0I",), "-V6": ("0I",), "-V65": ("0I",), 
					"+VII6": ("0I", "+I6"), "+V43": ("0I", "+I6"), "+V42": ("+I6",),
			}, "2HC1": {
					"0I": (
						("-V6", "-V"), ("-V", "-V6"), ("-V6", "+V43"), 
						("-V65", "+V43"), ("-V6", "+VII6"), ("-V65", "+VII6"), 
						("+V43", "-V65"), ("+V", "+V42"), ("+V43", "+V42"), 
						("+VII6", "+V42"), ("-V6", "+V42"), ("-V65", "+V42"), 
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V42")),
					"+I6": (("+V42", "-V65"), ("+I64", "+V"), ("+I64", "-V"), 
						("+I64", "+V42")), 
					"+II": (("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V42")), 
					"+II6": (("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V42")), 
					"+IV": (("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V42")),
					"+IV_MAJOR": (
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V42")),
					"-VI": (("-I64", "-V"),), "-IV6": (("-I64", "-V"),),
					"-IV6_MAJOR": (
						("-I64", "-V"), ("-V6", "-V6"), ("-V65", "-V65"), 
						("-V", "-V")), 
					"-II": (("-I64", "-V"),), "-II6": (("-I64", "-V"),),
					"-IV": (("-I64", "-V"),),
			}, "2HC2": {
					"+V": ("0I",), "-V": ("0I",), "-V6": ("0I",), "-V65": ("0I",), 
					"+V43": ("0I",), "+VII6": ("0I",), "+V42": ("+I6",),
			}, "1END_EX1": {
					"0I": ("+V", "+V7", "-V", "-V7"), "+I6": ("+V", "+V7"), 
					"+II": ("+V", "-V", "+V7", "-V7"), "+II6": ("+V", "+V7"), 
					"+IV": ["+V", "+V7"], "+IV_MAJOR": ("+IV", "+V", "+V7"),
					"-VI": ("-V",), "-IV6": ("-V", "-V7"), "-IV6_MAJOR": ("-V",),
					"-II": ("-V", "-V7"), "-II6": ("-V", "-V7"), "-IV": ("-V", "-V7"),
			}, "2END_EX1": {
					"0I": [
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V7"), 
						("+I64", "-V7")],
					"+I6": [
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V7"), 
						("+I64", "-V7")],
					"+II": (
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V7"), 
						("+I64", "-V7")), 
					"-II": (("-I64", "-V"), ("-I64", "-V7")),
					"+II6": (
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V7"), 
						("+I64", "-V7")), 
					"-II6": (("-I64", "-V"), ("-I64", "-V7")),
					"+IV": (
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V7"), 
						("+I64", "-V7")),
					"-IV": (("-I64", "-V"), ("-I64", "-V7")),
					"+IV_MAJOR": (
						("+I64", "+V"), ("+I64", "-V"), ("+I64", "+V7"), 
						("+I64", "-V7")),
					"-VI": (("-I64", "-V"),), "-IV6": (("-I64", "-V"),),
					"-IV6_MAJOR": (("-I64", "-V"),)
			}, "1EXTON1": {
					"0I": ("-V6", "-V65", "+VII6", "+V43"), 
					"+I6": ("+VII6", "+V43", "-V6", "-V65", "+V42"),
			}, "1EXTON2": {
					"-V6": ("0I",), "-V65": ("0I",), "+VII6": ("0I", "+I6"), 
					"+V43": ("0I", "+I6"), "+V42": ("+I6",),
			}, "SDOM_AT_-1": {
					"0I": ["+II6", "+IV", "-VI", "-IV6"], "+I6": ["+II6", "+IV"],
			}, "SDOM_AT_-2": {
					"0I": ["+II6", "+IV", "-VI", "-IV6"], "+I6": ["+II6", "+IV"],
			}, "SDOM_AF_-1": {
					"0I": ["+II6", "+IV", "-VI", "-IV6"], "+I6": ["+II6", "+IV"], 
					"+IV": ("+II", "+II6"), "+II": ("+II6",), "+II6": ("+II",),
					"-VI": ["-II6", "-IV", "-IV6"], "-IV6": ["-II6", "-IV"]
			}, "3SDOM_EX1": {
					"0I": [
						("+I6", "+I6", "+I6"), ("+I6", "+I6", "+IV"), 
						("+I6", "+I6", "+II6"), ("-VI", "-VI", "-II6"), 
						("-VI", "-VI", "-IV"), ("-VI", "-VI", "-IV6")],
					"+I6": [
						("0I", "0I", "0I"), ("0I", "0I", "+IV"), 
						("0I", "0I", "+II6")]
			}
		}

		if mode == "ionian":
			self.key_sigs = (
				"C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F")

			self.chord_ids["SDOM_AT_-1"]["0I"].append("+II")
			self.chord_ids["SDOM_AT_-1"]["+I6"].append("+II")
			self.chord_ids["SDOM_AT_-2"]["0I"].append("+II")
			self.chord_ids["SDOM_AT_-2"]["+I6"].append("+II")
			self.chord_ids["SDOM_AF_-1"]["0I"].append("+II")
			self.chord_ids["SDOM_AF_-1"]["+I6"].append("+II")

			self.chord_ids["SDOM_AF_-1"]["-VI"].append("-II")
			self.chord_ids["SDOM_AF_-1"]["-IV6"].append("-II")
			self.chord_ids["1HC1"]["-VI"].extend(("-V6", "-V65"))
			self.chord_ids["1HC1"]["-IV6"].extend(("-V6", "-V65"))

			self.chord_ids["3SDOM_EX1"]["0I"].extend((
				("+II", "+I6", "+II6"), ("+II6", "+I6", "+II"), 
				("+I6", "+I6", "+II"), ("-VI", "-VI", "-II")))
			self.chord_ids["3SDOM_EX1"]["+I6"].extend((
				("+II", "+I6", "+II6"), ("+II6", "+I6", "+II"), 
				("0I", "0I", "+II")))
			self.chord_ids["1END_EX1"]["+IV"].append("+IV_MINOR")

		elif mode == "aeolian":
			self.key_sigs = (
				"A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D")

			self.chord_ids["SDOM_AT_-1"]["0I"].append("+IV_MAJOR")
			self.chord_ids["SDOM_AT_-1"]["+I6"].append("+IV_MAJOR")
			self.chord_ids["SDOM_AF_-1"]["0I"].append("+IV_MAJOR")
			self.chord_ids["SDOM_AF_-1"]["+I6"].append("+IV_MAJOR")
			self.chord_ids["3SDOM_EX1"]["0I"].append(("+I6", "+I6", "+IV_MAJOR"))
			self.chord_ids["3SDOM_EX1"]["+I6"].append(("0I", "0I", "+IV_MAJOR"))

			self.chord_ids["SDOM_AT_-1"]["0I"].append("-IV6_MAJOR")
			self.chord_ids["SDOM_AF_-1"]["0I"].append("-IV6_MAJOR")

			self.chord_ids["2END_EX1"]["0I"].append(("+IV_MAJOR", "+IV"))
			self.chord_ids["2END_EX1"]["+I6"].append(("+IV_MAJOR", "+IV"))
