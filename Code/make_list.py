# ------------------------------------------------------------------------------

import unittest
from music21 import roman
from itertools import combinations
import csv

# ------------------------------------------------------------------------------

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

    def __init__(self, listLength=9, maxFig=9):

        self.listLength = listLength
        self.maxFig = maxFig
        self.figures()

    def figures(self):
        '''
        Prepares the combinations of figures.
        '''

        self.figs = []

        for thisLength in range(1, self.listLength):
            for iteration in combinations(range(2, self.maxFig+1), thisLength):
                full = iteration[::-1]
                compressed = ''.join([str(x) for x in full])
                self.figs.append(compressed)

# ------------------------------------------------------------------------------

    def rnArray(self, major=True, minor=True):
        '''
        Prepares the RNs from the figures.
        '''

        self.allRomanListOfLists = []

        for fig in self.figs:
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

            self.allRomanListOfLists.append(thisFigListOfLists)

# ------------------------------------------------------------------------------

    def makeTSVFile(self,
                    outFilePath,
                    outFileName='TSV_FILE.tsv',):
        '''
        Outputs data to (a) TSV file(s).
        '''

        with open(outFilePath + outFileName, 'a') as csvfile:
            csvOut = csv.writer(csvfile, delimiter='\t',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)

            headers = ['Figure', 'MajorContext', 'MinorContext']

            csvOut.writerow([x for x in headers])

            for sublist in self.allRomanListOfLists:
                csvOut.writerow([x for x in sublist])

# ------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testList(self):

        figs = RNlists(listLength=3, maxFig=4)
        figs.rnArray()

        self.assertIsInstance(figs.allRomanListOfLists, list)
        self.assertIsInstance(figs.allRomanListOfLists[0], list)
        self.assertEqual(len(figs.allRomanListOfLists), 6)
        self.assertEqual(len(figs.allRomanListOfLists[0]), 84)
        self.assertEqual(figs.allRomanListOfLists[0][0][0], 'bio2')

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
