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
- major and minor handled separately
- expressed as percentages


TODO:
===============================

Currently limited to single chord. Expand to progressions

"""
from fractions import Fraction

from . import get_distributions
from .chord_features import simplify_chord
from .. import get_corpus_files, CORPUS_FOLDER, CODE_FOLDER, load_json, write_json
from pathlib import Path

from music21 import converter, roman

RESOURCES_FOLDER = CODE_FOLDER / "Resources"


# ------------------------------------------------------------------------------

# Code

def get_usage(
        base_path: Path = CORPUS_FOLDER / "OpenScore-LiederCorpus",
        source_analysis_not_tabular: bool = True,
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

    If `source_analysis_not_tabular` then the data is extracted directly from analysis files;
    if false then from the tabluar `slices_with_analysis` files.
    """

    if this_mode not in ["major", "minor", "both"]:
        raise ValueError('Invalid mode: chose one of "major", "minor", "both".')

    working_dict = {}

    if source_analysis_not_tabular:

        files = get_corpus_files(base_path, file_name="analysis.txt")

        for path_to_file in files:
            try:
                data = converter.parse(
                    path_to_file,
                    format="Romantext"
                ).recurse().getElementsByClass(roman.RomanNumeral)
                print(".", len(data))
            except:
                print(f"Cannot load {path_to_file}")
                continue

            for d in data:
                # Mode
                if this_mode == "major" and d.key.mode != "major":
                    continue
                elif this_mode == "minor" and d.key.mode != "minor":
                    continue

                # Init new entries
                if d.figure not in working_dict:
                    working_dict[d.figure] = 0

                # Length or count:
                if weight_by_length:
                    working_dict[d.figure] += d.quarterLength
                else:
                    working_dict[d.figure] += 1

    else:  # tabular
        files = get_corpus_files(base_path, file_name="slices_with_analysis.tsv")

        for path_to_file in files:
            try:
                data = get_distributions.DistributionsFromTabular(path_to_file).profiles_by_chord
                print(".")
            except:
                print(f"Cannot load {path_to_file}")
                continue

            for d in data:
                # Mode
                if this_mode == "major" and d["key"][0].islower():  # Major e.g. "C", "Ab".
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

    # Always convert fractions to floats (for json)
    for k in working_dict:
        if isinstance(working_dict[k], Fraction):
            working_dict[k] = float(working_dict[k])

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

    # Always round
    for x in working_dict:
        working_dict[x] = round(working_dict[x], 3)

    return working_dict


def simplify_or_consolidate_usage_dict(
        file_name: str,
        simplify_not_consolidate: bool = True,
        major_not_minor: bool = True,
        sort_dict: bool = True,
        percentages: bool = True,
        write: bool = True,
        haupt_function: bool = False,
        full_function: bool = False,
        no_root_alt: bool = False,
        no_quality_alt: bool = False,
        no_inv: bool = False,
        no_other_alt: bool = True,  # NB
        no_secondary: bool = True,  # NB
        overwrite: bool = False,
) -> dict:
    """
    For a full usage dict (with separate entries for each exact figure),
    return a dict which either
    1) simplifies the total syntax range, joining items together figures according to
    the types of simplification set out in `simplify_chord` (reduction _to_ c.10% of total), or
    2) consolidates duplicate entries like V42 ad V2 as defined at `careful_consolidate`
    (reduction _by_ c.10% of total),
    """

    if simplify_not_consolidate:
        assert (file_name.endswith(".json"))
    else:  # consolidate
        assert (file_name.endswith("_raw.json"))

    if write:
        if simplify_not_consolidate:
            out_file_name = file_name.replace(".json", "_simple.json")
        else:
            out_file_name = file_name.replace("_raw.json", ".json")  # as the VoR

        out_path = RESOURCES_FOLDER / "chord_usage" / out_file_name

        if out_path.exists() and not overwrite:
            print(f"The path {out_path} exists and overwrite is set to False, skipping.")
            return

    in_path = RESOURCES_FOLDER / "chord_usage" / file_name
    print(f"Processing {in_path}.")

    this_usage_dict = load_json(in_path)

    working_dict = {}

    for k, v in this_usage_dict.items():

        if simplify_not_consolidate:
            new_key = simplify_chord(k,
                                     haupt_function=haupt_function,
                                     full_function=full_function,
                                     no_root_alt=no_root_alt,
                                     no_quality_alt=no_quality_alt,
                                     no_inv=no_inv,
                                     no_other_alt=no_other_alt,
                                     no_secondary=no_secondary)
        else:  # consolidate
            new_key = careful_consolidate(k, major_not_minor=major_not_minor)

        if new_key not in working_dict:
            working_dict[new_key] = 0  # init
        working_dict[new_key] += v  # in any case

    if sort_dict:
        working_dict = sort_this_dict(working_dict)

    if percentages:
        working_dict = dict_in_percentages(working_dict)

    if write:
        write_json(working_dict, out_path)

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
        write: bool = True,
        overwrite: bool = False
) -> None:
    """
    Retrieve the major and minor usage of one corpus and

    Args:
        corpus: which corpus (must be a child directory of "Corpus")
        write (bool): optionally write the data (x2) to the "Resources" folder.
        overwrite (bool): write over an existing file, or skip.

    Returns: None

    """

    for this_mode in ["major", "minor"]:

        json_path = RESOURCES_FOLDER / "chord_usage" / f"{this_mode}_{corpus}_raw.json"

        if json_path.exists() and not overwrite:
            print(f"The path {json_path} exists and overwrite is set to False, skipping.")
            continue

        data = get_usage(CORPUS_FOLDER / corpus,
                         percentages=False,
                         this_mode=this_mode,
                         plateau=2.0,
                         simplify=False)

        if write:
            write_json(data, json_path)


def careful_consolidate(
        original_string: str,
        check_pitches: bool = True,
        major_not_minor: bool = True,
        rn: roman.RomanNumeral | None = None
) -> str:
    """
    There are multiple legal ways of expressing the same chord.
    Notably, this includes the equivalences between:
    1. compressed versus verbose figures (e.g., `V642`, `V6/4/2`, `V42`, `V4/2`, `V2`);
    2. "cautionary" accidentals (e.g., `#viio` typical in DCML and `viio` used elsewhere).

    Case 1 is simple.

    Case 2 applies because the default music21 reading of Romantext
    (used throughout this meta-corpus) handles 6th and 7th degrees in minor
    with the CAUTIONARY setting
    In that context both `#vii` and `vii` account for the same collection of pitches in minor:
    the leading sharp (#) is redundant.
    The same goes for the bVI and VI: the leading flat (b) is redundant.
    Using different symbols for the same chord is fine for most tasks,
    but is not suitable for this and related functions which
    count the relative usage of (actually) different figures.

    This function seeks to rationalise and consolidate as many of those cases as possible
    by compressing these cases.

    (For more on this topic see `music21.roman.Minor67Default` there,
    and the `When-in-Rome/syntax.md` page here,
    noting also that this is _not_ the default behaviour of `roman.RomanNumeral`,
    which uses the QUALITY setting).

    TODO: could perhaps be applied to the source files: e.g, remove all "42" from the corpus.

    Args:
        original_string (str): The string you start with (and also return in the case of no swap)
        check_pitches (bool): check that the implied pitches are the same before and after.
        major_not_minor (bool): Either / or. Required for re-creating the Roman Numeral.
        rn (roman.RomanNumeral): Pass the actual Roman Numeral where availalbe (saves re-creating).

    Returns: that same str, modified where appropriate.
    """

    print(f"Consolidating {original_string} ...")

    if major_not_minor:
        tonality = "C"
    else:
        tonality = "a"

    replace_pairs = {
        "642": "2",
        "6/4/2": "2",
        "4/2": "2",
        "42": "2",

        "643": "43",
        "6/4/3": "43",
        "4/3": "43",

        "653": "65",
        "6/5/3": "65",
        "6/5": "65",

        "753": "7",

        "N63": "bII6",
        "N6": "bII6",
        "N": "bII6",
        "N53": "bII",
        "N5": "bII",
    }

    working_string = original_string

    for key, value in replace_pairs.items():
        if key in original_string:
            working_string = working_string.replace(key, value)

    replace_pairs_minor = {
        "#vii": "vii",
        "bVI": "VI"
    }

    if not major_not_minor:  # TODO handles all relevant cases of multiple replacements?
        for key, value in replace_pairs_minor.items():
            if key in working_string:
                working_string = working_string.replace(key, value)

    if working_string == original_string:
        print("... no change.")
        return original_string

    if check_pitches:
        print(f"... swapping to {working_string} ...")

        if rn:
            before_pitches = [p.name for p in rn.pitches]
            tonality = rn.key
        else:
            before_pitches = roman.RomanNumeral(original_string,
                                                tonality,
                                                sixthMinor=roman.Minor67Default.CAUTIONARY,
                                                seventhMinor=roman.Minor67Default.CAUTIONARY
                                                ).pitches
            before_pitches = [p.name for p in before_pitches]

        after_pitches = [p.name for p in roman.RomanNumeral(working_string, tonality).pitches]
        if before_pitches == after_pitches:
            print("... works.")
            return working_string
        else:
            print(f"... fails. Returning original ({original_string}).")
            print(f"{original_string} in {tonality} = {before_pitches}")
            print(f"{working_string} in {tonality} = {after_pitches}")
            return original_string
    else:
        return working_string


def get_Aug6s(
        corpus_name: str = "OpenScore-LiederCorpus",
        this_mode: str = "major"
) -> dict:
    """
    Usage of augmented chords, separating by category and ignoring inversion.

    Args:
        corpus_name: the usual
    Returns: dict with keys of chord figures and values of the combined usage.
    """

    if this_mode == "major":
        k = "C"
    elif this_mode == "minor":
        k = "a"
    else:
        raise ValueError

    no_inv = simplify_or_consolidate_usage_dict(
            f"{this_mode}_{corpus_name}.json",
            simplify_not_consolidate=True,
            no_inv=True,  # NB
            no_other_alt=True,
            no_secondary=True,
            major_not_minor=(this_mode == "major"),
            write=False)

    short_dict = {}
    for fig in no_inv:
        rn = roman.RomanNumeral(fig, k)
        if rn.isAugmentedSixth(permitAnyInversion=True):
            # Slightly verbose, and should be unnecessary given the filtering above, but safe
            if rn.romanNumeralAlone not in short_dict:
                print("Adding key:", rn.romanNumeralAlone)
                short_dict[rn.romanNumeralAlone] = 0
            short_dict[rn.romanNumeralAlone] += no_inv[fig]

    assert len(short_dict) <= 3

    return short_dict


def get_N6s(
        corpus_name: str = "OpenScore-LiederCorpus",
        this_mode: str = "major",
) -> dict:
    """
    Usage of "Neapolitan" 6 chords, separating by figure _including_ inversion.

    Similar to (cf) `get_Aug6s`, but reading from the
    `<mode>_<corpus>_simple.json` file directly:
    not using `simplify_or_consolidate_usage_dict` because the simplification options are the same.

    Args:
        corpus_name: the usual
    Returns: dict with keys of chord figures and values of the combined usage.
    """

    # Note key probably unnecessary but safer in case of odd spellings
    if this_mode == "major":
        k = "C"
    elif this_mode == "minor":
        k = "a"
    else:
        raise ValueError

    chord_usage_dir = CODE_FOLDER / "Resources" / "chord_usage"
    simple = load_json(chord_usage_dir / f"{this_mode}_{corpus_name}_simple.json")

    pop_list = []
    for fig in simple:
        if not roman.RomanNumeral(fig, k).isNeapolitan(require1stInversion=False):
            pop_list.append(fig)

    for p in pop_list:
        simple.pop(p)

    return simple


# ------------------------------------------------------------------------------

def pc_usage(
        corpus_name: str = "OpenScore-LiederCorpus",
) -> tuple[dict, dict]:
    """
    Usage of distinct pitch class sets in the corpora.
    E.g., `3-11B` stands for all major triads.
    A good way to look at usual configurations and how they are spelt,
    e.g., `Fr43` vs `V7[b5]/V`.

    Args:
        corpus_name: the usual
    Returns: dict with keys of forte classes and values of the associated figures.
    """

    chord_usage_dir = CODE_FOLDER / "Resources" / "chord_usage"
    minor_data = load_json(chord_usage_dir / f"minor_{corpus_name}.json")  # _simple?
    major_data = load_json(chord_usage_dir / f"major_{corpus_name}.json")

    major_pcs = {}
    minor_pcs = {}
    for x in major_data:
        pc = roman.RomanNumeral(x, "C").forteClass
        if pc not in major_pcs:
            major_pcs[pc] = []
        major_pcs[pc] += [x]
    for x in minor_data:
        pc = roman.RomanNumeral(x, "c").forteClass
        if pc not in minor_pcs:
            minor_pcs[pc] = []
        minor_pcs[pc] += [x]

    return major_pcs, minor_pcs


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--all",
                        action="store_true",
                        help="Get raw usage then consolidate and simplify on all WiR corpora.")
    parser.add_argument("--get_usage", action="store_true")
    parser.add_argument("--simplify", action="store_true")
    parser.add_argument("--consolidate", action="store_true")
    parser.add_argument("--corpus", type=str,
                        required=False,
                        default="OpenScore-LiederCorpus",
                        help="Local base_path within the WiR corpus.")

    args = parser.parse_args()

    if args.all:
        for c in [
            "Chamber_Other",
            "Early_Choral",
            "Keyboard_Other",
            "OpenScore-LiederCorpus",
            "Orchestral",
            "Piano_Sonatas",
            "Quartets",
            "Variations_and_Grounds"
        ]:
            raw_usage_maj_min_one_corpus(corpus=c)
            for this_mode in ["major", "minor"]:
                simplify_or_consolidate_usage_dict(
                    f"{this_mode}_{c}_raw.json",  # raw to consolidated
                    simplify_not_consolidate=False,
                    major_not_minor=(this_mode == "major"))
                simplify_or_consolidate_usage_dict(
                    f"{this_mode}_{c}.json",  # consolidated to simple
                    simplify_not_consolidate=True,
                    major_not_minor=(this_mode == "major"))

    elif args.get_usage:
        raw_usage_maj_min_one_corpus(corpus=args.corpus)

    elif args.simplify:
        for this_mode in ["major", "minor"]:
            simplify_or_consolidate_usage_dict(
                f"{this_mode}_{args.corpus}.json",  # consolidated to simple
                simplify_not_consolidate=True,
                major_not_minor=(this_mode == "major"))

    elif args.consolidate:
        for this_mode in ["major", "minor"]:
            simplify_or_consolidate_usage_dict(
                f"{this_mode}_{args.corpus}_raw.json",  # raw to consolidated
                simplify_not_consolidate=False,
                major_not_minor=(this_mode == "major"))

    else:
        parser.print_help()
