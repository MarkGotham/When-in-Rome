# -*- coding: utf-8 -*-
"""
===============================
ANTHOLOGY (anthology.py)
===============================

Mark Gotham, 2020


LICENCE:
===============================

Creative Commons Attribution-NonCommercial 4.0 International License.
https://creativecommons.org/licenses/by-nc/4.0/


ABOUT:
===============================

Methods for retrieving specific Roman numerals and/or progressions from analyses.

NOTE: musical logic previously here (isNeapolitan and isMixture) now moved to the main
music21 repo's [roman.py](https://github.com/cuthbertLab/music21/blob/master/music21/roman.py)

"""

from music21 import converter
from music21 import interval
from music21 import roman

from typing import List, Optional, Union

import csv
import fnmatch
import os
import unittest


# ------------------------------------------------------------------------------

class RnFinder(object):
    """
    For retrieving specific Roman numerals and/or progressions from analyses.
    """

    def __init__(self,
                 pathToFile: str):

        self.userRnProgressionList = []
        self.augmentedChords = []
        self.augmentedSixths = []
        self.neapolitanSixths = []
        self.appliedChords = []
        self.mixtures = []

        self.analysis = converter.parse(pathToFile, format='romanText')
        self.rns = [x for x in self.analysis.recurse().getElementsByClass('RomanNumeral')]

    def findMixtures(self):

        for rn in self.rns:
            # NOTE: musical logic previously here now moved to the main music21 repo
            if not rn.secondaryRomanNumeral:
                if rn.isMixture():
                    self.mixtures.append(dataFromRn(rn))

    def findAppliedChords(self):

        for rn in self.rns:
            if rn.secondaryRomanNumeral:
                self.appliedChords.append(dataFromRn(rn))

    def findNeapolitanSixths(self):

        for rn in self.rns:
            # NOTE: musical logic previously here now moved to the main music21 repo
            if rn.isNeapolitan():
                self.neapolitanSixths.append(dataFromRn(rn))

    def findAugmentedSixths(self):

        for rn in self.rns:
            if rn.isAugmentedSixth():
                self.augmentedSixths.append(dataFromRn(rn))

    def findAugmentedChords(self,
                            acceptSevenths: bool = True):

        for rn in self.rns:
            if rn.isAugmentedTriad():
                self.augmentedChords.append(dataFromRn(rn))
            elif acceptSevenths:
                if rn.isSeventh:
                    if rn.isSeventhOfType([0, 4, 8, 11]) or rn.isSeventhOfType([0, 3, 7, 11]):
                        self.augmentedChords.append(dataFromRn(rn))

    def findProgressionByRns(self,
                             rns_list: List[str]):
        """
        Find a specific progression of Roman numerals in a given key input by the user as
        a list of Roman numerals figures like ['I', 'V65', 'I']
        """

        lnrns = len(rns_list)

        for overallIndex in range(len(self.rns) - lnrns):
            thisRange = self.rns[overallIndex: overallIndex + lnrns]

            keysInThisRange = [x.key for x in thisRange]
            distinctKeys = set(keysInThisRange)
            if len(distinctKeys) > 1:  # modulates
                break

            figures = [x.figure for x in thisRange]
            if figures == rns_list:

                # Variant on dataFromRn
                info = [thisRange[0].getContextByClass('Measure').measureNumber,
                        figures,
                        thisRange[0].key]

                self.userRnProgressionList.append(info)

    def findProgressionByTypeAndRoot(self,
                                     qualitiesList: List = ['major', 'major'],
                                     intervalList: List[Union[str, interval.Interval]] = ['M2'],
                                     bassOrRoot: Union['root', 'bass'] = 'root',
                                     ):
        '''
        Find a specific progression of chords using Roman numerals but
        searching by triad quality and bass or root motion.
        The defaults seek instances of a pair of major triads with
        the root of the second being tone higher than the first.
        This method includes instances that traverse key change.

        The logic is similar to findProgressionByRns,
        but refactored due to the creation of interval object here.
        '''

        lnQs = len(qualitiesList)

        if lnQs != len(intervalList) + 1:
            raise ValueError('There must be exactly one more quality than interval.')

        validQualities = ['diminished', 'minor', 'major', 'augmented']
        for q in qualitiesList:
            if q not in validQualities:
                raise ValueError(f'All the qualities values must be in {validQualities}')

        if bassOrRoot == 'bass':
            allRelevant = [[x.quality, x.bass.name, x.figure, x.key.name] for x in self.rns]
        elif bassOrRoot == 'root':
            allRelevant = [[x.quality, x.root.name, x.figure, x.key.name] for x in self.rns]
        else:
            raise ValueError('The bassOrRoot variable must be either bass or root.')

        for i in range(len(intervalList)):
            if isinstance(intervalList[i], interval.Interval):
                intervalList[i] = intervalList[i].name

        # Add intervals
        for x in range(len(allRelevant)):
            thisEntry = allRelevant[x]
            nextEntry = allRelevant[x + 1]
            i = interval.Interval(thisEntry[1], nextEntry[1]).name  # bass or root
            thisEntry.append(i)

        for index in range(len(allRelevant) - lnQs):
            thisRange = allRelevant[index: index + lnQs]
            these_qualities = [x[0] for x in thisRange]
            these_intervals = [x[-1] for x in thisRange]
            if (these_qualities == qualitiesList) and these_intervals == intervalList:
                info = [self.rns[index].getContextByClass('Measure').measureNumber,
                        [x[2] for x in thisRange],  # figures
                        [x[3] for x in thisRange],  # key(s).  TODO. better way for key changes?
                        ]
                self.userRnProgressionList.append(info)

    def findPotentialCommonToneDiminishedSeventh(self,
                                                 requireProlongation: bool = True):
        """
        Find a potential instance of the common tone diminished seventh in any form by seeking:
        a diminished seventh,
        which shares at least one pitch with
        the chord before, the one after, or both.

        If requireProlongation is True, the results are limited to cases where the
        diminished seventh is preceded and followed by the same chord.
        """

        for index in range(1, len(self.rns) - 1):

            info = []

            thisChord = self.rns[index]

            if thisChord.isDiminishedSeventh():

                previousChord = self.rns[index - 1]
                nextChord = self.rns[index + 1]
                if requireProlongation:
                    if previousChord != nextChord:
                        break

                pitchesNow = set([p.name for p in thisChord.pitches])

                if previousChord.key == thisChord.key:  # currently required, may change
                    if previousChord.figure != thisChord.figure:  # TODO handling of repeating RNs
                        pitchesBefore = set([p.name for p in previousChord.pitches])
                        if pitchesNow & pitchesBefore:  # any shared pitch(class)
                            info = [previousChord.getContextByClass('Measure').measureNumber,
                                    [previousChord.figure, thisChord.figure],
                                    previousChord.key.name,
                                    ]
                        else:
                            if requireProlongation:
                                continue  # can't be without the previous chord


                nextChord = self.rns[index + 1]
                if nextChord.key == thisChord.key:
                    if nextChord.figure != thisChord.figure:
                        if requireProlongation and (nextChord.figure != previousChord.figure):
                            # info = []
                            continue
                        pitchesAfter = set([p.name for p in previousChord.pitches])
                        if pitchesNow & pitchesAfter:
                            if info:  # before and after, add to existing (combine all three)
                                info[1].append(nextChord.figure)
                            else:
                                info = [thisChord.getContextByClass('Measure').measureNumber,
                                        [thisChord.figure, nextChord.figure],
                                        thisChord.key.name,
                                        ]

                if info:
                    self.userRnProgressionList.append(info)


# ------------------------------------------------------------------------------

# Static

def dataFromRn(rn):
    msn = rn.getContextByClass('Measure').measureNumber
    return [msn, rn.figure, rn.key.name.replace('-', 'b')]


# ------------------------------------------------------------------------------

corpora = ['Early_Choral',
           'Etudes_and_Preludes',
           'OpenScore-LiederCorpus',
           'Orchestral',
           'Piano_Sonatas',
           'Quartets',
           'Variations_and_Grounds']

validSearches = ['Modal Mixture',
                 'Augmented Chords',
                 'Augmented Sixths',
                 'Neapolitan Sixths',
                 'Applied Chords',
                 'Common Tone Diminished Sevenths',
                 'Progressions']


def oneSearchOneCorpus(corpus: str = 'OpenScore-LiederCorpus',
                       what: str = 'Modal Mixture',
                       progression: Optional[list] = [],
                       write: bool = True):
    """
    Runs the search methods on a specific pair of corpus and serach term.
    Settable to find any of
        'Modal Mixture',
        'Augmented Chords',
        'Augmented Sixths',
        'Neapolitan Sixths',
        'Applied Chords',
        'Common Tone Diminished Sevenths'
        and
        'Progressions'.
    Defaults to the 'OpenScore-LiederCorpus' and 'Modal mixture'.
    If searching for a progression, set the progression variable to a list of
    Roman numerals figure strings like ['I', 'V65', 'I']
    """

    if what not in validSearches:
        raise ValueError(f'For what, please select from among {validSearches}.')

    if what == 'Progression':
        if not progression:
            raise ValueError("If searching for a progression with the 'what' parameter, "
                             "set the 'progression' parameter to a list of Roman numeral figures "
                             "like ['I', 'V65', 'I'].")

    if corpus not in corpora:
        raise ValueError(f'Please select a corpus from among {corpora}.')

    lied = False
    if corpus == 'OpenScore-LiederCorpus':
        lied = True
        url = ''

    totalList = []

    corpusPath = os.path.join('..', 'Corpus', corpus)
    outPath = os.path.join('..', 'Anthology', corpus)

    for dpath, dname, fname in os.walk(corpusPath):
        for name in fname:
            if name == "analysis.txt":

                fullPath = str(os.path.join(dpath, name))
                pathtoFolder = fullPath[:-len(name)]
                print(pathtoFolder)

                idsDraft = pathtoFolder.split('/')[-4:-1]
                ids = [x.replace('_', ' ') for x in idsDraft]

                # URL for lieder
                if lied:
                    for fileName in os.listdir(pathtoFolder):
                        if fnmatch.fnmatch(fileName, 'lc*.mscx'):
                            lc = fileName[2:-5]
                            url = f'<a href="https://musescore.com/score/{lc}">{lc}</a>'
                            break
                    if not url:
                        print(f'No <lc*.mscx> file found in {pathtoFolder}')

                rnf = RnFinder(fullPath)

                if what == 'Modal Mixture':
                    rnf.findMixtures()
                    tempList = rnf.mixtures
                elif what == 'Augmented Chords':
                    rnf.findAugmentedChords()
                    tempList = rnf.augmentedChords
                elif what == 'Augmented Sixths':
                    rnf.findAugmentedSixths()
                    tempList = rnf.augmentedSixths
                elif what == 'Neapolitan Sixths':
                    rnf.findNeapolitanSixths()
                    tempList = rnf.neapolitanSixths
                elif what == 'Applied Chords':
                    rnf.findAppliedChords()
                    tempList = rnf.appliedChords
                elif what == 'Common Tone Diminished Sevenths':
                    rnf.findPotentialCommonToneDiminishedSeventh()
                    tempList = rnf.userRnProgressionList
                elif what == 'Progressions':
                    rnf.findProgressionByRns(rns_list=progression)
                    tempList = rnf.userRnProgressionList

                for x in tempList:
                    p = ids + x
                    if lied:
                        p += [url]
                    totalList.append(p)

    sortedList = sorted(totalList, key=lambda x: (x[0], x[1], x[2]))

    if not write:
        return sortedList

    with open(os.path.join(outPath, what + '.tsv'), "w") as svfile:
        svOut = csv.writer(svfile, delimiter='\t',
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)

        heads = ['COMPOSER',
                 'COLLECTION',
                 'MOVEMENT',
                 'MEASURE (START)',
                 'FIGURE(S)',
                 'KEY']
        if lied:
            heads.append('URL')

        svOut.writerow(heads)

        for entry in sortedList:
            svOut.writerow([x for x in entry])


def allSearchesOneCorpus(corpus: str = 'OpenScore-LiederCorpus'):
    """
    Runs the oneSearchOneCorpus function for
    one corpus and
    all search terms except 'Progressions'.
    """

    for w in validSearches[:-1]:  # omit progressions
        oneSearchOneCorpus(corpus=corpus, what=w)


def processAll():
    """
    Runs the oneSearchOneCorpus function for all pairs of
    corpus and search terms except 'Progressions'.
    """

    for c in corpora:
        for w in validSearches[:-1]:  # omit progressions
            oneSearchOneCorpus(corpus=c, what=w)


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testMixture(self):

        for fig in ['i', 'iio', 'bIII', 'iv', 'v', 'bVI', 'bVII', 'viio7']:
            # True, major key:
            self.assertTrue(roman.RomanNumeral(fig, 'A').isMixture())
            # False, minor key:
            self.assertFalse(roman.RomanNumeral(fig, 'a').isMixture())

        for fig in ['I', 'ii', '#iii', 'IV', 'viiø7']:
            # False, major key:
            self.assertFalse(roman.RomanNumeral(fig, 'A').isMixture())
            # True, minor key:
            self.assertTrue(roman.RomanNumeral(fig, 'a').isMixture())


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
