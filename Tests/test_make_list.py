import unittest

from Code.make_list import RNlists


class Test(unittest.TestCase):

    def testList(self):

        figs = RNlists(listLength=3, maxFig=4)
        figs.rnArray()

        self.assertIsInstance(figs.allRomanListOfLists, list)
        self.assertIsInstance(figs.allRomanListOfLists[0], list)
        self.assertEqual(len(figs.allRomanListOfLists), 6)
        self.assertEqual(len(figs.allRomanListOfLists[0]), 84)
        self.assertEqual(figs.allRomanListOfLists[0][0][0], 'bio2')
