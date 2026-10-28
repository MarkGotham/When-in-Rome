import os
import tempfile
import unittest

from music21 import chord, converter, expressions

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

    def testFeedbackNumbers(self):
        """
        Each harmonic range with feedback gets a number,
        shown both on the score and in the printed feedback.
        """

        basePath = TEST_RESOURCES_FOLDER / "Example"
        sa = ScoreAndAnalysis(os.path.join(basePath, "score.mxl"),
                              analysisLocation=os.path.join(basePath, "analysis.txt"),
                              tolerance=60)

        with tempfile.TemporaryDirectory() as outPath:
            sa.writeScoreWithAnalysis(outPath=outPath, outFile="annotated.mxl")
            sa.printFeedback(outPath=outPath, outFile="feedback")
            with open(os.path.join(outPath, "feedback.txt")) as f:
                feedback = f.read()

        numbered = [hr for hr in sa.harmonicRanges if hr.feedbackNumber]
        self.assertGreater(len(numbered), 0)
        self.assertEqual([hr.feedbackNumber for hr in numbered],
                         list(range(1, len(numbered) + 1)))

        analysis = sa.scoreWithAnalysis.parts[-1]
        markers = analysis.recurse().getElementsByClass(expressions.TextExpression)
        self.assertEqual([te.content for te in markers],
                         [f"\u26a0\ufe0e{hr.feedbackNumber}" for hr in numbered])
        redChords = [c for c in analysis.recurse().getElementsByClass(chord.Chord)
                     if c.style.color == "red"]
        self.assertEqual(len(redChords), len(numbered))

        hr = sa.harmonicRanges[20]
        self.assertIn(f"[{hr.feedbackNumber}] {hr.bassFeedbackMessage}", feedback)
