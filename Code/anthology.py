# -*- coding: utf-8 -*-
'''
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

'''

from music21 import converter
from music21 import roman

from typing import Optional

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
            if isMixture(rn):
                self.mixtures.append(dataFromRn(rn))

    def findAppliedChords(self):

        for rn in self.rns:
            if rn.secondaryRomanNumeral:
                self.appliedChords.append(dataFromRn(rn))

    def findNeapolitanSixths(self):

        for rn in self.rns:
            if rn.scaleDegree == 2:
                if rn.frontAlterationAccidental:
                    if rn.frontAlterationAccidental.name == 'flat':
                        if rn.quality == 'major':
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

    def findProgressionByRns(self, rns_list: list):
        '''
        Find a specific progression of Roman numerals in a given key input by the user as
        a list of Roman numerals figures like ['I', 'V65', 'I']
        '''

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

    # def findProgressionByTypeAndRoot(self, rn1, rn2):
    #     '''
    #     Equivalent method for finding progressions by triad type and root motion,
    #     including across key-changes.
    #     '''
    # TODO


# ------------------------------------------------------------------------------

# Static

def isMixture(rn: roman.RomanNumeral,
              considerSecondaryNumerals: bool = False):
        '''
        Checks if a RomanNumeral is an instance of 'modal mixture' in which the chord is not
        diatonic in the key specified, but would be would be in the parallel (German: variant)
        major / minor and can therefore be thought of as a 'mixture' or major and minor modes, or
        as a 'borrowing' from the one to the other.
        Examples include i in major or I in minor (sic).

        Specifically, this method returns True for all and only the following cases in any
        inversion:

        Major context:
        scale degree 1 and triad quality minor (minor tonic chord);
        scale degree 2 and triad quality diminished (covers both iio and iiø7);
        scale degree b3 and triad quality major (e.g. Eb in C);
        scale degree 4 and triad quality minor;
        scale degree 5 and triad quality minor (NB: potentially controversial);
        scale degree b6 and triad quality major;
        scale degree b7 and triad quality major; and
        scale degree 7 and it's a diminished seventh specifically (the triad is dim. in both).

        Minor context:
        scale degree 1 and triad quality major (major tonic chord);
        scale degree 2 and triad quality minor (not diminished);
        scale degree #3 and triad quality minor (e.g. e in c);
        scale degree 4 and triad quality major; and
        scale degree 7 and it's a half diminished seventh specifically (the triad is dim. in both).
        '''

        if considerSecondaryNumerals and rn.secondaryRomanNumeral:
            return rn.secondaryRomanNumeral.isMixture()

        if (not rn.isTriad) and (not rn.isSeventh):
            return False

        if not rn.key.mode:  # keyObj can also be a Scale (with no mode)
            return False

        mode = rn.key.mode
        if mode not in ('major', 'minor'):
            return False

        scaleDegree = rn.scaleDegree
        if scaleDegree not in range(1, 8):
            return False

        quality = rn.quality
        if quality not in ('diminished', 'major', 'minor'):
            return False

        if rn.frontAlterationAccidental:
            frontAccidentalName = rn.frontAlterationAccidental.name
        else:
            frontAccidentalName = 'natural'

        majorKeyMixtures = {
            (1, 'minor', 'natural'),
            (2, 'diminished', 'natural'),
            (3, 'major', 'flat'),
            (4, 'minor', 'natural'),
            (5, 'minor', 'natural'),  # Potentially controversial
            (6, 'major', 'flat'),
            (7, 'major', 'flat'),  # Note diminished 7th handled separately
        }

        minorKeyMixtures = {
            (1, 'major', 'natural'),
            (2, 'minor', 'natural'),
            (3, 'minor', 'sharp'),
            (4, 'major', 'natural'),
            # 5 N/A
            # 6 N/A
            # 7 half-diminished handled separately
        }

        if mode == 'major':
            if (scaleDegree, quality, frontAccidentalName) in majorKeyMixtures:
                return True
            elif (scaleDegree == 7) and (rn.isDiminishedSeventh()):
                return True
        elif mode == 'minor':
            if (scaleDegree, quality, frontAccidentalName) in minorKeyMixtures:
                return True
            elif (scaleDegree == 7) and (rn.isHalfDiminishedSeventh()):
                return True

        return False


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
                 'Progressions']


def oneSearchOneCorpus(corpus: str = 'OpenScore-LiederCorpus',
                       what: str = 'Modal Mixture',
                       progression: Optional[list] = [],
                       write: bool = True):
    '''
    Runs the search methods on a specific pair of corpus and serach term.
    Settable to find any of
        'Modal Mixture',
        'Augmented Chords',
        'Augmented Sixths',
        'Neapolitan Sixths',
        'Applied Chords',
        and
        'Progressions'.
    Defaults to the 'OpenScore-LiederCorpus' and 'Modal mixture'.
    If searching for a progression, set the progression variable to a list of
    Roman numerals figure strings like ['I', 'V65', 'I']
    '''

    if what not in validSearches:
        raise ValueError(f'For what, please select from among {validSearches}.')

    if what == 'Progression':
        if not progression:
            raise ValueError('If searching for a progression with the \'what\' parameter, '
                             'set the \'progression\' parameter to a list of Roman numeral figures '
                             'like [\'I\', \'V65\', \'I\'].')

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


def process():
    '''
    Runs the oneSearchOneCorpus funcion for all pairs of
    corpus and search terms except 'Progressions'.
    '''

    for c in corpora:
        for w in validSearches[:-1]:  # omit progressions
            oneSearchOneCorpus(corpus=c, what=w)


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testMixture(self):

        for fig in ['i', 'iio', 'bIII', 'iv', 'v', 'bVI', 'bVII', 'viio7']:
            # True, major key:
            self.assertTrue(isMixture(roman.RomanNumeral(fig, 'A')))
            # False, minor key:
            self.assertFalse(isMixture(roman.RomanNumeral(fig, 'a')))

        for fig in ['I', 'ii', '#iii', 'IV', 'viiø7']:
            # False, major key:
            self.assertFalse(isMixture(roman.RomanNumeral(fig, 'A')))
            # True, minor key:
            self.assertTrue(isMixture(roman.RomanNumeral(fig, 'a')))


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
