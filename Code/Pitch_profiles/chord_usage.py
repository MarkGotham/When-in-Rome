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


# ------------------------------------------------------------------------------

# Code

def get_usage(base_path: str = CORPUS_FOLDER / "OpenScore-LiederCorpus",
              weight_by_length: bool = True,
              sort_dict: bool = True,
              percentages: bool = True,
              this_mode: str = "major",
              plateau: float = 0.01,
              simplify: bool = False
              ):
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
        working_dict = simplify_usage_dict(working_dict)

    return working_dict


def simplify_usage_dict(this_usage_dict,
                        sort_dict: bool = True,
                        percentages: bool = True):
    """
    For a full usage dict (with separate entries for each exact figure),
    return a simplified form, joining items together figures according to 
    the types of simplification set out in simplify_chord.
    
    a dict for each chord and its usage.
    """
    working_dict = {}
    for k, v in this_usage_dict.items():
        simpler_key = simplify_chord(k)  # TODO simplification options here.
        if simpler_key not in working_dict:
            working_dict[simpler_key] = 0  # init
        working_dict[simpler_key] += v  # in any case

    if sort_dict:
        working_dict = sort_this_dict(working_dict)

    if percentages:
        working_dict = dict_in_percentages(working_dict)

    return working_dict


def sort_this_dict(working_dict):
    """
    Sorts a dict by the values, high to low.
    """
    return {k: v for k, v in sorted(working_dict.items(),
                                    key=lambda item: item[1],
                                    reverse=True)}


def dict_in_percentages(working_dict):
    """
    Convert a dict into expression the values as percentages of the total.
    """
    total = sum([working_dict[x] for x in working_dict])
    for x in working_dict:
        working_dict[x] *= (100 / total)
        working_dict[x] = round(working_dict[x], 3)

    return working_dict


def all_formats_one_corpus(corpus: str = "OpenScore-LiederCorpus",
                           write: bool = True):

    for this_mode in ["major", "minor"]:

        data = get_usage(CORPUS_FOLDER / corpus,
                         this_mode=this_mode,
                         # plateau=0.01,
                         simplify=False)
        json_path = CODE_FOLDER / "Resources" / f"{this_mode}_{corpus}.json"

        if write:
            write_json(data, json_path)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--get_usage", action="store_true")
    parser.add_argument("--simplify", type=bool, required=False, default=False)
    parser.add_argument("--corpus", type=str,
                        required=False,
                        default="OpenScore-LiederCorpus",
                        help="Local base_path within the WiR corpus.")

    args = parser.parse_args()

    if args.get_usage:
        all_formats_one_corpus(corpus=args.corpus)
    else:
        parser.print_help()
