# -*- coding: utf-8 -*-
"""

NAME:
===============================
Harmonic Function (harmonicFunction.py)


BY:
===============================
Mark Gotham


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Mapping between Roman numeral figures and harmonic function labels.

NOTE: functionality and documentation previously here now moved to the central music21 library:
[harmonicFunction.py](https://github.com/cuthbertLab/music21/blob/master/music21/analysis/harmonicFunction.py)

This module remains here for testing and developing further edits.

"""

from music21.analysis import harmonicFunction as hf
from music21 import roman
from typing import Union


# ------------------------------------------------------------------------------

def functionToFigure(harmonicFunctionLabel: str):
    """
    See notes at music21.analysis.harmonicFunction.functionToRoman
    Here, simple wrapper for string only in and out.
    """
    return str(hf.functionToRoman(harmonicFunctionLabel).figure)


def figureToFunction(rn: roman.RomanNumeral | str,
                     simplified: bool = False):
    """
    See notes at music21.analysis.harmonicFunction.romanToFunction
    Here, roman.RomanNumeral input (as there, required for key)
    but string output only.
    """

    # Adapt to m21 types - always RomanNumeral
    if isinstance(rn, str):
        rn = roman.RomanNumeral(rn)

    # Special cases: hard code here for now. TODO
    # NB: analyst specified `.figure` for "Cad64", `.romanNumeralAlone` otherwise
    if rn.figure == "Cad64":
        returnString = "D"
    elif rn.romanNumeralAlone == "vii":  # includes all "ø", "o", etc.
        returnString = "D"

    else:
        returnString = str(hf.romanToFunction(rn,
                                              onlyHauptHarmonicFunction=simplified))

    if rn.secondaryRomanNumeral:
        returnString = f"({returnString})"

    return returnString  # NB "None" in the case of no match
