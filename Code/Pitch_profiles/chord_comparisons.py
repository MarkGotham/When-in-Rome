"""
===============================
Chord Comparisons (chord_comparisons.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


Citation:
===============================

Gotham et al. "What if the 'When' Implies the 'What'?". ISMIR, 2021 (forthcoming)


ABOUT:
===============================

Functions for
comparing the pitch class profile of a source (e.g. passages of a symbolic score) to a prototype,
and for
building those prototype profiles from a user-defined corpus of sources.

"""

import chord_profiles
import get_distributions
import normalisation_comparison

import os


# ------------------------------------------------------------------------------

chord_types = ['diminished triad',
               'minor triad',
               'major triad',
               'augmented triad',
               'diminished seventh',
               'half-diminished seventh',
               'minor seventh',
               'dominant seventh',
               'major seventh']
# TODO consider more chords types: no 3rd, no 5th etc.


# ------------------------------------------------------------------------------

def best_fit_chord(usage_profile: list,
                   reference_profile_dict: dict = chord_profiles.binary,
                   reference_chord_names: list = chord_types,
                   comp_type='Manhattan',
                   return_in_chord_PCs_only: bool = False,
                   return_score: bool = False   ):
    """Find the best fit chord for a given usage in practice."""

    best_fit_name = 'Fake'  # Fake init, immediately replaced
    least_distance = 10  # also fake init
    best_fit_rotation = None
    for name in reference_chord_names:
        for i in range(12):
            profile = rotate(reference_profile_dict[name], i)
            # Compare real data (score or audio) with reference
            match = normalisation_comparison.compare_two_profiles(usage_profile,
                                                                  profile,
                                                                  comparison_type=comp_type)
            if match < least_distance:
                least_distance = match
                best_fit_name = name
                best_fit_rotation = i

    if return_in_chord_PCs_only:
        profile = rotate(chord_profiles.binary[best_fit_name], best_fit_rotation)
        return profile_to_PC_list(profile)
    return best_fit_name, best_fit_rotation


def profile_to_PC_list(profile: list):
    """
    Convert a profile into a list of the indexes used
    E.g., from a PCP to a (shorter) list of PCs.
    """
    return [i for i in range(len(profile)) if profile[i] > 0]


def compare_one_source(path_to_file: str,
                       return_percent: bool = False,
                       log_out_of_scope: bool = False,
                       reference_profile_dict: dict = chord_profiles.binary):
    """
    Compares all chord segments of a single file with
    reference profiles (user-defined: default is the binary profiles).
    Returns either the number of correct guesses and the total chords compared,
    or the same expressed as a percentage (if return_percent is set to True)
    """

    data = get_distributions.DistributionsFromTabular(path_to_file)
    data.get_distributions_by_chord()

    correct = 0
    incorrect = 0
    out_of_scope = 0
    total = len(data.distributions_by_chord)

    for d in data.distributions_by_chord:

        # Human analysis
        analysis_pcp, analysis_root = roman_to_pcp(d['chord'], d['key'],
                                                   root_0=True,
                                                   return_root=True)

        analysis_name = get_chord_name_from_binary_pcp(analysis_pcp)

        # Check within scope
        if analysis_name is None:
            out_of_scope += 1
            if log_out_of_scope:
                print('Out of scope chord: ', d['chord'])
            continue

        best_fit_name, best_fit_rotation = best_fit_chord(d['distribution'],
                                                          reference_profile_dict,
                                                          chord_types)

        match_success = ((best_fit_name, best_fit_rotation) == (analysis_name, analysis_root))

        if match_success:
            correct += 1
        else:
            incorrect += 1

    assert correct + incorrect + out_of_scope == total

    if return_percent:
        return final_percent_score(correct, incorrect, out_of_scope, total)
    else:
        return correct, incorrect, out_of_scope, total


def corpus_chord_comparison(root_path: str = '.',
                            reference_profile_dict: dict = chord_profiles.binary):
    """
    Run on all relevant files in the corpus.
    """

    paths = []

    for dpath, dname, fname in os.walk(root_path):
        for name in fname:
            if name.lower() == 'slices_with_analysis.tsv':
                full_path = str(os.path.join(dpath, name))
                paths.append(full_path)

    data = []

    for path_to_file in paths:
        data.append(compare_one_source(path_to_file,
                                       reference_profile_dict=reference_profile_dict))

    c_i_o = list(list(zip(*data)))
    [correct, incorrect, out_of_scope, total] = [sum(x) for x in c_i_o]

    percent = final_percent_score(correct, incorrect, out_of_scope, total)
    return correct, incorrect, out_of_scope, total, percent


# ------------------------------------------------------------------------------

def build_profiles_from_corpus(base_path: str,
                               log_out_of_scope: bool = False):
    """
    Builds a profile dict for the common triads and sevenths from a human-analysed corpus.

    Specifically, sums actual PCPs for sections according to theoretical PCP of each chord.
    """

    files = get_files(base_path)

    # Init with the 9 common chords x 12 transpositions
    new_dict = {}
    for chord_type in chord_types:
        new_dict[chord_type] = [0] * 12

    for path_to_file in files:
        data = get_distributions.DistributionsFromTabular(path_to_file)
        data.get_distributions_by_chord()

        for d in data.distributions_by_chord:
            analysis_pcp, root_pc = roman_to_pcp(d['chord'], d['key'],
                                                 root_0=True,
                                                 return_root=True)  # NB: rotation this time

            # Check analysis within scope
            analysis_name = get_chord_name_from_binary_pcp(analysis_pcp)
            if analysis_name:
                rotated_data_pcp = rotate(d['distribution'], - root_pc)
                for pc in range(12):
                    new_dict[analysis_name][pc] += rotated_data_pcp[pc]
            else:
                if log_out_of_scope:
                    print('Out of scope chord: ', d['chord'])

    new_dict = round_dict(new_dict)
    return new_dict


# ------------------------------------------------------------------------------

def get_chord_name_from_binary_pcp(pcp_list: list):
    """
    Reverse mapping from a binary pcp to chord name e.g.
    >>> get_chord_name_from_binary_pcp([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
    'diminished triad'
    """
    if len(pcp_list) != 12:
        raise ValueError('Invalid PCP: must be a 12-element list.')
    binary_profile = chord_profiles.binary
    for chord_type in chord_types:
        if binary_profile[chord_type] == pcp_list:
            return chord_type
    return None


def pitch_class_list_to_profile(pitch_class_list: list):
    """
    Convert a pitch class set or normal order to a pcp.
    >>> pitch_class_list_to_profile([0, 3, 6])
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]
    """
    profile = [0] * 12
    for pc in pitch_class_list:
        profile[pc] += 1
    return profile


def rotate(profile_list: list,
           i: int):
    """
    Rotate of a profile_list by i steps forward (sic).
    >>> rotate([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0], 3)
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
    """
    return profile_list[-i:] + profile_list[:-i]


def round_dict(dict_of_profiles: dict,
               round_places: int = 3):
    """
    Round every element of a dict.
    """
    for x in dict_of_profiles:
        for i in range(12):
            dict_of_profiles[x][i] = round(dict_of_profiles[x][i], round_places)

    return dict_of_profiles


def normalise_dict(dict_of_profiles: dict,
                   norm_type: str = 'l1'):
    """
    Normalise a dict by any of the types supported in normalisation_comparison.
    """
    for x in dict_of_profiles:
        dict_of_profiles[x] = normalisation_comparison.normalise(dict_of_profiles[x],
                                                                 normalisation_type=norm_type)

    return dict_of_profiles


# ------------------------------------------------------------------------------


def get_files(root_path: str = '../../Corpus/OpenScore-LiederCorpus/',
              file_name: str = 'slices_with_analysis.tsv'):
    paths = []
    for dpath, dname, fname in os.walk(root_path):
        for name in fname:
            if name == file_name:
                paths.append(str(os.path.join(dpath, name)))
    return paths


def final_percent_score(correct, incorrect, out_of_scope, total):
    """
    Percentage of correct from those tested (correct + incorrect), ignoring out of scope.
    """
    assert correct + incorrect + out_of_scope == total
    return round(100 * correct / (total - out_of_scope), 3)


def roman_to_pcp(figure: str,
                 key: str,
                 root_0: bool = False,
                 return_root: bool = False):
    """
    Converts a figure and key (e.g. 'ii' , 'Db')
    via a RomanNumeral object into a pitch classes profile (PCP).
    >>> roman_to_pcp('ii', 'Db')
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]

    Optionally, rotates the PCP to situate the root at position 0
    >>> roman_to_pcp('ii', 'Db', root_0=True)
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]

    Optionally, rotates the PCP to situate the root at position 0
    >>> roman_to_pcp('ii', 'Db', root_0=True)
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]

    Optionally, also return the root
    >>> roman_to_pcp('ii', 'Db', root_0=True, return_root=True)
    ([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], 3)

    Note: requires music21.
    """
    from music21 import roman
    rn = roman.RomanNumeral(figure, key)
    pitch_classes = [x.pitch.pitchClass for x in rn]  # e.g. [2, 5, 9]
    pcp = pitch_class_list_to_profile(pitch_classes)  # pitch classes profile [0, 0, 1 ...
    root_pc = rn.root().pitchClass

    if root_0:
        pcp = rotate(pcp, - root_pc)  # sic -

    if return_root:
        return pcp, root_pc
    else:
        return pcp


# ------------------------------------------------------------------------------

# Tests

def check_binary_profiles():
    """
    Create the binary profiles dict from scratch (normal forms) and check they match.
    """

    normal_forms_dict = {
        "diminished triad": [0, 3, 6],
        "minor triad": [0, 3, 7],
        "major triad": [0, 4, 7],
        "augmented triad": [0, 4, 8],
        "diminished seventh": [0, 3, 6, 9],
        "half-diminished seventh": [0, 3, 6, 10],
        "minor seventh": [0, 3, 7, 10],
        "dominant seventh": [0, 4, 7, 10],
        "major seventh": [0, 4, 7, 11],
    }

    test_dict = {}
    for norm in normal_forms_dict:
        pcp = pitch_class_list_to_profile(normal_forms_dict[norm])
        test_dict[norm] = pcp

    assert test_dict == chord_profiles.binary


def test_corpus_build():
    """
    Run the build process on Schubert's Winterreise and check nothing's changed
    (ie, it matches the values in chord_profiles).
    """
    base_path = '../../Corpus/OpenScore-LiederCorpus/'
    base_path += 'Schubert,_Franz/Winterreise,_D.911/'
    build = build_profiles_from_corpus(base_path)
    assert build == chord_profiles.winterreise


def test_corpus_comparison():
    """
    Run the comparison process for
    Schubert's Winterreise (source) against
    profiles built from the  full lieder dataset (reference),
    and check nothing's changed.
    """
    base_path = '../../Corpus/OpenScore-LiederCorpus/'
    base_path += 'Schubert,_Franz/Winterreise,_D.911/'
    comps = corpus_chord_comparison(base_path, reference_profile_dict=chord_profiles.lieder_sum)
    assert comps == (2013, 546, 96, 2655, 78.664)


def test_normalisation():
    """
    Test normalisation of dicts and match to existing collections.
    """
    for source_name in ['beethoven', 'lieder', 'winterreise']:
        source = getattr(chord_profiles, source_name)
        norm_source = normalise_dict(source, 'l1')
        assert norm_source == getattr(chord_profiles, source_name + '_sum')
        for key in norm_source:
            sum_source = sum(source[key])
            assert round(sum_source, 2) == 1


def run_tests():
    check_binary_profiles()
    test_corpus_build()
    test_corpus_comparison()
    test_normalisation()


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    run_tests()
