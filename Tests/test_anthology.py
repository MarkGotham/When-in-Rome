import unittest

from music21 import roman, chord

from Code.anthology import is_of_type, interval_match


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

    def test_is_of_type(self):
        self.assertTrue(is_of_type(roman.RomanNumeral('I'), [6, 10, 1]))
        self.assertTrue(is_of_type(chord.Chord('G- B-- D-'), '3-11A'))

    def test_interval_match(self):

        rns = [roman.RomanNumeral(x) for x in ['i', 'iiø65', 'V7']]

        intervalsType1 = ['M2', 'P4']
        self.assertTrue(interval_match(rns, intervalsType1, bass_not_root=False))
        self.assertFalse(interval_match(rns, intervalsType1, bass_not_root=True))

        intervalsType2 = ['P4', 'M2']
        self.assertTrue(interval_match(rns, intervalsType2, bass_not_root=True))
        self.assertFalse(interval_match(rns, intervalsType2, bass_not_root=False))
