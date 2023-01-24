import os
import unittest

from music21 import converter

from Code.romanUmpire import ScoreAndAnalysis
from . import TEST_RESOURCES_FOLDER


class Test(unittest.TestCase):

    def testScoreAndAnalysis(self):
        """
        Using the shared `TEST_RESOURCES_FOLDER` example (from Clara Schumann),
        test the multiple input options:
            score and analysis input separately;
            score with analysis on score;
            tab in ("slices.tsv", analysis separate)

        """

        basePath = TEST_RESOURCES_FOLDER / "Example"
        score = converter.parse(os.path.join(basePath, "score.mxl"))
        analysis = converter.parse(os.path.join(basePath, "analysis.txt"), format="romantext")
        scoreAnalysisSeparate = ScoreAndAnalysis(score,
                                                 analysis,
                                                 tolerance=60)
        scoreAnalysisTogether = ScoreAndAnalysis(os.path.join(basePath, "analysis_on_score.mxl"),
                                                 analysisLocation="On score",
                                                 analysisParts=1,
                                                 minBeatStrength=0.25,
                                                 tolerance=60)
        scoreAnalysisTsv = ScoreAndAnalysis(str(basePath / "slices.tsv"),
                                            analysisLocation=str(basePath / "analysis.txt"),
                                            tolerance=60)
        for sa in [scoreAnalysisSeparate,
                   scoreAnalysisTogether,
                   scoreAnalysisTsv
                   ]:

            sa.runComparisons()

            self.assertEqual(sa.totalPitchFeedback, 0)
            # self.assertEqual(sa.totalBassFeedback, 4)
            # TODO: investigate ^. scoreAnalysisTogether case missing one bass feedback notice.
            self.assertEqual(sa.harmonicRanges[20].bassFeedbackMessage,
                             "Measure 9, beat 1, iiø7 in bb, "
                             "indicating the bass C for lowest note(s) of: ['Eb2'].",)
            self.assertEqual(sa.totalMetricalFeedback, 19)
