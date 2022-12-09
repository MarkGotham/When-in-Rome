"""
===============================
Key Profiles (key_profiles.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


Citation:
===============================

Gotham et al. "What if the 'When' Implies the 'What'?". ISMIR, 2021
(see README.md)


ABOUT:
===============================

Provide a convenient way to navigate the pitch class usage profiles (PCP)
from the literature. Those PCPs are defined in the Resources folder
"""
from ..Resources.key_profiles_literature import source_list, QuinnWhite


# ------------------------------------------------------------------------------


def get_relevant_dist(source: dict = QuinnWhite,
                      mode: str = 'major',
                      tonic: int = 0):
    """
    As the sources set out different information in various ways,
    this convenience function attempts (where possible) to return the
    relevant distribution from simple user choices:
    source (one of the above dicts);
    mode (major or minor), and
    optionally tonic (as a pitch class 0-12).

    Tonic is only applicable to QuinnWhite who provide
    separate distributions for each key.
    In all cases, the returned distribution starts with the tonic at the 0th position.

    Clearly this function doesn't seek to cover all the variety in these sources, but
    simply to draw together those that are straightforwardly equivalent.
    """

    mode = mode.lower()

    if mode not in ['major', 'minor']:
        raise ValueError('Invalid mode')

    if source not in source_list:
        raise ValueError('Invalid source.')
    elif source["name"] == "QuinnWhite":  # special case of non-transposition equivalence
        dict_key = mode + str(tonic)
    elif source["name"] == "PrinceSchumuckler":
        dict_key = 'all_beats_' + mode  # ossia 'downbeat', debatable
    elif source["name"] == "TemperleyDeClerq":
        dict_key = 'harmony_' + mode
    elif source["name"] in ["deClerqTemperley", "Vuvan", "VuvanHughes"]:
        raise ValueError('Sorry that source is not really comparable in this way.')
    else:  # i.e. AardenEssen, AlbrechtShanahan, BellmanBudge, KrumhanslKessler,
        # KrumhanslSchmuckler, Sapp, TemperleyKostkaPayne
        dict_key = mode

    return source[dict_key]


def check_sum_1():
    """
    For each source, test that each distinct PCP entry sums to 1.
    If the original doesn't then an additional entry with '_sum' added to the key should.
    """

    for source in source_list:
        for key in source:
            if key in ['literature', 'about']:
                continue
            sum_source = sum(source[key])
            if round(sum_source, 2) != 1:
                sum_source = sum(source[key + '_sum'])
                assert round(sum_source, 2) == 1


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    check_sum_1()
