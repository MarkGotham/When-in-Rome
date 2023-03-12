# -*- coding: utf-8 -*-
"""
===============================
THE ROMAN UMPIRE (romanUmpire.py)
===============================

Mark Gotham, 2019–20


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


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
There is also an option for writing the score with analysis attached in musical notation and
highlighting moments for which there is feedback available directly on that score.
"""

from music21 import converter
from music21 import chord
from music21 import expressions
from music21 import layout
from music21 import roman
from music21 import stream

from copy import deepcopy
import csv
import os
from typing import Union, Optional

from . import alignStreams
from . import harmonicFunction
from . import import_SV

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


# Three supporting object types:

class Slice:
    """
    A reduction object corresponding to one 'vertical' slice through the score.
    A 'slice' is a momentary cross-section during which none of the notes change.
    """

    def __init__(self):
        self.uniqueOffsetID = None
        self.measure = None
        self.beat = None

        self.pitches = []
        self.quarterLength = None
        self.beatStrength = None


# ------------------------------------------------------------------------------

class HarmonicRange:
    """
    HarmonicRange objects cover part of a score, usually including:
    a Roman numeral and the corresponding score 'slices' for that range.
    In addition to details of the Roman numeral and the corresponding slices in question,
    this class also keeps track of the
        start/end positions;
        lengths in terms of both measures and quarter notes;
        all types of feedback generated.

    Usage here focusses on assessing the Roman numeral (key and figure).
    This object can also be used to assess key alone, e.g. for key finding tasks.
    """

    def __init__(self, source=None):

        # Initialise with Nones prior to (optionally) setting those values.

        self.startOffset: Optional[float] = None
        self.endOffset: Optional[float] = None
        self.quarterLength: Optional[float] = None

        self.startMeasure: Optional[int] = None
        self.endMeasure: Optional[int] = None
        self.measureLength: Optional[int] = None

        self.startBeat: Optional[float] = None
        self.endBeat: Optional[float] = None
        self.beatStrength: Optional[float] = None

        self.slices: Optional[list] = []

        self.scorePitchUsageDict = {}
        self.pitchesInBothScoreAndChord: Optional[list] = []

        # Feedback

        self.pitchFeedbackMessage: Optional[str] = None
        self.pitchMatchStrength: Optional[float] = None  # NB for pitch only
        self.pitchSuggestions: Optional[list] = []

        self.rareRnFeedbackMessage: Optional[str] = None

        self.metricalFeedbackMessage: Optional[str] = None

        self.bassFeedbackMessage: Optional[str] = None
        self.bassSuggestions: Optional[list] = []

        if source:

            if ('NotRest' in source.classes) and ('GeneralNote' in source.classes):
                # Covers notes and chords, excludes rests.
                self.getCoreValues(source)

                # Roman. Classes include 'Chord', 'NotRest', 'GeneralNote' as well as:
                if 'RomanNumeral' in source.classes:
                    self.getMoreValuesFromRN(source)

                    if rareRn(source):
                        msg = f'Measure {self.startMeasure}, beat {self.startBeat}: ' \
                              f'{source.figure} in {source.key}.'
                        self.rareRnFeedbackMessage = msg

                else:
                    self.figure: Optional[str] = None
                    self.key: Optional[str] = None
                    self.bassPitch: Optional[str] = None
                    self.chordPitches: Optional[list] = []

            else:
                raise ValueError('Initialise a HarmonicRange object either empty, or'
                                 'with a relevant object: Note, Chord, or RomanNumeral.')

    def getCoreValues(self, source):
        """
        Retrieve core variables from a relevant object: Note, Chord, or RomanNumeral.
        """
        self.startMeasure = int(source.measureNumber)
        self.startBeat = _intBeat(source.beat)
        self.beatStrength = source.beatStrength
        self.quarterLength = round(source.quarterLength, 2)
        self.startOffset = round(source.activeSite.offset + source.offset, 2)

    def getMoreValuesFromRN(self,
                            rn: roman.RomanNumeral):
        """
        Retrieve additional values specific to RomanNumeral objects.
        """
        self.figure = rn.figure
        self.key = rn.key.tonicPitchNameWithCase.replace('-', 'b')
        self.chordPitches = [p.nameWithOctave for p in rn.pitches]
        self.bassPitch = rn.bass().name

    def makeScorePitchUsageDict(self):
        """
        Make a 'ScorePitchUsageDict' dict for recording which pitches are used in the score
        and to what extent (combined length).
        """
        for s in self.slices:
            for p in s.pitches:
                if p in self.scorePitchUsageDict:
                    self.scorePitchUsageDict[p] += s.quarterLength
                else:
                    self.scorePitchUsageDict[p] = s.quarterLength

    def calculatePitchMatchStrength(self):
        """
        Calculates the 'PitchMatchStrength':
        the percentage of pitches in the score that are
        accounted for by the specified harmony (weighted by length).
        """
        used = 0
        total = 0

        comparison = [x[:-1] for x in self.chordPitches]  # Remove octave for comparison

        for x in self.scorePitchUsageDict:
            total += self.scorePitchUsageDict[x]
            if x[:-1] in comparison:
                self.pitchesInBothScoreAndChord.append(x)
                used += self.scorePitchUsageDict[x]

        if total == 0:
            self.pitchMatchStrength = 0
        else:
            self.pitchMatchStrength = round((100 * used / total), 2)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


class ScoreAndAnalysis:
    """
    Class for handling:
        'ground-truth' score data (either the score itself or a tabular representation thereof);
        Roman numeral analysis (either on the score or as a separate Roman text analysis file);
        comparisons between the two (with HarmonicRange objects).

    This class includes methods for
        processing feedback,
        writing feedback and / or scores for review

    Parameters:

    scoreOrData:
        a score (music21.stream.Score object) or str path to such a file.

    analysisLocation:
        defaults to 'On score' (for analyses input on the score itself);
        for separate analyses, analysisLocation should be the pre-converted rntxt file
        (again, that file itself, or a str path to such a file are both accepted).

    analysisParts:
        an int for the number of analysis (i.e. non-score) parts
        so the system knows to exclude them from score-based considerations.

    analysisPartNo:
        an int for the part number (in score order) of the analysis part where applicable.
        Defaults to -1 (i.e. the lowest part).

    minBeatStrength:
        A float for the least beat strength acceptable before the feedback draws
        attention to the chord change on the basis of the weak metrical position.

    tolerance:
        A percentage match for the proportional match between the pitches of the chord and the
        corresponding part of the piece.
        Matches lower that this value attract pitch feedback.

    carryPitchesOver:
        Do pitches remain in effect over rests?
        By default, this class ignores rests, leaving pitches in place until the next pitched event
        as part of calculating match strength.
    """

    def __init__(self,
                 scoreOrData: Union[stream.Score, str, os.PathLike],
                 analysisLocation: Union[stream.Score, stream.Part, str] = 'On score',
                 analysisParts: int = 1,
                 analysisPartNo: int = -1,
                 minBeatStrength: float = 0.25,
                 tolerance: int = 60,
                 carryPitchesOver: bool = True
                 ):

        self.scoreOrData = scoreOrData
        self.name = None

        self.analysisLocation = analysisLocation
        self.analysisParts = analysisParts
        self.analysisPartNo = analysisPartNo

        self.minBeatStrength = minBeatStrength
        self.tolerance = tolerance
        self.carryPitchesOver = carryPitchesOver

        self.slices = []
        self.prevSlicePitches = None

        self.harmonicRanges = []

        self.totalPitchFeedback = None  # None at init, 0 when running comparison
        self.totalMetricalFeedback = None  # sim.
        self.totalBassFeedback = None  # sim.
        self.totalRareRnFeedback = 0  # 0 at init (comparison works a bit differently)

        self.overallPitchScore = None
        self.overallBassScore = None

        self.errorLog = []

        self._parseScoreData()
        self._parseAnalysis()
        self.slicesMatchedUp: bool = False

        self.svOut = None

    def _parseScoreData(self):
        """
        Handles input options for score, either:
            a score in a recognised format (e.g. musicxml), or
            a tabular file (.tsv or .csv) having handled the slicing in advance.
        """

        if isinstance(self.scoreOrData, stream.Score):
            self.score = self.scoreOrData
            self._scoreInit()

        elif isinstance(self.scoreOrData, (str, os.PathLike)):
            self.name, extension = os.path.splitext(self.scoreOrData)

            if extension in ['.tsv', '.csv']:
                if self.analysisLocation == 'On score':
                    raise ValueError('Cannot use tabular input (no score) with analysis on score.')
                if extension == '.tsv':
                    split_marker = '\t'
                else:  # extension == '.csv':
                    split_marker = ','
                self.score = import_SV(self.scoreOrData, split_marker=split_marker)
                if self.score[0][0] != '0.0':  # First offset always 0. If not, header row
                    self.score = self.score[1:]  # Ignore header row
                self._retrieveSlicesFromList()  # NOTE: sets totalLength and scoreMeasures
            elif extension in ['.mxl', '.musicxml', '.midi', '.mid', '.krn']:  # Actual score:
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
        """
        Subsidiary preparation of, and extractions from, the score.
        """

        self._removeGraceNotes()
        self.score.expandRepeats()
        self._retrieveSlicesFromScore()
        self.totalLength = self.score.quarterLength
        self.scoreMeasures = len(self.score.parts[0].getElementsByClass('Measure'))

    def _parseAnalysis(self):
        """
        Handles input options for analysis, either:
            a music21 stream.Score in a recognised format (e.g. rntxt), or
            as lyrics on a score.
        """

        if isinstance(self.analysisLocation, stream.Score):
            self.analysis = self.analysisLocation.parts[0]
            # TODO validity checks on analysis (e.g. at least one Roman numeral)
            self._getSeparateAnalysis()
        elif isinstance(self.analysisLocation, (str, os.PathLike)):
            if self.analysisLocation == 'On score':
                self._getOnScoreAnalysis()
            else:  # analysisLocation must be a path to a Roman text file
                if os.path.isdir(self.analysisLocation):
                    self.analysisLocation /= 'analysis.txt'
                elif os.path.isfile(self.analysisLocation):
                    if not self.analysisLocation.endswith('txt'):
                        print(self.analysisLocation)
                        msg = "When the `analysisLocation` argument points to a file path, " \
                              "that file must have the extension `.txt` or `.rntxt`."
                        raise ValueError(msg)
                self.analysis = converter.parse(self.analysisLocation, format='Romantext').parts[0]
                self._getSeparateAnalysis()
        else:
            raise TypeError(f'The `analysisLocation` argument (currently {self.analysisLocation} '
                            'must be a music21 stream.Score() or '
                            'a path to a valid file.')

    def writeScoreWithAnalysis(self,
                               outPath: str = '.',
                               outFile: str = 'on_score',
                               feedback: bool = True,
                               voicingFromScore: bool = False,
                               includeFunctionLabels: bool = True,
                               lieder: bool = True):
        """
        Mostly to combine an off-score analysis with the corresponding score and write to disc.

        Option (feedback=True, default) to include markers in the score
        for moments with associated feedback.

        Error raised in the case of a call on score with analysis already on there
        (i.e. with analysisLocation = 'On score' in the init) and feedback as false.
        Nothing to add in that case.

        Additional presentation option (lieder=True, default) for returning the
        Mensurstrich brace to the piano part of the lieder.
        Don't worry if that doesn't mean anything to you.
        """

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

            reference = self.scoreWithAnalysis.parts[0].template()
            analysis = alignStreams.matchParts(reference_part=reference,
                                               part_to_adjust=analysis)

            for n in analysis.recurse().notes:
                if n.lyric:
                    n.lyric = n.lyric.replace('-', 'b')

            if includeFunctionLabels:  # TODO stripTies() or sim?
                for rn in analysis.recurse().getElementsByClass(roman.RomanNumeral):
                    if rn.pitches[0].octave == 5:
                        for p in rn.pitches:
                            p.octave -= 1
                    fx = harmonicFunction.figureToFunction(rn)
                    rn.addLyric(fx)

            self.scoreWithAnalysis.insert(0, analysis)

        if lieder:  # If lieder option is set to true and ...
            if len(self.scoreWithAnalysis.parts) == 4:  # there are 4 parts inc. the analysis
                staffGrouping = layout.StaffGroup([self.scoreWithAnalysis.parts[1],
                                                   self.scoreWithAnalysis.parts[2]
                                                   ],
                                                  name='Piano', abbreviation='Pno.', symbol='brace')
                staffGrouping.barTogether = 'Mensurstrich'
                self.scoreWithAnalysis.insert(0, staffGrouping)

        if feedback:
            self._feedbackOnScore()

        if voicingFromScore:
            self.makeScoreVoiceLeadingReduction()

        if outFile == 'on_score':
            if self.name:
                outFile = self.name + '_on_score.mxl'

        self.scoreWithAnalysis.write('mxl', fp=os.path.join(outPath, outFile))

    def makeScoreVoiceLeadingReduction(self):
        """
        Takes the analysis part and replaces the default, one-stave, close-position
        chords with voicing an spacing based on the pitches used in the score
        for a more musical reduction.
        """

        count = 0
        for rn in self.scoreWithAnalysis.parts[-1].recurse().getElementsByClass('RomanNumeral'):
            rn.pitches = self.harmonicRanges[count].pitchesInBothScoreAndChord
            count += 1

        count += 1  # sic, for off by one

        if count != len(self.harmonicRanges):  # i.e. number of hrs vs RNs
            self.errorLog.append(("There's a mismatch between the number of "
                                  "harmonicRange and Roman numeral objects. "
                                  "This shouldn't happen and the chords may be displaced."))

    def _removeGraceNotes(self):
        """
        Removes all grace notes in the score.
        They are of relatively low importance and
        can cause disproportionate problems when processing.
        """

        notesToRemove = []
        for n in self.score.recurse().notes:
            if n.duration.isGrace:
                notesToRemove.append(n)

        for n in notesToRemove:
            n.activeSite.remove(n)

    def _retrieveSlicesFromScore(self):
        """
        Extracts chord and rest info from the score as Slice objects and
        populates self.slices with a list of these Slices.

        If the analysisLocation is 'On score' then this method first
        removes that analysis from consideration.
        The number of analysis parts is given in the init by analysisParts.

        By default, this method ignores rests, in the sense that it assumes that the
        more recent chord remains in effect until the next pitched event.
        As such, there will be no slices with an empty pitch list: the previous slice's
        pitches are carried over to the next slice.
        This includes treating single pitches as a one-entry 'chord'.
        Override this behaviour by setting carryPitchesOver to False (returning empty pitch lists).
        """

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
                    if self.carryPitchesOver and self.prevSlicePitches:
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
                             outFile: str = 'slices',
                             includeAnalysis: bool = True,
                             changesOnly: bool = True):
        """
        Subsidiary method for writing out the Slice object information
        retrieved from the score to a value separated file with columns for:
        'offset', 'measure', 'beat', 'beatStrength', 'quarterLength', 'pitches'.

        Having done so, that information can be re-retrieved via retrieveSlicesFromList.
        Among other benefits, its computationally lighter to work with sv files than scores.

        Optionally, includeAnalysis adds two additional columns for 'key' and 'figure',
        populating those columns for each change of chord in the analysis.
        """

        headers = ['offset', 'measure', 'beat', 'beatStrength', 'quarterLength', 'pitches']
        if includeAnalysis:
            headers += ['key', 'figure']

        with open(f'{os.path.join(outPath, outFile)}.tsv', "w") as svfile:
            self.svOut = csv.writer(svfile, delimiter='\t',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)

            if includeAnalysis:
                for hr in self.harmonicRanges:
                    if not hr.slices:
                        print(f'No slices in this hr: {hr.startMeasure}')
                        break
                    self._writeSlice(hr.slices[0], analysis=True, key=hr.key, fig=hr.figure)
                    if len(hr.slices) > 1:
                        for s in hr.slices[1:]:
                            if changesOnly:
                                self._writeSlice(s, analysis=True)
                                # sic, not repeating key and figure where it doesn't change
                            else:
                                self._writeSlice(s, analysis=True, key=hr.key, fig=hr.figure)

            else:
                for s in self.slices:
                    self._writeSlice(s, analysis=False)

    def _writeSlice(self,
                    entry: Slice,
                    analysis: bool,
                    key: Optional[str] = '',
                    fig: Optional[str] = '',
                    ):
        """
        Write data from one slice to a csv.
        """
        if analysis:
            self.svOut.writerow([entry.uniqueOffsetID,
                                 entry.measure,
                                 entry.beat,
                                 entry.beatStrength,
                                 entry.quarterLength,
                                 entry.pitches,
                                 key,
                                 fig
                                 ])
        else:
            self.svOut.writerow([entry.uniqueOffsetID,
                                 entry.measure,
                                 entry.beat,
                                 entry.beatStrength,
                                 entry.quarterLength,
                                 entry.pitches,
                                 ])

    def _retrieveSlicesFromList(self):
        """
        Populates self.slices with a list of
        Slice objects extracted from entries in the 'score' (here a list).

        Checks that the list is plausible.
        """

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
        """
        For checking monotonic increment through the piece.
        if not, logs error and rejects element (slice or RN).
        """

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
        """
        Gets an analysis hosted in the main score,
        as lyrics in one part (the lowest, by default).
        Straight to putative 'HarmonicRange' object.
        """
        # TODO: support type='Lyric' for alternatives?

        self.prevailingKey = 'FAKE KEY'

        for x in self.score.parts[self.analysisPartNo].recurse().notes:

            if x.lyric:

                rn = self._romanFromLyric(x.lyric)
                if rn:
                    thisHarmonicRange = HarmonicRange(x)
                    thisHarmonicRange.getMoreValuesFromRN(rn)
                    # TODO compress but note the gap between a note and a contextless rn

                    self.harmonicRanges.append(thisHarmonicRange)

                else:
                    msg = f'Error retrieving a Roman numeral from the lyric {x.lyric} ' \
                          f'in measure {x.measureNumber} with the ' \
                          f'prevailing key of {self.prevailingKey}.'
                    self.errorLog.append(msg)

    def _romanFromLyric(self, lyric):
        """
        Converts lyrics in recognised format into m21 Roman Numeral objects.
        Format: '<Key>: <Figure>' for first entry and all key changes; otherwise just '<Figure>'.

        Includes the following substitutions:
        all spaces (including non-breaking spaces) with nothing;
        '-' with 'b' for flats;
        bracket types to accept e.g. (no5) as well as the official [no5]; and
        'sus' with '[addX]' for suspensions/added notes.
        """

        splitter_pairs = [('//', 1),  # Single '/' = applied chord; double '//' for alt. and pivot
                          ("\n", 0)  # case of two-line lyric as in RN + "\n"+ FN.
                          ]

        for this_string, this_position in splitter_pairs:
            if this_string in lyric:
                lyric = lyric.split(this_string)[this_position]

        replaceDict = {
            ' ': '',
            '\xa0': '',
            '-': 'b',
            '(': '[',
            ')': ']',
        }

        for x in replaceDict:
            lyric = lyric.replace(x, replaceDict[x])

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
        """
        Gets an analysis from a path to a RNTXT file.
        Straight to putative 'HarmonicRange' objects.
        """

        self.analysisMeasures = len(self.analysis.recurse().getElementsByClass('Measure'))

        if self.scoreMeasures != self.analysisMeasures:
            msg = f'WARNING: There are {self.scoreMeasures} measures in the score ' \
                  f'but {self.analysisMeasures} in your analysis. ' \
                  'This is usually a question of either the beginning or end: either\n' \
                  '1) The final chord in the analysis ' \
                  'comes before the final measure, or\n' \
                  "2) There's an anacrusis in the score without an accompanying harmony " \
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
        """
        Takes the prepared list of HarmonicRange objects (from the analysis)
        and adds to each the corresponding part of the score (as a list of 'slices')
        for subsequent comparison.
        """

        self.indexCount = 0

        for index in range(len(self.harmonicRanges) - 1):
            thisHR = self.harmonicRanges[index]
            thisHR.endOffset = self.harmonicRanges[index + 1].startOffset
            thisHR.quarterLength = thisHR.endOffset - thisHR.startOffset
            self._singleMatchUp(thisHR)

        # Special case of last one.
        self.harmonicRanges[-1].endOffset = self.totalLength
        self._singleMatchUp(self.harmonicRanges[-1])

        if self.indexCount != len(self.slices):
            msg = f'Slices missing: {self.indexCount} accounted for ' \
                  f'of {len(self.slices)} total.'
            self.errorLog.append(msg)

    def _singleMatchUp(self,
                       hr: HarmonicRange):
        """
        HarmonicRange and match up of a Roman numeral
        with slices (potentially) in that range by position in score.
        Note that harmony changes between slice changes are
        not supported and may lead to erratic results.
        I.e. chords should change where at least one pitch changes.
        """

        for thisSlice in self.slices[self.indexCount:]:
            if hr.startOffset <= thisSlice.uniqueOffsetID < hr.endOffset:
                hr.slices.append(thisSlice)
                self.indexCount += 1
            else:
                break

    def matchUp(self):
        """
        Checks that the slices have been matched up and if not then does so.
        Necessary given all the routes through.
        """
        if not self.slicesMatchedUp:
            self._rnSliceMatchUp()
            self.slicesMatchedUp = True

    # ------------------------------------------------------------------------------

    # Assessments:

    def runComparisons(self):
        """
        Runs comparison types for feedback:
            metricalPositions(),
            comparePitches(), and
            compareBass().
        NB: rareRn() runs separately. User can choose whether to display the feedback
        but it is collected in any case.
        """

        self.matchUp()
        self.metricalPositions()
        self.comparePitches()
        self.compareBass()

    def metricalPositions(self):
        """
        Creates feedback flagging up cases of chords on weak positions.
        """

        if self.totalMetricalFeedback:
            return

        self.totalMetricalFeedback = 0

        self.matchUp()

        for hr in self.harmonicRanges:
            if hr.beatStrength < self.minBeatStrength:
                # if hr.beatStrength < lastBeatStrength:  # TODO: this context

                msg = f'Measure {hr.startMeasure}, {hr.figure} in {hr.key} ' \
                      f'appears on beat {hr.startBeat}.'
                # No .replace('-', 'b') this time - only relevant to key, and handled above
                hr.metricalFeedbackMessage = msg

                self.totalMetricalFeedback += 1

                # lastBeatStrength = x.beatStrength  # TODO: this context

    def comparePitches(self):
        """
        Single RN-slice comparison for pitches:
        do the chords reflect the pitch content of the score section in question?
        """

        if self.totalPitchFeedback:
            return

        self.totalPitchFeedback = 0

        self.matchUp()

        pitchNumerator = 0

        for hr in self.harmonicRanges:

            if not hr.scorePitchUsageDict:
                hr.makeScorePitchUsageDict()
            if not hr.pitchMatchStrength:
                hr.calculatePitchMatchStrength()

            compLength = hr.endOffset - hr.startOffset

            pitchNumerator += (compLength * hr.pitchMatchStrength)

            if hr.pitchMatchStrength < self.tolerance:  # get feedback and reduce overallPitchScore

                # Suggestions
                pl = [pList.pitches for pList in hr.slices]
                suggestions = []
                for sl in hr.slices:
                    chd = chord.Chord(sl.pitches)
                    if chd.isTriad() or chd.isSeventh():
                        rn = roman.romanNumeralFromChord(chd, hr.key)
                        if rn.figure != hr.figure:
                            suggestions.append([sl.measure, sl.beat, rn.figure, sl.pitches])
                if len(suggestions) > 0:
                    for s in suggestions:
                        hr.pitchSuggestions.append(f'm{s[0]} b{s[1]} {s[2]} for the pitches {s[3]}')

                # Message
                msg = f'Measure {hr.startMeasure}, beat {hr.startBeat}, {hr.figure} in {hr.key}, ' \
                      f'indicating the pitches {hr.chordPitches} ' \
                      f'accounting for successive chord "slices" of {pl}.'
                msg = msg.replace('-', 'b')  # Ab not A-. Relevant to key, pitches, and slices
                hr.pitchFeedbackMessage = msg

                # Note: pitchMatchStrength now handled above

                self.totalPitchFeedback += 1

        self.overallPitchScore = round(pitchNumerator / self.totalLength, 2)

    def compareBass(self):
        """
        Single RN-slice comparison for bass pitches (inversion).
        Creates feedback for cases where
        the bass pitch indicated by the Roman numeral's inversion
        does not appear as the lowest note during the span in question.
        """

        if self.totalBassFeedback:
            return

        self.totalBassFeedback = 0

        self.matchUp()

        bassNumerator = 0

        for hr in self.harmonicRanges:

            # bassPitchesWithOctave = [slice.pitches[0] for slice in hr.slices]
            bassPitchesWithOctave = []  # Sometimes the slice is a rest I guess?
            for s in hr.slices:
                if len(s.pitches) > 0:
                    bassPitchesWithOctave.append(s.pitches[0])

            bassPitchesNoOctave = [p[:-1] for p in bassPitchesWithOctave]
            bassPitchesWithOctave = list(set(bassPitchesWithOctave))

            if hr.bassPitch not in bassPitchesNoOctave:

                inversionSuggestions = []

                for bassPitch in bassPitchesNoOctave:
                    if bassPitch in hr.chordPitches:  # already retrieved
                        suggestedPitches = hr.chordPitches
                        suggestedPitches.append(bassPitch + '0')  # To ensure it is lowest
                        suggestedChord = chord.Chord(suggestedPitches)
                        rn = roman.romanNumeralFromChord(suggestedChord, hr.key)
                        inversionSuggestions.append(
                            f'm{hr.startMeasure} b{hr.startBeat} {rn.figure}')

                msg = f'Measure {hr.startMeasure}, beat {hr.startBeat}, {hr.figure} in {hr.key}, ' \
                      f'indicating the bass {hr.bassPitch} ' \
                      f'for lowest note(s) of: {bassPitchesWithOctave}.'
                msg = msg.replace('-', 'b')  # E.g. Ab not A-. Key handled. Pitches, and slices here
                hr.bassFeedbackMessage = msg
                # TODO: implement a corresponding matchStrength for bass?
                hr.bassSuggestions = []

                if len(inversionSuggestions) > 0:
                    hr.bassSuggestions = list(set(inversionSuggestions))  # Once for each suggestion

                self.totalBassFeedback += 1

            else:  # hr.bassPitch in bassPitchesNoOctave:
                compLength = hr.endOffset - hr.startOffset
                bassNumerator += compLength

        self.overallBassScore = round(bassNumerator * 100 / self.totalLength, 2)

    def _proportionSimilarity(self,
                              hr: HarmonicRange,
                              sl: Slice):
        """
        Approximate measure of the 'similarity' between a
        reference HarmonicRange object (Roman numeral, etc) and an actual slice of the score.

        Returns the proportion of score pitches accounted for.

        Note:
        This is not limited to distinct pitches:
        it returns a better score for multiple tonics, for instance.
        """
        # TODO: Penalty for notes in the RN not used? Not here, only overall?

        if len(sl) == 0:
            self.errorLog.append(
                f'Roman numeral {hr.figure} in {hr.key}, m.{hr.startMeasure}: '
                f'No pitches in one of the slices.'
            )

            return 0

        intersection = [x for x in sl if x in hr.chordPitches]
        proportion = len(intersection) / len(sl)

        return proportion

    # ------------------------------------------------------------------------------

    # Feedback:

    def printFeedback(self,
                      pitches: bool = True,
                      metre: bool = True,
                      bass: bool = True,
                      rare: bool = True,
                      constructiveOnly: bool = False,
                      outPath: str = '.',
                      outFile: str = 'Feedback'):
        """
        Select feedback to print: any or all of:
            'pitches' for the pitch match between a Roman Numeral and score segment;
            'rare' for the use of a parseable but rare Roman Numeral;
            'metre' for metrical positions; and
            'bass' for bass notes / inversions.
        If constructiveOnly is True, then the returned feedback will be limited to
        cases for which there is a corresponding alternative suggestion ready.
        """

        if (not pitches) and (not rare) and (not metre) and (not bass):
            raise ValueError('Please select at least one of the feedback options.')

        if pitches:
            self.comparePitches()
            pitchToPrint = ['PITCH COVERAGE =====================\n']
            if self.totalPitchFeedback == 0:
                msg = 'The pitch coverage looks good: ' \
                      'all of the chords match the corresponding sections of the score well.\n'
                pitchToPrint.append(msg)
            else:  # if len(self.pitchFeedback) > 0:
                pitchToPrint.append(f'Total cases: {self.totalPitchFeedback}\n')
                pitchToPrint.append('Overall pitch match: '
                                    f'{self.overallPitchScore}%.\n')
                pitchToPrint.append('In the following cases, the chord indicated '
                                    'does not seem to capture everything going on:\n')
                for hr in self.harmonicRanges:
                    if hr.pitchFeedbackMessage:
                        if len(hr.pitchSuggestions) > 0:
                            pitchToPrint.append(hr.pitchFeedbackMessage)
                            pitchToPrint.append(f'Pitch match: {hr.pitchMatchStrength}%')
                            pitchToPrint.append('How about:')
                            for x in hr.pitchSuggestions:
                                pitchToPrint.append(x)
                            pitchToPrint.append('\n')
                        else:  # no suggestions
                            if not constructiveOnly:
                                pitchToPrint.append(hr.pitchFeedbackMessage)
                                pitchToPrint.append(f'Pitch match: {hr.pitchMatchStrength}%')
                                pitchToPrint.append('Sorry, no suggestions - '
                                                    "I can't find any triads or sevenths.")
                                pitchToPrint.append('\n')
                            # NB: nothing printed if no suggestions and constructiveOnly

        if rare:
            rareToPrint = ['RARE ROMAN NUMERALS =====================\n']
            self.totalRareRnFeedback == 0
            for hr in self.harmonicRanges:
                if hr.rareRnFeedbackMessage:
                    self.totalRareRnFeedback += 1
                    rareToPrint.append(hr.rareRnFeedbackMessage + '\n')

            if self.totalRareRnFeedback == 0:
                msg = 'No rare or unconventional Roman Numerals in this analysis.\n'
                rareToPrint.append(msg)
            else:
                msg = f'Total cases: {self.totalRareRnFeedback}\n' \
                      'The following Roman numerals are perfectly ' \
                      'clear and the system has no trouble parsing them, though ' \
                      'they are somewhat rare so may be worth reviewing:\n'
                rareToPrint.insert(1, msg)  # between header and feedback.

        if metre:
            self.metricalPositions()
            metreToPrint = ['HARMONIC RHYTHM =====================\n']
            if self.totalMetricalFeedback == 0:
                msg = 'The harmonic rhythm looks good: '
                msg += 'all the chord changes take place on strong metrical positions.\n'
                metreToPrint.append(msg)
            else:
                metreToPrint.append(f'Total cases: {self.totalMetricalFeedback}\n')
                metreToPrint.append('In the following cases, the chord change is '
                                    'at an unusually weak metrical position:\n')
                for hr in self.harmonicRanges:
                    if hr.metricalFeedbackMessage:
                        metreToPrint.append(hr.metricalFeedbackMessage + '\n')

        if bass:
            self.compareBass()
            bassToPrint = ['BASS / INVERSION =====================\n']
            if self.totalBassFeedback == 0:
                msg = 'The inversions look good: '
                msg += 'the bass note/s implied by the Roman numerals appear at least once '
                msg += 'in the lowest part during the relevant span.'
                bassToPrint.append(msg)
            else:
                bassToPrint.append(f'Total cases: {self.totalBassFeedback}\n')
                bassToPrint.append(f'Overall bass note match: {self.overallBassScore}%.\n')
                bassToPrint.append("In these cases, the specified bass note doesn't "
                                   'appear in the lowest part during. '
                                   '(NB: pedal points are not yet supported):\n')
                for hr in self.harmonicRanges:
                    if hr.bassFeedbackMessage:
                        if len(hr.bassSuggestions) > 0:
                            bassToPrint.append(hr.bassFeedbackMessage)
                            bassToPrint.append('How about:')
                            for x in hr.bassSuggestions:
                                bassToPrint.append(x)
                            bassToPrint.append('\n')
                        else:  # no suggestions
                            if not constructiveOnly:
                                bassToPrint.append(hr.bassFeedbackMessage)
                                bassToPrint.append('Sorry, no inversion suggestions - '
                                                   'none of the bass note(s) are in the chord.')
                                bassToPrint.append('\n')

        # Write
        text_file = open(f'{os.path.join(outPath, outFile)}.txt', "w")
        if pitches:
            for x in pitchToPrint:
                text_file.write(x + '\n')
            text_file.write('\n')
        if rare:
            for x in rareToPrint:
                text_file.write(x + '\n')
            text_file.write('\n')
        if metre:
            for x in metreToPrint:
                text_file.write(x + '\n')
            text_file.write('\n')
        if bass:
            for x in bassToPrint:
                text_file.write(x + '\n')
            text_file.write('\n')
        if len(self.errorLog) > 0:
            text_file.write('WARNINGS =====================\n')
            for x in self.errorLog:
                text_file.write(x + '\n')

        text_file.close()

    def _feedbackOnScore(self,
                         pitches: bool = True,
                         rare: bool = True,
                         metre: bool = True,
                         bass: bool = True):
        """
        Inserts comments on the score for moments where there is feedback available.
        As with the printFeedback method, you can chose to any or all of the feedback types:
        'pitches', 'rare', 'metre'; and 'bass'.
        """

        if pitches:
            self.comparePitches()
        if metre:
            self.metricalPositions()
        if bass:
            self.compareBass()

        for hr in self.harmonicRanges:
            if pitches and hr.pitchFeedbackMessage:
                self.insertFeedback(hr, '* Pitch')
            if rare and hr.rareRnFeedbackMessage:
                self.insertFeedback(hr, '* Rare')
            if metre and hr.metricalFeedbackMessage:
                self.insertFeedback(hr, '* Beat')
            if bass and hr.bassFeedbackMessage:
                self.insertFeedback(hr, '* Bass')

    def insertFeedback(self,
                       hr: HarmonicRange,
                       message: str):
        """
        Shared method for inserting feedback of each type in to the score.
        """
        te = expressions.TextExpression(message)  # NB: Have to make a new one each time
        te.placement = 'above'
        te.style.color = 'red'
        # Known issue: ^ This works within musicXML but readers like MuseScore don't show it.
        p = self.scoreWithAnalysis.parts[-1]
        m = p.measure(hr.startMeasure)
        mOffset = m.getOffsetInHierarchy(p)
        offsetInMeasure = hr.startOffset - mOffset  # TODO compress, but note not offset nor beat
        m.insert(offsetInMeasure, te)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def _intBeat(beat):
    """
    Beats as integers, or rounded decimals
    """

    if int(beat) == beat:
        return int(beat)
    else:
        return round(float(beat), 2)


def rareRn(rn: roman.RomanNumeral):
    """
    Returns True for rare Roman numerals that will parse ok but are unusual in analyses.
    Specifically,
    False = Triads, Sevenths, Augmented Sixths, Ninths in root position
    True = anything else including 9th inversions.
    """

    if rn.isTriad():
        return False
    elif rn.isSeventh():
        return False
    elif rn.isAugmentedSixth():
        return False
    elif rn.figure == 'V9':
        return False

    return True
