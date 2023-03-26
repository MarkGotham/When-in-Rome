import unittest

from music21 import roman
from Code.Pitch_profiles import chord_features, chord_usage


class Test(unittest.TestCase):

    def testSingleChordFeatures(self):
        """
        Artificial test of
        theoretically chosen major triad against
        practice suggesting diminished
        Returns: None
        """
        rn = roman.RomanNumeral('I')  # Tonic major
        profile = [309.17, 37.31, 10.09, 376.62, 10.75, 21.43,
                   316.04, 1.02, 19.79, 33.68, 24.33, 22.97]  # c diminished
        testFeaturesSet = chord_features.SingleChordFeatures(rn, profile)

        for pair in (
                ('chordQualityVector',
                 [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]),  # major
                ('thirdTypeVector',
                 [0, 1, 0]),  # major
                ('fifthTypeVector',
                 [0, 1, 0, 0]),  # perfect
                ('seventhTypeVector',
                 [0, 0, 0, 1]),  # None
                ('rootPitchClassVector',
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),  # C
                ('hauptFunctionVector',
                 [1, 0, 0, 0, 0, 0, 0]),  # T
                ('functionVector',
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),  # T
                ('chosenChordPCPVector',
                 [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),  # C major
                ('bestFitChordPCPVector',
                 [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]),  # c diminished

                ('chordTypeMatchVector',  # False, major vs dim.
                 [0]),
                ('chordRotationMatchVector',  # True, C = C
                 [1]),

                ('distanceToBestFitChordPCPVector',
                 [0.307]),
                ('distanceToChosenChordVector',
                 [0.7285]),

                ('fullChordCommonnessVector',
                 [1]),  # Most common ...
                ('simplifiedChordCommonnessVector',
                 [1])  # ... in both cases
        ):
            vector = getattr(testFeaturesSet, pair[0])
            self.assertEqual(vector, pair[1])

    def test_Aug6(self):

        maj = chord_usage.get_Aug6s(corpus_name="OpenScore-LiederCorpus", this_mode="major")
        min = chord_usage.get_Aug6s(corpus_name="OpenScore-LiederCorpus", this_mode="minor")

        self.assertEqual(round(maj["It"], 2), 0.05)
        self.assertEqual(round(min["It"], 2), 0.42)

    def test_N6(self):

        maj = chord_usage.get_N6s(corpus_name="OpenScore-LiederCorpus", this_mode="major")
        min = chord_usage.get_N6s(corpus_name="OpenScore-LiederCorpus", this_mode="minor")

        self.assertEqual(round(maj["bII"], 1), 0.1)
        self.assertEqual(round(min["bII6"], 1), 0.3)

    def testChordPCs(self):
        """
        Test list of pitch class sets associated with chords in the corpus.
        Returns: None
        """

        maj, min = chord_usage.pc_usage()

        for m in [maj, min]:
            self.assertTrue("i" in m['3-11A'])
            self.assertTrue("I" in m['3-11B'])
            self.assertTrue("V7" in m['4-27B'])
            self.assertTrue('Fr43' in m['4-25'])

        self.assertTrue('V43[b5]' in min['4-25'])  # Not in maj
