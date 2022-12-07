import unittest

from Code.Pitch_profiles.get_distributions import DistributionsFromTabular
from Code import CORPUS_FOLDER

from . import TEST_RESOURCES_FOLDER

class Test(unittest.TestCase):

    def test_two_songs(self):
        base_path = CORPUS_FOLDER / 'OpenScore-LiederCorpus'

        p = base_path /'Reichardt,_Louise' / 'Zwölf_Gesänge,_Op.3' / '01_Frühlingsblumen'
        test_p = DistributionsFromTabular(path_to_tab=str(p / 'slices_with_analysis.tsv'))
        test_p.get_profiles_by_key()
        self.assertEqual(len(test_p.profiles_by_key), 1)  # i.e. only one key

        q = base_path / 'Schumann,_Clara' / 'Lieder,_Op.12' / '04_Liebst_du_um_Schönheit'
        test_q = DistributionsFromTabular(path_to_tab=str(q / 'slices_with_analysis.tsv'))
        test_q.get_profiles_by_key()
        self.assertEqual(len(test_q.profiles_by_key), 9)  # i.e. 9 local key areas
        self.assertEqual(test_q.profiles_by_key[0]['key'], 'Db')  # Starting in Db
        self.assertEqual(test_q.profiles_by_key[-1]['key'], 'Db')  # And ending there too

        new_path = TEST_RESOURCES_FOLDER / "Example"
        test_r = DistributionsFromTabular(path_to_tab=str(new_path / 'slices_with_analysis.tsv'))
        self.assertEqual(test_q.get_profiles_by_key(),
                         test_r.get_profiles_by_key())  # i.e. exact copy of corpus entry

        test_s = DistributionsFromTabular(path_to_tab=str(new_path/ 'slices_with_analysis.tsv'),
                                          include_features=True)

        # NB: WRITES
        valid_formats = ['.csv', '.tsv', '.arff', '.json']
        valid_by_what = ['key', 'chord', 'measure']
        for vf in valid_formats:
            for vbw in valid_by_what:
                for this_bool in [False, True]:
                    test_r.write_distributions(by_what=vbw,
                                               write_features=this_bool,
                                               out_format=vf)
