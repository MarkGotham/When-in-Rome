#------------------------------------------------------------------------------

import unittest

from music21 import common
from music21 import exceptions21
from music21 import pitch
from music21 import interval
from music21 import roman

import numpy as np
import itertools
import csv

#------------------------------------------------------------------------------

# Prepare comprehensive lists

class RNlists:
        '''
        Prepares a comprehensive list of roman numeral types as realised by m21, encompassing:
        - every combination of the figures 2–9 (= 255)
        - Major/minor key (= 2),
        - Root accidental ['b', '', '#'] (= 3)
        - Scale degree, I-VII (= 7)
        - Chord type (o, m, M, +; e.g. ['io', 'i', 'I', 'I+',]).  (= 4)
        NB: there are 255*2*3*7*4 = 42,840 outcomes here so the file will be big (& slow to open)
        NB: most of these will be nonsense, just there for comprehensiveness.
        '''
        # TODO: ['b', '', '#'] for each figure.

        def figures(listLength=9, maxFig=9):
            '''
            Prepares the combinations of figures.
            '''

            figures = []

            for thisLength in range(1, listLength):
                for iteration in itertools.combinations(range(2, maxFig+1), thisLength):
                    full = iteration[::-1]
                    compressed = ''.join([str(x) for x in full])
                    figures.append(compressed)

            return figures

#------------------------------------------------------------------------------

        def RNarray(figures, major=True, minor=True, writeEachFig=True):
            '''
            Prepares the RNs from the figures.
            '''

            allRomanListOfLists = []

            for fig in figures:
                thisFigListOfLists = []
                for accidental in ['b', '', '#']:
                    for scaleDegree in ['i','ii','iii','iv','v','vi','vii']:
                        for chordType in [scaleDegree.lower()+'o',
                                          scaleDegree.lower(),
                                          scaleDegree.upper(),
                                          scaleDegree.upper()+'+']:
                            # Need to do accidental again for each element in figure. Maybe above?
                            componentParts = [accidental, chordType, str(fig)]

                            joinedRN = ''.join(componentParts)
                            majRN = roman.RomanNumeral(joinedRN, 'C')
                            minRN = roman.RomanNumeral(joinedRN, 'a')
                            outTrio = (joinedRN,
                                       [p.name for p in majRN.pitches],
                                       [p.name for p in minRN.pitches])
                            thisFigListOfLists.append(outTrio)

                if writeEachFig==True:
                    RNlists.makeTSVFile(thisFigListOfLists,
                            outFilePath='/Users/Mark/Documents/GitHub/When-in-Rome/Lists/',
                            outFileName=fig+'.tsv'
                            )
                else:
                    allRomanListOfLists.append(thisFigListOfLists)
                    return allRomanListOfLists

#------------------------------------------------------------------------------

        def makeTSVFile(data,
                        outFilePath,
                        outFileName='TSV_FILE.tsv',):
            '''
            Outputs data to (a) TSV file(s).
            '''

            with open(outFilePath+outFileName, 'a') as csvfile: # 'a' to allow multiple works
                csvOut = csv.writer(csvfile, delimiter='\t',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)

                headers = ['Figure', 'MajorContext', 'MinorContext']

                csvOut.writerow([x for x in headers])

                for sublist in data:
                    csvOut.writerow([x for x in sublist])

#------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testList(self):

        figs = RNlists.figures(listLength=3, maxFig=4)
        test = RNlists.RNarray(figs, writeEachFig=False)

        self.assertIsInstance(test, list)
        self.assertIsInstance(test[0], list)
        self.assertIsInstance(test[0][0], list)
        self.assertIsInstance(test[0][0][0], list)
        self.assertEqual(len(test), 1)
        self.assertEqual(len(test[0]), 84)
        self.assertEqual(test[0][0], 3)
        self.assertEqual(test[0][0][0], 4)
