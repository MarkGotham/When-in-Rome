import unittest

from music21 import converter

from Code.skeletonHarmony import RnAnalysis, rnString, intBeat, fixTextRn
from Code import CORPUS_FOLDER

from . import TEST_RESOURCES_FOLDER


class Test(unittest.TestCase):

    def testFullAnalysis(self):
        """
        Test the extraction of an analysis from an `analysis_on_score` file.
        As these are no longer provided across the corpus,
        we use the shared `TEST_RESOURCES_FOLDER` example (from Clara Schumann).
        """

        score = converter.parse(TEST_RESOURCES_FOLDER / "Example" / "analysis_on_score.mxl")
        rna = RnAnalysis(score)
        rna.prepList(template=False)  # ***

        self.assertEqual(rna.combinedList[0], "\nTime Signature: 4/4")
        self.assertEqual(rna.combinedList[15], "m13 I b3 i6")

    # ------------------------------------------------------------------------------

    def testPartialAnalysis(self):
        """
        Test the creation of an analysis from a partial one.
        See the dedicated partial analysis in the `TEST_RESOURCES_FOLDER` example.
        """

        score = converter.parse(TEST_RESOURCES_FOLDER / "testPartialAnalysis.mxl")

        preludeAnalysis = RnAnalysis(score,
                                     composer="J.S. Bach",
                                     title="Prelude No. 1 (BWV 846)"
                                     )
        preludeAnalysis.chfyChordAndLabel(ignoreParts=2)

        da = preludeAnalysis.deducedAnalysis

        self.assertEqual(da[0], [1, 1.0, "C: I"])
        self.assertEqual(da[11], [12, 1.0, "d: viio6#43"])  # TODO: music21's RomanNumeralFromChord
        self.assertEqual(da[19], [20, 1.0, "V7/IV"])
        self.assertEqual(da[22], [23, 1.0, "viio42"])

    # ------------------------------------------------------------------------------

    def testTemplate(self):
        """
        Test the creation of an analysis template from a score within the corpus.
        """

        from music21 import converter

        corpus = CORPUS_FOLDER / "OpenScore-LiederCorpus"
        composer = "Hensel,_Fanny_(Mendelssohn)"
        collection = "5_Lieder,_Op.10"
        song = "1_Nach_Süden"

        score = converter.parse(corpus / composer / collection / song / "score.mxl")
        rna = RnAnalysis(score)
        rna.prepList(template=True)  # ***

        self.assertEqual(rna.combinedList[0], "\nTime Signature: 12/8")
        self.assertEqual(rna.combinedList[15], "m14 b1")

    # ------------------------------------------------------------------------------

    def testRnString(self):
        test = rnString([1, 1, "G: I"])
        self.assertEqual(test, "m1 G: I")

    # ------------------------------------------------------------------------------

    def testIntBeat(self):
        test = intBeat(1, roundValue=2)
        self.assertEqual(test, 1)
        test = intBeat(1.5, roundValue=2)
        self.assertEqual(test, 1.5)
        test = intBeat(1.11111111, roundValue=2)
        self.assertEqual(test, 1.11)
        test = intBeat(8/3, roundValue=2)
        self.assertEqual(test, 2.67)

    def testFixTextRn(self):
        testString = "e:   viio6"  # Excessive spaces, remove them
        self.assertEqual(fixTextRn(testString), "e: viio6")

        testString = "f:i"  # No space, make one
        self.assertEqual(fixTextRn(testString), "f: i")

        testString = "F: I6"
        self.assertEqual(fixTextRn(testString), testString)  # Unchanged

        testString = "F: vii/o6"
        self.assertEqual(fixTextRn(testString), "F: viiø6")

        testString = "V\xc2\xa042(no3)"
        self.assertEqual(fixTextRn(testString), "V42[no3]")

        testString = "ii°6"
        self.assertEqual(fixTextRn(testString), "iio6")
