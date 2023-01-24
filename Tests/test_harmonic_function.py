import unittest

from music21 import roman

from Code.harmonicFunction import functionToFigure, figureToFunction


class Test(unittest.TestCase):

    def testInitialCases(self):
        self.assertEqual(functionToFigure("T"), "I")
        self.assertEqual(figureToFunction("i"), "t")

    def testSimplifiedAndPreferred(self):
        """tP preferred over dL and simplifies to t"""
        rn = roman.RomanNumeral("III", "a")
        self.assertEqual(figureToFunction(rn), "tP")
        self.assertEqual(figureToFunction(rn, simplified=True), "t")

    def testSpecialCases(self):
        self.assertEqual(figureToFunction(roman.RomanNumeral("Cad64", "Eb")), "D")
        self.assertEqual(figureToFunction(roman.RomanNumeral("Cad64", "eb")), "D")
        self.assertEqual(figureToFunction(roman.RomanNumeral("viio", "F#")), "D")
        self.assertEqual(figureToFunction(roman.RomanNumeral("viio", "f#")), "D")

    def testIgnoresInversion(self):
        """
        Inversion ignored using the romanNumeralAlone attribute.
        """
        self.assertEqual(str(figureToFunction("V42")), "D")
        self.assertEqual(figureToFunction(roman.RomanNumeral("i6")), "t")
