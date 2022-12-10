import unittest

from Code.Pitch_profiles.chord_usage import get_usage, simplify_usage_dict
from Code.Resources.chord_usage_stats import lieder_major, lieder_major_simple, lieder_minor, lieder_minor_simple, \
    lieder_both, lieder_both_simple
from Code import CORPUS_FOLDER

class Test(unittest.TestCase):

    def test_counter_of_use(self):
        base_path = CORPUS_FOLDER / 'OpenScore-LiederCorpus'
        # base_path += 'Reichardt,_Louise/'  # smaller test case
        for mode_corpus_pair in [('major', lieder_major, lieder_major_simple),
                                 ('minor', lieder_minor, lieder_minor_simple),
                                 ('both', lieder_both, lieder_both_simple)
                                 ]:
            usage = get_usage(base_path=base_path, mode=mode_corpus_pair[0], plateau=0.01)
            self.assertEqual(usage, mode_corpus_pair[1])

            simplified_usage = simplify_usage_dict(usage)
            self.assertEqual(simplified_usage, mode_corpus_pair[2])
