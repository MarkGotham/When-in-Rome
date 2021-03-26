# -*- coding: utf-8 -*-

from music21 import converter
from music21 import chord
from music21 import expressions
from music21 import layout
from music21 import roman
from music21 import stream

import os


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


def matchParts(referencePart: stream.Part,
               partToAdjust: stream.Part):
    """
    Resolve differences between two parts (here a score template and analysis part) with
    one defined as the reference part (score) and the other to be adjusted (analysis).
    Changes made:

    1. Number of measures.
    Often analyses have fewer measures than scores as the last chord is reached
    before the last measure, and those 'empty' measures are not explicitly encoded.
    This function adds empty measures to the analysis, padding it out so that they match up.

    2. Last measure duration.
    In the case of a part with an anacrusis, the first measures and last measure are incomplete:
    their combined value is equal to one full measure.
    Romantext supports the encoding of an anacrustic initial measure (e.g. m0 b3) but there
    is no equivalent way of setting the final measure's duration.
    This function shortens the final measure's duration to match that of the score
    in the case of a part with anacrusis (no action otherwise).

    :param referencePart: the 'model' part, defining the 'correct' values.
    :param partToAdjust: the part to alter according to values in the referencePart.
    :return: partToAdjust, altered.
    """

    # First and last measure duration
    referenceMeasures = referencePart.getElementsByClass('Measure')
    adjustMeasures = partToAdjust.getElementsByClass('Measure')
    measureDiff = len(referenceMeasures) - len(adjustMeasures)
    if measureDiff > 0:
        for x in range(measureDiff):
            partToAdjust.append(stream.Measure())

    # Anacrusis: incomplete first and last measures
    refFirst = referenceMeasures[0]
    if refFirst.duration != refFirst.barDuration:  # i.e. anacrusis
        refLast = referenceMeasures[-1]
        if refLast.duration != refLast.barDuration:
            adjustLast = adjustMeasures.getElementsByClass('Measure')[-1]
            adjustLast.splitAtQuarterLength(refLast.duration.quarterLength)

    return partToAdjust

# ------------------------------------------------------------------------------
