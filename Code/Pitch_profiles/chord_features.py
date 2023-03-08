"""
NAME:
===============================
Chord Features (chord_features.py)


BY:
===============================
Mark Gotham


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


Citation:
===============================
Watch this space!


ABOUT:
===============================
Extract features of chords
and chord-source comparisons
e.g., for categorisation tasks in machine learning.


TODO: Currently limited to single chord. Include chord progressions here too.

"""

from . import chord_comparisons
from . import normalisation_comparison
from ..Resources import chord_profiles, import_chord_usage_stats
from .. import harmonicFunction

from music21 import analysis, roman


# ------------------------------------------------------------------------------

class SingleChordFeatures:
    """
    Extract features of
    single chords,
    and
    chord-source comparisons.
    e.g. for categorisation in machine learning.

    Input arguments are:

    * Roman Numeral (use roman.RomanNumeral object where possible; otherwise, str for figure only,
    * sourceUsageProfile: list,
    * returnOneHot: bool = True,
    * comp_type: str = "L1"

    All vectors are provided in the form of a list of numerical value(s).
    There may be one or more, and entries may be ints or float.

    To support machine learning, each function has the option of returning
    a "one hot encoding" whenever the features are independent classes
    so that the model can learn specific weights.
    This is a vector of one 1 and otherwise all 0s.
    For example, for triad types, the one hot encodings are:
    ["100", "010", "001"] for ["major", "minor", "other"], respectively.
    If one hot encoding is not selected (False), the
    equivalent outputs are [0], [1], or [2] (i.e. the index in the above list).

    See specific methods for details.

    The features represented here include a lot of apparent redundancy.
    For example, features are provided not only for the triad quality,
    but also for the 3rd and 5th of the chord
    (which is included in the triad quality).
    This is because it is often hard or impossible to know in advance
    which features will be effective in a given use case.

    Connects with functionality for simplifying harmonies.
    """

    def __init__(self,
                 rn: roman.RomanNumeral | str,
                 sourceUsageProfile: list,
                 returnOneHot: bool = True,
                 comparison_type: str = "L1",
                 reference_usage_dict_name: str = "major_OpenScore-LiederCorpus.json"):

        if isinstance(rn, str):
            rn = roman.RomanNumeral(rn)
        self.rn = rn
        self.sourceUsageProfile = sourceUsageProfile
        self.returnOneHot = returnOneHot
        self.comparison_type = comparison_type

        self.chordQualityVector = None
        self.thirdTypeVector = None
        self.fifthTypeVector = None
        self.seventhTypeVector = None
        self.rootPitchClassVector = None
        self.getBasicChordFeatures()

        self.thisFn = str(harmonicFunction.figureToFunction(self.rn))
        self.hauptFunctionVector = self.getHauptFunctionVector()
        self.functionVector = self.getFunctionVector()

        self.chosenChordPCPVector = self.getChosenChordPCPVector()
        self.bestFitChordPCPVector = [0] * 12
        self.distanceToChosenChordVector = [0]
        self.distanceToBestFitChordPCPVector = [0]
        self.chordTypeMatchVector = [0]
        self.chordRotationMatchVector = [0]

        self.evaluateBestFit()

        self.reference_usage_dict = import_chord_usage_stats(reference_usage_dict_name)
        self.reference_usage_dict_simple = import_chord_usage_stats(
            reference_usage_dict_name.replace(".json", "_simple.json")
        )
        self.fullChordCommonnessVector = self.getFullChordCommonnessVector()
        self.simplifiedChordCommonnessVector = self.getSimplifiedChordCommonnessVector()

    def getBasicChordFeatures(self):
        """
        Retrieve basic chord features.

        Mostly open to the one hot format:
        - chordQualityVector: 4 triads, 4 sevenths, None/Other; dimensions = 9; discrete = True
        - thirdTypeVector: m3, M3, None/other; dimensions = 3; discrete = True
        - fifthTypeVector: d5, P5, A5, None/other; dimensions = 5; discrete = True
        - seventhTypeVector: d7, m7, M7, None/other; dimensions = 4; discrete = True
        - rootPitchClassVector: 0-11; dimensions = 12; discrete = True

        Multi-hot (too many types for one-hot to be really practical)
        TODO intervalVector: dimensions = 6; discrete = True

        """

        # Alternatively if not self.rn.containsTriad (includes sevenths) and
        # third = (r.third.pitchClass - r.root().pitchClass) % 12
        # etc

        commonName = self.rn.commonName

        chordData = {"diminished triad": ["m3", "d5", None],
                     "minor triad": ["m3", "P5", None],
                     "major triad": ["M3", "P5", None],
                     "augmented triad": ["M3", "A5", None],
                     "half-diminished seventh chord": ["m3", "d5", "m7"],
                     "diminished seventh chord": ["m3", "d5", "d7"],
                     "minor seventh chord": ["m3", "d5", "m7"],
                     "dominant seventh chord": ["M3", "P5", "m7"],
                     "major seventh chord": ["M3", "P5", "m7"],
                     }
        # TODO consider any special cases, e.g. if "augmented sixth" in name; if incomplete:

        chordTypes = list(chordData.keys())
        thirdTypes = ("m3", "M3")
        fifthTypes = ("d5", "P5", "A5")
        seventhTypes = ("d7", "m7", "M7")

        # NB _sharedIndexMethod handles not in list
        self.chordQualityVector = self._sharedIndexMethod(chordTypes, commonName)
        if commonName in chordData:
            thirdFifthSeventh = chordData[commonName]
        else:
            thirdFifthSeventh = ["Fake", "Fake", "Fake"]
        self.thirdTypeVector = self._sharedIndexMethod(thirdTypes, thirdFifthSeventh[0])
        self.fifthTypeVector = self._sharedIndexMethod(fifthTypes, thirdFifthSeventh[1])
        self.seventhTypeVector = self._sharedIndexMethod(seventhTypes, thirdFifthSeventh[2])

        self.rootPitchClassVector = self.rn.root().pitchClass  # 0-11
        if self.returnOneHot:
            emptyList = [0] * 12
            emptyList[self.rootPitchClassVector] = 1
            # print("***" + str(emptyList))
            self.rootPitchClassVector = emptyList

    def getHauptFunctionVector(self):
        """
        Mapping of
        "T", "t", "S", "s", "D", "d", and a final entry for None/Other
        to either an index position in that list, e.g. returning [3]
        or if returnOneHot, then in the format [0, 0, 0, 1, ...

        self.hauptFunctionVector
        dimensions = 7
        discrete = True
        """

        thisHauptFn = self.thisFn[0]
        hauptFunctionList = ["T", "t", "S", "s", "D", "d"]

        return self._sharedIndexMethod(hauptFunctionList, thisHauptFn)

    def getFunctionVector(self):
        """
        Mapping of the 18 functions
        "T", "Tp", "Tg", "t", "tP", "tG",
        "S", "Sp", "Sg", "s", "sP", "sG",
        "D", "Dp", "Dg", "d", "dP", "dG",
        and a final entry for None/Other
        to either an index position in that list, e.g. returning [3]
        or if returnOneHot, then in the format [0, 0, 0, 1, 0, 0, 0, ...

        self.functionVector
        dimensions = 19
        discrete = True
        """

        functionList = [str(x) for x in analysis.harmonicFunction.HarmonicFunction]
        # I.e. "T", "Tp", "Tg", "t", "tP", "tG", ...
        return self._sharedIndexMethod(functionList, self.thisFn)

    def _sharedIndexMethod(
            self,
            thisList: list | tuple,
            thisItem: str | None
    ) -> int:
        """
        Get the index of an entry in a list,
        or (if self.returnOneHot) then
        a new list with all 0s excepts one 1 for the entry index.

        For an element not in the list, returns an index of N + 1.
        """
        possibilities = len(thisList)  # E.g. for function vectors, 6 or 18
        try:
            index = thisList.index(thisItem)
        except:
            index = possibilities  # i.e. final, None/Other
        if self.returnOneHot:
            vector = [0] * (possibilities + 1)  # 6 + 1 = 7; 18 + 1 = 19
            vector[index] = 1  # e.g. [0, 0, 0, 1, 0, 0, 0, ...
        else:
            vector = [index]  # e.g. [3]

        return vector

    # ------------------------------------------------------------------------------

    def getChosenChordPCPVector(
            self,
            root_0: bool = False
    ):
        """
        12-element vector, with 1 or 0 for each pitch class in the chord.
        self.chosenChordPCPVector
        dimensions = 12
        discrete = True
        E.g. [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0] for C major

        NOTE:
        - No mapping and no returnOneHot option.
        - Source PCP produced separately by combine_slice_group (get_distributions)
        """
        return chord_comparisons.roman_to_pcp(self.rn.figure,
                                              self.rn.key,
                                              root_0=root_0,  # ?
                                              return_root=False)

    def evaluateBestFit(
            self,
            reference_profile_dict: dict = chord_profiles.binary,
    ):
        """
        Is the asserted chord the best fit from a profile matching perspective?
        If so, both
        self.chordTypeMatchVector = [1]
        and
        self.chordRotationMatchVector = [1]
        Note: this is 1/0 for True/False, whether or not one hot encoding is set so both are.
        dimensions = 1
        discrete = True

        This method also keeps values for ...

        self.bestFitChordPCPVector
        dimensions = 12
        discrete = True
        E.g. [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0] for C major

        ... and the various distances.

        self.distanceToChosenChordVector
        dimensions = 1
        discrete = False (continuous, float in the range 0-1)
        """

        a, b, c = chord_comparisons.best_fit_chord(
            self.sourceUsageProfile,
            reference_profile_dict=reference_profile_dict,
            reference_chord_names=chord_comparisons.chord_types,
            comp_type=self.comparison_type,
            return_in_chord_PCs_only=False,
            return_least_distance=True)

        bestFitChordName, bestFitChordRotation, self.distanceToBestFitChordPCPVector = a, b, [c]

        bestProfilePreRotation = chord_profiles.binary[bestFitChordName]
        self.bestFitChordPCPVector = chord_comparisons.rotate(bestProfilePreRotation,
                                                              bestFitChordRotation)

        # self.chordTypeMatchVector = [0] from init
        if bestFitChordName == self.rn.commonName:
            self.chordTypeMatchVector = [1]

        # self.bestFitChordRotationMatch = [0] from init
        if bestFitChordRotation == self.rn.root().pitchClass:  # check ***:
            self.chordRotationMatchVector = [1]

        # TODO only if not a match. Otherwise same.
        # Map to range 0-1
        comparison_type = self.comparison_type.lower()
        if comparison_type in ["sum", "manhattan", "l1"]:
            denominator = 2
        elif comparison_type in ["euclidean", "l2"]:
            import math
            denominator = math.sqrt(2)
        else:
            raise ValueError(f"Invalid comparison type")

        self.distanceToChosenChordVector = [self.getDistanceToChosenChord() / denominator]

    def getDistanceToChosenChord(self):
        """
        self.distanceToChosenChordVector
        dimensions = 1
        discrete = False (continuous)
        """
        return normalisation_comparison.compare_two_profiles(self.sourceUsageProfile,
                                                             self.chosenChordPCPVector,
                                                             comparison_type=self.comparison_type)

    def getFullChordCommonnessVector(self):
        """
        How commonly used is this exact chord?
        Calculated as a percentage usage / the top percentage
        so the range is 0-1, with
        1 for the most commonly used chord, and
        0 for an entry unseen in the reference corpus.

        self.fullChordCommonnessVector
        dimensions = 1
        discrete = False (continuous)
        """

        thisKey = self.rn.figure
        return [getCommonPercentage(self.reference_usage_dict, thisKey)]

    def getSimplifiedChordCommonnessVector(self):
        """
        Same as for getFullChordCommonnessVector, but with the simplified chord.

        self.simplifiedChordCommonnessVector
        dimensions = 1
        discrete = False (continuous)
        """
        this_key = simplify_chord(self.rn.figure)
        return [getCommonPercentage(self.reference_usage_dict_simple, this_key)]


def getCommonPercentage(thisDict, thisKey):
    """
    Shared function for
    getFullChordCommonnessVector,
    getSimplifiedChordCommonnessVector.
    """
    try:
        thisPercent = thisDict[thisKey]  # Fails if not in the dict
        maxPercent = list(thisDict.values())[0]
    except KeyError:
        return 0

    return round(thisPercent / maxPercent, 3)


def simplify_chord(
        rn: roman.RomanNumeral | str,
        haupt_function: bool = False,
        full_function: bool = False,
        no_root_alt: bool = False,
        no_quality_alt: bool = False,
        no_inv: bool = False,
        no_other_alt: bool = False,
        no_secondary: bool = False,
) -> str:
    """
    Given a chord simplify that chord in one or more ways.
    The input rn argument is best expressed as a `roman.RomanNumeral` object.
    It will also accept a string (converting this to the `roman.RomanNumeral` object) though
    some results in that case will be affected because the tonality is not known.

    The following documents, demonstrates, and tests the various options
    alongside roman.RomanNumeral attributes where relevant.

    The first option is basically the most drastic simplification:
    `haupt_function` returns the basic function.
    See notes at `When-in-Rome/Code/harmonicFunction`
    and its partial derivative at `music21.analysis.harmonicFunction`.
    E.g., the major tonic chord `I` has a Hauptfunction of `T`.

    >>> simplify_chord('I', haupt_function = True)
    'T'

    `full_function` is like `haupt_function`,
    but it supports Nebenfunktionen like `Tp` where relevant.

    E.g., `haupt_function` will return `T` for `I`, but also `vi`:
    >>> simplify_chord('I', haupt_function = True)
    'T'

    >>> simplify_chord('vi', haupt_function = True)
    'T'

    The `full_function` option still returns `T` for `I`, but `Tp` for `vi`.
    >>> simplify_chord('I', full_function = True)
    'T'

    >>> simplify_chord('vi', full_function = True)
    'Tp'

    We now move on to the simplification of special parts of the Roman numeral,
    using the particularly comlpex (and rather unlikely) example of `#ivo65[add#6]/V`.
    >>> rn_string = '#ivo65[add#6]/V'

    The full list of these `no` options is (in order of presentation):
    `no_root_alt`,
    `no_quality_alt`,
    `no_inv`,
    `no_other_alt`,
    `no_secondary`,

    `no_root_alt` removes any root alteration.
    Note that ignoring root alteration is as drastic as it sounds and is
    desirable only in special cases
    (e.g., for significant dimension reduction in feature extraction)
    and almost certainly in combination with other removals set out below.
    >>> simplify_chord(rn_string, no_root_alt = True)
    'ivo65[add#6]/V'

    `no_quality_alt` removes any quality modifiers:
    the upper/lower case distinction for minor versus major remains,
    but augmented and diminished symbols are lost (including for 7th chords).
    >>> simplify_chord(rn_string, no_quality_alt = True)
    '#iv65[add#6]/V'

    `no_inv` removes the inversion:
    >>> simplify_chord(rn_string, no_inv = True)
    '#ivo7[add#6]/V'

    Note how this removes the `65` (first inversion) but retains the fact of being a seventh.
    `no_inv` also incidentally maps 9ths to 7ths in the same breath.
    This behaiour may change.
    >>> simplify_chord('V9[add#6]/V', no_inv = True)
    'V7[add#6]/V'

    `no_other_alt` removes any added, removed, and chromatically altered tones
    (excepting the root modifier discussed above).
    This is probably the most straightforwardly useful single option as
    only some analysts specify at this level of detail,
    so removing it can close the gap between analystical styles, for instance.
    >>> simplify_chord(rn_string, no_other_alt = True)
    '#ivo65/V'

    `no_secondary` removes secondary Roman numerals:
    >>> simplify_chord(rn_string, no_secondary = True)
    '#ivo65[add#6]'

    Note the following.

    1. function labels (currently) make
    all of these `no` options reductant (implied, and not even called).
    (This may change if inversion labels are introduced to the functions.)

    2. the `no` options are, of course, eminently combinable.
    Here, for example, is `no_inv` combined with `no_other_alt`:
    >>> simplify_chord(rn_string, no_inv = True, no_other_alt = True)
    '#ivo7/V'

    3. all options are set to False by default, forcing the user to choose which to use.
    >>> simplify_chord(rn_string)
    '#ivo65[add#6]/V'

    Now, some notes of semi-corresponding attributes in music21.
    Here, we work party on the string, to ensure no unexpected sideeffects.
    (For instance, testing saw the unwarranted introduction of root motification `#`s)
    Here, for reference, are some of those music21 attributes.

    `music21 roman.RomanNumeral.romanNumeral` removes all but the Roman numeral
    and any root modifier.

    >>> rn = roman.RomanNumeral(rn_string)
    >>> rn.romanNumeral
    '#iv'

    `music21 roman.RomanNumeral.romanNumeralAlone` is similar, but it also removes
    that root modifier.

    >>> rn = roman.RomanNumeral(rn_string)
    >>> rn.romanNumeralAlone
    'iv'

    `music21 roman.RomanNumeral.primaryFigure` removes the secondary Roman numeral,
    and so is similar to `no_secondary`.
    >>> rn.primaryFigure
    '#ivo65[add#6]'

    Clearly this function supports corpus-level analysis.
    For a quick example, see `test_chord_function` in the unittests.
    """

    if isinstance(rn, str):
        rn = roman.RomanNumeral(rn)

    if haupt_function or full_function:
        return harmonicFunction.figureToFunction(rn,
                                                 simplified=haupt_function
                                                 )

    splits = rn.primaryFigure.split("[")
    working_string = splits[0]

    other_alt = []

    if len(splits) > 1:  # may be one or more [noX][addY] ...
        other_alt = [x[:-1] for x in splits[1:]]

    if no_root_alt:
        if rn.frontAlterationString:
            assert working_string[0] in ("#", "b")
            working_string = working_string[1:]

    if no_quality_alt:
        for quality in ["o", "ø", "+"]:  # simple, only used in that position
            working_string = working_string.replace(quality, "")

    if no_inv:
        if rn.figuresWritten:
            replace = ""
            if rn.isSeventh() or rn.containsSeventh():
                replace = "7"  # quality handled elsewhere
            if rn.figuresWritten in working_string:
                working_string = working_string.replace(rn.figuresWritten, replace)
            else:  # some complex exceptions. Seemingly only Aug6ths.
                print(f"Warning: {rn.figuresWritten} not in {rn.primaryFigure}. "
                      f"Returning RN alone: {rn.romanNumeralAlone}")
                working_string = rn.romanNumeralAlone
                # Known issue for some .isAugmentedSixth() cases.
                # E.g., "Fr6" figuresWritten is 43

    if other_alt and not no_other_alt:  # alternatively use `.addedSteps` etc.
        for x in other_alt:
            working_string += f"[{x}]"

    if rn.secondaryRomanNumeral and not no_secondary:  # or split by "/"
        working_string += "/" + rn.secondaryRomanNumeral.figure

    return working_string


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest

    doctest.testmod()
