from music21 import *

chorale = corpus.parse('bwv43.11') # replace with chorale
# chorale.remove(chorale.parts[0]) # remove any instrumental parts or comment out
choraleChords = chorale.chordify()

choraleReduction = chorale.partsToVoices(voiceAllocation=2) 
choraleReduction.parts[-1][0].clef = clef.BassClef()

choraleKey = 'G' # replace with key

keySignature = key.Key(choraleKey)
keySigAccidentals = set([str(a) for a in keySignature.alteredPitches] + [p.name for p in scale.MajorScale(choraleKey).pitches])

measure = choraleReduction.parts[-1].recurse().getElementsByClass('Measure')
chords = choraleChords.recurse().getElementsByClass('Chord')

fbDictionary = open("Bach_Dictionary_Chords.txt", "r")
fbDictFile = fbDictionary.read()

rnAnalysisText = open("%s_rn_analysis.txt" % chorale.metadata.title, "w")
rnAnalysisText.write("%s RN Analysis\n" % chorale.metadata.title)

def leadingTone(chord):
	for s in chord.pitches:
		if s.accidental is not None:
			if s.name not in keySigAccidentals:
				return s

def modulatedKey(leadingNote):
	modKey = key.Key(mode='major').deriveByDegree(7, leadingNote.name)
	tonicChord = [p.name for p in modKey.pitchesFromScaleDegrees([1, 3, 5])]
	if all(p in keySigAccidentals for p in tonicChord):
		return modKey
	else:
		return modKey.parallel

def harmonicAnalysis():
	rnAnalysisList = []
	for c in chords:
		if leadingTone(c) is not None:
			rn = roman.romanNumeralFromChord(c, modulatedKey(leadingTone(c)))
			rn_secondary = roman.romanNumeralFromChord(modulatedKey(leadingTone(c)).getChord(), keySignature)
			rnAnalysisList.append("%s/%s" % (rn.figure, rn_secondary.romanNumeral))
		else:
			rn = roman.romanNumeralFromChord(c, keySignature)
			rnAnalysisList.append(rn.figure)
	return rnAnalysisList
	
def figuredBassAnalysis():
	fbChoraleList = []	
	for c in chords:
		c.closedPosition(inPlace=True)
		fb = c.annotateIntervals(returnList=True)
		fbChoraleList.append(''.join(fb))
	return fbChoraleList
	
def makeChoraleReduction():
	
	m = -1
	
	for c, r, f in zip(chords, harmonicAnalysis(), figuredBassAnalysis()):
		
		if c.offset == 0.0:			
			m += 1
			rnAnalysisText.write("\nMeasure: %s\n" % measure[m].measureNumber)
			
			if f in fbDictFile and f != '2':
				t = expressions.TextExpression(r)
				t.style.fontSize=8
				measure[m].insert(c.offset, t)
				rnAnalysisText.write("%s Beat: %s, Duration: %s " % (r, c.beatStr, c.quarterLength))
				if 'Fermata' in c.classes:
					rnAnalysisText.write("Fermata\n")
				elif hasattr(c, 'expressions'):
					for expression in c.expressions:
						if 'Fermata' in expression.classes:
							rnAnalysisText.write("Fermata")
				rnAnalysisText.write("\n")
			else:
				rnAnalysisText.write("(%s) Beat: %s, Duration: %s\n" % (r, c.beatStr, c.quarterLength))

		else: 		
			if f in fbDictFile and f != '2':
				t = expressions.TextExpression(r)
				t.style.fontSize=8
				measure[m].insert(c.offset, t)
				rnAnalysisText.write("%s Beat: %s, Duration: %s " % (r, c.beatStr, c.quarterLength))
				if 'Fermata' in c.classes:
					rnAnalysisText.write("Fermata\n")
				elif hasattr(c, 'expressions'):
					for expression in c.expressions:
						if 'Fermata' in expression.classes:
							rnAnalysisText.write("Fermata")
				rnAnalysisText.write("\n")
			else:
				rnAnalysisText.write("(%s) Beat: %s, Duration: %s\n" % (r, c.beatStr, c.quarterLength))
	
for m in measure:
	if m.measureNumber % 4 == 0:
		m.insert(layout.SystemLayout(isNew=True))

for s in choraleReduction.parts:
	s.finalBarline = 'final'

makeChoraleReduction()
choraleReduction.show()

fbDictionary.close()
rnAnalysisText.close()
