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

        corpus = "OpenScore-LiederCorpus"

        for this_mode in ["major", "minor"]:
            no_inv = chord_usage.simplify_or_consolidate_usage_dict(
                f"{this_mode}_{corpus}.json",
                simplify_not_consolidate=True,
                no_inv=True,
                no_other_alt=True,
                no_secondary=True,
                major_not_minor=(this_mode == "major"),
                write=False)

            pop_list = []

            for fig in no_inv:
                if not roman.RomanNumeral(fig).isAugmentedSixth():
                    pop_list.append(fig)

            for p in pop_list:
                no_inv.pop(p)

            if this_mode == "major":
                self.assertAlmostEqual(no_inv["It"], 0.051)
            else:  # minor
                self.assertAlmostEqual(no_inv["It"], 0.37)
