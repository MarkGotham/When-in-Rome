# -*- coding: utf-8 -*-
"""
NAME:
===============================
Create Sub-Corpus (create_sub-corpus.py)

BY:
===============================
Mark Gotham

LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/

ABOUT:
===============================
Initialise a local sub-corpus of When in Rome with
metadata pre-defined and stored Resources.metadata.<name>.

Make the directory structure
and populate each end directory (without child directory)
with initial information in the "remote.json" file.

"""

# ------------------------------------------------------------------------------

import json
import shutil
from pathlib import Path

from . import CORPUS_FOLDER, DT_BASE
from .Resources import metadata


# ------------------------------------------------------------------------------

# Specific

def chorales(move_analyses: bool = False) -> None:
    """
    Build the chorales sub-corpus.
    Scores = MG external repo
    Analyses = DT.

    Args:
        move_analyses: If True, move DT analyses from local copy to WiR.
    Returns: None
    """

    source = metadata.chorales
    parent_dir_path = make_parent_dirs(source)
    chorales_DT = DT_BASE / source["analysis_source"]  # "Bach Chorales"

    for riemenschneider_number in range(1, source["items"] + 1):  # range(371)

        md = dict()

        num = str(riemenschneider_number).zfill(3)

        new_dir = parent_dir_path / num
        make_dir(new_dir)

        md[source["item_keys"]] = riemenschneider_number,
        md["remote_score_mxl"] = source["remote_score_mxl"] + num + "/short_score.mxl"
        md["composer"] = get_composer(source)
        r_string = f"riemenschneider{num}.txt"
        md["analysis_source"] = f"{source['analysis_source']}/{r_string}"
        write_json(md, new_dir / "remote.json")

        if move_analyses:
            src = chorales_DT / r_string
            dst = new_dir / "analysis.txt"
            shutil.copy(src, dst)


def madrigals(move_analyses: bool = True) -> None:
    """
    Build the madrgials sub-corpus.
    Scores = music21 external repo
    Analyses = DT.

    Args:
        move_analyses: If True, move DT analyses from local copy to WiR.
    Returns: None
    """

    source = metadata.madrigals
    parent_dir_path = make_parent_dirs(source)
    madrigals_DT = DT_BASE / source["analysis_source"]  # "Bach Chorales"

    for item in source["items"]:

        book = item[0]
        book_dir = parent_dir_path / f"Madrigals_Book_{item[0]}"
        make_dir(book_dir)

        for number in range(1, item[1] + 1):

            num_dir = book_dir / str(number).zfill(2)
            make_dir(num_dir)

            m21_dt_string = f"madrigal.{book}.{number}"

            md = dict()
            md["book"] = book
            md["number"] = number
            md["analysis_source"] = source["analysis_source"] + f"/{m21_dt_string}.txt"
            md["remote_score_mxl"] = source["remote_score_mxl"] + f"{m21_dt_string}.mxl"

            if move_analyses:
                analysis_src = madrigals_DT / f"{m21_dt_string}.txt"
                analysis_dst = num_dir / "analysis.txt"
                shutil.copy(analysis_src, analysis_dst)

            print(book, number)
            print(md)
            write_json(md, num_dir / "remote.json")


def chopin(move_analyses: bool = True) -> None:
    """
    A special case triangulating 3 different external repos.
    DT set
    - incomplete: 31 of 55
    - inconsistent naming (this Hits 26 of 31)
    """

    source = metadata.chopin
    parent_dir_path = make_parent_dirs(source)
    dt = DT_BASE / "Chopin"

    for item in source["items"]:

        md = dict()

        for i in range(len(source["item_keys"])):
            md[source["item_keys"][i]] = item[i]

        # Brown, Mkdir
        brown_string = f"BI{md['Brown Catalogue'][0]}"
        if md["Brown Catalogue"][1]:
            brown_string += f"-{md['Brown Catalogue'][1]}"

        new_dir = parent_dir_path / brown_string
        make_dir(new_dir)

        # Opus
        opus_string = ""
        dcml_string = brown_string
        if md["Opus"][0]:
            opus_string = str(md["Opus"][0]).zfill(2)
            if md["Opus"][1]:
                opus_string += f"-{md['Opus'][1]}"

        if opus_string:
            dcml_string += f"op{opus_string}"

        sapp_dt_string = f"mazurka{opus_string}"

        # DCML complete
        md["analysis_source"] = source["analysis_source"] + f"{dcml_string}.tsv"
        md["remote_score_mscx"] = source["remote_score_mscx"] + f"{dcml_string}.mscx"

        if opus_string:  # else omit this info. Not complete sets
            md["analysis_DT_source"] = f"{source['analysis_DT_source']}/{sapp_dt_string}.txt"
            # NB ^ Object of type PosixPath is not JSON serializable.
            md["remote_score_krn"] = source["remote_score_krn"] + sapp_dt_string + ".krn"

        if move_analyses:
            src = dt / f"{sapp_dt_string}.txt"
            if src.exists():
                print(f"Processing {src} ...")
                dst = new_dir / "analysis_DT.txt"
                shutil.move(src, dst)
                print("done")
            else:
                print(f"Error with {src}")

        write_json(md, parent_dir_path / brown_string / "remote.json")


# ------------------------------------------------------------------------------

# Shared

def get_composer(
        source: dict
) -> str:
    """
    Get a usable string for the composer name from the path entry of the source dict.
    Args:
        source: a metadata entry
    Returns: the composer as a string in the format `<last name>, <first name/s>`
    """
    return source["path_within_WiR"][1].replace("_", " ")


def write_json(
        this_metadata: dict,
        json_path: Path
) -> None:
    """
    Write the metadata in json format to the specified path
    """
    with open(json_path, "w") as json_file:
        json.dump(this_metadata, json_file, indent=4)


def make_dir(this_path: Path):
    if not this_path.exists():
        this_path.mkdir()


def make_parent_dirs(
        source: dict
) -> Path:
    """
    Making the parent directories
    and return the immediate parent for the corpus at hand.
    """
    parent_dir_path = CORPUS_FOLDER
    for x in source["path_within_WiR"]:
        parent_dir_path = parent_dir_path / x
        make_dir(parent_dir_path)
    return parent_dir_path


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--chorales", action="store_true")
    parser.add_argument("--madrigals", action="store_true")
    parser.add_argument("--chopin", action="store_true")

    args = parser.parse_args()

    if args.chorales:
        chorales()
    elif args.madrigals:
        madrigals()
    elif args.chopin:
        chopin()
    else:
        parser.print_help()
