import unittest

from Code.make_list import RNlists


class Test(unittest.TestCase):

    def testList(self):

        figs = RNlists(listLength=3, maxFig=4, write=False)
        self.assertIsInstance(figs.rn_Array, list)
        self.assertIsInstance(figs.rn_Array[0], list)
        self.assertEqual(len(figs.rn_Array), 6)
        self.assertEqual(len(figs.rn_Array[0]), 84)
        self.assertEqual(figs.rn_Array[0][0][0], 'bio2')


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    Test()
