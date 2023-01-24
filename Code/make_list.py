# -*- coding: utf-8 -*-
"""
NAME:
===============================
Make List (make_list.py)


BY:
===============================
Mark Gotham


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Prepares a comprehensive list of Roman numeral types as realised by m21 defaults, encompassing:
- every combination of the figures 2–9 (= 255)
- Major/minor key (= 2),
- Root accidental ["b", "", "#"] (= 3)
- Scale degree, I-VII (= 7)
- Chord type (o, m, M, +; e.g. ["io", "i", "I", "I+",]).  (= 4)
NB: there are 255*2*3*7*4 = 42,840 outcomes here so the file will be big (& slow to open)
NB: most of these will be nonsense, just there for comprehensiveness.

"""

from music21 import roman
from itertools import combinations
import csv
from . import REPO_FOLDER


# ------------------------------------------------------------------------------

class RNlists:
    def __init__(self,
                 listLength: int = 9,
                 maxFig: int = 9,
                 major: bool = True,
                 minor: bool = True,
                 write: bool = True,
                 ):

        self.rn_Array = []
        self.figs = None
        self.listLength = listLength
        self.maxFig = maxFig
        self.major = major
        self.minor = minor

        self.write = write
        if write:
            self.headers = ["Figure"]
            if major:
                self.headers.append("MajorContext")
            if minor:
                self.headers.append("MinorContext")

        self.figures()
        self.get_rns()

    def figures(self):
        """
        Prepares the combinations of figures.
        """

        self.figs = []

        for thisLength in range(1, self.listLength):
            for iteration in combinations(range(2, self.maxFig + 1), thisLength):
                full = iteration[::-1]
                compressed = "".join([str(x) for x in full])
                self.figs.append(compressed)

    def get_rns(self):
        """
        Prepares the RNs from the figures.
        """

        for fig in self.figs:
            this_list_of_lists = []
            for accidental in ["b", "", "#"]:
                for scaleDegree in ["i", "ii", "iii", "iv", "v", "vi", "vii"]:
                    for chordType in [scaleDegree + "o",
                                      scaleDegree,
                                      scaleDegree.upper(),
                                      scaleDegree.upper() + "+"]:
                        # TODO: ["b", "", "#"] for each figure.
                        joinedRN = "".join([accidental, chordType, str(fig)])
                        out = [joinedRN]
                        if self.major:
                            out.append([x.name for x in roman.RomanNumeral(joinedRN, "C").pitches])
                        if self.minor:
                            out.append([x.name for x in roman.RomanNumeral(joinedRN, "a").pitches])
                        this_list_of_lists.append(out)

            if self.write:
                with open(REPO_FOLDER / "Lists" / f"{fig}.tsv", "a") as csvfile:
                    csvOut = csv.writer(csvfile, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
                    csvOut.writerow([x for x in this_list_of_lists])
            else:
                self.rn_Array.append(this_list_of_lists)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    RNlists()
