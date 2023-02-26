"""
NAME:
===============================
Chord Usage (chord_usage.py)


BY:
===============================
Mark Gotham


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


CITATION:
===============================
Watch this space!


ABOUT:
===============================
Retrieve usage stats for all chord types in a corpus.

Also includes functionality for simplifying harmonies and
corresponding assessment of that data.

Specifically:
- 2x Corpora: lieder (OpenScore LiederCorpus); Beethoven (Beethoven)
- major and minor handled separately
- expressed as percentages


TODO:
===============================

Currently limited to single chord. Expand to progressions

"""

import json
from . import get_distributions
from .chord_features import simplify_chord
from .. import get_corpus_files, CORPUS_FOLDER, CODE_FOLDER, write_json

RESOURCES_FOLDER = CODE_FOLDER / "Resources"


# ------------------------------------------------------------------------------

# Code

def get_usage(
        base_path: str = CORPUS_FOLDER / "OpenScore-LiederCorpus",
        weight_by_length: bool = True,
        sort_dict: bool = True,
        percentages: bool = True,
        this_mode: str = "major",
        plateau: float = 0.01,
        simplify: bool = False
) -> dict:
    """
    For a given corpus, iterate over all figures and return 
    a dict for each chord and its usage.
    
    Choose a mode (this_mode = "major", "minor", "both").
    It usually makes sense to separate by mode 
    (e.g., usage of "i" varies significantly between major and minor).
    
    Optionally set a plateau for minimum usage, ignoring one-offs.
    By default, this value is 0.01 (i.e., very low).
    Set at a higher value to cut off at that level. 
    This applies to both percentage and otherwise.
    E.g., 0.01 for low percentages or
    1 for single quarterLength usage (or equivalent).
    """

    if this_mode not in ["major", "minor", "both"]:
        raise ValueError('Invalid mode: chose one of "major", "minor", "both".')

    files = get_corpus_files(base_path, file_name="slices_with_analysis.tsv")

    working_dict = {}

    for path_to_file in files:
        try:
            data = get_distributions.DistributionsFromTabular(path_to_file).profiles_by_chord
            print(".")
        except:
            print(f"Cannot load {path_to_file}")
            continue

        for d in data:
            # Mode
            if this_mode == "major" and not d["key"][0].isupper():  # Major e.g. "C", "Ab".
                continue
            elif this_mode == "minor" and d["key"][0].isupper():  # Should be lower e.g. ab".
                continue

            # Init new entries
            if d["chord"] not in working_dict:
                working_dict[d["chord"]] = 0

                # Length or count:
            if weight_by_length:
                working_dict[d["chord"]] += d["quarter length"]
            else:
                working_dict[d["chord"]] += 1

    if sort_dict:
        working_dict = sort_this_dict(working_dict)

    if percentages:
        working_dict = dict_in_percentages(working_dict)

    if plateau:

        pop_keys = []
        for key in list(working_dict.keys()):
            if working_dict[key] < plateau:
                pop_keys.append(key)

        for key in pop_keys:  # iterate all as it might not be sorted
            working_dict.pop(key)

    if simplify:
        working_dict = simplify_or_consolidate_usage_dict(working_dict)

    return working_dict


def simplify_or_consolidate_usage_dict(
        file_name: str,
        simplify_not_consolidate: bool = True,
        major_not_minor: bool = True,
        sort_dict: bool = True,
        percentages: bool = True,
        write: bool = True
) -> dict:
    """
    For a full usage dict (with separate entries for each exact figure),
    return a dict which either
    1) simplifies the total syntax range, joining items together figures according to
    the types of simplification set out in `simplify_chord` (reduction _to_ c.10% of total), or
    2) consolidates duplicate entries like V42 ad V2 as defined at `careful_consolidate`
    (reduction _by_ c.10% of total),
    """
    assert (file_name.endswith("_raw.json"))
    raw_path = RESOURCES_FOLDER / "chord_usage" / file_name
    f = open(raw_path)
    this_usage_dict = json.load(f)

    working_dict = {}

    for k, v in this_usage_dict.items():

        if simplify_not_consolidate:
            new_key = simplify_chord(k)  # TODO simplification options here.
        else:
            new_key = careful_consolidate(k, major_not_minor=major_not_minor)

        if new_key not in working_dict:
            working_dict[new_key] = 0  # init
        working_dict[new_key] += v  # in any case

    if sort_dict:
        working_dict = sort_this_dict(working_dict)

    if percentages:
        working_dict = dict_in_percentages(working_dict)

    if write:
        if simplify_not_consolidate:
            out_file_name = file_name.replace("_raw.json", "_simple.json")
        else:
            out_file_name = file_name.replace("_raw.json", ".json")  # as the VoR
        write_json(working_dict, RESOURCES_FOLDER / "chord_usage" / out_file_name)

    return working_dict


def sort_this_dict(
        working_dict
) -> dict:
    """
    Sorts a dict by the values, high to low.
    """
    return {k: v for k, v in sorted(working_dict.items(),
                                    key=lambda item: item[1],
                                    reverse=True)}


def dict_in_percentages(
        working_dict
) -> dict:
    """
    Convert a dict into expression the values as percentages of the total.
    """
    total = sum([working_dict[x] for x in working_dict])
    for x in working_dict:
        working_dict[x] *= (100 / total)
        working_dict[x] = round(working_dict[x], 3)

    return working_dict


def raw_usage_maj_min_one_corpus(
        corpus: str = "OpenScore-LiederCorpus",
        write: bool = True
) -> None:
    """
    Retrieve the major and minor usage of one corpus and

    Args:
        corpus: which corpus (must be a child directory of "Corpus")
        write (bool): optionally write the data (x2) to the "Resources" folder.

    Returns: None

    """

    for this_mode in ["major", "minor"]:

        data = get_usage(CORPUS_FOLDER / corpus,
                         this_mode=this_mode,
                         # plateau=0.01,
                         simplify=False)
        json_path = RESOURCES_FOLDER / "chord_usage" / f"{this_mode}_{corpus}_raw.json"

        if write:
            write_json(data, json_path)


def careful_consolidate(
        original_string: str,
        check_pitches: bool = True,
        major_not_minor: bool = True,
) -> str:
    """
    There are multiple legal ways of expressing the same chord.
    Notably, this includes:
    - compressed versus verbose figures: e.g., V642, V42, V2 are equivalent.
    - "cautionary" accidentals: e.g., #viio (typical in DCML) and viio (used elsewhere).
    This function seeks to rationalise and consolidate as many of those cases as possible
    by compressing these cases,
    TODO: promote this higher up. Remove all "42" from the corpus.

    Returns: that same str rationalised.

    Args:
        original_string (str): The string you start with (and also return in the case of no swap)
        check_pitches (bool): check that the implied pitches are the same before and after.
        major_not_minor (bool): Either / or. Required for re-creating the Roman Numeral.
    """

    if major_not_minor:
        tonality = "C"
    else:
        tonality = "a"

    replace_pairs = {
        "642": "2",
        "42": "2",
        "653": "65",
        "753": "7",
        # TODO full list. e.g., DT uses "V6/5"
    }

    new_string = None

    for key, value in replace_pairs.items():
        if key in original_string:
            new_string = original_string.replace(key, value)

    replace_pairs_minor = {
        "#vii": "vii",
        "bVI": "VI"
    }

    if new_string is None:
        new_string = original_string

    if not major_not_minor:  # TODO handles all relevant cases of multiple replacements?
        for key, value in replace_pairs_minor.items():
            if key in original_string:
                new_string = new_string.replace(key, value)

    if check_pitches:
        from music21 import roman
        before_pitches = roman.RomanNumeral(original_string, tonality).pitches
        after_pitches = roman.RomanNumeral(new_string, tonality).pitches
        if before_pitches == after_pitches:
            return new_string
        else:
            print(f"Swap from {original_string} to {new_string} failed. Returning original.")
    else:
        return new_string


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--get_usage", action="store_true")
    parser.add_argument("--simplify", action="store_true")
    parser.add_argument("--consolidate", action="store_true")
    parser.add_argument("--corpus", type=str,
                        required=False,
                        default="OpenScore-LiederCorpus",
                        help="Local base_path within the WiR corpus.")

    args = parser.parse_args()

    if args.get_usage:
        raw_usage_maj_min_one_corpus(corpus=args.corpus)

    elif args.simplify:
        for this_mode in ["major", "minor"]:
            out_data = simplify_or_consolidate_usage_dict(f"{this_mode}_{args.corpus}_raw.json",
                                                          simplify_not_consolidate=True,
                                                          major_not_minor=(this_mode == "major"))

    elif args.consolidate:
        for this_mode in ["major", "minor"]:
            out_data = simplify_or_consolidate_usage_dict(f"{this_mode}_{args.corpus}.json",
                                                          simplify_not_consolidate=False,
                                                          major_not_minor=(this_mode == "major"))

    else:
        parser.print_help()
