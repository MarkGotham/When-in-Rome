import unittest

from music21 import roman

from Code.harmonicFunction import functionToFigure, figureToFunction


class Test(unittest.TestCase):

    def testInitialCases(self):
        self.assertEqual(functionToFigure('T'), 'I')
        self.assertEqual(figureToFunction('i'), 't')

    def testSimplifiedAndPreferred(self):
        """tP preferred over dL and simplifies to t"""
        self.assertEqual(figureToFunction('III'), 'tP')
        self.assertEqual(figureToFunction('III', simplified=True), 't')

    def testRomanNumeralObjects(self):
        self.assertEqual(figureToFunction(roman.RomanNumeral('IV')), 'S')
        self.assertEqual(figureToFunction(roman.RomanNumeral('iv')), 's')

    def testIgnoresInversion(self):
        """
        If the input is a string, then no match will be found (returns False).
        If the input is a roman.RomanNumeral object they will be ignored
        (using the romanNumeralAlone attribute).
        """
        self.assertEqual(figureToFunction('V42'), False)
        self.assertEqual(figureToFunction(roman.RomanNumeral('i6')), 't')
