import unittest

from Code import CORPUS_FOLDER
from Code.Pitch_profiles import chord_profiles
from Code.Pitch_profiles.chord_comparisons import pitch_class_list_to_profile, build_profiles_from_corpus, \
    corpus_chord_comparison, normalise_dict


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

    def test_corpus_build(self):
        """
        Run the build process on Schubert's Winterreise and check nothing's changed
        (ie, it matches the values in chord_profiles).
        """
        base_path = CORPUS_FOLDER / 'OpenScore-LiederCorpus'
        base_path = str(base_path / 'Schubert,_Franz' / 'Winterreise,_D.911')
        build = build_profiles_from_corpus(base_path)
        self.assertEqual(build, chord_profiles.winterreise)

    def test_corpus_comparison(self):
        """
        Run the comparison process for
        Schubert's Winterreise (source) against
        profiles built from the  full lieder dataset (reference),
        and check nothing's changed.
        """
        base_path = CORPUS_FOLDER / 'OpenScore-LiederCorpus'
        base_path = str(base_path / 'Schubert,_Franz' / 'Winterreise,_D.911')
        comps = corpus_chord_comparison(base_path, reference_profile_dict=chord_profiles.lieder_sum)
        self.assertEqual(comps, (2013, 546, 96, 2655, 78.664))

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
