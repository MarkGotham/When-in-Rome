# -*- coding: utf-8 -*-
"""

NAME:
===============================
Chords and progressions


BY:
===============================
Mark Gotham


SOURCE:
===============================
https://github.com/MarkGotham/When-in-Rome/blob/master/Code/chords_and_progs.py
And for application to that meta-corpus, see also:
https://github.com/MarkGotham/When-in-Rome/blob/master/Code/anthology.py


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================
Methods for determining if a chord / progression
belongs to a specific type.

"""

from music21 import chord, interval, roman
from typing import List, Union
from . import harmonicFunction


# ------------------------------------------------------------------------------

# Chords

def is_of_type(
        this_chord: Union[roman.RomanNumeral, chord.Chord],
        query_type: Union[str, List[int], chord.Chord]
) -> bool:
    """
    Tests whether a chord (`this_chord`) is of a particular type (`query_type`).

    There are only two match criteria.
    First chords must have the same normal order.
    This means that C major and D major do match (transposition equivalence included),
    but C major and c minor do not (inversion equivalence excluded).

    Second, relevant pitch spelling must also match, so
    dominant sevenths do not match German sixth chords.

    this_chord can be a chord.Chord object
    or a roman.RomanNumeral (which inherits from chord.Chord).
    Raises an error otherwise.

    The query_type can be in almost any format.
    First, it can also be a chord.Chord object, including the same object as this_chord:
    >>> majorTriad1 = chord.Chord("C E G")
    >>> majorTriad2 = chord.Chord("D F# A")
    >>> minorTriad1 = chord.Chord("C E- G")

    >>> is_of_type(majorTriad1, majorTriad1)
    True

    >>> is_of_type(majorTriad1, majorTriad2)
    True

    >>> is_of_type(majorTriad1, minorTriad1)
    False

    Second, is anything you can use to create a chord.Chord object, i.e.
    string of pitch names (with or without octave), or a list of
    pitch.Pitch objects,
    note.Note objects,
    MIDI numbers, or
    pitch class numbers.
    It bears repeating here that transpositon equivalence is fine:
    >>> is_of_type(majorTriad1, [2, 6, 9])
    True

    Third, it accepts some common names from  can be any string returned by music21.chord.commonName.
    These include fixed strings for
    single pitch chords (including "note", "unison", "Perfect Octave", ...),
    dyads (e.g. "Major Third"),
    triads ("major triad"),
    sevenths ("dominant seventh chord"), and
    other special cases ("all-interval tetrachord", "whole tone"),
    The full list (based on one by Solomon) can be seen at music21.chord.tables.SCREF.

    >>> is_of_type(majorTriad1, "major triad")
    True

    >>> is_of_type(majorTriad1, "whole tone scale")
    False

    >>> wholeToneChord = chord.Chord([0, 2, 4, 6, 8, 10])
    >>> is_of_type(wholeToneChord, "whole tone scale")
    True

    Additionally, chord.commonName supports categories of strings like (fill in the <>)
    See the full list.

    As with chord.commonName, chords with no common name return the Forte Class
    so that too is a valid entry (but only in those cases).
    Any well-formed Forte Class string is acceptable, e.g., "6-36B",
    (which chord.commonName returns for cases with no common name):
    >>> is_of_type(wholeToneChord, "6-35")
    True

    Raises an error if the `query_type` is (still!) not valid.
    """

    if "Chord" not in this_chord.classes:  # accept RN etc.
        raise ValueError("Invalid this_chord: must be a chord.Chord object")

    # Make reference (another chord.Chord object) from query_type
    ref_common = None

    try:
        reference = chord.Chord(query_type)  # string of pitches; list of ints (normal order), pitches, notes, and more
        ref_common = reference.commonName
    except:  # cannot make a chord directly ...
        if isinstance(query_type, str):
            # First try Forte class: only case of "-" at index 1 or 2.
            if "-" in query_type[1:3]:
                reference = chord.fromForteClass(query_type)  # note only the string part of fromForteClass
                ref_common = reference.commonName
            else:  # take the string directly as a common name
                ref_common = query_type

    if not ref_common:
        raise ValueError(f"Invalid query_type. Cannot make a chord.Chord from {query_type}")

    return this_chord.commonName == ref_common


def is_applied_chord(
        rn: roman.RomanNumeral,
        require_dominant_function: bool = True
):
    """
    Applied chords suggest a local tonic chord other than the home tonic.
    (see https://viva.pressbooks.pub/openmusictheory/chapter/tonicization/)

    Typically, these take the form of a
    secondary dominant - i.e., `V(7)/x` - or
    secondary leading-tone - `viio(7)/x` chord,
    where x is the secondary tonality.

    Args:
        rn (roman.RomanNumeral): The roman.RomanNumeral object to consider.
        require_dominant_function (bool): Require that the applied chord has dominant function.
    """
    if not rn.secondaryRomanNumeral:
        return False
    if require_dominant_function:
        f = harmonicFunction.figureToFunction(rn.romanNumeral)  # NB not figure
        return f == "D"

    # TODO: consider options for requiring:
    #     Resolution: rn.next() == rn.secondaryRomanNumeral.figure is diatonic.
    #     Diatonic: rn.secondaryRomanNumeral.figure is diatonic.


# ------------------------------------------------------------------------------

# Quasi-Progressions

def is_potential_Cto_Dim_7(
        chord_before: Union[roman.RomanNumeral, chord.Chord],
        diminished_seventh: Union[roman.RomanNumeral, chord.Chord],
        chord_after: Union[roman.RomanNumeral, chord.Chord],
        require_prolongation: bool = True):
    """
    Find a potential instance of the common tone diminished seventh in any form by seeking:
    a diminished seventh,
    which shares at least one pitch with
    the chord before, the one after, or both.

    This function works entirely by pitch class content and so
    chord spelling is not considered, nor the relation to keys.
    E.g., V in C and I in G are equivalent.

    Args:
        chord_before: the roman.RomanNumeral object immediately preceding.
        diminished_seventh: the roman.RomanNumeral object that is a possible Cto7.
        chord_after: the roman.RomanNumeral object immediately following.
        require_prolongation (bool): diminished seventh is preceded and followed by the same chord
            (as defined by the pitch content, again not inversion or spelling).
    """
    if chord_before.isDiminishedSeventh():
        return False
    if not diminished_seventh.isDiminishedSeventh():
        return False
    if chord_after.isDiminishedSeventh():
        return False

    pcs_before = set([p.pitchClass for p in chord_before.pitches])
    pcs_now = set([p.pitchClass for p in diminished_seventh.pitches])
    pcs_after = set([p.pitchClass for p in chord_after.pitches])

    if require_prolongation:
        if pcs_before != pcs_after:
            return False

    if pcs_now & pcs_before:  # any shared pitch(class)
        return True

    if pcs_now & pcs_after:  # any shared pitch(class)
        return True


# ------------------------------------------------------------------------------

# Progressions: fifths

def descending_fifths(
        chord_list: List[Union[roman.RomanNumeral, chord.Chord]],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    Is this progression a descending cycle of fifths, i.e.:
    each root is a generic fifth below the previous one.

    >>> rns_strings = ["V/ii", "ii", "V"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]
    >>> descending_fifths(rns)
    True

    See also the paired `ascending_fifths()` which would be True in this case:

    >>> rns_strings = ["iv", "i", "V", "V/V"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]
    >>> descending_fifths(rns)
    False

    >>> ascending_fifths(rns)
    True

    Note how they are transposition and octave neutral
    (i.e., while named after rising/falling 5ths, falling/rising 4ths are fine).

    Args:
        chord_list: a list of Roman Numeral object (the requirement for exactly 4 may change)
        require_one_key (bool): Limit returns to non-modulating cases.
        exclude_Cad64 (bool): If True, ignore any succession with a Cad64 in it (however spelt).
            The label `Cad64` deliberately avoids the contentious question of what the root is.
        exclude_Aug6 (bool): The root of these chords is also ambiguous.
    Returns: bool
    """
    if not _shared_quint_checks_ok(
        chord_list,
        require_4=False,
        require_one_key=require_one_key,
        exclude_Cad64=exclude_Cad64,
        exclude_Aug6=exclude_Aug6
    ):
        return False

    int_list = [-5] * (len(chord_list) - 1)

    return interval_match(
        chord_list,
        int_list,
        bass_not_root=False,
        specific_not_generic=False
    )


def ascending_fifths(
        chord_list: List[Union[roman.RomanNumeral, chord.Chord]],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    See notes at the paired `descending_fifths()`
    """
    if not _shared_quint_checks_ok(
        chord_list,
        require_one_key=require_one_key,
        exclude_Cad64=exclude_Cad64,
        exclude_Aug6=exclude_Aug6
    ):
        return False

    return interval_match(
        chord_list,
        [5, 5, 5],
        bass_not_root=False,
        specific_not_generic=False
    )


def fallender_Quintanstieg(
        chord_list: List[Union[roman.RomanNumeral, chord.Chord]],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    In the minimum definition of the `fallende Quintstiege` progression,
    there are two pairs of adjacent chords with roots a 5th apart, where the
    - fifth is ascending;
    - step between 5th-related pairs is descending.

    >>> rns_strings = ["iv/ii", "ii", "iv", "i"]
    >>> rns = [roman.RomanNumeral(x, "a") for x in rns_strings]
    >>> fallender_Quintanstieg(rns)
    True

    See also the paired aufsteigender_Quintfall() which would be True in this case:

    >>> rns_strings = ["V", "I", "V/ii", "ii"]
    >>> rns = [roman.RomanNumeral(x, "a") for x in rns_strings]
    >>> fallender_Quintanstieg(rns)
    False

    >>> aufsteigender_Quintfall(rns)
    True

    Args:
        chord_list: a list of exactly 4 Roman Numeral chords (for the minimum definition)
        require_one_key (bool): Limit returns to non-modulating cases.
        exclude_Cad64 (bool): If True, ignore any succession with a Cad64 in it (however spelt).
            The label `Cad64` deliberately avoids the contentious question of what the root is.
        exclude_Aug6 (bool): The root of these chords is also ambiguous.
    Returns: bool
    """
    if not _shared_quint_checks_ok(
        chord_list,
        require_one_key=require_one_key,
        exclude_Cad64=exclude_Cad64,
        exclude_Aug6=exclude_Aug6
    ):
        return False

    return interval_match(
        chord_list,
        [5, -6, 5],
        bass_not_root=False,
        specific_not_generic=False
    )


def aufsteigender_Quintfall(
        chord_list: List[Union[roman.RomanNumeral, chord.Chord]],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    In the minimum definition of this progression,
    there are two pairs of adjacent chords with roots a 5th apart, where the
    - fifth is descending;
    - step between 5th-related pairs is ascending.

    See notes at the paired `fallender_Quintanstieg()`
    """
    if not _shared_quint_checks_ok(
        chord_list,
        require_one_key=require_one_key,
        exclude_Cad64=exclude_Cad64,
        exclude_Aug6=exclude_Aug6
    ):
        return False

    return interval_match(
        chord_list,
        [-5, 6, -5],
        bass_not_root=False,
        specific_not_generic=False
    )



def _shared_quint_checks_ok(
    chord_list: List[Union[roman.RomanNumeral, chord.Chord]],
    require_4: bool = True,
    require_one_key: bool = True,
    exclude_Cad64: bool = True,
    exclude_Aug6: bool = True
) -> bool:

    if require_4 and len(chord_list) != 4:
        raise ValueError("Please call on a list of exactly 4 chords.")

    if require_one_key:
        if changes_key(chord_list):
            return False

    for rn in chord_list:

        if exclude_Cad64:
            if rn.inversion() == 2:
                if rn.scaleDegree == 1:
                    return False

        if exclude_Aug6:
            if rn.isAugmentedSixth(permitAnyInversion=True):
                return False

    return True


# ------------------------------------------------------------------------------

# Progressions: Other

def is_quiescenza(
        rns_list: list[roman.RomanNumeral],
        require_full_cadence: bool = True
) -> bool:
    """
    The "Quiescenza" tonicises scale degree 4 with V/IV to IV or similar:
    with or without 7th on the V and heading to either IV (typical in major) or iv (minor).

    Partimenti tradition considers this suitable for the end.
    There are examples of that in the corpus (Bach Prelude no1 in C).
    ... but it also often appears at the start (Brahms Requiem, Schubert Ave Maria)
    ... and elsewhere.

    This function returns True iff:
    - there are 4 chords (otherwise error),
    - with no change of key (otherwise error)
    - the 1st: has a secondary tonality of scale degree 4 and a dominant function primary figure.
    - the 2nd: has a sub-dominant function figure and no secondary tonality.

    Additionally, if `require_full_cadence` is True:
    - the 3rd has a dominant function (no secondary tonality).
    - the 4th has a tonic function (no secondary tonality).

    Some true examples:

    >>> figs = ["V7/IV", "IV", "viio", "I"]
    >>> rns = [roman.RomanNumeral(f, "F") for f in figs]
    >>> is_quiescenza(rns)
    True

    >>> figs = ["V2/IV", "IV6", "V9", "I"]
    >>> rns = [roman.RomanNumeral(f, "F") for f in figs]
    >>> is_quiescenza(rns)
    True

    >>> figs = ["viio/iv", "iv", "V[no3]", "I"]
    >>> rns = [roman.RomanNumeral(f, "F") for f in figs]
    >>> is_quiescenza(rns)
    True

    And some false ones:

    >>> figs = ["V", "V6", "viio", "i"]
    >>> rns = [roman.RomanNumeral(f, "F") for f in figs]
    >>> is_quiescenza(rns)
    False

    >>> figs = ["V7/ii", "ii", "V", "vi"]
    >>> rns = [roman.RomanNumeral(f, "F") for f in figs]
    >>> is_quiescenza(rns)
    False

    """
    # 4 chords (otherwise error),
    if len(rns_list) != 4:
        raise ValueError("Please enter a list of four RNs.")

    # no change of key (otherwise error)
    if changes_key(rns_list):
        raise ValueError("Please enter a list of four RNs within one primary key.")

    # the first has a secondary tonality ...
    if not rns_list[0].secondaryRomanNumeral:
        return False

    # ... with scale degree 4
    if rns_list[0].secondaryRomanNumeral.scaleDegree != 4:
        return False

    # ... and a primary figure of a dominant function.
    if harmonicFunction.figureToFunction(rns_list[0].primaryFigure) != "D":
        return False

    # the second has no secondary tonality ...
    if rns_list[1].secondaryRomanNumeral:
        return False

    # ... and a primary (only) figure of a sub-dominant function.
    if harmonicFunction.figureToFunction(rns_list[1].primaryFigure) not in ["S", "s"]:
        return False

    if require_full_cadence:

        # the third has no secondary tonality ...
        if rns_list[2].secondaryRomanNumeral:
            return False

        # ... and a primary (only) figure of a dominant function.
        if harmonicFunction.figureToFunction(rns_list[2].primaryFigure) != "D":
            return False

        # the last has no secondary tonality ...
        if rns_list[3].secondaryRomanNumeral:
            return False

        # ... and a primary (only) figure of a tonic function.
        if harmonicFunction.figureToFunction(rns_list[3].primaryFigure) not in ["T", "t"]:
            return False

    return True


# ------------------------------------------------------------------------------

def interval_match(
        chord_list: List[Union[roman.RomanNumeral, chord.Chord]],
        query_intervals: list,
        bass_not_root: bool = True,
        specific_not_generic: bool = True,
) -> bool:
    """
    Check whether the intervals (bass or root) between a succession of chords match a query.
    Requires the creation of `interval.Interval` objects.
    Minimised here to reduce load on large corpus searches.

    Works on chords (`chord.Chord`) and Roman numerals (`roman.RomanNumeral`) objects.

    >>> ints = [-7, 9, -7]
    >>> rns_strings = ["V", "I", "V/ii", "ii"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]

    >>> interval_match(rns, ints)
    True


    >>> chord_strings = ["G", "C", "A", "D"]
    >>> rns = [chord.Chord(x) for x in chord_strings]

    >>> interval_match(rns, ints)
    True

    Supports the use of generic instead of specific intervals.
    So the same example above could look like this:

    >>> generic = [-5, 6, -5]

    By default, the interals are assumed to be specific:
    >>> interval_match(rns, generic)
    False

    ... But this is settable with `specific_not_generic` as False:
    >>> interval_match(rns, generic, specific_not_generic=False)
    True

    Use `bass_not_root` to distinguish between inversions.
    If the Vs in the above example are now in first inversion:

    >>> rns_strings = ["V6", "I", "V6/ii", "ii"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]

    Then with the default value of `bass_not_root` as True, the match is lost:

    >>> interval_match(rns, ints, specific_not_generic=True)
    False

    >>> interval_match(rns, generic, specific_not_generic=False)
    False

    ... but again this is settable to work on roots with bass_not_root=False.
    The roots are unchanged but the alteration to inversions here:

    >>> interval_match(rns, ints, bass_not_root=False, specific_not_generic=True)
    True

    >>> interval_match(rns, generic, bass_not_root=False, specific_not_generic=False)
    True

    As in so many cases then, the assingment of both bass and root matter.
    So the following is false despite significant similarity to the V6 case above.
    >>> rns_strings = ["viio", "I", "viio/ii", "ii"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]
    >>> interval_match(rns, ints, bass_not_root=False, specific_not_generic=False)
    False

    The functional equivalence between these examples is supported in some cases on the code base,
    but not (currently) here.

    Args:
        rns: a list of roman.RomanNumeral objects
        query_intervals: the query list of intervals
            (any valid string for interval.Interval or interval.GenericInterval)
        bass_not_root: intervals between the bass notes (if true, default) or the roots.
        specific_not_generic: work with interval.Interval or interval.GenericInterval objects

    Returns: bool
    """
    if bass_not_root:
        pitches = [x.bass() for x in chord_list]
    else:  # root
        pitches = [x.root() for x in chord_list]

    if len(pitches) != len(query_intervals) + 1:
        raise ValueError("There must be exactly one more RN than interval.")

    for i in range(len(query_intervals)):

        # print(pitches[i], pitches[i + 1])
        source = interval.Interval(pitches[i], pitches[i + 1])

        if specific_not_generic:
            source = source.semitones % 12  # removes octave, preserves direction
            comparison = interval.Interval(query_intervals[i]).semitones % 12
        else:  # generic
            source = source.generic.mod7
            comparison = interval.GenericInterval(query_intervals[i]).mod7

        # print(source, comparison)

        if source != comparison:
            return False  # false as soon as one does not match

    return True


def changes_key(
        rns_list: list[roman.RomanNumeral]
) -> bool:
    """
    Convenience function for checking whether a succession of Roman numerals involves a key change.
    This is useful (at least in some current operationalisations) for excluding from consideration.

    Args:
        rns_list: a list of roman.RomanNumeral (sic, not chord.Chord in this case as key is required).

    Returns: bool
    """

    keys = [x.key for x in rns_list]
    if None in keys:
        raise ValueError("All of the roman.RomanNumeral objects must have key specified.")

    distinct_keys = set([x.name for x in keys])
    if len(distinct_keys) > 1:
        return True

    return False


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest
    doctest.testmod()
