import unittest

from Code.Pitch_profiles.get_distributions import DistributionsFromTabular
from . import TEST_RESOURCES_FOLDER


class Test(unittest.TestCase):

    def test_two_songs(self):
        base_path = TEST_RESOURCES_FOLDER / "Example"
        test_p = DistributionsFromTabular(path_to_tab=str(base_path / 'slices_with_analysis.tsv'))
        self.assertEqual(len(test_p.profiles_by_key), 9)  # i.e. 9 local key areas
        self.assertEqual(test_p.profiles_by_key[0]['key'], 'Db')  # Starting in Db
        self.assertEqual(test_p.profiles_by_key[-1]['key'], 'Db')  # And ending there too
