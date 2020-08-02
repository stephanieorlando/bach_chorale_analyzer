from music21 import *
import csv

chorale = corpus.parse('bach/bwv248.9-s.mxl') # replace with chorale
#chorale.remove(chorale.parts[-1]) # remove any instrumental parts or comment out

choraleKey = 'D' # replace with key

choraleChords = chorale.chordify()

choraleReduction = chorale.partsToVoices(voiceAllocation=2) 
choraleReduction.parts[-1][0].clef = clef.BassClef()


keySig = key.Key(choraleKey)
keySigAccidentals = set([p.name for p in scale.MajorScale(choraleKey).pitches] + [p.name for p in scale.MinorScale(choraleKey).pitches])

measure = choraleReduction.parts[-1].recurse().getElementsByClass('Measure')
chords = choraleChords.recurse().getElementsByClass('Chord')

rnAnalysisList = []
fbChoraleList = []

fbDictionary = open("Bach_Dictionary_Chords.txt", "r")
fbDictFile = fbDictionary.read()

rnAnalysisText = open("%s_rn_analysis.txt" % chorale.metadata.title, "w")
rnAnalysisText.write("%s RN Analysis\n" % chorale.metadata.title)

bach_pd_chords = open('Bach_Music21_PD-fermata.csv', mode='a')
pd_chord_writer = csv.writer(bach_pd_chords, delimiter=',')

def leadingTone(chord):
	for s in chord.pitches:
		if s.accidental is not None:
			if s.name not in keySigAccidentals:
				return s
			elif s.name == keySig.pitchFromDegree(7).transpose(-1).name and keySig.mode == 'major':
				return s

def modulatedKey(leadingNote):
	if leadingNote.name == keySig.pitchFromDegree(7).transpose(-1).name and keySig.mode == 'major':
		modKey = key.Key(mode='major').deriveByDegree(4, leadingNote.name)
	else:
		modKey = key.Key(mode='major').deriveByDegree(7, leadingNote.name)

	tonicChord = [p.name for p in modKey.pitchesFromScaleDegrees([1, 3, 5])]

	if all(p in keySigAccidentals for p in tonicChord):
		return modKey
	else:
		return modKey.parallel

def harmonicAnalysis():
	for c in chords:
		if leadingTone(c) is not None:
			rn = roman.romanNumeralFromChord(c, modulatedKey(leadingTone(c)))
			rn_secondary = roman.romanNumeralFromChord(modulatedKey(leadingTone(c)).getChord(), keySig)
			rnAnalysisList.append("%s/%s" % (rn.figure, rn_secondary.romanNumeral))
		else:
			rn = roman.romanNumeralFromChord(c, keySig)
			rnAnalysisList.append(rn.figure)
	return rnAnalysisList
	
def figuredBassAnalysis():	
	for c in chords:
		c.closedPosition(inPlace=True)
		fb = c.annotateIntervals(returnList=True)
		fbChoraleList.append(''.join(fb))
	return fbChoraleList

def makeFiveChords(n):
	fiveChords = []
	i = 0
	while len(fiveChords) < 5:
		if fbChoraleList[n - i] in fbDictFile and fbChoraleList[n - i] != '2':
			fiveChords.append(rnAnalysisList[n - i])
		i += 1
	return chorale.metadata.title, fiveChords[4], fiveChords[3], fiveChords[2], fiveChords[1], fiveChords[0], chords[n].measureNumber


def makeChoraleReduction():

	harmonicAnalysis()
	figuredBassAnalysis()

	m = -1
	n = 0
	
	for c, r, f in zip(chords, rnAnalysisList, fbChoraleList):
		
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
					pd_chord_writer.writerow(makeFiveChords(n))
				elif hasattr(c, 'expressions'):
					for expression in c.expressions:
						if 'Fermata' in expression.classes:
							rnAnalysisText.write("Fermata")
							pd_chord_writer.writerow(makeFiveChords(n))
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
					pd_chord_writer.writerow(makeFiveChords(n))
				elif hasattr(c, 'expressions'):
					for expression in c.expressions:
						if 'Fermata' in expression.classes:
							rnAnalysisText.write("Fermata")
							pd_chord_writer.writerow(makeFiveChords(n))
				rnAnalysisText.write("\n")
			else:
				rnAnalysisText.write("(%s) Beat: %s, Duration: %s\n" % (r, c.beatStr, c.quarterLength))

		n += 1
	"""
		# if the chorale contains measures that begin with a rest, use this and comment text expression out
		c.closedPosition(forceOctave=4, inPlace=True)
		if f in fbDictFile and f != '2':
			c.addLyric(r)
		

	choraleReduction.insert(0, choraleChords)
	"""		

	
for m in measure:
	if m.measureNumber % 4 == 0:
		m.insert(layout.SystemLayout(isNew=True))

for s in choraleReduction.parts:
	s.finalBarline = 'final'

makeChoraleReduction()
choraleReduction.show()

fbDictionary.close()
rnAnalysisText.close()
bach_pd_chords.close()
