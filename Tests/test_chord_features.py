import unittest

from music21 import roman

from Code.Pitch_profiles.chord_features import SingleChordFeatures


class Test(unittest.TestCase):

    def testSingleChordFeatures(self):
        rn = roman.RomanNumeral('I')  # Tonic major
        profile = [309.17, 37.31, 10.09, 376.62, 10.75, 21.43,
                   316.04, 1.02, 19.79, 33.68, 24.33, 22.97]  # c diminished
        testFeaturesSet = SingleChordFeatures(rn, profile)

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
                 [1]),  # Most common = 1
                ('simplifiedChordCommonnessVector',
                 [0.908])  # Still very common
        ):
            vector = getattr(testFeaturesSet, pair[0])
            self.assertEqual(vector, pair[1])
