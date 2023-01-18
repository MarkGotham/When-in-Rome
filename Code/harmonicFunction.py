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
    """
    return hf.functionToRoman(harmonicFunctionLabel)


def figureToFunction(romanNumeralFigure: Union[str, roman.RomanNumeral],
                     simplified: bool = False):
    """
    See notes at music21.analysis.harmonicFunction.romanToFunction
    """

    # Adapt to m21 types - always RomanNumeral
    if not isinstance(romanNumeralFigure, roman.RomanNumeral):
        romanNumeralFigure = roman.RomanNumeral(romanNumeralFigure)

    # Special cases: hard code here for now. TODO
    # NB: analyst specified figure for Cad64, romanNumeralAlone otherwise
    if romanNumeralFigure.figure == "Cad64":
        returnString = "D"
    elif romanNumeralFigure.romanNumeralAlone == "vii":  # includes all "ø", "o", etc.
        returnString = "D"

    else:
        returnString = hf.romanToFunction(romanNumeralFigure,
                                          onlyHauptHarmonicFunction=simplified)

    if romanNumeralFigure.secondaryRomanNumeral:
        returnString = f"({returnString})"

    return returnString  # NB "None" in the case of no match
