import unittest

from Code.Resources import key_profiles_literature
from Code.Pitch_profiles.normalisation_comparison import normalise, compare_two_profiles, best_key


class Test(unittest.TestCase):

    def test_normalisation(self):
        """
        Test the sum and max normalisation methods with Prince and Schmuckler all beats major.
        """
        d = [0.919356471, 0.114927991, 0.729198287, 0.144709771, 0.697021822, 0.525970522,
             0.214762724, 1, 0.156143546, 0.542952545, 0.142399406, 0.541215555]

        d_l1 = normalise(d, normalisation_type='l1')
        self.assertEqual(round(sum(d_l1), 2), 1)

        d_l2 = normalise(d, normalisation_type='l2')
        self.assertEqual(round(sum([x ** 2 for x in d_l2]), 2), 1)

        d_max = normalise(d, normalisation_type='Max')
        self.assertEqual(max(d_max), 1)

    def test_Euclid(self):

        # No difference (0) between a distribution profile and itself
        d1 = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        d2 = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        d = compare_two_profiles(d1, d2, comparison_type='Euclidean')
        self.assertEqual(d, 0)

        # Max difference between two distributions with one distinct pitch each ...
        d1 = [1, 0]
        d2 = [0, 1]
        # This equates to 2 for L1 comparison, and sqrt(2) for L2:
        for comp, dist in (('L1', 2), ('L2', 1.414)):
            self.assertEqual(compare_two_profiles(d1, d2, comparison_type=comp), dist)

        # ... likewise for complements in any dimension
        d1 = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        d2 = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
        d = compare_two_profiles(d1, d2, comparison_type='Euclidean')
        self.assertEqual(d, 1.414)

    def test_all_PCPs(self):
        """
        Check best key on all relevant PCP model prototypes
        and both Euclidean and Manhattan comparison types
        with the first segment of Beethoven Sonata no.1 (f minor).
        """
        data = [20.03, 1.0, 0.0, 0.0, 10.36, 15.2, 0.0, 15.2, 13.86, 0.0, 11.52, 0.0]
        for mod in [key_profiles_literature.AardenEssen,
                    key_profiles_literature.AlbrechtShanahan,
                    key_profiles_literature.BellmanBudge,
                    key_profiles_literature.KrumhanslKessler,
                    key_profiles_literature.KrumhanslSchmuckler,
                    key_profiles_literature.PrinceSchumuckler,
                    key_profiles_literature.QuinnWhite,
                    key_profiles_literature.Sapp,
                    key_profiles_literature.TemperleyKostkaPayne,
                    key_profiles_literature.TemperleyDeClerq
                    ]:
            for comp in ['Euclidean', 'Manhattan']:
                k = best_key(data, mod, comparison_type=comp)
                self.assertEqual(k, 'f')

    def test_flat_profile(self):
        """
        For most models (with transposition equivalence) a flat usage profile
        (e.g. silence) does not distinguish between key options.
        It does, however, typically 'prefer' minor keys
        as the reference prototype tends to be 'flatter' (i.e. more chromatic) than major.
        The way this code is set up, it will arbitrarily return the first tested minor key (c).

        As ever, QuinnWhite provides the exception: the profiles are not equivalent by key
        so an actual choice of the flattest profile is returned, here 'bb'.

        Note that if major and minor are exactly even, then best_key returns the minor option.
        This is extremely unlikely in practice apart from these cases of a flat usage profile.
        Even then it is only relevant when the source profile also consists of the same elements
        in major and minor, rearranged in (i.e. Sapp in which both are 2 x '2', 5 x '1', 5 x '0').
        """
        flat_profile = [1.5] * 12
        comps = ['L1', 'L2']
        mods = [(key_profiles_literature.KrumhanslKessler, 'c'),
                (key_profiles_literature.AlbrechtShanahan, 'c'),
                (key_profiles_literature.Sapp, 'c'),
                (key_profiles_literature.TemperleyDeClerq, 'c'),
                (key_profiles_literature.QuinnWhite, 'bb'),
                ]
        for mod in mods:
            for comp in comps:
                res = best_key(flat_profile, model=mod[0], comparison_type=comp)
                self.assertEqual(res, mod[1])
