import unittest

from music21 import roman, chord

from Code.anthology import isOfType, intervalMatch


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

    def testIsOfType(self):
        self.assertTrue(isOfType(roman.RomanNumeral('I'), [6, 10, 1]))
        self.assertTrue(isOfType(chord.Chord('G- B-- D-'), '3-11A'))

    def testIntervalMatch(self):

        rns = [roman.RomanNumeral(x) for x in ['i', 'iiø65', 'V7']]

        intervalsType1 = ['M2', 'P4']
        self.assertTrue(intervalMatch(rns, intervalsType1, bassOrRoot='root'))
        self.assertFalse(intervalMatch(rns, intervalsType1, bassOrRoot='bass'))

        intervalsType2 = ['P4', 'M2']
        self.assertTrue(intervalMatch(rns, intervalsType2, bassOrRoot='bass'))
        self.assertFalse(intervalMatch(rns, intervalsType2, bassOrRoot='root'))
