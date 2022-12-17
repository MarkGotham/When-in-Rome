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

    def testScoreAndAnalysis(self):
        """
        Score and analysis as separate files, both pre-parsed.
        """

        basePath = TEST_RESOURCES_FOLDER / "Example"
        score = converter.parse(os.path.join(basePath, 'score.mxl'))
        analysis = converter.parse(os.path.join(basePath, 'analysis.txt'), format='romantext')
        scoreAnalysisSeparate = ScoreAndAnalysis(score,
                                                 analysis,
                                                 tolerance=60)  # Tests setting a high bar
        scoreAnalysisTogether = ScoreAndAnalysis(os.path.join(basePath, 'analysis_on_score.mxl'),
                                                 analysisLocation='On score',
                                                 analysisParts=1,
                                                 minBeatStrength=0.25,
                                                 tolerance=60)  # default value
        scoreAnalysisTsv = ScoreAndAnalysis(str(basePath / 'slices.tsv'),
                                            analysisLocation=str(basePath / 'analysis.txt'),
                                            tolerance=60)
        for sa in [scoreAnalysisSeparate,
                   scoreAnalysisTogether,
                   scoreAnalysisTsv]:
            sa.runComparisons()
            self.assertEqual(sa.totalPitchFeedback, 27)
            self.assertEqual(sa.harmonicRanges[4].pitchFeedbackMessage[:28],
                             'Measure 2, beat 3, ii7 in Db')
            self.assertEqual(sa.totalBassFeedback, 4)
            self.assertEqual(sa.totalMetricalFeedback, 19)
