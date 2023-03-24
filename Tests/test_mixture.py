# -*- coding: utf-8 -*-

import unittest
from itertools import combinations

from music21 import chord, key, roman

from Code import mixture


# ------------------------------------------------------------------------------

def chord_combinations(
        key_obj: key.Key | str,
        cardinality: int = 3,
) -> dict:
    """
    Get scale degrees for a key (major or minor as given by key_obj).
    Build every permutation per cardinality.
    For 3 ignore non triads; for 4 ignore non sevenths.
    (Other cardinalities currently untested.)
    """

    if not isinstance(key_obj, key.Key):
        if isinstance(key_obj, str):
            key_obj = key.Key(key_obj)
        else:
            raise TypeError("key_obj must be a key.Key or str")

    if key_obj.mode == "minor":
        natural_minor = [p.name for p in key_obj.pitches]
        homeKeyPitches = natural_minor[:6]  # sic, include m6 - VI not mixture
        key_root = natural_minor[0]
        major = [p.name for p in key.Key(key_root.upper()).pitches]
    elif key_obj.mode == "major":
        major = [p.name for p in key_obj.pitches]
        homeKeyPitches = major  # sic, all
        key_root = major[0]
        natural_minor = [p.name for p in key.Key(key_root.lower()).pitches]
    else:
        raise ValueError("key_obj must have `.mode` attribute of `major` or `minor`.")

    combined = list(set(natural_minor + major))

    # Exclude
    all_combs = combinations(combined, cardinality)
    out_info = {}
    for t in all_combs:
        pitches = [x for x in t]
        chd = chord.Chord(pitches)
        if cardinality == 3:
            if not chd.isTriad():
                continue
        elif cardinality == 4:
            if not chd.isSeventh():
                continue

        # Include
        diatonic = True
        for p in pitches:
            if p not in homeKeyPitches:
                diatonic = False
        if diatonic:
            continue

        # Exclude
        chord_root = chd.root().name
        root_enforced_pitches = [chord_root + "2"] + pitches
        rn = roman.romanNumeralFromChord(chord.Chord(root_enforced_pitches), key_obj)
        rn = mixture.add_mixture_info(rn)
        if rn.mixture_metric >= 0:
            out_info[rn.figure] = mixture.rn_to_mixture_list(rn)

    return out_info


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def test_mixture(self):
        """
        Test a range of cases, both for is_mixture defaults
        (see doctests for non-default options)
        and for the expected metric in both major and minor.
        """

        # Fig, majorScore, minorScore
        for fig_score_pairs in (
                ('i', 2, -2),
                ('iio', 2, -2),
                ('iv', 2, -2),
                ('v', 1, 0),
                ('bVI', 4, -4),
                ('bVII', 1, 0),
                ('viio7', 2, -1),
        ):
            # True, major key:
            maj_RN = roman.RomanNumeral(fig_score_pairs[0], 'C')
            maj_RN = mixture.add_mixture_info(maj_RN)
            self.assertEqual(maj_RN.mixture_metric, fig_score_pairs[1])
            self.assertTrue(mixture.is_mixture(maj_RN))

            # False, minor key:
            min_RN = roman.RomanNumeral(fig_score_pairs[0], 'a',
                                        sixthMinor=roman.Minor67Default.CAUTIONARY,
                                        seventhMinor=roman.Minor67Default.CAUTIONARY)
            min_RN = mixture.add_mixture_info(min_RN)
            self.assertEqual(min_RN.mixture_metric, fig_score_pairs[2])
            self.assertFalse(mixture.is_mixture(min_RN))

        for fig_score_pairs in (
                ('I', -2, 2),  # M3
                ('ii', 0, 1),  # M6 (NB not iio)
                ('IV', 0, 1),  # M6
                ('viiø7', 0, 2),  # M6, M7
        ):
            # False, major key:
            maj_RN = roman.RomanNumeral(fig_score_pairs[0], 'C')
            maj_RN = mixture.add_mixture_info(maj_RN)
            self.assertEqual(maj_RN.mixture_metric, fig_score_pairs[1])
            self.assertFalse(mixture.is_mixture(maj_RN))

            # True, minor key:
            min_RN = roman.RomanNumeral(fig_score_pairs[0], 'a',
                                        sixthMinor=roman.Minor67Default.CAUTIONARY,
                                        seventhMinor=roman.Minor67Default.CAUTIONARY)
            min_RN = mixture.add_mixture_info(min_RN)
            self.assertEqual(min_RN.mixture_metric, fig_score_pairs[2])
            self.assertTrue(mixture.is_mixture(min_RN))

    def test_combinations(self):
        """
        Test the most mixed instances from chord_combinations.
        """

        in_out = (
            (chord_combinations("C")["bVI"], ['Ab-C-Eb', 2, 0, 0, 4]),
            (chord_combinations("C", cardinality=4)["iv7"], ['F-Ab-C-Eb', 2, 0, 0, 4]),
            (chord_combinations("a")["I"], ['A-C#-E', 1, 0, 0, 2]),
            (chord_combinations("a", cardinality=4)["#iii7"], ['C#-E-G#-B', 1, 1, 0, 3])
        )

        for x in in_out:
            self.assertEqual(x[0], x[1])

    def test_usage(self):
        """
        Test the usage from chord_usage data.
        """
        maj = mixture.in_practice(
            corpus="OpenScore-LiederCorpus",
            major_mode=True
        )
        self.assertEqual(maj["i"][:-1], ['C-Eb-G', 1, 0, 0, 2])
        self.assertEqual(round(maj["i"][-1], 1), 1.1)
        self.assertEqual(maj["iv"][:-1], ['F-Ab-C', 1, 0, 0, 2])
        self.assertEqual(round(maj["iv"][-1], 1), 0.9)

        min = mixture.in_practice(
            corpus="OpenScore-LiederCorpus",
            major_mode=False
        )
        self.assertEqual(min["V"][:-1], ['E-G#-B', 0, 1, 0, 1])
        self.assertEqual(round(min["V"][-1], 1), 12.7)
        self.assertEqual(min["I"][:-1], ['A-C#-E', 1, 0, 0, 2])
        self.assertEqual(round(min["I"][-1], 1), 3.0)


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
