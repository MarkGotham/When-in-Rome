"""
===============================
Normalisation Comparison (normalisation_comparison.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Static functions common to several modules here.

"""

from typing import List, Union

import numpy as np
import math
import unittest

import key_profiles

# ------------------------------------------------------------------------------

# Basic pitch spelling conversions

# Assume simple spelling in this direction
pitch_name_from_class_dict = {0: 'C',
                              1: 'C#',
                              2: 'D',
                              3: 'Eb',
                              4: 'E',
                              5: 'F',
                              6: 'F#',
                              7: 'G',
                              8: 'Ab',
                              9: 'A',
                              10: 'Bb',
                              11: 'B',
                              }

# Support up to double sharp/flats spelling in this direction:
pitch_class_from_name_dict = {'cbb': 10,
                              'cb': 11,
                              'c': 0,
                              'c#': 1,
                              'c##': 2,

                              'dbb': 0,
                              'db': 1,
                              'd': 2,
                              'd#': 3,
                              'd##': 4,

                              'ebb': 2,
                              'eb': 3,
                              'e': 4,
                              'e#': 5,
                              'e##': 6,

                              'fbb': 3,
                              'fb': 4,
                              'f': 5,
                              'f#': 6,
                              'f##': 7,

                              'gbb': 5,
                              'gb': 6,
                              'g': 7,
                              'g#': 8,
                              'g##': 9,

                              'abb': 7,
                              'ab': 8,
                              'a': 9,
                              'a#': 10,
                              'a##': 11,

                              'bbb': 9,
                              'bb': 10,
                              'b': 11,
                              'b#': 0,
                              'b##': 1,
                              }


def pitch_name_from_class(num: int):
    """
    Returns a pitch name (str) from a pitch class (0-12).
    Note: Always returns the simplest spelling (e.g. C not B#).

    >>> pitch_name_from_class(4)
    'E'

    """
    return pitch_name_from_class_dict[num]


def pitch_class_from_name(pitch_name: str):
    """
    Returns pitch class (0-12) from a pitch name (str).

    >>> pitch_class_from_name('Bb')
    10

    Supports up to double sharps/flats (B## to Fbb)
    and both the 'Bbb' and 'B--' conventions.

    >>> pitch_class_from_name('Bbb')
    9

    >>> pitch_class_from_name('B-')
    10

    Accepts key strings like 'Bb major',
    taking the first part (before the space) for the pitch name.

    >>> pitch_class_from_name('Bb major')
    10

    """
    if ' ' in pitch_name:
        pitch_name = pitch_name.split(' ')[0]
    pitch_name = pitch_name.lower().replace('-', 'b')
    return pitch_class_from_name_dict[pitch_name]


def pc_list_to_distribution(pc_list: List[int]):
    """
    Convert any list of pitch classes (int 0-11)
    to a pitch class distribution with a count (1) for each.

    >>> pc_list_to_distribution([0, 0, 0, 4, 4, 7, 7, 7])
    [3, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 0]

    Raises an error if any list entry is not an int 0-11.
    """
    distribution = [0] * 12
    for pc in pc_list:
        distribution[pc] += 1
    return distribution


# ------------------------------------------------------------------------------

# Files, Imports, Tabular

def importSV(pathToFile: str,
             splitMarker: str = ''):
    """
    Imports TSV file data for further processing.
    """

    if not splitMarker:
        ext = pathToFile.split('.')[-1]
        if ext == 'tsv':
            splitMarker = '\t'
        elif ext == 'csv':
            splitMarker = ','

    with open(pathToFile, 'r') as f:
        data = []
        for row_num, line in enumerate(f):
            values = line.strip().split(splitMarker)
            data.append([v.strip('\"') for v in values])
    f.close()

    return data


def data_by_heading(file_path: str,
                    headings_row: int = 0):
    """
    Imports an SV file from the provided `file_path`
    and converts the data to a directly to list of dicts
    with headers given by the data in the `headings_row`.
    """

    table = importSV(file_path)

    headings = table[headings_row]
    out_list = []
    for entry in table[headings_row + 1:]:
        data = {}
        for idx, col in enumerate(entry):
            data[headings[idx]] = col
        out_list.append(data)
    return out_list


# ------------------------------------------------------------------------------

# Numeracy

def normalise(distribution: list,
              normalisation_type: str = 'Euclidean',
              round_output: bool = True,
              round_places: int = 3):
    """
    Normalise usage profiles in standard ways by setting argument `normalisation_type` as:
    - 'Euclidean' or 'l2': normalise to a unit sphere in N-dimensional space;
    - 'Sum', 'Manhattan', or 'l1': divide each value by the total across the distribution;
    - 'Max', 'Maximum' or 'infinity': divide each value by the largest (the most used position);

    These strings are not case-sensitive (unaffected by presence/absence of initial caps etc).

    Optionally, also round values (round_output=True, default)
    to N decimal places (set by round_places, default=3).
    """

    max_use = max(distribution)
    if max_use == 0:
        return distribution  # All 0s: don't divide by 0 (or indeed do anything!)

    normalisation_type = normalisation_type.lower()

    if normalisation_type in ['euclidean', 'l2']:
        val = math.sqrt(sum([x ** 2 for x in distribution]))

    elif normalisation_type in ['sum', 'manhattan', 'l1']:
        val = sum(distribution)

    elif normalisation_type in ['max', 'maximum', 'infinity']:
        val = max_use

    else:
        raise ValueError('Invalid normalisation_type')

    norm_dist = [(x / val) for x in distribution]

    if round_output:
        return [round(x, round_places) for x in norm_dist]
    else:
        return norm_dist


def check_length_match(x: list,
                       y: list):
    """
    Simple checks that two lists are of the same length.
    If so, returns the length of the list; if not, raises an error.

    >>> check_length_match([1, 2], [2, 1])
    2
    """
    ln1 = len(x)
    ln2 = len(y)
    if ln2 != ln1:
        raise ValueError(f'Lengths (currently {ln1} and {ln2}) must match')
    else:
        return ln1


def manhattan_distance(x: list,
                       y: list):
    """
    The l1 aka 'Manhattan' distance between two points in N dimensional space.

    List length check and normalisation included.
    """
    check_length_match(x, y)
    x = normalise(x, 'l1')
    y = normalise(y, 'l1')
    return sum([abs(x[n] - y[n]) for n in range(len(x))])


def euclidean_distance(x: list,
                       y: list):
    """
    The Euclidean distance between two points
    is the length of the line segment connecting them in N dimensional space and
    is given by the Pythagorean formula.

    List length check and normalisation included.
    """
    check_length_match(x, y)
    x = normalise(x, 'l2')
    y = normalise(y, 'l2')
    return np.sqrt(sum([(x[n] - y[n]) ** 2 for n in range(len(x))]))


# ------------------------------------------------------------------------------

# Comparisons

def compare_two_profiles(data1: list,  # e.g. source
                         data2: list,  # e.g. reference
                         comparison_type: str = 'Euclidean',
                         round_places: int = 3):
    """
    Compares two distributions such as a
    source usage profile (from score or audio)
    with a reference prototype.

    This function requires the two distributions to be of equal length
    (e.g. both 12 units in length for pitch class profiles).

    The comparison options are the same as for normalisation (l1, l2, etc).
    """

    check_length_match(data1, data2)

    comparison_type = comparison_type.lower()

    if comparison_type in ['sum', 'manhattan', 'l1']:
        comp = manhattan_distance(data1, data2)

    elif comparison_type in ['euclidean', 'l2']:
        comp = euclidean_distance(data1, data2)

    else:
        raise ValueError('Invalid comparison_type.')

    return round(comp, round_places)


def compare_all_rotations(source,
                          reference: dict = key_profiles.QuinnWhite,
                          comparison_type: str = 'Euclidean',
                          mode: str = 'major'):
    """
    Runs comparisons for rotations of a source distribution against a reference.
    to get match evaluations for all 12 either major or minor keys.
    (See best_key for handling of both with this function.)

    e.g.
    first rotation: [1, 0, 0 ... ]
    second rotation: [0, 1, 0 ... ]
    etc.

    Prototype distributions usually assume transposition equivalence,
    so this typically means comparing those rotations of a source against the same profile.

    Quinn and White provide the exception.
    As they have different profiles for each key, the source rotation for each key is
    compared with those key-specific profiles.

    :param source: a distribution in practice
    :param reference: one of the usage profiles from the literature stored in pitch_profiles
    :param comparison_type: 'Euclidean', 'L1', etc.
    :param mode: 'major' or 'minor'
    :return: comparison values for each rotation in a list
    """

    comparisons = []

    for x in range(len(source)):
        rotation = source[x:] + source[:x]
        reference_dist = key_profiles.get_relevant_dist(reference,
                                                        mode=mode,
                                                        tonic=x)
        comp = compare_two_profiles(rotation, reference_dist, comparison_type=comparison_type)
        comparisons.append(comp)

    return comparisons


def best_fit(values,
             lowest_best: bool = True,
             index_also: bool = True):
    """
    Return best fit from a user-defined list of options.
    By default (lowest_best=True),
    seek the lowest value as the comparison metrics assess difference.

    :param values: the list of options.
    :param lowest_best: True if lower values indicate less difference.
    :param index_also: also return the index of the best option. If
    :return: value only, or if index_also is True, then [index, value]
    """

    if lowest_best:
        value = min(values)
    else:
        value = max(values)

    if index_also:
        index = values.index(value)
        return [index, value]
    else:
        return value


def best_major_minor_both(major_options: list,
                          minor_options: list,
                          pc_not_string: bool = False,
                          lowest_best: bool = True):
    """
    Takes in list of distance metrics for major and minor.
    Returns a list of three entries: best major, best minor, best overall.

    If pc_not_string is False (default), then the returned values are strings,
    if True, then they are ints.

    Note: if the best major and minor are exactly even, the minor option is returned.
    This is extremely unlikely in practice. See note and demo in `test_flat_profile`.
    """

    out = []

    best_major = best_fit(major_options)
    majName = best_major[0]  # 0 = index
    if not pc_not_string:
        majName = pitch_name_from_class_dict[majName]  # pc already upper case
        # majName += ' major'
    out.append(majName)

    best_minor = best_fit(minor_options)
    minName = best_minor[0]
    if not pc_not_string:
        minName = pitch_name_from_class_dict[minName].lower()
        # minName += ' minor'
    out.append(minName)

    best = majName
    min_lower = best_major[1] >= best_minor[1]  # 1 = value
    if lowest_best and min_lower:
        best = minName
    if (not lowest_best) and (not min_lower):
        best = minName

    out.append(best)

    return out


def best_key(dist: list,
             model: dict = key_profiles.AlbrechtShanahan,
             comparison_type: str = 'Euclidean'):
    """
    Run the comparisons for both major and minor over a given model usage
    given by the 'model' variable and returns the best key.
    """

    majors = compare_all_rotations(dist, model, comparison_type=comparison_type, mode='major')
    minors = compare_all_rotations(dist, model, comparison_type=comparison_type, mode='minor')
    return best_major_minor_both(majors, minors, pc_not_string=False)[2]


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def test_normalisation(self):
        """
        Test the sum and max normalisation methods with Prince and Schmuckler all beats major.
        """
        d = [0.919356471, 0.114927991, 0.729198287, 0.144709771, 0.697021822, 0.525970522,
             0.214762724, 1, 0.156143546, 0.542952545, 0.142399406, 0.541215555]

        d_l1 = normalise(d, normalisation_type='l1')
        self.assertEqual(round(sum(d_l1), 2), 1)

        d_l2 = normalise(d, normalisation_type='l2')
        self.assertEqual(round(sum([x ** 2 for x in d_l2]), 2), 1)

        d_max = normalise(d, normalisation_type='Max')
        self.assertEqual(max(d_max), 1)

    def test_Euclid(self):

        # No difference (0) between a distribution profile and itself
        d1 = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        d2 = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        d = compare_two_profiles(d1, d2, comparison_type='Euclidean')
        self.assertEqual(d, 0)

        # Max difference (sqrt 2) between two distributions with one distinct pitch each ...
        d1 = [1, 0]
        d2 = [0, 1]
        d = compare_two_profiles(d1, d2, comparison_type='Euclidean')
        self.assertEqual(d, 1.414)

        # ... likewise for complements in any dimension
        d1 = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
        d2 = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
        d = compare_two_profiles(d1, d2, comparison_type='Euclidean')
        self.assertEqual(d, 1.414)

    def test_all_PCPs(self):
        """
        Check best key on all relevant PCP model prototypes
        and both Euclidean and Manhattan comparison types
        with the first segment of Beethoven Sonata no.1 (f minor).
        """
        data = [20.03, 1.0, 0.0, 0.0, 10.36, 15.2, 0.0, 15.2, 13.86, 0.0, 11.52, 0.0]
        for mod in [key_profiles.AardenEssen,
                    key_profiles.AlbrechtShanahan,
                    key_profiles.BellmanBudge,
                    key_profiles.KrumhanslKessler,
                    key_profiles.KrumhanslSchmuckler,
                    key_profiles.PrinceSchumuckler,
                    key_profiles.QuinnWhite,
                    key_profiles.Sapp,
                    key_profiles.TemperleyKostkaPayne,
                    key_profiles.TemperleyDeClerq
                    ]:
            for comp in ['Euclidean', 'Manhattan']:
                k = best_key(data, mod, comparison_type=comp)
                self.assertEqual(k, 'f')

    def test_flat_profile(self):
        """
        For most models (with transposition equivalence) a flat usage profile
        (e.g. silence) does not distinguish between key options.
        It does, however, typically 'prefer' minor keys
        as the reference prototype tends to be 'flatter' (i.e. more chromatic) than major.
        The way this code is set up, it will arbitrarily return the first tested minor key (c).

        As ever, QuinnWhite provides the exception: the profiles are not equivalent by key
        so an actual choice of the flattest profile is returned, here 'bb'.

        Note that if major and minor are exactly even, then best_key returns the minor option.
        This is extremely unlikely in practice apart from these cases of a flat usage profile.
        Even then it is only relevant when the source profile also consists of the same elements
        in major and minor, rearranged in (i.e. Sapp in which both are 2 x '2', 5 x '1', 5 x '0').
        """
        flat_profile = [1.5] * 12
        comps = ['L1', 'L2']
        mods = [(key_profiles.KrumhanslKessler, 'c'),
                (key_profiles.AlbrechtShanahan, 'c'),
                (key_profiles.Sapp, 'c'),
                (key_profiles.TemperleyDeClerq, 'c'),
                (key_profiles.QuinnWhite, 'bb'),
                ]
        for mod in mods:
            for comp in comps:
                res = best_key(flat_profile, model=mod[0], comparison_type=comp)
                self.assertEqual(res, mod[1])


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    unittest.main()
