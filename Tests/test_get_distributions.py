import unittest

from Code.Pitch_profiles.get_distributions import DistributionsFromTabular
from . import TEST_RESOURCES_FOLDER


class Test(unittest.TestCase):

    def test_two_songs(self):
        base_path = TEST_RESOURCES_FOLDER / "Example"
        test_p = DistributionsFromTabular(path_to_tab=str(base_path / 'slices_with_analysis.tsv'))
        test_p.get_profiles_by_key()
        self.assertEqual(len(test_p.profiles_by_key), 9)  # i.e. 9 local key areas
        self.assertEqual(test_p.profiles_by_key[0]['key'], 'Db')  # Starting in Db
        self.assertEqual(test_p.profiles_by_key[-1]['key'], 'Db')  # And ending there too

        # NB: WRITES
        valid_formats = ['.csv', '.tsv', '.arff', '.json']
        valid_by_what = ['key', 'chord', 'measure']
        for vf in valid_formats:
            for vbw in valid_by_what:
                for this_bool in [False, True]:
                    test_p.write_distributions(by_what=vbw,
                                               write_features=this_bool,
                                               out_format=vf)
