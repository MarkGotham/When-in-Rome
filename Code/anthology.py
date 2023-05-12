# -*- coding: utf-8 -*-
"""

NAME:
===============================
Anthology (anthology.py)

BY:
===============================
Mark Gotham


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Methods for retrieving specific Roman numerals and/or progressions from analyses.

NOTE: musical logic previously here (isNeapolitan and isMixture) now moved to the main
music21 repo [roman.py](https://github.com/cuthbertLab/music21/blob/master/music21/roman.py)

"""

from music21 import bar, chord, converter
from music21 import instrument, interval
from music21 import layout, metadata
from music21 import roman, stream, tempo

from pathlib import Path

import csv
from . import CORPUS_FOLDER, REPO_FOLDER, get_corpus_files, harmonicFunction, mixture
from .Pitch_profiles.chord_usage import careful_consolidate


# ------------------------------------------------------------------------------

class RnFinder(object):
    """
    For retrieving specific Roman numerals and/or progressions from analyses.
    Separate methods on this class per search term (e.g., `find_mixtures`).
    All such results stored in the `.results` attributes:
    that are lists of dicts returns by data_from_Rn.
    """

    def __init__(self,
                 pathToFile: str | Path):

        self.analysis = converter.parse(pathToFile, format="romanText")
        self.rns = [x for x in self.analysis.recurse().getElementsByClass("RomanNumeral")]
        self.results = []

    def find_mixtures(self):
        """
        NOTE: musical logic previously here now moved to the main music21 repo.
        """

        for rn in self.rns:
            if not rn.secondaryRomanNumeral:
                if mixture.is_mixture(rn):
                    self.results.append(data_from_Rn(rn))

    def find_applied_chords(self,
                            require_dominant_function: bool = True):
        for rn in self.rns:
            if is_applied_chord(rn, require_dominant_function=require_dominant_function):
                self.results.append(data_from_Rn(rn))

    def find_Neapolitan_sixths(self):
        """
        NOTE: musical logic previously here now moved to the main music21 repo
        """

        for rn in self.rns:

            if rn.isNeapolitan(require1stInversion=False):
                self.results.append(data_from_Rn(rn))

    def find_augmented_sixths(self):
        """
        NOTE:
            includes those literally called `Ger65` etc.,
            but also de facto cases like `V43[b5]`.
        """

        for rn in self.rns:
            #
            if rn.isAugmentedSixth():
                self.results.append(data_from_Rn(rn))

    def find_augmented_chords(self,
                              acceptSevenths: bool = True,
                              requireAugAsTriad: bool = True):

        """
        Finds cases of augmented triads (e.g. III+) in any inversion.

        If acceptSevenths is True (default) then also seeks cases of
        sevenths containing an augmented triad.

        If requireAugAsTriad is True (default), then limit these sevenths to cases
        where the augmented triad is the triad (with an added sevenths), e.g. V+7.
        If not, accept cases where the augmented triad is
        formed by the 3rd, 5th and 7th of the chord (e.g. minor-major sevenths).
        """

        for rn in self.rns:
            if rn.isAugmentedTriad():
                self.results.append(data_from_Rn(rn))
            elif acceptSevenths:
                if rn.isSeventh:
                    if rn.isSeventhOfType([0, 4, 8, 11]) or rn.isSeventhOfType([0, 4, 8, 10]):
                        self.results.append(data_from_Rn(rn))
                    elif not requireAugAsTriad:
                        if rn.isSeventhOfType([0, 3, 7, 11]):
                            self.results.append(data_from_Rn(rn))

    def find_rn_progression(self,
                            rns_list: list[str]):
        """
        Find a specific progression of Roman numerals in a given key input by the user as
        a list of Roman numeral figures like ["I", "V65", "I"]
        """

        lnrns = len(rns_list)

        for index in range(len(self.rns) - lnrns):
            thisRange = self.rns[index: index + lnrns]

            if changes_key(thisRange):
                break

            figures = [x.figure for x in thisRange]
            if figures == rns_list:
                self.results.append(data_from_Rn_list(rns_list))

    def find_prog_by_qual_and_intv(
            self,
            qualities: list | None = None,
            intervals: list[interval.GenericInterval | interval.Interval] | None = None,
            # TODO qualities, intervals or both. Neither = error.
            # TODO accept generic intervals too
            bass_not_root: bool = True
    ):
        """
        Find a specific progression of Roman numerals
        searching by chord type quality and (optionally) bass or root motion.

        For instance, to find everything that might constitute a ii-V-I progression
        (regardless of whether those are the exact Roman numerals used), search for
        qualities=["Minor", "Major", "Major"],
        intervals=["P4", "P-5"].
        bass_not_root=False.

        This method accepts many input types.
        For the range accepted by qualities,
        see documentation at is_of_type().

        Blank entries are also fine.
        For instance, to find out how augmented chords resolve, search for
        qualities=["Augmented triad", ""].
        To add the preceding chord as well, expand to:
        qualities=["", "Augmented triad", ""].
        Note that intervals is left unspecified (we are interested in any interval succession).
        Anytime the intervals is left blank, the search runs on quality only
        (and vice versa).
        """
        if not qualities and not intervals:
            raise ValueError("Pick at least one of qualities and intervals")

        lnQs = len(qualities)

        if intervals:
            if lnQs != len(intervals) + 1:
                raise ValueError("There must be exactly one more chord than interval.")

        # 1. Search quality match first: quality is required
        for index in range(len(self.rns) - lnQs):
            theseRns = self.rns[index: index + lnQs]
            for i in range(lnQs):
                if not is_of_type(theseRns[i], qualities[i]):
                    continue  # TODO check
            # 2. Only search for interval match if required and if the qualities already match.
            if intervals:
                if interval_match(theseRns,
                                  intervals,
                                  bass_not_root):
                    self.results.append(data_from_Rn_list(theseRns))

    def find_Cto_dim7(
            self,
            require_prolongation: bool = True
    ):
        """
        Find a potential instance of the common tone diminished seventh in any form by seeking:
        a diminished seventh,
        which shares at least one pitch with
        the chord before, the one after, or both.

        If require_prolongation is True, the results are limited to cases where the
        diminished seventh is preceded and followed by the same chord.
        """

        for index in range(1, len(self.rns) - 1):

            this_chord = self.rns[index]

            if this_chord.isDiminishedSeventh():

                if is_potential_Cto_Dim_7(
                        self.rns[index - 1],
                        this_chord,
                        self.rns[index + 1],
                        require_prolongation=require_prolongation
                ):
                    self.results.append(
                        data_from_Rn_list(
                            [self.rns[index - 1],
                             this_chord,
                             self.rns[index + 1]
                             ]
                        )
                    )

    def find_quiescenzas(self):
        """
        Find specific cases of the "Quiescenza".
        Basically this is of the kind V/IV to IV,
        with or without 7th on the V and heading to either IV (typical in major) or iv (minor).
        Partimenti tradition considers this suitable for the end.
        There are examples of that in the corpus (Bach Prelude no1 in C).
        ... but it also often appears at the start.
        That being the case, this method differs from others on the class by returning
        not only the specific progression, but also the location

        See is_quiescenza for more info.
        """

        last_measure = self.rns[-1].getContextByClass("Measure").measureNumber

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if changes_key(this_range):
                continue

            if is_quiescenza(this_range):
                info = data_from_Rn_list(this_range)
                info["MEASURE"] += f"/{last_measure}"  # interested in position in work.
                self.results.append(info)

    def find_descending_fifths(self):
        """
        Find cases of
        descending_fifths()
        as defined at that functions below.
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if descending_fifths(this_range):
                self.results.append(data_from_Rn_list(this_range))

    def find_ascending_fifths(self):
        """
        Find cases of the
        ascending_fifths()
        as defined at that functions below.
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if ascending_fifths(this_range):
                self.results.append(data_from_Rn_list(this_range))

    def find_aufsteigender_Quintfall(self):
        """
        Find specific cases of the
        aufsteigender_Quintfall()
        as defined at that functions below.

        Apologies for the mixed languages.
        The long form of this method can be called:
        "Ich frage mich, ob das ein aufsteigender Quintfall ist."
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if aufsteigender_Quintfall(this_range):
                self.results.append(data_from_Rn_list(this_range))

    def find_fallender_Quintanstieg(self):
        """
        Find specific cases of the
        fallender_Quintanstieg()
        as defined at that function below.
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if fallender_Quintanstieg(this_range):
                self.results.append(data_from_Rn_list(this_range))


# ------------------------------------------------------------------------------

# Static functions for progressions

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


def is_potential_Cto_Dim_7(
        chord_before: roman.RomanNumeral,
        diminished_seventh: roman.RomanNumeral,
        chord_after: roman.RomanNumeral,
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


def descending_fifths(
        chord_list: list[roman.RomanNumeral],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    Is this progression a descending cycle of fifths, i.e.:
    each root is a generic fifth below the previous one.

    >>> rns_strings = ["V/ii", "ii", "V", "i"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]
    >>> descending_fifths(rns)
    True

    See also the paired ascending_fifths() which would be True in this case:

    >>> rns_strings = ["iv", "i", "V", "V/V"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]
    >>> descending_fifths(rns)
    False

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
        require_one_key=require_one_key,
        exclude_Cad64=exclude_Cad64,
        exclude_Aug6=exclude_Aug6
    ):
        return False

    return interval_match(
        chord_list,
        [-5, -5, -5],
        bass_not_root=False,
        specific_not_generic=False
    )


def ascending_fifths(
        chord_list: list[roman.RomanNumeral],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    Is this progression an ascending cycle of fifths, i.e.:
    each root is a generic fifth above the previous one.

    >>> rns_strings = ["iv", "i", "V", "V/V"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]
    >>> ascending_fifths(rns)
    True

    See also the paired descending_fifths() which would be True in this case:

    >>> rns_strings = ["V/ii", "ii", "V", "i"]
    >>> rns = [roman.RomanNumeral(x, "a") for x in rns_strings]
    >>> ascending_fifths(rns)
    False

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
        chord_list: list[roman.RomanNumeral],
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
        chord_list: list[roman.RomanNumeral],
        require_one_key: bool = False,
        exclude_Cad64: bool = True,
        exclude_Aug6: bool = True
) -> bool:
    """
    In the minimum definition of this progression,
    there are two pairs of adjacent chords with roots a 5th apart, where the
    - fifth is descending;
    - step between 5th-related pairs is ascending.

    >>> rns_strings = ["V", "I", "V/ii", "ii"]
    >>> rns = [roman.RomanNumeral(x, "a") for x in rns_strings]
    >>> aufsteigender_Quintfall(rns)
    True

    See also the paired fallender_Quintanstieg() which would be True in this case:

    >>> rns_strings = ["iv/ii", "ii", "iv", "i"]
    >>> rns = [roman.RomanNumeral(x, "a") for x in rns_strings]
    >>> aufsteigender_Quintfall(rns)
    False

    >>> rns_strings = ["V7", "I", "V7", "I64"]
    >>> rns = [roman.RomanNumeral(x, "a") for x in rns_strings]
    >>> aufsteigender_Quintfall(rns)
    False

    Note how they are transposition and octave neutral
    (i.e., while named after rising/falling 5ths, falling/rising 4ths are fine).

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
        [-5, 6, -5],
        bass_not_root=False,
        specific_not_generic=False
    )


def _shared_quint_checks_ok(
    chord_list: list[roman.RomanNumeral],
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

# Other Static

def data_from_Rn(
        rn: roman.RomanNumeral,
        consolidate: bool = True
) -> dict:
    if consolidate:
        fig = careful_consolidate(
            rn.figure,
            major_not_minor=(rn.key.mode == "major"),
            rn=rn
        )
    else:
        fig = rn.figure

    return {"MEASURE": rn.getContextByClass("Measure").measureNumber,
            "FIGURE": fig,
            "KEY": rn.key.name.replace("-", "b"),
            "BEAT": rn.beat,
            "BEAT STRENGTH": rn.beatStrength,
            "LENGTH": rn.quarterLength}


def data_from_Rn_list(
        rn_list: list[roman.RomanNumeral],
        consolidate: bool = True
) -> dict:

    # figures
    if consolidate:
        figs = [careful_consolidate(
            rn.figure,
            major_not_minor=(rn.key.mode == "major"),
            rn=rn
        ) for rn in rn_list]
    else:
        figs = [rn.figure for rn in rn_list]
    figures = "-".join(figs)

    # keys
    keys = [rn_list[0].key.name]
    for rn in rn_list[1:]:
        if rn.key.name not in keys:
            keys.append(rn.key.name)
    keys = "-".join([k.replace("-", "b") for k in keys])

    measure_start = rn_list[0].getContextByClass("Measure").measureNumber
    measure_end = rn_list[-1].getContextByClass("Measure").measureNumber

    return {"MEASURE": f"{measure_start}-{measure_end}",
            "FIGURE": figures,
            "KEY": keys,
            "BEAT": rn.beat,
            "BEAT STRENGTH": rn.beatStrength,
            "LENGTH": rn.quarterLength}


def is_of_type(
        this_chord: chord.Chord,
        query_type: str | list[int] | chord.Chord
) -> bool:
    """
    Tests whether a chord (this_chord) is of a particular type (query_type).

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
    # >>> majorTriad = chord.Chord("C E G")
    # >>> is_of_type(majorTriad, majorTriad)
    # True

    Second, is anything you can use to create a chord.Chord object, i.e.
    string of pitch names (with or without octave), or a list of
    pitch.Pitch objects,
    note.Note objects,
    MIDI numbers, or
    pitch class numbers.
    It bear repeating here that transpositon equivalence is fine:
    # >>> is_of_type(majorTriad, [2, 6, 9])
    # True

    # TODO: implement chord.fromCommonName then add this:
    # Third, it can be any string returned by music21.chord.commonName.
    # These include fixed strings for
    # single pitch chords (including "note", "unison", "Perfect Octave", ...),
    # dyads (e.g. "Major Third"),
    # triads ("minor triad"),
    # sevenths ("dominant seventh chord"), and
    # other special cases ("all-interval tetrachord"),
    # The full list (based on one by Solomon) can be seen at music.chord.tables.SCREF.
    # TODO >>> is_of_type(majorTriad, "whole tone scale")
    # TODO False
    #
    # >>> wholeToneChord = chord.Chord([0, 2, 4, 6, 8, 10])
    #
    # TODO >>> is_of_type(wholeToneChord, "whole tone scale")
    # TODO True
    #
    # Additionally, chord.commonName supports categories of strings like (fill in the <>)
    # "enharmonic equivalent to <>",
    # "<> with octave doublings",
    # "forte class <>", and
    # "<> augmented sixth chord" (and where relevant) "in <> position".
    # TODO >>> is_of_type(wholeToneChord, "forte class <>" )
    # True
    #
    # As with chord.commonName, chords with no common name return the Forte Class
    # so that too is a valid entry (but only in those cases).
    # Any well-formed Forte Class string is acceptable, as is the format "forte class 6-36B",
    # (which chord.commonName returns for cases with no common name):
    # TODO >>> is_of_type(wholeToneChord, "6-35")
    # True

    Raises an error if the query_type is (still!) not valid.
    """

    if "Chord" not in this_chord.classes:
        raise ValueError("Invalid this_chord: must be a chord.Chord object")

    # Make reference (another chord.Chord object) from query_type
    reference = None
    try:
        reference = chord.Chord(query_type)
        # accepts string of pitches;
        # list of ints (normal order), pitches, notes, or strings;
        # even an existing chord.Chord object.
    except:  # cannot make a chord directly. Assume string.
        if isinstance(query_type, str):
            if "-" in query_type:  # take it to be a Forte class.
                f = "forte class "
                if query_type.startswith(f):
                    query_type = query_type.replace(f, "")
                reference = chord.fromForteClass(query_type)
            else:  # a string, not a Forte class, take it to be a common name.
                # TODO
                # reference = chord.fromCommonName(query_type)
                pass
        # else:
        #     raise ValueError(f"Invalid query_type. Cannot make a chord.Chord from {query_type}")
    if not reference:
        raise ValueError(f"Invalid query_type. Cannot make a chord.Chord from {query_type}")

    t = this_chord.commonName == reference.commonName
    return t


def interval_match(
        rns: list[roman.RomanNumeral],
        query_intervals: list,
        bass_not_root: bool = True,
        specific_not_generic: bool = True,
) -> bool:
    """
    Check whether the intervals (bass or root) between a succession of Roman numerals match a query.
    Requires the creation of interval.Interval objects.
    Minimised here to reduce load on large corpus searches.

    >>> ints = [-7, 9, -7]
    >>> rns_strings = ["V", "I", "V/ii", "ii"]
    >>> rns = [roman.RomanNumeral(x) for x in rns_strings]

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
        pitches = [x.bass() for x in rns]
    else:  # root
        pitches = [x.root() for x in rns]

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
        rns_list: a list of roman.RomanNumeral

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

corpora = [
    "Chamber_Other",
    "Early_Choral",
    "Keyboard_Other",
    "OpenScore-LiederCorpus",
    "Orchestral",
    "Piano_Sonatas",
    "Quartets",
    "Variations_and_Grounds"
]

valid_searches = [
    "Modal Mixture",
    "Augmented Chords",
    "Augmented Sixths",
    "Neapolitan Sixths",
    "Applied Chords",
    "Common Tone Diminished Sevenths",
    "Quiescenzas",
    "ascending_fifths",
    "descending_fifths",
    "aufsteigender_Quintfall",
    "fallender_Quintanstieg",
    "Progressions",
]


def one_search_one_corpus(corpus: str = "OpenScore-LiederCorpus",
                          what: str = "Modal Mixture",
                          progression: list | None = None,
                          write_summary: bool = True,
                          heads: list | None = None,
                          write_examples: bool = False,
                          ):
    """
    Runs the search methods on a specific pair of corpus and search term.
    Settable to find any of the `valid_searches` ("Modal Mixture", ...).
    Defaults to the "OpenScore-LiederCorpus" and "Modal mixture".
    If searching for a progression, set the progression variable to a list of
    Roman numerals figure strings like ["I", "V65", "I"]
    """

    if heads is None:
        heads = ["COMPOSER",
                 "COLLECTION",
                 "MOVEMENT",
                 "MEASURE",
                 ]
        if what != "Common Tone Diminished Sevenths":
            heads += ["FIGURE", "KEY"]  # single figure and key unhelpful in Cto7 case

    if what not in valid_searches:
        raise ValueError(f"For what, please select from among {valid_searches}.")

    if what == "Progression":
        if not progression:
            raise ValueError("If searching for a progression with the `what` parameter, "
                             "set the 'progression' parameter to a list of Roman numeral figures.")

    if corpus not in corpora:
        raise ValueError(f"Please select a corpus from among {corpora}.")

    lied = False
    if corpus == "OpenScore-LiederCorpus":
        lied = True

    out_data = []
    totalRns = 0
    totalLength = 0

    corpus_path = CORPUS_FOLDER / corpus
    sv_out_path = REPO_FOLDER / "Anthology" / corpus
    eg_out_path = REPO_FOLDER.parent / "Anthology" / corpus  # Now an external repo

    print(f"Searching for {what} within the {corpus} collection:")

    files = get_corpus_files(corpus_path,
                             file_name="analysis.txt"
                             )

    # URLs
    base_url = f'<a href="https://github.com/MarkGotham/'
    raw_url = f'<a href="https://raw.githubusercontent.com/MarkGotham/'
    wir = base_url + f"When-in-Rome/blob/master/Corpus/{corpus}/"
    ant_online = raw_url + f"Anthology/main/{corpus}/"
    eg_url_base = ant_online + what.replace(' ', '_') + "/"
    score_online = '<a href="https://musescore.com/score/'

    for file_path in files:
        try:
            rnf = RnFinder(file_path)
            totalRns += len(rnf.rns)
            totalLength += rnf.analysis.quarterLength
            print(".")
        except:
            print(f"Error with {file_path}")
            continue

        path_to_dir = file_path.parent
        path_parts = path_to_dir.parts[-3:]
        composer, collection, movement = [x.replace("_", " ") for x in path_parts]

        # URL for lieder
        if lied:
            matches = get_corpus_files(path_to_dir, "lc*.mscz")
            if matches:
                lc_num = matches[0].stem[2:]  # NB stem is a string filename w/out extension
                score_url = score_online + f'{lc_num}">{lc_num}</a>'
                download = wir + "/".join(path_parts).replace(",", "%2C")
                mscz_download = download + f'/lc{lc_num}.mscz">.mscz</a>'
                mxl_download = download + '/score.mxl">.mxl</a>'
            else:
                print(f"No <lc*.mscz> file found in {path_to_dir}")
                lc_num = "x_lc_missing"
                score_url = "x_url_missing"
                mscz_download = "mscz_missing"
                mxl_download = "mxl_missing"

        if what == "Modal Mixture":
            rnf.find_mixtures()
        elif what == "Augmented Chords":
            rnf.find_augmented_chords()
        elif what == "Augmented Sixths":
            rnf.find_augmented_sixths()
        elif what == "Neapolitan Sixths":
            rnf.find_Neapolitan_sixths()
        elif what == "Applied Chords":
            rnf.find_applied_chords()
        elif what == "Common Tone Diminished Sevenths":
            rnf.find_Cto_dim7()
        elif what == "Quiescenzas":
            rnf.find_quiescenzas()
        elif what == "ascending_fifths":
            rnf.find_ascending_fifths()
        elif what == "descending_fifths":
            rnf.find_descending_fifths()
        elif what == "fallender_Quintanstieg":
            rnf.find_fallender_Quintanstieg()
        elif what == "aufsteigender_Quintfall":
            rnf.find_aufsteigender_Quintfall()
        elif what == "Progressions":
            rnf.find_rn_progression(rns_list=progression)

        for x in rnf.results:

            x["COMPOSER"] = composer
            x["COLLECTION"] = collection
            x["MOVEMENT"] = movement

            if lied:
                # For pdf write only (not sv)
                x["source_path"] = path_to_dir
                x["eg_file"] = f'{lc_num}_{x["MEASURE"]}'  # TODO -1 getting added. Review.
                # For sv
                x["SCORE"] = score_url
                if score_url == "x_url_missing":
                    x["DOWNLOAD"] = "x_missing"
                    x["EXAMPLE"] = "x_missing"
                else:
                    x["DOWNLOAD"] = f"{mscz_download} {mxl_download}"
                    x["EXAMPLE"] = eg_url_base + f'{x["eg_file"]}-1.png">{x["eg_file"]}</a>'

        out_data += rnf.results

    sortedList = sorted(out_data, key=lambda x: (x["COMPOSER"],
                                                 x["COLLECTION"],
                                                 x["MOVEMENT"]
                                                 )
                        )

    totalRnLength = sum([x["LENGTH"] for x in sortedList])
    print(f"*** Summary of {what} found in the {corpus} collection:\n"
          f"\tFiles: {len(files)}.\n"
          f"\tCases (count): {len(sortedList)} from {totalRns} RNs overall.\n"
          f"\tLength: {totalRnLength} from {totalLength} total.\n")

    if not write_summary and not write_examples:
        return sortedList

    if write_summary:
        with open(sv_out_path / (what + ".csv"), "w") as svfile:
            svOut = csv.writer(svfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)

            if lied:
                heads += ["SCORE", "DOWNLOAD", "EXAMPLE"]

            svOut.writerow(heads)

            for entry in sortedList:
                row = [entry[head] for head in heads]
                svOut.writerow(row)

    if write_examples and corpus == "OpenScore-LiederCorpus" and lc_num:
        what = what.replace(" ", "_")  # TODO higher up?
        for item in sortedList:
            in_path = item["source_path"] / "score.mxl"  # TODO consider "analysis_on_score.mxl"
            if not in_path.exists:
                print(f"Warning: {in_path} file does not exist. Skipping.")
                continue

            example_path = eg_out_path / what
            score = converter.parse(in_path)

            # Range to use
            if what in [
                "Quiescenzas",
                "ascending_fifths",
                "descending_fifths",
                "aufsteigender_Quintfall",
                "fallender_Quintanstieg"
            ]:
                # ^ special handling of progressions
                start = int(item["MEASURE"].split("/")[0])
                end = start + 2
                item["eg_file"] = item["eg_file"].split("/")
            else:
                start = item["MEASURE"] - 1
                end = item["MEASURE"] + 1

            example = clean_up(score.measures(start, end))

            example.insert(0, metadata.Metadata())
            example.metadata.composer = item["COMPOSER"]
            example.metadata.title = f'{item["COLLECTION"]}. {item["MOVEMENT"]}. m{item["MEASURE"]}'

            # Currently always the middle of 3 measures. If not, consider:
            # te = expressions.TextExpression(f'{item["KEY"]}: {item["FIGURE"]}')
            # example.parts[0].measure(1).insert( ...

            example.coreElementsChanged()

            try:
                example.write(
                    "musicxml.png",  # sic, this as the format
                    fp=example_path / (item["eg_file"] + ".png")
                )
            except:
                print(f"Warning: unable to write {eg_out_path}")

            # music21 insists on also writing the xml. Remove:
            inadvertent_score_path = example_path / (item["eg_file"] + ".musicxml")
            if inadvertent_score_path.exists():
                inadvertent_score_path.unlink()
            else:
                print(f"Warning: No file found at {inadvertent_score_path}")


def clean_up(
        this_stream: stream,
        lied: bool = True
) -> stream:
    """
    Temporary function for cleaning example score outputs.
    Adapted from my `stream/tools` module for m21.

    Args:
        this_stream: the stream to work on. Note: In place is hard coded in.
        lied (bool): Lied-specific special cases.

    Returns: that same stream, modified.

    # TODO promote higher up the workflow, e.g., for creation of analysis_on_score
    # TODO possibly also remove `bar.Barline type=double` when not last measure
    """

    # for p in this_stream.parts:
    #     p.partAbbreviation = None
    #     # TODO ^ not effective. Resolved elsewhere.
    #
    #     last_measure = p.getElementsByClass(stream.Measure).last()
    #     last_measure.append(bar.Barline(type='final', location='right'))
    #     # TODO ^ not effective. (Partial) terminal double bar added by notation apps.

    if lied:
        i = this_stream.parts[0].getInstrument()
        this_stream.parts[0].replace(i, instrument.Instrument("Voice"))
        # TODO ^ this issue with voice part name is common. Resolve at source. Patch for now.

    remove_dict = {}

    for this_class in [
        layout.PageLayout,
        layout.SystemLayout,
        tempo.MetronomeMark,
        # NB: keep layout.StaffGroup
        bar.Barline,  # TODO Also not effective. See above
    ]:
        for this_state in this_stream.recurse().getElementsByClass(this_class):
            if this_state.activeSite in remove_dict:  # There may be several in same (e.g., measure)
                remove_dict[this_state.activeSite].append(this_state)
            else:
                remove_dict[this_state.activeSite] = [this_state]

    for activeSiteKey, valuesToRemove in remove_dict.items():
        activeSiteKey.remove(valuesToRemove, recurse=True)

    return this_stream


def all_searches_one_corpus(corpus: str = "OpenScore-LiederCorpus"):
    """
    Runs the one_search_one_corpus function for
    one corpus and
    all search terms except "Progressions".
    """

    for w in valid_searches[:-1]:  # omit progressions
        one_search_one_corpus(corpus=corpus, what=w)


def all_corpora_one_search(what: str = "fallender_Quintanstieg"):
    """
    Runs the one_search_one_corpus function for
    one corpus and
    all search terms except "Progressions".
    """

    for c in corpora:
        one_search_one_corpus(corpus=c, what=what)


def all_searches_all_corpora():
    """
    Runs the one_search_one_corpus function for all pairs of
    corpus and search terms except "Progressions".
    """

    for c in corpora:
        for w in valid_searches[:-1]:  # omit progressions
            one_search_one_corpus(corpus=c, what=w)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest

    doctest.testmod()
