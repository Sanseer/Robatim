from midiutil import MIDIFile
import random

I, I6, I64 = 1_530, 1_630, 1_640
II, II6 = 2_530, 2_630
IV = 4_530
V, V6  = 5_530, 5_630
V7, V65, V43, V42 = 5_753, 5_653, 5_643, 5_642
VII6 = 7_630

modes = {
	"aeolian": (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24), 
	"ionian": (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24)
}
major_scales = {"C":"#", "G":"#", "D":"#", "A":"#", "E":"#", "B":"#", 
	"F#":"#", "Db":"b", "Ab":"b", "Eb":"b", "Bb":"b", "F":"b"
}
minor_scales = {"A":"#", "E":"#", "B":"#", "F#":"#", "C#":"#", "G#":"#", 
	"D#":"#", "Bb":"b", "F":"b", "C":"b", "G":"b", "D":"b"
}

"""Do you need pedantic accidental designations based on key signature such as Cb or E#
if so use all_notes instead of tonics variable, 
the latter of which has dependencies"""

all_notes = (
	"A", ("A#","Bb"), "B", "C", ("C#", "Db"), "D",
	"E", ("F"), ("F#", "Gb"), "G", ("G#", "Ab")
)
tonics = {
	"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,"F": 5, "F#": 6, 
	"Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B":11
}
"""tuple with one item needs comma. Negative chords denote descent
You can create fake passing chords by combining accents"""
expand_tonic = {
	I: ((-V6, I), (VII6, I6), (VII6, -I), (-V65, I6), (V43, I6), 
		(V42, I6), (-V65, I), (V43, -I)), 
	I6: ((-V6, I), (-VII6, I6), (-VII6, -I), (-V65, I), (-V43, -I))
}
accent_tonic = {
	I: (I6,), I6: (-I,)
}
tonic_to_subdom = {
	I: (II, II6, IV), I6: (II6, IV)
}
accent_subdom = {
	II: (II6,), II6: (-II,), IV: (-II, II6)
}
"""Custom IV key for following dict"""
expand_subdom = {
	II: ((I6, II6),), II6: ((-I6, -II),), IV: ((II6, II),(II, II6))
}
subdom_to_dom = {
	II: (V, V7, V65), II6: (V, V7, V42), IV: (V, V7, V42)
}
accent_dom = {
	V: (V6, V65,), V6: (-V,)
}
bass_notes = {
	I:0, II: 1, V43: 1, VII6: 1, I6: 2, IV: 3, II6: 3, V42: 3, V: 4, V7: 4, 
	I64: 4, V6: 6, V65: 6
}
# Flat is better than nested
chord_tones = {
	(I, I6): (0, 2, 4), (V, V6): (1, 4, 6), (VII6): (1, 3, 6), 
	(V7, V65, V43, V42): (1, 3, 4, 6)
}
"""A and P for accent and passing chords. Both are based on preceding chords
An accent chord sequence is a single chord added to a sequence. Addendum of 1 (e.g., I6)
Passing chord: I VII6 I. Addendum of 2. First chord from prior sequence.
A to P is an accent chord that become a passing chord: I6 I VII6 I Addendum of 3
First chord from prior sequence. I is the accent here. """
antecedent = {
	("P","A"):(2,2,2), ("A","P","A"): (1,1,2,2), ("A","A","P"):(2,1,1,2),
	("A","P","P"):(1,1,1,1,2)
}
"""F denotes the final chord, dominant or tonic depending on half/authentic cadence. 
Final dominant can be V7 or V. Some chord combos may have multiple possible note combos
This is designated with numbers. S for subdominant"""
consequent1 = {
	("AS","AS","FD"): (2,2,4), ("AS","AS","AS","FD"): (2,2,2,2), 
	("AS", "PS", "FD"): (1,1,2,4), ("AS", "PS", "PS", "FD"):(1,1,1,1,2,2),
	("AS1", "PS", "FD"): (2,2,2,2)
}
"""FT: Final tonic"""
consequent2 = {
	("AS", "AS", "AD", "FT"): (2,2,2,2), ("AS", "AD", "FT"): (2,2,4),
	("AS", "AS1", "AD", "FT"): (2,1,1,4)
}
names = {
	"1":"I", "2":"II", "3":"III", "4":"IV", "5":"V", "6":"VI", "7":"VII",
	"530":"", "753":"7", "630":"6", "653": "65", "640":"64", "643": "43", "642":"42"   
}

class Voice:

	mode = ""
	tonic = ""
	accidental = ""
	chord_path = []
	note_values = [2] #don't forget to add 4 as last item whole note
	chord_types = []
	bass_notes = []
	soprano_notes = []
	alto_notes = []
	tenor_notes = []
	lily_parts = []
	chord_symbols = []

	def make_letter(self, real_note):
		"""Converts pitch magnitudes into standard note names"""
		letter_choices = []
		note_number = real_note % 12

		for letter, num in tonics.items():
			if num == note_number:
				letter_choices.append(letter)
			if len(letter_choices) > 1:
				for letter in letter_choices:
					if Voice.accidental in letter:
						notation = letter
			elif len(letter_choices) == 1:
				notation = letter_choices[0]

		octave = real_note // 12 - 1
		note_symbol = notation + str(octave)
		return note_symbol

	def make_letters(self):
		for real_note in self.real_notes:
			self.sheet_notes.append(self.make_letter(real_note))
		# print(self.sheet_notes)

	def convert_chords(self):
		new_chords_names = []
		for chord in Voice.chord_path:
			chord = str(abs(chord))
			root = chord[0]
			position = chord[-3:]
			correct_name = chord.replace(root, names[root],1)
			correct_name = correct_name.replace(position, names[position])
			new_chords_names.append(correct_name)
		return new_chords_names

	def lily_convert(self):
		self.lily_notes = []
		rhythm = self.invert_note_values()
		chord_symbols = self.convert_chords()
		print(chord_symbols)
		index = 0
		for sheet_note in self.sheet_notes:
			new_symbol = ""
			octave_mark = ""
			letter = sheet_note[0].lower()
			octave = int(sheet_note[-1])
			if octave < 3:
				shift = 3 - octave
				octave_mark =  str(shift * ",")
			elif octave > 3:
				shift = octave - 3
				octave_mark = str(shift * "")
			if "#" in sheet_note or "b" in sheet_note:
				old_symbol = sheet_note[1]
				if old_symbol == "#":
					new_symbol = "is"
				elif old_symbol == "b":
					new_symbol = "es"
			lily_note = letter + new_symbol + octave_mark + str(rhythm[index]) + " "
			self.lily_notes.append(lily_note)
			index += 1
		lily_string = ""
		for note in self.lily_notes:
			lily_string += note
		Voice.lily_parts.append(lily_string)


	def invert_note_values(self):
		correct_durations = {1:4, 4:1, 2:2}
		fixed_durations = []
		for index in range(len(Voice.note_values)):
			time = Voice.note_values[index]
			fixed_durations.append(correct_durations[time])
		return fixed_durations


class Bass(Voice):
	"""The first voice to create in a song"""

	def __init__(self, tonic="D", mode="ionian"):
		Voice.chord_path = [I]
		Voice.tonic = tonic
		self.scale_notes = [0]
		Voice.mode = self.mode = mode
		self.real_notes = []
		self.sheet_notes = []
		if mode == "ionian":
			Voice.accidental = major_scales[tonic]
		elif mode == "aeolian":
			Voice.accidental = minor_scales[tonic]
		self.voice = "bass"
		self.lily_notes = []
		self.old_chord = Voice.chord_path[-1]

	def create_chords(self):
		"""Creates full chord progression"""
		tonic_chords, tonic_note_values, old_chord = self.create_tonic_zone()
		self.make_half_cadence()
		Voice.note_values.extend(tonic_note_values)
		Voice.chord_path.extend(tonic_chords)
		self.old_chord = old_chord
		self.make_authentic_cadence()

	def create_passing_chords(self, chord_options):
		chords_chosen = random.choice(chord_options)
		[Voice.chord_path.append(chord) for chord in chords_chosen]
		self.old_chord = Voice.chord_path[-1]

	def create_accent_chord(self,chord_options):
		chord_choice = random.choice(chord_options)
		Voice.chord_path.append(chord_choice)
		self.old_chord = Voice.chord_path[-1]

	def create_tonic_zone(self):
		rhythm_sequence = random.choice(tuple(antecedent.keys()))
		Voice.note_values.extend(antecedent[rhythm_sequence])
		print(Voice.note_values)
		print(rhythm_sequence)
		for rhythm in rhythm_sequence:
			if rhythm == "P":
				chord_options = expand_tonic[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "A":
				chord_options = accent_tonic[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
		return Voice.chord_path[:], Voice.note_values[:], self.old_chord

	def make_half_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent1.keys()))
		Voice.note_values.extend(consequent1[rhythm_sequence])
		print(Voice.note_values)
		print(rhythm_sequence)
		self.choose_chord(rhythm_sequence)

	def choose_chord(self, rhythm_sequence):
		counter = 0
		for rhythm in rhythm_sequence:
			counter += 1
			if counter == 1:
				chord_options = tonic_to_subdom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif "AS" in rhythm:
				chord_options = accent_subdom[abs(self.old_chord)]
				self.create_accent_chord(chord_options)
			elif rhythm == "AD":
				chord_options = (V, V7)
				self.create_accent_chord(chord_options)
			elif rhythm == "PS":
				chord_options = expand_subdom[abs(self.old_chord)]
				self.create_passing_chords(chord_options)
			elif rhythm == "FD":
				chord_options = (V, V7)
				self.create_accent_chord(chord_options)
			elif rhythm == "FT":
				chord_options = (I,)
				self.create_accent_chord(chord_options)

	def make_authentic_cadence(self):
		rhythm_sequence = random.choice(tuple(consequent2.keys()))
		Voice.note_values.extend(consequent2[rhythm_sequence])
		print(Voice.note_values)
		print(rhythm_sequence)
		self.choose_chord(rhythm_sequence)

	def add_notes(self):
		"""Add notes to bass based on chords. First chord must be tonic"""
		old_scale_degree = 0
		old_pitch = 0
		old_position = 0
		for chord in Voice.chord_path[1:]:
			new_scale_degree = int(bass_notes[abs(chord)])

			# Deciding between regular and inverted chord
			if chord > 0 or chord < 0 and old_scale_degree > new_scale_degree:
				shift = new_scale_degree - old_scale_degree
				new_position = old_position + shift
				new_pitch = modes[self.mode][new_position]

			elif chord < 0 and new_scale_degree > old_scale_degree:
				old_position += 7
				shift = new_scale_degree - old_scale_degree - 7
				new_position = old_position + shift
				new_pitch = old_pitch + modes[self.mode][new_position] - \
					modes[self.mode][old_position]

			pitch_change = new_pitch - old_pitch
			self.scale_notes.append(new_pitch)
			old_pitch = new_pitch
			old_position = new_scale_degree
			old_scale_degree = new_scale_degree

	def convert_notes(self):
		"""Converts notes from diatonic scale degrees to pitch magnitudes"""
		self.real_notes = [note + 60 + tonics[Voice.tonic] for note in self.scale_notes]
		copy_notes = self.real_notes[:]
		for index in range(len(self.real_notes)):
			# Raise seventh only for ascending
			if self.mode == "aeolian" and bass_notes[abs(Voice.chord_path[index])] == 6:
				print("RAISED SEVENTH!")
				self.real_notes[index] += 1
			if Voice.tonic == "C":
				self.real_notes[index] -= 12
			else:
				self.real_notes[index] -= 24

	def create_part(self):
		"""Creates the bass portion of the song"""
		print(f"Song in {Voice.tonic} {self.mode} with {Voice.accidental}'s")
		self.create_chords()
		self.add_notes()
		self.convert_notes()
		self.make_letters()
		self.lily_convert()
		return self.real_notes

def random_key():
	mode = "aeolian"
	mode = random.choice(["ionian", "aeolian"])
	if mode == "ionian":
		return random.choice(tuple(major_scales.keys())), mode
	elif mode == "aeolian":
		return random.choice(tuple(minor_scales.keys())), mode

def create_song(parts="4"):
	song_notes = []
	if parts >= 1:
		song_notes.append(Bass(*random_key()).create_part())
	if parts >= 2:
		pass
	if parts >= 3:
		pass
	if parts >= 4:
		pass
	make_lily_file()
	return song_notes

def make_lily_file():
	if Voice.mode == "ionian":
		mode = "major "
	elif Voice.mode == "aeolian":
		mode = "minor "
	with open("old_layout.txt", 'r') as f:
		new_file = f.read()
	for index in range(len(Voice.lily_parts)):
		new_file = new_file.replace("PART_SLOT", "\\key " + 
			Voice.tonic.replace("#","is").replace("b","is").lower() 
			+ " \\" + mode + Voice.lily_parts[index], 1)
	new_file = new_file.replace("PART_SLOT", "")
	new_file = new_file.replace("Symphony", "Cantus in " + Voice.tonic + " " +  
		mode)
	with open("new_layout.txt", 'w') as f:
		f.write(new_file)

song_degrees = create_song(1)

if __name__ ==  "__main__":
	program = 40
	track    = 0
	channel  = 0
	time     = 0   # In beats
	# duration = 1   # In beats
	tempo    = 100  # In BPM
	volume   = 100 # 0-127, as per the MIDI standard

	MyMIDI = MIDIFile(1) # One track, defaults to format 1 (tempo track
	                     # automatically created)
	MyMIDI.addTempo(track,time, tempo)

	# Slow ending
	MyMIDI.addTempo(track, 26, tempo * .9)


	MyMIDI.addProgramChange(track, channel, time, program)

	index = 0
	for part in song_degrees:
		for pitch, duration in zip(part, Voice.note_values):
		    MyMIDI.addNote(track, channel, pitch, time, duration, volume)
		    time = time + (Voice.note_values[index]) 
		    index += 1


	with open("my_song0.mid", "wb") as output_file:
	    MyMIDI.writeFile(output_file)