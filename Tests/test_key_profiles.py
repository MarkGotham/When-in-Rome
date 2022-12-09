import unittest

from Code.Resources.key_profiles_literature import source_list


class Test(unittest.TestCase):

    def test_sum_key_profiles(self):
        """
        For each source, test that each distinct PCP entry sums to 1.
        If the original doesn't then an additional entry with '_sum' added to the key should.
        """

        for source in source_list:
            for key in source:
                if key in ['literature', 'about', 'name']:
                    continue
                sum_source = sum(source[key])
                if round(sum_source, 2) != 1:
                    sum_source = sum(source[key + '_sum'])
                    assert round(sum_source, 2) == 1
