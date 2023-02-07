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

# Early Choral

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
            md["composer"] = get_composer(source)
            md["analysis_source"] = source["analysis_source"] + f"/{m21_dt_string}.txt"
            md["remote_score_mxl"] = source["remote_score_mxl"] + f"{m21_dt_string}.mxl"

            if move_analyses:
                analysis_src = madrigals_DT / f"{m21_dt_string}.txt"
                analysis_dst = num_dir / "analysis.txt"
                shutil.copy(analysis_src, analysis_dst)

            print(book, number)
            print(md)
            write_json(md, num_dir / "remote.json")


# ------------------------------------------------------------------------------

# Keyboard_Other

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
        md["composer"] = get_composer(source)

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
            move_and_report(dt / f"{sapp_dt_string}.txt", new_dir / "analysis_DT.txt")

        write_json(md, parent_dir_path / brown_string / "remote.json")


def debussy_suite_bergamasque() -> None:
    source = metadata.debussy_suite_bergamasque
    parent_dir_path = make_parent_dirs(source)
    count = 0
    for item in source["items"]:
        count += 1
        md = expand_catalogue(source["item_keys"], item)  # Opus, Number
        md["composer"] = get_composer(source)
        their_str = f"l{str(md['Lesure Catalogue']).zfill(3)}-{str(count).zfill(2)}" \
                    f"_suite_{str(md['Name']).lower()}"
        # l075-01_suite_prelude.tsv
        our_string = f"{count}_{md['Name']}"
        make_dir(parent_dir_path / our_string)
        md["analysis_source"] = source["analysis_source"] + f"{their_str}.tsv"
        md["remote_score_mscx"] = source["remote_score_mscx"] + f"{their_str}.mscx"
        write_json(md, parent_dir_path / our_string / "remote.json")


def dvorak_silhouettes() -> None:
    simple_case(metadata.dvorak_silhouettes)


def liszt_pelerinage() -> None:
    source = metadata.liszt_pelerinage
    parent_dir_path = make_parent_dirs(source)
    for item in source["items"]:
        md = expand_catalogue(source["item_keys"], item)  # Opus, Number
        md["composer"] = get_composer(source)
        their_str = f"{str(md['Searle'])}.{str(md['Number']).zfill(2)}_{md['Name']}"
        # 160.01_Chapelle_de_Guillaume_Tell.tsv
        our_string = f"S{str(md['Searle'])}_{str(md['Number'])}_{md['Name']}"
        make_dir(parent_dir_path / our_string)
        md["analysis_source"] = source["analysis_source"] + f"{their_str}.tsv"
        md["remote_score_mscx"] = source["remote_score_mscx"] + f"{their_str}.mscx"
        write_json(md, parent_dir_path / our_string / "remote.json")


def grieg_lyric_pieces() -> None:
    simple_case(metadata.grieg_lyric_pieces)


def medtner_tales() -> None:
    simple_case(metadata.medtner_tales)


def schumann_kinderszenen() -> None:
    source = metadata.schumann_kinderszenen
    parent_dir_path = make_parent_dirs(source)
    for item in range(1, source["items"] + 1):
        md = dict()
        md["Opus"] = 15
        md["Number"] = item
        md["composer"] = get_composer(source)
        their_str = f"n{str(item).zfill(2)}"
        make_dir(parent_dir_path / str(item))
        md["analysis_source"] = source["analysis_source"] + f"{their_str}.tsv"
        md["remote_score_mscx"] = source["remote_score_mscx"] + f"{their_str}.mscx"

        write_json(md, parent_dir_path / str(item) / "remote.json")


def tchaikovsky_seasons() -> None:
    source = metadata.tchaikovsky_seasons
    parent_dir_path = make_parent_dirs(source)
    for item in range(1, source["items"] + 1):
        md = dict()
        md["Opus"] = "37a"
        md["Number"] = item
        md["composer"] = get_composer(source)
        their_str = f"op37a{str(item).zfill(2)}"
        make_dir(parent_dir_path / str(item))
        md["analysis_source"] = source["analysis_source"] + f"{their_str}.tsv"
        md["remote_score_mscx"] = source["remote_score_mscx"] + f"{their_str}.mscx"

        write_json(md, parent_dir_path / str(item) / "remote.json")


# ------------------------------------------------------------------------------

# Piano_Sonatas

def sonatas_Beethoven(move_analyses: bool = True) -> None:
    source = metadata.sonatas_Beethoven
    parent_dir_path = make_parent_dirs(source)
    dt = DT_BASE / "Beethoven"

    count = 0

    for item in source["items"]:

        md = expand_catalogue(source["item_keys"], item)  # Opus, Number, Name, Movements, DCML

        count += 1
        md["sonata_number"] = count
        md["composer"] = get_composer(source)

        opus_number_str = f"Op{str(md['Opus']).zfill(3)}"
        if md['Number']:
            opus_number_str += f"_No{md['Number']}"

        wir_dir = opus_number_str
        dt_file_name = wir_dir.lower().replace("_", "")

        if md['Name']:
            wir_dir += f"({md['Name']})"

        make_dir(parent_dir_path / wir_dir)

        for movement in range(1, item[3] + 1):  # last entry is number of movements

            md["movement"] = movement
            mvt_dir = parent_dir_path / wir_dir / str(movement)
            make_dir(mvt_dir)

            sonata_string = str(md['sonata_number']).zfill(2) + "-" + str(movement)  # 01-1
            dt_mvt = f"{dt_file_name}-{str(movement)}.txt"  # op002no1-1.txt

            md["analysis_source"] = None

            # 3x incomplete corpora!
            # BPS
            if movement == 1:
                md["analysis_BPS_source"] = f"{source['analysis_BPS_source']}{count}/chords.xlsx"
            else:
                md["analysis_BPS_source"] = None  # Reset for movements 2+
                # Sic, first movements one, no zero-pad
            # DCML
            if item[4]:
                md["analysis_DCML_source"] = source["analysis_DCML_source"] + f"{sonata_string}.tsv"
                md["remote_score_mscx"] = source["remote_score_mscx"] + f"{sonata_string}.mscx"
            else:
                md["analysis_DCML_source"] = None
                md["remote_score_mscx"] = None

            # DT
            dt_file = dt / dt_mvt
            if dt_file.exists():
                md["analysis_DT_source"] = f"{source['analysis_DT_source']}/{dt_mvt}"
                if move_analyses:
                    move_and_report(dt_file, mvt_dir / "analysis_DT.txt")
            else:
                md["analysis_DT_source"] = None

            print(f"Writing json metadata for {mvt_dir}")
            write_json(md, mvt_dir / "remote.json")


def sonatas_Mozart(move_analyses: bool = True) -> None:
    source = metadata.sonatas_Mozart
    parent_dir_path = make_parent_dirs(source)
    dt = DT_BASE / "Mozart"

    count = 0

    for item in source["items"]:

        md = dict()
        count += 1
        md["sonata_number"] = count
        md["composer"] = get_composer(source)
        md[source["item_keys"][0]] = item  # Köchel

        koechel_string = f"K{item}"
        k_dir = parent_dir_path / koechel_string
        make_dir(k_dir)

        for movement in range(1, 3 + 1):
            mvt_dir = k_dir / str(movement)
            make_dir(mvt_dir)

            km_string = koechel_string + "-" + str(movement)

            md["analysis_source"] = source["analysis_source"] + f"{km_string}.tsv"
            md["remote_score_mscx"] = source["remote_score_mscx"] + f"{km_string}.mscx"
            md["analysis_DT_source"] = f"{source['analysis_DT_source']}/{km_string}.txt"

            if move_analyses:
                move_and_report(dt / f"{km_string}.txt", mvt_dir / "analysis_DT.txt")
                # No K533

            write_json(md, mvt_dir / "remote.json")


# ------------------------------------------------------------------------------

# Quartets

def quartets_Beethoven():
    source = metadata.quartets_Beethoven
    parent_dir_path = make_parent_dirs(source)
    for item in source["items"]:
        md = expand_catalogue(source["item_keys"], item)
        md["composer"] = get_composer(source)
        our_string = f"Op{md['Opus']}_No{md['Number']}"
        make_dir(parent_dir_path / our_string)
        for m in range(1, item[2] + 1):
            md["movement"] = m
            make_dir(parent_dir_path / our_string / str(m))
            their_str = f"op20n{md['Number']}-0{m}."
            md["analysis_source"] = f"{source['analysis_source']}{md['Number']}/" \
                                    f"{'i' * m}/{their_str}hrm"
            md["remote_score_krn"] = source["remote_score_krn"] + f"{their_str}krn"

            write_json(md, parent_dir_path / our_string / str(m) / "remote.json")


def haydn_op20():
    source = metadata.haydn_op20
    parent_dir_path = make_parent_dirs(source)
    for item in source["items"]:
        md = expand_catalogue(source["item_keys"], item)
        md["composer"] = get_composer(source)
        our_string = f"Op{md['Opus']}_No{md['Number']}"
        make_dir(parent_dir_path / our_string)
        for m in range(1, item[2] + 1):
            md["movement"] = m
            make_dir(parent_dir_path / our_string / str(m))
            their_str = f"op20n{md['Number']}-0{m}."
            md["analysis_source"] = f"{source['analysis_source']}{md['Number']}/" \
                                    f"{'i' * m}/{their_str}hrm"
            md["remote_score_krn"] = source["remote_score_krn"] + f"{their_str}krn"

            write_json(md, parent_dir_path / our_string / str(m) / "remote.json")


def haydn_op74():
    source = metadata.haydn_op74
    parent_dir_path = make_parent_dirs(source)
    for item in source["items"]:
        md = expand_catalogue(source["item_keys"], item)
        md["composer"] = get_composer(source)
        our_string = f"Op{md['Opus']}_No{md['Number']}"
        make_dir(parent_dir_path / our_string)
        for m in range(1, item[2] + 1):
            md["movement"] = m
            make_dir(parent_dir_path / our_string / str(m))
            their_str = f"op74n{md['Number']}-0{m}."  # "op74n3-04"
            md["analysis_source"] = f"{source['analysis_source']}/{their_str}txt"
            md["remote_score_krn"] = source["remote_score_krn"] + f"{their_str}krn"

            write_json(md, parent_dir_path / our_string / str(m) / "remote.json")


# ------------------------------------------------------------------------------

# Shared

def simple_case(source: dict) -> None:
    """
    A simple case of expanding opus, number, composer etc.
    Usually slight variants to encode.
    Args:
        source (dict): one of the metadata.<x> dict entries.

    Returns: None
    """
    parent_dir_path = make_parent_dirs(source)
    for item in source["items"]:
        md = expand_catalogue(source["item_keys"], item)  # Opus, Number
        md["composer"] = get_composer(source)
        their_str = f"op{str(md['Opus']).zfill(2)}n{str(md['Number']).zfill(2)}"
        our_string = f"Op{str(md['Opus']).zfill(2)}_No{md['Number']}"
        make_dir(parent_dir_path / our_string)
        md["analysis_source"] = source["analysis_source"] + f"{their_str}.tsv"
        md["remote_score_mscx"] = source["remote_score_mscx"] + f"{their_str}.mscx"
        write_json(md, parent_dir_path / our_string / "remote.json")


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


def expand_catalogue(
        item_keys: list | tuple,
        items_list: list | tuple,
) -> dict:
    """
    Expand the catalogue metadata for one work as provided.
    """
    this_dict = {}
    for k in range(len(item_keys)):
        this_dict[item_keys[k]] = items_list[k]
    return this_dict


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


def move_and_report(src, dest):
    print(f"Processing {src} ...")
    if src.exists():
        shutil.copy(src, dest)
        print("... done")
    else:
        print(f"... Error with {src}")


# ------------------------------------------------------------------------------

if __name__ == "__main__":

    import argparse


    def run_args():

        parser = argparse.ArgumentParser()

        arg_strings = (
            "chorales",
            "madrigals",

            "chopin",
            "debussy_suite_bergamasque",
            "dvorak_silhouettes",
            "grieg_lyric_pieces",
            "liszt_pelerinage",
            "medtner_tales",
            "schumann_kinderszenen",
            "tchaikovsky_seasons",

            "sonatas_Mozart",
            "sonatas_Beethoven",

            "quartets_beethoven",
            "haydn_op20",
            "haydn_op74"
        )

        for x in arg_strings:
            parser.add_argument("--" + x, action="store_true")

        args = parser.parse_args()

        for y in arg_strings:
            if args.__getattribute__(y):
                eval(y + "()")
                return

        parser.print_help()


    run_args()
