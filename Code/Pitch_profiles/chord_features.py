"""
===============================
Chord Features (chord_features.py)
===============================

Mark Gotham, 2022


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
e.g. for categorisation tasks in machine learning.


TODO: Currently limited to single chord. expand to – chord progressions

"""
from music21.analysis import harmonicFunction as hf

from . import chord_comparisons
from . import normalisation_comparison
from ..Resources import chord_profiles, chord_usage_stats

from music21 import analysis, roman

from typing import Union, Optional


# ------------------------------------------------------------------------------

class SingleChordFeatures:
    '''
    Extract features of 
    single chords, 
    and 
    chord-source comparisons.
    e.g. for categorisation in machine learning.

    Input arguments are:

    * Roman Numeral (use roman.RomanNumeral object where possible; otherwise, str for figure only,
    * sourceUsageProfile: list,
    * returnOneHot: bool = True,
    * comp_type: str = 'L1'

    All vectors are provided in the form of a list of numerical value(s).
    There may be one or more, and entries may be ints or float. 

    To support machine learning, each function has the option of returning 
    a 'one hot encoding' whenever the features are independent classes
    so that the model can learn specific weights.
    This is a vector of one 1 and otherwise all 0s.
    For example, for triad types, the one hot encodings are:
    ['100', '010', '001'] for ['major', 'minor', 'other'], respectively.
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
    '''

    def __init__(self,
                 rn: Union[roman.RomanNumeral, str],
                 sourceUsageProfile: list,
                 returnOneHot: bool = True,
                 comparison_type: str = 'L1'):

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

        self.thisFn = str(analysis.harmonicFunction.romanToFunction(self.rn))
        self.hauptFunctionVector = self.getHauptFunctionVector()
        self.functionVector = self.getFunctionVector()

        self.chosenChordPCPVector = self.getChosenChordPCPVector()
        self.bestFitChordPCPVector = [0] * 12
        self.distanceToChosenChordVector = [0]
        self.distanceToBestFitChordPCPVector = [0]
        self.chordTypeMatchVector = [0]
        self.chordRotationMatchVector = [0]

        self.evaluateBestFit()

        self.fullChordCommonnessVector = self.getFullChordCommonnessVector()
        self.simplifiedChordCommonnessVector = self.getSimplifiedChordCommonnessVector()

    def getBasicChordFeatures(self):
        '''
        Retrieve basic chord features.

        Mostly open to the one hot format:
        - chordQualityVector: 4 triads, 4 sevenths, None/Other; dimensions = 9; discrete = True
        - thirdTypeVector: m3, M3, None/other; dimensions = 3; discrete = True
        - fifthTypeVector: d5, P5, A5, None/other; dimensions = 5; discrete = True
        - seventhTypeVector: d7, m7, M7, None/other; dimensions = 4; discrete = True
        - rootPitchClassVector: 0-11; dimensions = 12; discrete = True

        Multi-hot (too many types for one-hot to be really practical)
        TODO intervalVector: dimensions = 6; discrete = True

        '''

        # Alternatively if not self.rn.containsTriad (includes sevenths) and
        # third = (r.third.pitchClass - r.root().pitchClass) % 12
        # etc

        commonName = self.rn.commonName

        chordData = {'diminished triad': ['m3', 'd5', None],
                     'minor triad': ['m3', 'P5', None],
                     'major triad': ['M3', 'P5', None],
                     'augmented triad': ['M3', 'A5', None],
                     'half-diminished seventh chord': ['m3', 'd5', 'm7'],
                     'diminished seventh chord': ['m3', 'd5', 'd7'],
                     'minor seventh chord': ['m3', 'd5', 'm7'],
                     'dominant seventh chord': ['M3', 'P5', 'm7'],
                     'major seventh chord': ['M3', 'P5', 'm7'],
                     }
        # TODO consider any special cases, e.g. if 'augmented sixth' in name; if incomplete:

        chordTypes = list(chordData.keys())
        thirdTypes = ('m3', 'M3')
        fifthTypes = ('d5', 'P5', 'A5')
        seventhTypes = ('d7', 'm7', 'M7')

        # NB _sharedIndexMethod handles not in list
        self.chordQualityVector = self._sharedIndexMethod(chordTypes, commonName)
        if commonName in chordData:
            thirdFifthSeventh = chordData[commonName]
        else:
            thirdFifthSeventh = ['Fake', 'Fake', 'Fake']
        self.thirdTypeVector = self._sharedIndexMethod(thirdTypes, thirdFifthSeventh[0])
        self.fifthTypeVector = self._sharedIndexMethod(fifthTypes, thirdFifthSeventh[1])
        self.seventhTypeVector = self._sharedIndexMethod(seventhTypes, thirdFifthSeventh[2])

        self.rootPitchClassVector = self.rn.root().pitchClass  # 0-11
        if self.returnOneHot:
            emptyList = [0] * 12
            emptyList[self.rootPitchClassVector] = 1
            # print('***' + str(emptyList))
            self.rootPitchClassVector = emptyList

    def getHauptFunctionVector(self):
        '''
        Mapping of
        'T', 't', 'S', 's', 'D', 'd', and a final entry for None/Other
        to either an index position in that list, e.g. returning [3]
        or if returnOneHot, then in the format [0, 0, 0, 1, ...

        self.hauptFunctionVector
        dimensions = 7
        discrete = True
        '''

        thisHauptFn = self.thisFn[0]
        hauptFunctionList = ['T', 't', 'S', 's', 'D', 'd']

        return self._sharedIndexMethod(hauptFunctionList, thisHauptFn)

    def getFunctionVector(self):
        '''
        Mapping of the 18 functions 
        'T', 'Tp', 'Tg', 't', 'tP', 'tG', 
        'S', 'Sp', 'Sg', 's', 'sP', 'sG', 
        'D', 'Dp', 'Dg', 'd', 'dP', 'dG',
        and a final entry for None/Other
        to either an index position in that list, e.g. returning [3]
        or if returnOneHot, then in the format [0, 0, 0, 1, 0, 0, 0, ...

        self.functionVector
        dimensions = 19
        discrete = True
        '''

        functionList = [str(x) for x in analysis.harmonicFunction.HarmonicFunction]
        # I.e. 'T', 'Tp', 'Tg', 't', 'tP', 'tG', ...
        return self._sharedIndexMethod(functionList, self.thisFn)

    def _sharedIndexMethod(self, thisList: list, thisItem: Optional[str]):
        '''
        Get the index of an entry in a list,
        or (if self.returnOneHot) then
        a new list with all 0s excepts one 1 for the entry index.

        For an element not in the list, returns an index of N + 1.
        '''
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

    def getChosenChordPCPVector(self, root_0: bool = False):
        '''
        12-element vector, with 1 or 0 for each pitch class in the chord.
        self.chosenChordPCPVector
        dimensions = 12
        discrete = True
        E.g. [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0] for C major

        NOTE:
        - No mapping and no returnOneHot option.
        - Source PCP produced separately by combine_slice_group (get_distributions)
        '''
        return chord_comparisons.roman_to_pcp(self.rn.figure,
                                              self.rn.key,
                                              root_0=root_0,  # ?
                                              return_root=False)

    def evaluateBestFit(self,
                        reference_profile_dict: dict = chord_profiles.binary,
                        ):
        '''
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
        '''

        a, b, c = chord_comparisons.best_fit_chord(self.sourceUsageProfile,
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
        if comparison_type in ['sum', 'manhattan', 'l1']:
            denominator = 2
        elif comparison_type in ['euclidean', 'l2']:
            import math
            denominator = math.sqrt(2)
        else:
            raise ValueError(f'Invalid comparison type')

        self.distanceToChosenChordVector = [self.getDistanceToChosenChord() / denominator]

    def getDistanceToChosenChord(self):
        '''
        self.distanceToChosenChordVector
        dimensions = 1
        discrete = False (continuous)
        '''
        return normalisation_comparison.compare_two_profiles(self.sourceUsageProfile,
                                                             self.chosenChordPCPVector,
                                                             comparison_type=self.comparison_type)

    def getFullChordCommonnessVector(self,
                                     thisDict=chord_usage_stats.lieder_both):
        '''
        How commonly used is this exact chord?
        Calculated as a percentage usage / the top percentage
        so the range is 0-1, with 
        1 for the most commonly used chord, and 
        0 for an entry unseen in the reference corpus.

        self.fullChordCommonnessVector
        dimensions = 1
        discrete = False (continuous)

        '''
        thisKey = self.rn.figure
        return [getCommonPercentage(thisDict, thisKey)]

    def getSimplifiedChordCommonnessVector(self):
        '''
        Same as for getFullChordCommonnessVector, but with the simplified chord.

        self.simplifiedChordCommonnessVector
        dimensions = 1
        discrete = False (continuous)
        '''
        thisDict = chord_usage_stats.usage_dict_simplified
        thisKey = simplify_chord(self.rn.figure)
        return [getCommonPercentage(thisDict, thisKey)]


def getCommonPercentage(thisDict, thisKey):
    '''
    Shared function for 
    getFullChordCommonnessVector, 
    getSimplifiedChordCommonnessVector.
    '''
    try:
        thisPercent = thisDict[thisKey]  # Fails if not in the dict
        maxPercent = list(thisDict.values())[0]
    except KeyError:
        return 0

    return round(thisPercent / maxPercent, 3)


def simplify_chord(rn: Union[roman.RomanNumeral, str],
                   hauptHarmonicFunction: bool = False,
                   fullHarmonicFunction: bool = False,
                   ignoreInversion: bool = False,
                   ignoreRootAlt: bool = False,
                   ignoreOtherAlt: bool = True,
                   ):
    """
    Given a chord (expressed as a roman.RomanNumeral or figure str),
    simplify that chord in one or more ways:

    hauptHarmonicFunction:
        returns the basic function like T, S, D.
        E.g., 'I' becomes 'T'.
        See notes at music21.analysis.harmonicFunction

    fullHarmonicFunction:
        Likewise, but supports Nebenfunktionen, e.g. Tp.
        E.g., 'vi' in a major key becomes 'Tp'.
        Again, see notes at music21.analysis.harmonicFunction

    ignoreInversion:
        E.g., '#ivo65' becomes '#ivo'.

    ignoreRootAlt:
        E.g., '#ivo' becomes 'ivo'.
        (NB: Not usually desirable!)

    ignoreOtherAlt:
        Ignore modifications of and added, removed, or chromatically altered tones.
        So '#ivo[add#6]' becomes '#ivo'.

    These are all settable separately, and so potentially combinable,
    but note that there is a hierarchy here.
    For instance, anything involving the function labels currently makes all the others
    reductant.

    >>> rn = roman.RomanNumeral('#ivo65[add4]/v')
    >>> rn.figure
    '#ivo65[add4]/v'

    >>> rn.primaryFigure
    '#ivo65[add4]'

    >>> rn = roman.RomanNumeral('#ivo65[add4]')
    >>> rn.romanNumeral
    '#iv'

    >>> rn.romanNumeralAlone
    'iv'

    """

    if isinstance(rn, str):
        rn = roman.RomanNumeral(rn)

    if hauptHarmonicFunction or fullHarmonicFunction:
        return hf.romanToFunction(rn, hauptHarmonicFunction=hauptHarmonicFunction)

    if any([ignoreInversion, ignoreRootAlt, ignoreOtherAlt]):
        # TODO fully, separate handling. Make a convenience fx in m21
        # See doc notes above on .romanNumeral, .romanNumeralAlone, etc
        # HOw to handle secondary? rn.primaryFigure - follow m21 conventions
        # ignoreAdded = rn.romanNumeral
        # ignore # vs .figure vs .romanNumeralAlone
        if ignoreRootAlt:
            return rn.romanNumeralAlone
        else:
            if ignoreOtherAlt:  # added etc., but keep root alt
                return rn.romanNumeral
