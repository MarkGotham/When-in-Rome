import unittest

from Code.Resources import chord_profiles
from Code.Pitch_profiles.chord_comparisons import pitch_class_list_to_profile, normalise_dict


class Test(unittest.TestCase):

    def test_binary_profiles(self):
        """
        Create the binary profiles dict from scratch (normal forms) and check they match.
        """

        normal_forms_dict = {
            "diminished triad": [0, 3, 6],
            "minor triad": [0, 3, 7],
            "major triad": [0, 4, 7],
            "augmented triad": [0, 4, 8],
            "diminished seventh chord": [0, 3, 6, 9],
            "half-diminished seventh chord": [0, 3, 6, 10],
            "minor seventh chord": [0, 3, 7, 10],
            "dominant seventh chord": [0, 4, 7, 10],
            "major seventh chord": [0, 4, 7, 11],
        }

        test_dict = {}
        for norm in normal_forms_dict:
            pcp = pitch_class_list_to_profile(normal_forms_dict[norm])
            test_dict[norm] = pcp

        self.assertEqual(test_dict, chord_profiles.binary)

    def test_normalisation(self):
        """
        Test normalisation of dicts and match to existing collections.
        """
        for source_name in ['beethoven', 'lieder', 'winterreise']:
            source = getattr(chord_profiles, source_name)
            norm_source = normalise_dict(source, 'l1')
            self.assertEqual(norm_source, getattr(chord_profiles, source_name + '_sum'))
            for key in norm_source:
                sum_source = sum(source[key])
                self.assertEqual(round(sum_source, 2), 1)
