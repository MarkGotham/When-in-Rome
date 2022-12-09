import os
import unittest

from music21 import converter

from Code.romanUmpire import ScoreAndAnalysis
from Code import CORPUS_FOLDER
from . import TEST_RESOURCES_FOLDER


class Test(unittest.TestCase):
    """
    Test the three main use cases:
        score and analysis input separately;
        score with analysis on score;
        tab in (analysis separate)
    """

    def testScoreInAnalysisSeparate(self):
        """
        Score and analysis as separate files, both pre-parsed.
        """

        corpus = 'Etudes_and_Preludes'
        composer = 'Bach,_Johann_Sebastian'
        collection = 'The_Well-Tempered_Clavier_I'
        piece = '01'

        basePath = str(CORPUS_FOLDER / corpus / composer / collection / piece)
        score = converter.parse(os.path.join(basePath, 'score.mxl'))
        analysis = converter.parse(os.path.join(basePath, 'analysis.txt'), format='romantext')
        testSeparate = ScoreAndAnalysis(score,
                                        analysis,
                                        tolerance=80)  # Tests setting a high bar
        testSeparate.runComparisons()

        self.assertEqual(testSeparate.totalPitchFeedback, 2)
        self.assertEqual(testSeparate.harmonicRanges[27].pitchFeedbackMessage[:28],
                         'Measure 28, beat 1, viio42/v')
        self.assertEqual(testSeparate.totalBassFeedback, 2)  # The same moments
        self.assertEqual(testSeparate.totalMetricalFeedback, 0)

    # ------------------------------------------------------------------------------

    def testScoreInWithAnalysis(self):
        """
        Score and analysis in same file, parsed here from the file path.
        """

        corpus = 'OpenScore-LiederCorpus'
        composer = 'Schubert,_Franz'
        collection = 'Schwanengesang,_D.957'
        piece = '02_Kriegers_Ahnung'

        basePath = str(CORPUS_FOLDER / corpus / composer / collection / piece)

        onScoreTest = ScoreAndAnalysis(os.path.join(basePath, 'analysis_on_score.mxl'),
                                       analysisLocation='On score',
                                       analysisParts=1,
                                       minBeatStrength=0.25,
                                       tolerance=60)  # default value

        onScoreTest.runComparisons()
        self.assertEqual(onScoreTest.totalPitchFeedback, 0)
        self.assertEqual(onScoreTest.totalBassFeedback, 0)
        self.assertEqual(onScoreTest.totalRareRnFeedback, 0)
        self.assertEqual(onScoreTest.totalMetricalFeedback, 4)

    # ------------------------------------------------------------------------------

    def testTabIn(self):
        """
        Score and analysis in separate files, with the score represented in tabular format.
        """

        basePath = TEST_RESOURCES_FOLDER / "Example"
        testTab = ScoreAndAnalysis(str(basePath / 'slices.tsv'),
                                   analysisLocation=str(basePath / 'analysis.txt'),
                                   tolerance=70)
        testTab.runComparisons()

        self.assertEqual(testTab.totalPitchFeedback, 17)
        self.assertEqual(testTab.harmonicRanges[4].pitchFeedbackMessage[:28],
                         'Measure 2, beat 3, ii7 in Db')
        self.assertEqual(testTab.totalBassFeedback, 4)
        self.assertEqual(testTab.totalMetricalFeedback, 19)
