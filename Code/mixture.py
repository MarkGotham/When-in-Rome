# -*- coding: utf-8 -*-
"""
NAME:
===============================
Mixture (mixture.py)

BY:
===============================
Mark Gotham

LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/

ABOUT:
===============================
Developing more robust definitions for different kind of modal mixture and their relative strength.

NOTE:
first implementation previously in this repo now in music21.
This implementation of the multiple option approach is new.

"""

# ------------------------------------------------------------------------------

from music21 import chord, expressions, interval, meter, pitch, roman, stream

from Code.Pitch_profiles import chord_usage


# ------------------------------------------------------------------------------

def is_mixture(
        rn: roman.RomanNumeral,
        spelling_matters: bool = True,
        accept_secondary: bool = True,
        secondary_against_home_key: bool = True,
        exclude_clear_non_mixture: bool = False,
        require_fits_all_minor: bool = False,
        require_shared_or_mixed: bool = False,
        minimum_score: int = 0
) -> bool:
    """
    Find instances of modal mixture as defined in [forthcoming].

    At a minimum, this means the presence of
    at least one pitch that is potentially an instance of mixture:
    a tone that can be considered outside the host mode but within the parallel (German: Variant).

    Accounting for all minor forms, this means
    {m3, m6, m7} for mixture of minor into major, and
    {M3, M6, M7} for major into minor.

    Note the absence of m7 into minor:
    while this could be considered outside the host mode
    (depending on the minor mode in question),
    it cannot be considered a borrowing from the major.

    First an example of borrowing from the minor into major (m6).

    >>> flat_6 = roman.RomanNumeral("iv", "G")
    >>> is_mixture(flat_6)
    True

    Now a complementary example of borrowing from the major into the minor (M3).

    >>> picardy = roman.RomanNumeral("I", "c")
    >>> is_mixture(picardy)
    True

    Users may select True/False for each of several (following) criteria,
    avoiding certain pitches that strengthen/weaken the case for mixture specifically.
    (Remember that this is distinct from other types of chromaticism.)

    Chords make a stronger case for mixture by
    avoiding pitches that are unequivocally not mixed.
    In major this means {M3}; in minor it is {m3, m6}.
    Set `exclude_clear_non_mixture` to True to require this (default = False).

    >>> min_6_maj_3 = ["F", "Ab", "C", "E"]
    >>> min_6_maj_3 = roman.romanNumeralFromChord(chord.Chord(min_6_maj_3), "C")
    >>> is_mixture(min_6_maj_3)  #, exclude_clear_non_mixture=False)
    True

    >>> is_mixture(min_6_maj_3, exclude_clear_non_mixture=True)
    False

    The `require_shared_or_mixed` argument (default = False) provides a
    stronger version of this, which expands on the `exclude_clear_non_mixture`
    criteria to also exclude any pitches that are outside the combined modes
    (major or at least one of the parallel minor forms):
    i.e., not #1 / b2 or #4 / b5.
    If either excluded pitch is present, then this function returns False.

    >>> sharp_4_flat_3 = roman.RomanNumeral("viio7/V", "C")
    >>> is_mixture(sharp_4_flat_3, require_shared_or_mixed=False)
    True

    >>> is_mixture(sharp_4_flat_3, require_shared_or_mixed=True)
    False

    This helps make sense of the status of Neapolitan- and Augmented Sixth chords.
    Both can be considered in terms of modal mixture into major, due to the use of m6,
    but both also use chromatic pitches:
    b2 in the case of the Neapolitan, and
    (at least) #4 in the case of the Augmented Sixth chords.
    When `require_shared_or_mixed` is True, they return False; when False, then True.

    >>> aug_6 = roman.RomanNumeral("Ger65", "C")
    >>> is_mixture(aug_6, require_shared_or_mixed=True)
    False

    >>> is_mixture(aug_6, require_shared_or_mixed=False)
    True

    Avoiding {M6, m7, M7} makes the chord consistent across minor forms.
    In major, meeting this condition counts towards mixture, in minor it counts against.
    Set `require_fits_all_minor` = True to require this (default = False).

    >>> m3_M6 = chord.Chord("A C Eb")
    >>> m3_M6 = roman.romanNumeralFromChord(m3_M6, "C")
    >>> is_mixture(m3_M6, require_fits_all_minor=False)
    True

    >>> is_mixture(m3_M6, require_fits_all_minor=True)
    False

    Note that for (potential minor mixture into) major key contexts,
    `require_fits_all_minor` is more restrictive than `require_shared_or_mixed`
    so setting `require_fits_all_minor` to True and `require_shared_or_mixed` to False
    is contradictory and print a warning.

    This function can work either by comparing pitch classes
    (i.e. as numbers 0-11, ignoring spelling)
    or with full pitch spelling. See notes at `add_mixture_info()`.

    Finally, there is the question of how to handle applied (secondary) chords.
    Here, `secondary_against_home_key` is True by default, meaning that
    the pitches of the chord are considered against the primary ("home") key.
    Set `secondary_against_home_key` = False to override this and consider
    mixture against the secondary key.

    This is potentiatlly significant in dealing with numerals like
    "viio7/v".
    It is clear whether that chord is really "viio7/v" or "viio7/V" and analysts do not agree.
    Again, by using the deafult of comparing this chord against the primary tonality, that
    "viio7/v" or "viio7/V" are equivalent.

    >>> in_v = roman.RomanNumeral("viio7/v", "C")
    >>> in_V = roman.RomanNumeral("viio7/V", "C")

    Show they have different figures ...
    >>> in_v.figure == in_V.figure
    False

    ... but the same pitches:
    >>> [p.name for p in in_v.pitches] == [p.name for p in in_V.pitches]
    True

    Of "/v" (minor), first with `secondary_against_home_key` (so against the home key, i.e., "C"):

    >>> is_mixture(in_v)
    True

    Now with `secondary_against_home_key` as False, so with the key as "v" in "C" (i.e. "g").
    >>> is_mixture(in_v, secondary_against_home_key=False)
    False

    Now of "/V" (major), first against the home key (i.e., "C"), as above.

    >>> is_mixture(in_V)
    True

    And finally with `secondary_against_home_key` as False, so "V" in "C" (i.e. "G" major).
    >>> is_mixture(in_V, secondary_against_home_key=False)
    True

    """

    if rn.key.mode == 'major':
        if require_fits_all_minor and (not require_shared_or_mixed):
            require_shared_or_mixed = True
    #         print(
    #             "In major, `require_fits_all_minor` is more restrictive than "
    #             "`require_shared_or_mixed`. Calling `require_fits_all_minor` but not "
    #             "`require_shared_or_mixed` is contradictory."
    #             "Setting `require_shared_or_mixed` to True."
    #         )

    if rn.secondaryRomanNumeral and not accept_secondary:
        print(f"The figure {rn.figure} has a secondary secondary Roman numeral and you have"
              "set `accept_secondary` to False. Returning False.")
        return False

    rn = add_mixture_info(rn,
                          spelling_matters=spelling_matters,
                          secondary_against_home_key=secondary_against_home_key)

    # Not mixture in any context. Not even settable.
    if rn.potential_mixture_count < 1 and rn.clear_mixture_count < 1:
        return False

    if exclude_clear_non_mixture and rn.clear_non_mixture_count > 0:
        return False

    if require_shared_or_mixed:
        if rn.clear_non_mixture_count > 0 or rn.other_count > 0:
            return False

    if require_fits_all_minor and not (rn.all_natural and rn.all_harmonic):
        return False

    if rn.mixture_metric >= minimum_score:
        return True
    else:
        return False


pitch_names = (
    "C",
    "C#",
    "D",
    "E-",
    "E",
    "F",
    "F#",
    "G",
    "A-",
    "A",
    "B-",
    "B"
)

pitch_classes = (range(12))


def add_mixture_info(
        rn: roman.RomanNumeral,
        spelling_matters: bool = True,
        secondary_against_home_key: bool = True,
        # Metric:
        clear_mixture_weight: int = 2,
        potential_mixture_weight: int = 1,
        other_weight: int = 1
) -> roman.RomanNumeral:
    """
    Takes in a normal roman.RomanNumeral object and 
    returns it with new, mixture-specific attributes added.

    Several of these attributes involve counting tones by their mixture status.
    Tones may be:
    - neutral (shared by major and minor)
    - definitely indicative of mixture
    - potentially indicate of mixture
    - definitely indicative of non-mixture
    - chromatic (none of the above - neither diatonic nor mixture).

    .clear_mixture_count: int counting notes that definitely indicate mixture
    E.g., minor third and minor sixth in major key.
    >>> i_in_C = roman.RomanNumeral("i", "C")
    >>> i_in_C = add_mixture_info(i_in_C)
    >>> i_in_C.clear_mixture_count
    1

    >>> bVI_in_C = roman.RomanNumeral("bVI", "C")
    >>> bVI_in_C = add_mixture_info(bVI_in_C)
    >>> bVI_in_C.clear_mixture_count
    2

    .potential_mixture_count: int counting notes that only might indicate mixture.
    E.g., the minor seventh in major key is not in major,
    but can also only be considered mixture depending on the type of minor scale.
    >>> v_in_C = roman.RomanNumeral("v", "C")
    >>> v_in_C = add_mixture_info(v_in_C)
    >>> v_in_C.potential_mixture_count
    1

    Note that this is separate from the .clear_mixture_count.
    >>> v_in_C.clear_mixture_count
    0

    .clear_non_mixture_count: int counting notes that certainly indicate non-mixture
    E.g., the major third in major key.

    >>> tonic_major = roman.RomanNumeral("I", "C")
    >>> tonic_major = add_mixture_info(tonic_major)
    >>> tonic_major.clear_non_mixture_count
    1
    
    .other_count: int counting instances of other notes
    that are neither diatonic nor mixture (none of the above).
    E.g., the diminished fifth.
    >>> rn_Gb = roman.RomanNumeral("io", "C")  # includes Gb
    >>> rn_Gb = add_mixture_info(rn_Gb)
    >>> rn_Gb.other_count
    1

    Note that this `other_count` can depend on whether `spelling_matters`.
    Iff spelling_matters then the flat 6th degee must be spelt as such (e.g., as Ab in C).
    If not, then enharmonics count too (i.e., G# in C).
    In comparing G# and Ab in C major, only G# adds to the other_count, and only if spelling_matters.
    
    >>> rn_Ab = roman.RomanNumeral("iio", "C")  # includes Ab
    >>> no_spelling = add_mixture_info(rn_Ab, spelling_matters = False)
    >>> no_spelling.other_count
    0

    >>> with_spelling = add_mixture_info(rn_Ab, spelling_matters = True)
    >>> with_spelling.other_count
    0

    >>> rn_G_sharp = roman.RomanNumeral("I+", "C")  # includes G#
    >>> pitch_class_8 = add_mixture_info(rn_G_sharp, spelling_matters = False)
    >>> pitch_class_8.other_count
    0

    >>> raised_fifth = add_mixture_info(rn_G_sharp, spelling_matters = True)
    >>> raised_fifth.other_count
    1

    Several other boolean summative attributes derive from these counters:
    .all_harmonic: bool checking if all pitches are in the harmonic minor.
    >>> viio7 = roman.RomanNumeral("viio7", "C")  # includes B, Ab
    >>> viio7 = add_mixture_info(viio7)
    >>> viio7.all_harmonic
    True

    .all_natural:
    bool, likewise for natural minor.
    >>> v_in_C.all_natural  # As above. Includes Bb
    True

    .includes_chromatic:
    bool, true if there is at least 1 chromatic pitch (as defined above).
    >>> rn_Gb.includes_chromatic  # As above. Includes Gb
    True

    .all_shared_or_mixed:
    bool, as for "chromatic" with the additional consideration of "clearlyNotMixed".
    
    Finally, the `.mixture_metric` attribute (int) is also summative,
    providing an approximate strength value for a mixture (which can be negative).
    The result of the mixture_metric can be weighted with the following settable arguments
    which weight each relevant tone to the value given:
        clear_mixture_weight: int = 2
        potential_mixture_weight: int = 1
        other_weight: int = 1
    With these weights the maximum value per note is 2 and the minimium is -2.
    In princple then this number can be multiplied up for each tone.
    Even mixture chords rarely have more than 2 notes indicative of mixture,
    though it is possible, especially if we accept added tones.
    >>> maximix = roman.RomanNumeral("i[addb6][addb7]", "C")  # includes Eb, Ab, Bb
    >>> maximix = add_mixture_info(maximix)
    >>> maximix.mixture_metric
    5

    Note that this whole function works by transposing the pitches to C and
    comparing against C major or minor as appropriate.
    This is prefered over alternatives
    (like creating a new RN in C major / minor)
    so that specifications on the original object (like roman.Minor67Default)
    are reliably preserved.
    
    The spelling_matters argument determines whether to use pitch spelling or
    pitch classes as discussed above.

    See further doctests and demonstrations at .is_mixture(), including for
    the options with handling secondary Roman numerals with the
    .secondary_against_home_key argument.

    """

    # Prep mode: Here, then potentially revised in consideration of secondaries
    if rn.key.mode == "major":
        major_mode = True  # Bool: T/F for Major/Minor
    elif rn.key.mode == "minor":
        major_mode = False
    else:
        raise ValueError("Key mode must be minor or major.")

    # Tonic and secondaries
    original_tonic = rn.key.tonic
    if rn.secondaryRomanNumeral and not secondary_against_home_key:
        original_tonic = rn.secondaryRomanNumeral.root()
        if rn.secondaryRomanNumeral.figure[0].islower():  # lower case = minor
            major_mode = False  # Override setting for primary key above

    # transposed_pitches
    root_interval = interval.Interval(original_tonic, pitch.Pitch("C"))
    transposed_pitches = [p.transpose(root_interval) for p in rn.pitches]

    # Prep pitches:
    if spelling_matters:
        chord_pitches = [x.name for x in transposed_pitches]  # NB: already in C or c
        reference_pitches = pitch_names
    else:  # not spelling_matters. chord_pitches with root 0:
        # chord_pitches = [(x.pitchClass - rootPC % 12) for x in rn.pitches]
        # ^ prev. when transposing
        chord_pitches = [x.pitchClass for x in transposed_pitches]
        reference_pitches = pitch_classes

    # Init attributes
    # Counts:
    rn.potential_mixture_count = 0
    rn.clear_mixture_count = 0  # These two ... 
    rn.clear_non_mixture_count = 0  # ... are paired
    rn.other_count = 0
    rn.mixture_metric = 0
    # Bools:
    rn.all_shared_or_mixed = True
    rn.all_natural = True
    rn.all_harmonic = True
    rn.includes_chromatic = False

    for pc in chord_pitches:
        if pc not in reference_pitches:
            rn.other_count += 1
        elif pc in [reference_pitches[1], reference_pitches[6]]:
            rn.other_count += 1

    if rn.clear_non_mixture_count > 0:  # False iff one negates
        rn.all_shared_or_mixed = False
    if rn.other_count > 0:
        rn.all_shared_or_mixed = False
        rn.includes_chromatic = True
        rn.all_natural = False
        rn.all_harmonic = False

    # Logic of category membership, pitch by pitch:

    # m3
    if reference_pitches[3] in chord_pitches:
        if major_mode:
            rn.clear_mixture_count += 1
        else:  # minor
            rn.clear_non_mixture_count += 1

    # M3
    if reference_pitches[4] in chord_pitches:
        rn.all_natural = False
        rn.all_harmonic = False
        if major_mode:
            rn.clear_non_mixture_count += 1
        else:  # minor
            rn.clear_mixture_count += 1

    # m6
    if reference_pitches[8] in chord_pitches:
        if major_mode:
            rn.clear_mixture_count += 1
        else:  # minor
            rn.clear_non_mixture_count += 1

    # M6
    if reference_pitches[9] in chord_pitches:
        rn.all_natural = False
        rn.all_harmonic = False
        if not major_mode:  # minor. Major n/a
            rn.potential_mixture_count += 1

    # m7
    if reference_pitches[10] in chord_pitches:
        rn.all_harmonic = False
        if major_mode:
            rn.potential_mixture_count += 1
        # else:  # minor n/a

    # M7
    if reference_pitches[11] in chord_pitches:
        rn.all_natural = False
        if not major_mode:  # minor. Major n/a
            rn.potential_mixture_count += 1

    # mixture_metric
    # +
    rn.mixture_metric += (rn.clear_mixture_count * clear_mixture_weight)
    rn.mixture_metric += rn.potential_mixture_count * potential_mixture_weight
    # -
    rn.mixture_metric -= rn.clear_non_mixture_count * clear_mixture_weight
    rn.mixture_metric -= rn.other_count * other_weight

    return rn


# ------------------------------------------------------------------------------

def in_practice(
        corpus: str = "OpenScore-LiederCorpus",
        major_mode: bool = True,
        write: bool = False
) -> dict:
    """
    Take all the chords used as recorded in one of the chord_usage_dicts,
    filter for those that match specific mixture criteria,
    return summative data about each case for either C major or a minor.
    """

    if major_mode:
        key = "C"
        this_mode = "major"
    else:
        key = "a"
        this_mode = "minor"

    simple_dict = chord_usage.simplify_or_consolidate_usage_dict(
        f"{this_mode}_{corpus}.json",
        simplify_not_consolidate=True,
        no_inv=True,
        no_other_alt=False,
        no_secondary=False,
        major_not_minor=(this_mode == "major"),
        write=False)

    out_info = {}
    if write:
        p = stream.Part()
        p.insert(meter.TimeSignature("1/4"))

    for fig in simple_dict:
        rn = add_mixture_info(roman.RomanNumeral(fig, key))
        if rn.mixture_metric > 0:
            out_info[fig] = rn_to_mixture_list(rn) + [simple_dict[fig]]
            if write:
                rn.addLyric(fig)
                rn.addLyric(simple_dict[fig])
                p.append(rn)

    if write:
        te = expressions.TextExpression("Modal mixture. Most common cases into the "
                                        f"{this_mode} mode in the {corpus}")
        te.placement = "above"
        p.insert(0, te)
        p.makeMeasures()
        p.show()

    return out_info


def rn_to_mixture_list(
        rn: roman.RomanNumeral
) -> list:
    """
    Present a tuple with mixture information for a roman.RomanNumeral object.
    Supports triads and sevenths.
    Expected to have add_mixture_info run in advance.
    """

    pitch_names = list(set([p.name.replace("-", "b") for p in rn.pitches]))

    presentable_pitches = pitches_in_order(pitch_names,
                                           root=rn.root().name.replace("-", "b"))
    return [
        "-".join(presentable_pitches),
        rn.clear_mixture_count,
        rn.potential_mixture_count,
        rn.clear_non_mixture_count,
        rn.mixture_metric
    ]


def pitches_in_order(
        list_of_pitch_names: list[str],
        root: str,
        rotate_to_root: bool = True
) -> list:
    """
    Takes a list of pitch names and returns them in order with:
    alphabetical ordering first (A-G)
    and then (optionally) rotation to begin on the root.
    Args:
        list_of_pitch_names: a list of pitch names (no octave)
        root: the pitch name of the root (deduced elsewhere)
        rotate_to_root (bool):

    Returns: list
    """
    list_of_pitch_names = sorted(list_of_pitch_names)
    if rotate_to_root:
        if root in list_of_pitch_names:  # rare cases of [no1]
            root_index = list_of_pitch_names.index(root)
            return list_of_pitch_names[root_index:] + list_of_pitch_names[:root_index]
        else:
            print(f"Warning: Root {root} not in {list_of_pitch_names}. No rotation.")
            return list_of_pitch_names
    else:
        return list_of_pitch_names


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest

    doctest.testmod()
