# -*- coding: utf-8 -*-
"""

NAME:
===============================
Align Streams (alignStreams.py)

BY:
===============================
Mark Gotham


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================
Resolve differences in the bar/measure notational between two parts.
Now effectively a local test suite for external repo https://github.com/MarkGotham/bar-measure

"""

# ------------------------------------------------------------------------------


from music21 import clef, key, meter, stream


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


def matchParts(
        reference_part: stream.Part,
        part_to_adjust: stream.Part
) -> stream.Part:
    """
    Resolve differences between two parts (here a score template and analysis part) with
    one defined as the reference part (score) and the other to be adjusted (analysis).
    Changes made (in order):

    0. Split/join measures.
    See notes at `split_join` TODO

    1. Number of measures.
    Often analyses have fewer measures than scores as the last chord is reached
    before the last measure, and those "empty" measures are not explicitly encoded.
    This function adds empty measures to the analysis, padding it out so that they match up.

    2. Last measure duration.
    In the case of a part with an anacrusis, the first measures and last measure are incomplete:
    their combined value is equal to one full measure.
    Romantext supports the encoding of an anacrustic initial measure (e.g. m0 b3) but there
    is no equivalent way of setting the duration of the final measure.
    This function shortens that final measure duration to match that of the score
    in the case of a part with anacrusis (no action otherwise).

    3. Remove duplicated (redundant) classes like time signatures.
    See notes at `remove_duplicates`.
    Example use:
    Where analyses have repeat measures, and where those measures have a time signature,
    the time signature is repeated leading to duplicates that are redundant.
    This is especially common when repeating the first measure.

    :param reference_part: the "model" part, defining the "correct" values.
    :param part_to_adjust: the part to alter according to values in the reference_part.
    :return: part_to_adjust, altered.
    """

    # 0. Split measures. TODO

    # 1. Number of measures
    referenceMeasures = reference_part.getElementsByClass("Measure")
    adjustMeasures = part_to_adjust.getElementsByClass("Measure")

    measureDiff = len(referenceMeasures) - len(adjustMeasures)
    if measureDiff > 0:
        for x in range(measureDiff):
            part_to_adjust.append(stream.Measure())

    # 2. Anacrusis: incomplete first and last measures
    refFirst = referenceMeasures[0]
    if refFirst.duration != refFirst.barDuration:  # i.e., anacrusis
        refLast = referenceMeasures[-1]
        if refLast.duration != refLast.barDuration:
            adjustLast = adjustMeasures.getElementsByClass("Measure")[-1]
            adjustLast.splitAtQuarterLength(refLast.duration.quarterLength)

    # 3. Time signatures
    return remove_duplicates(part_to_adjust)


def remove_duplicates(
    this_stream: stream.Stream,
    classes_to_remove: list = None
) -> stream.Stream:
    """
    Removes objects of the specified classes which
    duplicate the existing context and have no effect.
    
    Options are the objects by type: currently only
    time signatures,
    key signatures, and
    clefs.
    Calling any other (unsupported) classes will raise a ValueError.

    Note: currently runs on str comparison.
    TODO: replace with object comparison once reliable in music21.

    Args:
        this_stream: a stream.Stream object (usually a stream.Part), adjusted and returned.
        classes_to_remove(list): which classes to check duplicates

    Returns: this_stream, adjusted.
    """

    if classes_to_remove is None:
        classes_to_remove = [meter.TimeSignature, key.KeySignature, clef.Clef]
    remove_list = []

    supported_classes = [meter.TimeSignature, key.KeySignature, clef.Clef]

    for this_class in classes_to_remove:
        if this_class not in supported_classes:
            raise ValueError(f"{this_class} invalid. Only {supported_classes} are supported.")

        all_states = this_stream.recurse().getElementsByClass(this_class)

        if len(all_states) < 2:  # Not used, or does not change
            continue

        current_state = all_states[0]  # First to initialize: not a duplicate by definition
        for this_state in all_states[1:]:
            if str(this_state) == str(current_state):
                # TODO ^ object (not str) comparison when reliable in music21
                remove_list.append(this_state)
            else:
                current_state = this_state

    for item in remove_list:
        m = item.getContextByClass(stream.Measure)
        m.remove(item, recurse=True)

    return this_stream
