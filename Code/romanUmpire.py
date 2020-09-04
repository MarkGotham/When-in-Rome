# -*- coding: utf-8 -*-
'''
===============================
THE ROMAN UMPIRE (romanUmpire.py)
===============================

Mark Gotham, 2019–20


LICENCE:
===============================

Creative Commons Attribution-NonCommercial 4.0 International License.
https://creativecommons.org/licenses/by-nc/4.0/


ABOUT:
===============================

This is a 'spell checker' for Roman numeral analysis.
It works by pairing up each Roman numeral with
the 'vertical' slices that take place during the span in question and
assessing how well that Roman numeral accounts for the corresponding slices of score.

COMPARISONS
Currently, the comparisons involve simple metrics for the:
    proportion of notes in the score matching the corresponding Roman numeral (weighed by length);
    (unusually weak) metrical positions of chord changes; and
    presence in the score of the bass note asserted by the inversion.

FEEDBACK
Feedback is available in any or all of those areas, and can be set to flag up either:
    all areas that the code finds questionable, or
    only those for which it offers 'constructive' suggestions for replacement.

INPUT
This code accepts:
... score input as either a
    score in a recognised format (e.g. musicxml), or
    tabular file (.tsv or .csv) having handled the slicing in advance.
... analysis input in either the:
    (plain text) 'Roman text' format or
    as lyrics on the score (see https://fourscoreandmore.org/working-in-harmony/analysis/)

OUTPUT
The comparison feedback is written out as a text file
in the local folder (by default) or elsewhere if specified.

'''

from music21 import converter
from music21 import chord
from music21 import expressions
from music21 import layout
from music21 import note
from music21 import roman
from music21 import stream

from copy import deepcopy
import csv
import os
import unittest


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


# Three supporting object types:

class Slice:
    '''
    A reduction object corresponding to one 'vertical' slice through the score.
    A 'slice' is a momentary cross-section during which none of the notes change.
    '''

    def __init__(self):
        self.uniqueOffsetID = None
        self.measure = None
        self.beat = None

        self.pitches = []
        self.quarterLength = None
        self.beatStrength = None


# ------------------------------------------------------------------------------

class HarmonicRange:
    '''
    HarmonicRange objects cover part of a score, usually including:
    a Roman numeral and the corresponding score 'slices' for that range.
    In addition to details of the Roman numeral and the corresponding slices in question,
    this class also keeps track of the start/end positions and lengths
    in terms of both measures and quarter notes.

    Usage here focusses on assessing the Roman numeral (key and figure).
    This object can also be used to assess key alone, e.g. for key finding tasks.
    '''

    def __init__(self, source=None):

        # Initialise with Nones prior to (optionally) setting those values.

        self.startOffset = None
        self.endOffset = None
        self.quarterLength = None

        self.startMeasure = None
        self.endMeasure = None
        self.measureLength = None

        self.startBeat = None
        self.endBeat = None
        self.beatStrength = None

        self.slices = []

        if source:

            if ('NotRest' in source.classes) and ('GeneralNote' in source.classes):
                # Covers notes and chords, excludes rests.
                self.getCoreValues(source)

                # Roman. Classes include 'Chord', 'NotRest', 'GeneralNote' as well as:
                if 'RomanNumeral' in source.classes:
                    self.getMoreValuesFromRN(source)
                else:
                    self.figure = None
                    self.key = None
                    self.bassPitch = None
                    self.pitches = []

            else:
                raise ValueError('Initialise a HarmonicRange object either empty, or'
                                 'with a relevant object: Note, Chord, or RomanNumeral.')

    def getCoreValues(self, source):
        """"
        Retrieve core variables from a relevant object: Note, Chord, or RomanNumeral.
        """
        self.startMeasure = int(source.measureNumber)
        self.startBeat = _intBeat(source.beat)
        self.beatStrength = source.beatStrength
        self.quarterLength = round(source.quarterLength, 2)
        self.startOffset = round(source.activeSite.offset + source.offset, 2)

    def getMoreValuesFromRN(self, rn):
        """"
        Retrieve additional values specific to RomanNumeral objects.
        """
        self.figure = rn.figure
        self.key = rn.key
        self.pitches = [p.name for p in rn.pitches]
        self.bassPitch = rn.bass().name

# ------------------------------------------------------------------------------


class Feedback:
    '''
    For organising what advice to return / print.
    All types or just some?
    All cases or only where constructive suggestions are on offer?
    '''

    def __init__(self,
                 hr: HarmonicRange,
                 msg: str):

        self.startOffset = hr.startOffset
        self.measure = hr.startMeasure
        self.beat = hr.startBeat

        self.message = msg  # for all cases
        self.matchStrength = None  # for pitch HarmonicRange only
        self.suggestions = []  # where possible


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class ScoreAndAnalysis:
    '''
    Class for handling:
        'ground-truth' score data (either the score itself or a tabular representation thereof);
        Roman numeral analysis (either on the score or as a separate Roman text analysis file);
        comparisons between the two (with HarmonicRange objects).

    The analysisLocation variable:
        defaults to 'On score' (for analyses input on the score itself);
        for separate analyses, analysisLocation should be the pre-converted rntxt file.

    I.e. this class supports many input methods.
    In all cases, everything (score/data and the optional separate analysis) should be pre-parsed.

    '''

    def __init__(self,
                 scoreOrData,  # stream.Score or str path
                 analysisLocation='On score',  # stream.Score or str path
                 analysisParts: int = 1,
                 analysisPartNo: int = -1,
                 minBeatStrength: float = 0.25,
                 tolerance: float = 0.6):

        self.scoreOrData = scoreOrData
        self.analysisLocation = analysisLocation
        self.analysisParts = analysisParts
        self.analysisPartNo = analysisPartNo
        self.minBeatStrength = minBeatStrength
        self.tolerance = tolerance

        self.slices = []
        self.prevSlicePitches = None

        self.harmonicRanges = []

        self.pitchFeedback = None
        self.metricalPositionFeedback = None
        self.bassFeedback = None
        self.errorLog = []

        self._parseScoreData()
        self._parseAnalysis()
        self._rnSliceMatchUp()

    def _parseScoreData(self):
        '''
        Handles input options for score, either:
            a score in a recognised format (e.g. musicxml), or
            a tabular file (.tsv or .csv) having handled the slicing in advance.
        '''

        if type(self.scoreOrData) is stream.Score:
            self.score = self.scoreOrData
            self._scoreInit()

        elif type(self.scoreOrData) is str:
            self.name, extension = os.path.splitext(self.scoreOrData)

            if extension in ['.tsv', '.csv']:
                if self.analysisLocation == 'On score':
                    raise ValueError('Cannot use tabular input (no score) with analysis on score.')
                if extension == '.tsv':
                    splitMarker = '\t'
                else:  # extension == '.csv':
                    splitMarker = ','
                self.score = _importSV(self.scoreOrData, splitMarker=splitMarker)
                self._retrieveSlicesFromList()  # NOTE: sets totalLength and scoreMeasures
            elif extension in ['.mxl', '.musicxml', '.midi', '.mid']:  # Actual score:
                self.score = converter.parse(self.scoreOrData)
                self._scoreInit()
            else:
                msg = f'The extension {extension} is not supported for score / data input.'
                raise ValueError(msg)

        else:
            raise ValueError(f'The scoreOrData argument (currently {self.scoreOrData} '
                             'must be a music21 stream.Score() or '
                             'a path to a valid score or tabular file.')

    def _scoreInit(self):
        '''
        Subsidiary preparation of, and extractions from, the score.
        '''

        self._removeGraceNotes()
        self._retrieveSlicesFromScore()
        self.totalLength = self.score.quarterLength
        self.scoreMeasures = len(self.score.parts[0].getElementsByClass('Measure'))

    def _parseAnalysis(self):
        '''
        Handles input options for analysis, either:
            a music21 stream.Score in a recognised format (e.g. rntxt), or
            as lyrics on a score.
        '''

        if type(self.analysisLocation) is stream.Score:
            self.analysis = self.analysisLocation  # TODO further validity check (has Roman numerals)
        elif type(self.analysisLocation) is str:
            if self.analysisLocation == 'On score':
                self._getOnScoreAnalysis()
            else:  # analysisLocation must be a path to a Roman text file
                if os.path.splitext(self.analysisLocation)[1] not in ['.txt', '.rntxt']:
                    msg = 'The \'analysisLocation\' argument must point to one of ' \
                          'the path (str) to a Roman text file with extension .txt; ' \
                          'such a file already parsed by music21; or ' \
                          'simple the string \'onscore\' to indicate that it\'s on the score already.'
                    raise ValueError(msg)
                self.analysis = converter.parse(self.analysisLocation, format='Romantext').parts[0]
                self._getSeparateAnalysis()

    def writeScoreWithAnalysis(self,
                               outPath: str = '.',
                               outFile: str = 'Analysis_on_score',
                               feedback: bool = True,
                               lieder: bool = True):
        '''
        Mostly to combine an off-score analysis with the corresponding score and write to disc.

        Option (feedback=True, default) to include '***' above relevant moments.

        Error raised in the case of a call on score with analysis already on there
        (i.e. with analysisLocation = 'On score' in the init)
        and feedback as false.
        Nothing to add in that case.

        Additional presentation option (lieder=True, default) for returning the
        Mensurstrich brace to the piano part of the lieder.
        Don't worry if that doesn't mean anything to you.
        '''

        if self.analysisLocation == 'On score':
            if not feedback:
                msg = 'This method is for combining a score with ' \
                      'an analysis hosted separately, and / or for ' \
                      'flagging up moments for which there is feedback available.\n' \
                      'You have called this on a score with the analysis already on there, ' \
                      'and declined feedback, so this method has nothing to offer.'
                raise ValueError(msg)
            else:
                self.scoreWithAnalysis = self.score
        else:
            self.scoreWithAnalysis = deepcopy(self.score)
            analysis = deepcopy(self.analysis)
            analysis.partName = 'Analysis'

            measureDiff = self.scoreMeasures - self.analysisMeasures
            if measureDiff > 0:
                for x in range(measureDiff):
                    analysis.append(stream.Measure())

            self.scoreWithAnalysis.insert(0, analysis)

        if lieder:  # If lieder option is set to true and ...
            if len(self.scoreWithAnalysis.parts) == 4:  # there are 4 parts inc. the analysis
                staffGrouping = layout.StaffGroup([self.scoreWithAnalysis.parts[1],
                                                   self.scoreWithAnalysis.parts[2]
                                                   ],
                                                  name='Piano', abbreviation='Pno.', symbol='brace')
                staffGrouping.barTogether = 'Mensurstrich'
                self.scoreWithAnalysis.insert(0, staffGrouping)

        self._feedbackOnScore()

        if outFile == 'Analysis_on_score':
            outFile = self.name + '_with_analysis_onscore',

        self.scoreWithAnalysis.write(fmt='musicxml', fp=f'{os.path.join(outPath, outFile)}.musicxml')

    def _removeGraceNotes(self):
        '''
        Removes all grace notes in the score.
        They are of relatively low importance and
        can cause disproportionate problems when processing.
        '''

        notesToRemove = []
        for n in self.score.recurse().notes:
            if n.duration.isGrace:
                notesToRemove.append(n)

        for n in notesToRemove:
            n.activeSite.remove(n)

    def _retrieveSlicesFromScore(self):
        '''
        Extracts chord and rest info from the score as Slice objects and
        populates self.slices with a list of these Slices.

        If the analysisLocation is 'On score' then first
        removes that analysis from consideration
        (the number of analysis parts is given by analysisParts).
        '''

        if self.analysisLocation == 'On score':
            noAnalysisScore = deepcopy(self.score)
            for x in range(self.analysisParts):
                noAnalysisScore.remove(noAnalysisScore.parts[-1])
            chordScore = noAnalysisScore.chordify()
        else:
            chordScore = self.score.chordify()

        self.lastBeat = 0
        self.lastMeasure = 0
        self.lastUniqueOffsetID = 0

        for x in chordScore.recurse():

            if ('Rest' in x.classes) or ('Chord' in x.classes):

                if not self.checkMonotonicIncrease(x):
                    continue

                thisEntry = Slice()

                thisEntry.measure = int(x.measureNumber)
                thisEntry.beat = _intBeat(x.beat)
                thisEntry.beatStrength = x.beatStrength
                thisEntry.quarterLength = round(float(x.quarterLength), 2)
                thisEntry.uniqueOffsetID = round(x.activeSite.offset + x.offset, 2)

                if 'Chord' in x.classes:
                    thisEntry.pitches = [p.nameWithOctave for p in x.pitches]
                    self.prevSlicePitches = thisEntry.pitches

                if 'Rest' in x.classes:
                    if self.prevSlicePitches:
                        thisEntry.pitches = self.prevSlicePitches
                    else:
                        thisEntry.pitches = []
                        self.errorLog.append('Roman numeral allocated before the first note.\n'
                                             'Please check and correct.'
                                             )

                self.lastBeat = thisEntry.beat
                self.lastMeasure = thisEntry.measure
                self.lastUniqueOffsetID = thisEntry.uniqueOffsetID

                self.slices.append(thisEntry)

    def writeSlicesFromScore(self,
                             outPath: str = '.',
                             outFile: str = 'ScoreInfoSV'):
        '''
        Optional, subsidiary method for writing out the Slice object information
        retrieved from the score to a value separated file.

        Having done so, that information can be re-retrieved via retrieveSlicesFromList.
        '''

        with open(f'{os.path.join(outPath, outFile)}.tsv', "w") as svfile:
            svOut = csv.writer(svfile, delimiter='\t',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for entry in self.slices:
                svOut.writerow([entry.uniqueOffsetID,
                                entry.measure,
                                entry.beat,
                                entry.beatStrength,
                                entry.quarterLength,
                                entry.pitches,
                                ])

    def _retrieveSlicesFromList(self):
        '''
        Populates self.slices with a list of
        Slice objects extracted from entries in the 'score' (here a list).

        Checks that the list is plausible.
        '''

        lastEntryMeasure = -1

        for x in self.score:  # sic, checked that the 'score' is a list

            thisEntry = Slice()

            thisEntry.uniqueOffsetID = float(x[0])
            thisEntry.measure = int(x[1])
            if thisEntry.measure < lastEntryMeasure:
                raise ValueError('The list of measures slices should monotonically increase')
            else:
                lastEntryMeasure = thisEntry.measure
            thisEntry.beat = float(x[2])
            thisEntry.beatStrength = float(x[3])
            thisEntry.quarterLength = float(x[4])
            thisEntry.pitches = x[5][2:-2].split('\', \'')

            self.slices.append(thisEntry)

        # Total length and score measures from 'this' (which is to say, last) entry
        self.totalLength = thisEntry.uniqueOffsetID + thisEntry.quarterLength
        self.scoreMeasures = thisEntry.measure

    def checkMonotonicIncrease(self, x):
        '''
        For checking monotonic increment through the piece.
        if not, logs error and rejects element (slice or RN).
        '''

        measure = int(x.measureNumber)
        beat = _intBeat(x.beat)
        uniqueOffsetID = round(x.activeSite.offset + x.offset, 2)

        if uniqueOffsetID < self.lastUniqueOffsetID:
            msg = f'checkMonotonicIncrease fail on uniqueOffsetID: {uniqueOffsetID}.'
            self.errorLog.append(msg)
            return False

        if measure < self.lastMeasure:
            msg = f'checkMonotonicIncrease fail on measure number: {measure}.'
            self.errorLog.append(msg)
            return False

        if measure == self.lastMeasure:
            if beat < self.lastBeat:
                msg = f'checkMonotonicIncrease fail on beat number {beat} in measure {measure}.'
                self.errorLog.append(msg)
                return False

        return True

    def _getOnScoreAnalysis(self):
        '''
        Gets an analysis hosted in the main score,
        as lyrics in one part (the lowest, by default).
        Straight to putative 'HarmonicRange' object.
        '''
        # TODO: support type='Lyric' for alternatives?

        self.prevailingKey = 'FAKE KEY'

        for x in self.score.parts[self.analysisPartNo].recurse().notes:

            if x.lyric:

                rn = self._romanFromLyric(x.lyric)
                if rn:
                    thisHarmonicRange = HarmonicRange(x)
                    thisHarmonicRange.figure = rn.figure
                    thisHarmonicRange.key = rn.key
                    # TODO compress but note the gap between a note and a contextless rn

                    self.harmonicRanges.append(thisHarmonicRange)

                else:
                    msg = f'Error retrieving a Roman numeral from the lyric {x.lyric} ' \
                          f'in measure {x.measureNumber} with the ' \
                          f'prevailing key of {self.prevailingKey}.'
                    self.errorLog.append(msg)

    def _romanFromLyric(self, lyric):
        '''
        Converts lyrics in recognised format into m21 Roman Numeral objects.
        Format: 'Key: Figure' for first entry and all key changes; otherwise just 'Figure'.

        Includes the following substitutions:
        all spaces (including non-breaking spaces) with nothing;
        '-' with 'b' for flats;
        bracket types to accept e.g. (no5) as well as the official [no5]; and
        'sus' with '[addX]' for suspensions/added notes.
        '''

        lyric = lyric.replace(' ', '')
        lyric = lyric.replace('\xa0', '')

        lyric = lyric.replace('-', 'b')

        lyric = lyric.replace('(', '[')
        lyric = lyric.replace(')', ']')

        if 'sus' in lyric:
            lyric = lyric.replace('sus', '[add')
            lyric += ']'

        if ':' in lyric:
            self.prevailingKey, figure = lyric.split(':')
        else:
            figure = lyric  # hence self.prevailingKey

        asRoman = roman.RomanNumeral(figure,
                                     self.prevailingKey,
                                     # sixthMinor=roman.Minor67Default.CAUTIONARY,
                                     # seventhMinor=roman.Minor67Default.CAUTIONARY,
                                     )

        if asRoman.figure:  # TODO: better test?
            return asRoman
        else:
            return False

    def _getSeparateAnalysis(self):
        '''
        Gets an analysis from a path to a RNTXT file.
        Straight to putative 'HarmonicRange' objects.
        '''

        self.analysisMeasures = len(self.analysis.getElementsByClass('Measure'))

        if self.scoreMeasures != self.analysisMeasures:
            msg = f'WARNING: There are {self.scoreMeasures} measures in the score ' \
                  f'but {self.analysisMeasures} in your analysis. ' \
                  'This is usually a question of either the beginning or end: either\n' \
                  '1) The final chord in the analysis ' \
                  'comes before the final measure, or\n' \
                  '2) There\'s an anacrusis in the score without an accompanying harmony ' \
                  '(i.e. the analysis is missing measure 0). ' \
                  'In that latter case, the score and analysis will be misaligned, ' \
                  'and the HarmonicRanges will not work properly. ' \
                  'Best to put in a chord of some kind for the anacrusis.\n'

            self.errorLog.append(msg)

        self.lastBeat = 0
        self.lastMeasure = 0
        self.lastUniqueOffsetID = 0

        for x in self.analysis.recurse().getElementsByClass('RomanNumeral'):

            if not self.checkMonotonicIncrease(x):
                continue

            thisHarmonicRange = HarmonicRange(x)
            self.harmonicRanges.append(thisHarmonicRange)

# ------------------------------------------------------------------------------

    def _rnSliceMatchUp(self):
        '''
        Compares a score-analysis pair.
        Currently using a simple metric for proportion of notes the same
        weighted by length (time).
        '''

        self.indexCount = 0

        for index in range(len(self.harmonicRanges) - 1):
            self.harmonicRanges[index].endOffset = self.harmonicRanges[index + 1].startOffset
            self._singleMatchUp(self.harmonicRanges[index])

        # Special case of last one.
        self.harmonicRanges[-1].endOffset = self.totalLength
        self._singleMatchUp(self.harmonicRanges[-1])

        if self.indexCount != len(self.slices):
            msg = f'Slices missing: {self.indexCount} accounted for ' \
                  f'of {len(self.slices)} total.'
            self.errorLog.append(msg)

    def _singleMatchUp(self,
                       thisHarmonicRange: HarmonicRange):
        '''
        HarmonicRange and match up of a Roman numeral
        with slices (potentially) in that range by position in score.
        Note that harmony changes between slice changes are
        not supported and may lead to erratic results.
        I.e. chords should change where at least one pitch changes.
        '''

        tc = thisHarmonicRange

        for thisSlice in self.slices[self.indexCount:]:
            if tc.startOffset <= thisSlice.uniqueOffsetID < tc.endOffset:
                tc.slices.append(thisSlice)
                self.indexCount += 1
            else:
                break

# ------------------------------------------------------------------------------

# Assessments:

    def runComparisons(self):
        '''
        Runs all three comparison types for feedback on:
            metricalPositions(),
            comparePitches(), and
            compareBass().
        '''

        self.metricalPositions()
        self.comparePitches()
        self.compareBass()

    def metricalPositions(self):
        '''
        Check beatStrengths and returns unlikely choices.
        '''

        if self.metricalPositionFeedback is not None:  # already done
            return

        self.metricalPositionFeedback = []

        for comp in self.harmonicRanges:
            if comp.beatStrength < self.minBeatStrength:
                # if comp.beatStrength < lastBeatStrength:  # TODO: this context

                msg = f'Measure {comp.startMeasure}, {comp.figure} in {comp.key} ' \
                      f'appears on beat {comp.startBeat}.'
                fb = Feedback(comp, msg)

                self.metricalPositionFeedback.append(fb)

                # lastBeatStrength = x.beatStrength  # TODO: this context

    def comparePitches(self):
        '''
        Single RN-slice comparison for pitches:
        do the chords reflect the pitch content of the score section in question?
        '''

        if self.pitchFeedback is not None:  # already done
            return

        self.pitchFeedback = []

        pitchNumerator = 0

        for comp in self.harmonicRanges:

            overall = 0

            harmonicRangeLength = sum([round(sl.quarterLength, 2) for sl in comp.slices])
            # Note: Avoid division by 0

            for thisSlice in comp.slices:  # NB: Rest slices handled already
                pitchesNameNoOctave = [x[:-1] for x in thisSlice.pitches]  # Pitch only
                proportionSame = self._proportionSimilarity(comp, pitchesNameNoOctave)
                # weighedSimilarity = proportionSame * slice.beatStrength  # TODO
                overall += thisSlice.quarterLength * proportionSame / harmonicRangeLength
                overall = round(overall, 2)

            compLength = comp.endOffset - comp.startOffset

            if overall >= self.tolerance:
                pitchNumerator += compLength

            else:  # overall < self.tolerance:  # Process feedback and reduce pitchScore.

                pitchNumerator += (compLength * overall)

                # Suggestions
                pl = [pList.pitches for pList in comp.slices]
                suggestions = []
                for sl in comp.slices:
                    chd = chord.Chord(sl.pitches)
                    if (chd.isTriad() or chd.isSeventh()):
                        rn = roman.romanNumeralFromChord(chd, comp.key)
                        if rn.figure != comp.figure:
                            suggestions.append([sl.measure, sl.beat, rn.figure, sl.pitches])

                msg = f'Measure {comp.startMeasure}, beat {comp.startBeat}, {comp.figure} in {comp.key}, ' \
                      f'indicating the pitches {comp.pitches} ' \
                      f'accounting for successive slices of {pl}.'
                fb = Feedback(comp, msg)
                fb.matchStrength = f'Match strength estimated at {round(overall * 100, 2)}%.'
                fb.suggestions = []

                if len(suggestions) > 0:
                    for s in suggestions:
                        fb.suggestions.append(f'm{s[0]} b{s[1]} {s[2]} for the slice {s[3]}')

                self.pitchFeedback.append(fb)

            self.pitchScore = round(pitchNumerator * 100 / self.totalLength, 2)

    def compareBass(self):
        '''
        Single RN-slice comparison for bass pitches (inversion).
        Creates feedback for cases where
        the bass pitch indicated by the Roman numeral's inversion
        does not appear as the lowest note during the span in question.
        '''

        if self.bassFeedback is not None:  # already done
            return

        self.bassFeedback = []

        bassNumerator = 0

        for comp in self.harmonicRanges:

            # bassPitchesWithOctave = [slice.pitches[0] for slice in comp.slices]
            bassPitchesWithOctave = []  # Sometimes the slice is a rest I guess?
            for slice in comp.slices:
                if len(slice.pitches) > 0:
                    bassPitchesWithOctave.append(slice.pitches[0])

            bassPitchesNoOctave = [p[:-1] for p in bassPitchesWithOctave]
            bassPitchesWithOctave = list(set(bassPitchesWithOctave))

            if comp.bassPitch not in bassPitchesNoOctave:

                inversionSuggestions = []

                for bassPitch in bassPitchesNoOctave:
                    if bassPitch in comp.pitches:  # already retrieved
                        suggestedPitches = comp.pitches
                        suggestedPitches.append(bassPitch + '0')  # To ensure it is lowest
                        suggestedChord = chord.Chord(suggestedPitches)
                        rn = roman.romanNumeralFromChord(suggestedChord, comp.key)
                        inversionSuggestions.append(f'm{comp.startMeasure} b{comp.startBeat} {rn.figure}')

                msg = f'Measure {comp.startMeasure}, beat {comp.startBeat}, {comp.figure} in {comp.key}, ' \
                      f'indicating the bass {comp.bassPitch} ' \
                      f'for lowest note(s) of: {bassPitchesWithOctave}.'
                fb = Feedback(comp, msg)
                # fb.matchStrength = N/A
                fb.suggestions = []

                if len(inversionSuggestions) > 0:
                    fb.suggestions = list(set(inversionSuggestions))  # Once for each suggestion

                self.bassFeedback.append(fb)

            else:  # comp.bassPitch in bassPitchesNoOctave:
                compLength = comp.endOffset - comp.startOffset
                bassNumerator += compLength

        self.bassScore = bassNumerator / self.totalLength

    def _proportionSimilarity(self,
                              comp: HarmonicRange,
                              query: Slice):
        '''
        Approximate measure of the 'similarity' between a
        reference HarmonicRange object (Roman numeral, etc) and query (actual slice in score).

        Returns the proportion of score pitches accounted for.

        Note:
        This is not limited to distinct pitches:
        it returns a better score for multiple tonics, for instance.
        '''
        # TODO: Penalty for notes in the RN not used? Not here, only overall?

        if len(query) == 0:
            self.errorLog.append(
                f'Roman numeral {comp.figure} in {comp.key}, m.{comp.startMeasure}: '
                f'No pitches in one of the slices.'
            )

            return 0

        intersection = [x for x in query if x in comp.pitches]
        proportion = len(intersection) / len(query)

        return proportion

# ------------------------------------------------------------------------------

# Feedback:

    def printFeedback(self,
                      pitches: bool = True,
                      metre: bool = True,
                      bass: bool = True,
                      constructiveOnly: bool = False,
                      outPath=None,
                      outFile=None):
        '''
        Select feedback to print: any or all of:
            'pitches' for pitch HarmonicRanges;
            'metre' for metrical positions; and
            'bass' for bass notes / inversions.
        If constructiveOnly is True, then the returned feedback will be limited to
        cases for which there is a corresponding alternative suggestion ready.
        '''

        allToPrint = []

        if (not pitches) and (not metre) and (not bass):
            allToPrint.append('Please select at least one of pitches, metre, or bass '
                              'to receive feedback on that / those aspect(s).')
            return

        if pitches:
            self.comparePitches()
            allToPrint.append('\nPITCH COVERAGE =====================\n')
            if len(self.pitchFeedback) == 0:
                msg = 'The pitch coverage looks good: ' \
                      'all of the chords match the corresponding sections of the score well.\n'
                allToPrint.append(msg)
            else:  # if len(self.pitchFeedback) > 0:
                allToPrint.append(f'I rate the pitch coverage at about {self.pitchScore}%. '
                                  'In the following cases, the chord indicated '
                                  'does not seem to capture everything going on:\n')
                for fb in self.pitchFeedback:
                    if len(fb.suggestions) > 0:
                        allToPrint.append(fb.message)
                        allToPrint.append(fb.matchStrength)
                        allToPrint.append('How about:')
                        [allToPrint.append(x) for x in fb.suggestions]
                        allToPrint.append('\n')
                    else:  # no suggestions
                        if constructiveOnly == False:
                            allToPrint.append(fb.message)
                            allToPrint.append(fb.matchStrength)
                            allToPrint.append('Sorry, no suggestions - '
                                              'I can\'t find any triads or sevenths.')
                            allToPrint.append('\n')
                        # Note: if constructiveOnly == True, print nothing

        if metre:
            self.metricalPositions()
            allToPrint.append('\nHARMONIC RHYTHM =====================\n')
            if len(self.metricalPositionFeedback) == 0:
                msg = 'The harmonic rhythm looks good: '
                msg += 'all the chord changes take place on strong metrical positions.'
                allToPrint.append(msg)
            else:  # if len(self.metricalPositionFeedback) > 0:
                allToPrint.append('In the following cases, the chord change is '
                                  'at an unusually weak metrical position:')
                [allToPrint.append(fb.message) for fb in self.metricalPositionFeedback]
            allToPrint.append('\n')

        if bass:
            self.compareBass()
            allToPrint.append('\nBASS / INVERSION =====================\n')
            if len(self.bassFeedback) == 0:
                msg = 'The inversions look good: '
                msg += 'the bass note/s implied by the Roman numerals appear at least once '
                msg += 'in the lowest part during the relevant span.'
                allToPrint.append(msg)
            else:  # len(self.bassFeedback) > 0:
                allToPrint.append(f'Bass note match: {round(self.bassScore * 100, 2)}%.')
                allToPrint.append('The following chords look ok, '
                                  'except for the bass note / inversion. '
                                  '(NB: pedal points are not currently supported):')
                for fb in self.bassFeedback:
                    if len(fb.suggestions) > 0:
                        allToPrint.append(fb.message)
                        allToPrint.append('How about:')
                        [allToPrint.append(x) for x in fb.suggestions]
                        allToPrint.append('\n')
                    else:  # no suggestions
                        if constructiveOnly == False:
                            allToPrint.append(fb.message)
                            allToPrint.append('Sorry, no inversion suggestions - '
                                              'none of the bass note(s) are in the chord.')
                            allToPrint.append('\n')
                        # if constructiveOnly == True, print nothing

        if len(self.errorLog) > 0:
            allToPrint.append('\nWARNINGS =====================\n')
            [allToPrint.append(x) for x in self.errorLog]

        if not outPath:
            outPath = '.'
        if not outFile:
            outFile = 'Feedback'
        text_file = open(f'{os.path.join(outPath, outFile)}.txt', "w")
        [text_file.write(x + '\n') for x in allToPrint]
        text_file.close()

    def _feedbackOnScore(self,
                         pitches: bool = True,
                         metre: bool = True,
                         bass: bool = True):
        '''
        Inserts comments on the score for moments where there is feedback available.

        Like printFeedback, option to use any or all of:
            'pitches' for pitch HarmonicRanges;
            'metre' for metrical positions; and
            'bass' for bass notes / inversions.
        '''

        totalFeedback = []

        if pitches:
            if not self.pitchFeedback:
                self.comparePitches()
                totalFeedback += [x for x in self.pitchFeedback]

        if metre:
            if not self.metricalPositionFeedback:
                self.metricalPositions()
                totalFeedback += [x for x in self.metricalPositionFeedback]

        if bass:
            if not self.bassFeedback:
                self.compareBass()
                totalFeedback += [x for x in self.bassFeedback]

        te = expressions.TextExpression('***')
        te.placement = 'above'
        for x in self.totalFeedback:
            self.score.parts[-1].startMeasure(x.startMeasure).insert(x.offset, te)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


# Static

def _intBeat(beat):
    '''
    Beats as integers, or rounded decimals
    '''

    if int(beat) == beat:
        return int(beat)
    else:
        return round(float(beat), 2)


def _importSV(pathToFile: str,
              splitMarker: str = '\t'):
    '''
    Imports TSV file data for further processing.
    '''

    with open(pathToFile, 'r') as f:
        data = []
        for row_num, line in enumerate(f):
            values = line.strip().split(splitMarker)
            data.append([v.strip('\"') for v in values])
    f.close()

    return data


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

class Test(unittest.TestCase):
    '''
    Test the three main use cases:
        score and analysis input separately;
        score with analysis on score;
        tab in (analysis separate)
    '''

    def testScoreInAnalysisSeparate(self):
        basePath = os.path.join('..', 'Corpus', 'Bach_Preludes', '1')

        testSeparate = ScoreAndAnalysis(os.path.join(basePath, 'score.mxl'),
                                        analysisLocation=os.path.join(basePath, 'human.txt'))

        testSeparate.runComparisons()

        self.assertEqual(len(testSeparate.pitchFeedback), 2)
        self.assertEqual(testSeparate.pitchFeedback[0].message[:29],
                         'Measure 28, beat 1, viio642/v')

        self.assertEqual(len(testSeparate.bassFeedback), 2)
        self.assertEqual(testSeparate.bassFeedback[0].message[:29],
                         'Measure 28, beat 1, viio642/v')
        # Same measure raises both errors due to the bass.

        self.assertEqual(len(testSeparate.metricalPositionFeedback), 0)

# ------------------------------------------------------------------------------

    def testScoreInWithAnalysis(self):
        basePath = os.path.join('..', 'Corpus', 'OpenScore-LiederCorpus')
        composer = 'Schubert,_Franz'
        collection = 'Schwanengesang,_D.957'
        song = '02_-_Kriegers_Ahnung'
        combinedPath = os.path.join(basePath, composer, collection, song)

        onScoreTest = ScoreAndAnalysis(os.path.join(combinedPath, 'human_onscore.musicxml'),
                                       analysisLocation='On score',
                                       analysisParts=1,
                                       minBeatStrength=0.25,
                                       tolerance=0.6)

        onScoreTest.runComparisons()

        self.assertEqual(len(onScoreTest.pitchFeedback), 1)
        self.assertEqual(onScoreTest.pitchFeedback[0].message[:30],
                         'Measure 46, beat 2, viio6 in A')

        self.assertEqual(len(onScoreTest.bassFeedback), 0)

        self.assertEqual(len(onScoreTest.metricalPositionFeedback), 5)

# ------------------------------------------------------------------------------

    def testTabIn(self):
        basePath = os.path.join('..', 'Corpus', 'OpenScore-LiederCorpus')
        composer = 'Hensel,_Fanny_(Mendelssohn)'
        collection = '5_Lieder,_Op.10'
        song = '1_-_Nach_Süden'
        combinedPath = os.path.join(basePath, composer, collection, song)

        testTab = ScoreAndAnalysis(os.path.join(combinedPath, 'slices.tsv'),
                                   analysisLocation=os.path.join(combinedPath, 'human.txt'))

        testTab.runComparisons()

        self.assertEqual(len(testTab.pitchFeedback), 4)
        self.assertEqual(testTab.pitchFeedback[0].message[:29],
                         'Measure 11, beat 3, viio6/V i')

        self.assertEqual(len(testTab.bassFeedback), 10)
        self.assertEqual(testTab.bassFeedback[0].message[:29],
                         'Measure 11, beat 3, viio6/V i')

        self.assertEqual(len(testTab.metricalPositionFeedback), 4)


# ------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
