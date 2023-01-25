# -*- coding: utf-8 -*-
"""
NAME:
===============================
Collect Convert (collect_convert.py)

BY:
===============================
Mark Gotham

LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/

ABOUT:
===============================
Collect external files and / or convert them for inclusion in "When in Rome"
or reference to the via the `remote_score.json` files.

"""

# ------------------------------------------------------------------------------

import json
import os
import re
import shutil

from pathlib import Path

from . import REPO_FOLDER
from . import CORPUS_FOLDER
from . import get_corpus_files

from music21 import converter, environment, metadata, romanText


# ------------------------------------------------------------------------------

def convert_musescore_score_corpus(
        in_path: str | os.PathLike,
        out_path: str | os.PathLike,
        corpus_name: str = "mozart_piano_sonatas",
        in_format: str = ".mscx",
        out_format: str = ".mxl",
        write: bool = True,
) -> list:
    """
    Basic script for creating or updating a
    `<corpus_name>_corpus_conversion.json` file with
    the latest contents of the corpus so that it can be used
    for batch conversion of
    musescore files (mscx or mscz)
    to mxl or other fileformat.

    Specifically, set up to map from DCML conventions
    e.g., in the mozart_piano_sonatas from `/K279-1.mscx` into
    local convention for subfolders `/K279/1/score.mxl`.

    Implement the batch conversion of one such file
    e.g., `corpus_conversion.json`
    from this folder with the command:
    >>> mscore -j corpus_conversion.json

    For information about `mscore` and a within-app plugin alternative, see
    https://musescore.org/en/handbook/3/command-line-options#Run_a_batch_job_converting_multiple_documents

    TODO when implementing curl option for copying remote files, include that option here:
    https://raw.githubusercontent.com/DCMLab/mozart_piano_sonatas/main/scores/K279-1.mscx
    """

    valid_formats = [".mscx", ".mscz", ".mxl", ".pdf", ".mid"]
    if in_format not in valid_formats:
        raise ValueError(f"Invalid in_format: must be one of {valid_formats}")
    if out_format not in valid_formats:
        raise ValueError(f"Invalid out_format: must be one of {valid_formats}")

    valid_corpora = ["ABC", "mozart_piano_sonatas"]
    if corpus_name not in valid_corpora:
        raise ValueError(f"Invalid in_format: must be one of {valid_corpora}")

    out_data = []

    for f in os.listdir(in_path):
        if f.endswith(in_format):
            if corpus_name == "ABC":
                cln, mvt = dcml_ABC_to_local(f)
            elif corpus_name == "mozart_piano_sonatas":
                cln, mvt = f.split("-")  # e.g., K279-1.mscx >>> K279, 1.mcsx
                mvt = mvt.split(".")[0]  # e.g.,  1.mcsx >>> 1

            # if not isdir, mkdir
            cln_path = os.path.join(out_path, cln)
            if not os.path.isdir(cln_path):
                os.mkdir(cln_path)
            mvt_path = os.path.join(cln_path, mvt)
            if not os.path.isdir(mvt_path):
                os.mkdir(mvt_path)

            x = {"in": in_path + f,
                 "out": str(mvt_path) + "/score" + out_format
                 }

            out_data.append(x)

    if write:
        out_path = os.path.join(".", corpus_name + "_corpus_conversion.json")
        with open(out_path, "w") as json_file:
            json.dump(out_data, json_file)

    return out_data


def copy_DCML_tsv_analysis_files(
        in_path: str | os.PathLike,
        out_path: str | os.PathLike,
        corpus_name: str = "mozart_piano_sonatas",
) -> None:
    """
    Copy DCML analysis files (.tsv) to the relevant
    `working` folder of this repo.

    TODO: DRY - refactor with `convert_musescore_score_corpus`
    """

    valid_corpora = ["ABC", "mozart_piano_sonatas"]
    if corpus_name not in valid_corpora:
        raise ValueError(f"Invalid in_format: must be one of {valid_corpora}")

    for f in os.listdir(in_path):
        if f.endswith(".tsv"):
            if corpus_name == "ABC":
                cln, mvt = dcml_ABC_to_local(f)
            elif corpus_name == "mozart_piano_sonatas":
                cln, mvt = f.split("-")  # e.g., K279-1.mscx >>> K279, 1.mcsx
                mvt = mvt.split(".")[0]  # e.g.,  1.mcsx >>> 1

            # if not isdir, mkdir
            cln_path = os.path.join(out_path, cln)
            if not os.path.isdir(cln_path):
                os.mkdir(cln_path)
            mvt_path = os.path.join(cln_path, mvt)
            if not os.path.isdir(mvt_path):
                os.mkdir(mvt_path)
            working_path = os.path.join(mvt_path, "Working")
            if not os.path.isdir(working_path):
                os.mkdir(working_path)

            print(f"Processing {working_path} ...", end="", flush=True)

            shutil.copy(in_path + f,
                        os.path.join(working_path, "DCML_analysis.tsv")
                        )
            print(" done.")


def copy_DT_analysis_files(
        in_path: str | os.PathLike,
        do_chorales: bool = True,
        do_Monteverdi: bool = True,
        do_Beethoven: bool = False,
) -> None:
    """
    Copy Dmitri's analysis files (romantext)
    from a local copy of his corpus to the relevant folder of WiR.
    Also uses or writes `remote_score.json` files as appropriate to each sub-corpus.
    TODO use direct URLs if ever released in that way.

    Current sub-corpora:
    - Bach chorales (expansion of music21 provision)
    - Monteverdi madrigals (expansion of music21 provision)
    - Beethoven sonatas (use existing `remote_score.json` files)

    TODO DRY
    """

    if do_chorales:

        chorales_WiR = CORPUS_FOLDER / "Early_Choral" / "Bach,_Johann_Sebastian" / "Chorales"
        chorales_DT = Path(in_path) / "Bach Chorales"
        chorales_MG = raw_git + f"MarkGotham/Chorale-Corpus/"

        for x in range(1, 372):
            num = str(x).zfill(3)
            src = chorales_DT / f"riemenschneider{num}.txt"
            dst = chorales_WiR / num / "analysis.txt"
            # shutil.copy(src, dst)

            this_metadata = dict(catalogue_type="Riemenschneider",
                                 catalogue_number=x,
                                 remote_URL_path=chorales_MG + f"{num}/short_score.mxl"
                                 )

            write_path = chorales_WiR / num / "remote_score.json"
            with open(write_path, "w") as json_file:
                json.dump(this_metadata, json_file, indent=4)

    if do_Monteverdi:

        monte_WiR = CORPUS_FOLDER / "Early_Choral" / "Monteverdi,_Claudio"
        monte_DT = Path(in_path) / "Monteverdi"
        monte_m21 = raw_git + "cuthbertLab/music21/master/music21/corpus/monteverdi/"

        for this_file in os.listdir(monte_DT):
            # Shared:
            book, number = this_file.split(".")[1:3]  # "madrigal.{book}.{number}.<ext>"
            dst = monte_WiR / f"Madrigals_Book_{book}" / number.zfill(2)

            # Analyses from DT:
            analysis_src = monte_DT / this_file
            analysis_dst = dst / "analysis.txt"
            # shutil.copy(analysis_src, analysis_dst)

            # Scores: remote point to music21 (currently no separate DT urls available)
            this_metadata = dict(book=int(book),
                                 number=int(number),
                                 remote_URL_path=monte_m21 + f"madrigal.{book}.{number}.mxl"
                                 )

            write_path = dst / "remote_score.json"
            with open(write_path, "w") as json_file:
                json.dump(this_metadata, json_file, indent=4)


def dcml_ABC_to_local(
        f: str
) -> list:
    """
    Converts from DCML ABC file names to local convertion
    Args:
        f: a DCML ABC file name like `n01op18-1_01.mscx`

    Returns: list
    """
    g = f.split("op")[1]  # n01op18-1_01.mscx >>> 18-1_01.mscx
    g = g.split(".")[0]  # 18-1_01.mscx >>> 18-1_01
    cln, mvt = g.split("_")  # 18-1_01 >>> 18-1, 01
    mvt = mvt[1]  # Remove DCML padding "01" >>> "1". Never 10+ mvts
    no = ""
    if "-" in cln:  # Only if applicable. 18-1 >>> 18, 1
        cln, no = cln.split("-")
        no = "No" + no  # No1
    if len(cln) == 2:  # 18, 59 etc.
        cln = "0" + cln  # Add padding. Op100+ in collection.
    cln = "Op" + cln
    if no:
        cln = "_".join([cln, no])  # Op018_No1
    mvt = mvt.split(".")[0]  # e.g.,  1.mcsx >>> 1

    return [cln, mvt]


def convert_DCML_tsv_analyses(
        corpus: str = "Quartets",
        # overwrite: bool = True
) -> None:
    """
    Convert local copies of DCML analysis files (.tsv) to rntxt.
    """

    file_paths = get_corpus_files(sub_corpus_path=CORPUS_FOLDER / corpus,
                                  file_name="DCML_analysis.tsv")

    for f in file_paths:

        new_dir = os.path.dirname(os.path.dirname(f))
        out_path = os.path.join(new_dir, "analysis.txt")

        path_parts = Path(os.path.realpath(new_dir)).parts

        genre, composer, opus, movement = path_parts[-4:]
        genre = genre[:-1].replace("_", " ")  # Cut plural "s"
        composer = composer.replace("_", " ")

        work_str = genre  # Both cases
        if "Mozart" in composer:
            work_str += f" {opus}"  # Straightforward K number, always 3 digits
        elif "Beethoven" in composer:
            m = re.search(r"Op0*(?P<opus>\d+)(_No0?(?P<num>\d+))?", opus)
            work_str += f" Op. {m.group('opus')}"
            if m.group("num"):
                work_str += f" No. {m.group('num')}"
        work_str += f", Movement {movement}"  # Both cases

        print(f"Processing {out_path} ...", end="", flush=True)
        analysis = romanText.tsvConverter.TsvHandler(f, dcml_version=2).toM21Stream()
        analysis.insert(0, metadata.Metadata())
        analysis.metadata.composer = composer
        analysis.metadata.analyst = "DCMLab. See https://github.com/DCMLab/"
        analysis.metadata.title = work_str

        # TODO overwrite / path exists check
        converter.subConverters.ConverterRomanText().write(
            analysis, "romanText", fp=out_path
        )
        print(" done.")


def remote_scores(
        local_path: list = ["Piano_Sonatas", "Beethoven,_Ludwig_van"],
        write_score: bool = False
) -> None:
    """
    Reference (by default) or (optionally) retrieve externally hosted scores.
    This is designed to prevent duplication and automatically include source updates.
    It makes sense for those in a format which can be directly parsed by music21
    (i.e., not MuseScore files conversion of which requires `mscore`).

    TODO: option to CURL a local copy of the source and convert from there (bypass m21 environment).

    :param local_path: the local path (within When in Rome) to the corpus expressed as a list.
    :param write_score: If true, convert to mxl and write a local copy.
        (See notes and warning at the `convert_and_write_local` function.)
        If false, simply write "remote_score.json" files with the remote path and some metadata.
        Please also check and observe the licence of all scores, especially those hosted externally.
    :return: None

    """

    valid_local_paths = [
        ["Piano_Sonatas", "Beethoven,_Ludwig_van"],
        ["Variations_and_Grounds", "Beethoven,_Ludwig_van", "_"],
        ["Variations_and_Grounds", "Mozart,_Wolfgang_Amadeus", "_"],
    ]

    if local_path == valid_local_paths[0]:
        remote_Beethoven(local_path=local_path, write_score=write_score)
    elif local_path == valid_local_paths[1]:
        remote_TAVERN(local_path=local_path, Beethoven=True, write_score=write_score)
    elif local_path == valid_local_paths[2]:
        remote_TAVERN(local_path=local_path, Beethoven=False, write_score=write_score)
    else:
        raise ValueError(f"Invalid local_path. Chose one of {valid_local_paths}")


raw_git = 'https://raw.githubusercontent.com/'


def list_dir_sorted_not_hidden(
        this_dir: os.PathLike
) -> list:
    """
    Convenience function for os.listdir with sorting and ignoring hidden files.
    """
    return sorted([f for f in os.listdir(this_dir) if not f.startswith(".")])


def remote_Beethoven(
        local_path,
        write_score: bool = False,
        external_corpus: str = "Sapp"
) -> None:
    """
    Remote scores for the Beethoven piano sonatas.

    :param local_path: See notes at `remote_scores`.
    :param write_score: See notes at `remote_scores`.
    :param external_corpus: Which external corpus to use.
        Only `Sapp` is currently supported.

    Returns: None
    """

    local_base_path = os.path.join(CORPUS_FOLDER, *local_path)

    if external_corpus == "Sapp":
        remote_base_path = raw_git + "craigsapp/beethoven-piano-sonatas/master/kern/sonata"
    else:
        raise ValueError("Invalid external_corpus: only `Sapp` is currently supported")
        # TODO any other corpora that emerge.

    opus_strings = list_dir_sorted_not_hidden(local_base_path)

    sonata_number = 0

    for o in opus_strings:
        sonata_number += 1
        sonata_path = os.path.join(local_base_path, o)
        movements = list_dir_sorted_not_hidden(sonata_path)

        for movt in movements:
            sonata_string = str(sonata_number).zfill(2)  # zero-pad sonatas e.g., 01
            m = re.search(r"Op0*(?P<opus>\d+)(_No0?(?P<num>\d+))?", o)
            opus_number = [int(m.group("opus"))]
            if m.group("num"):
                opus_number.append(int(m.group("num")))
            remote_URL_path = remote_base_path + f"{sonata_string}-{movt}.krn"
            movement_path = os.path.join(sonata_path, movt)
            this_metadata = dict(catalogue_type="Opus",
                                 catalogue_number=opus_number,
                                 sonata_number=sonata_number,
                                 movement=int(movt),
                                 remote_URL_path=remote_URL_path
                                 )

            if write_score:
                convert_and_write_local(remote_URL_path=remote_URL_path,
                                        local_path=movement_path)
            else:
                write_path = os.path.join(movement_path, "remote_score.json")
                with open(write_path, "w") as json_file:
                    json.dump(this_metadata, json_file, indent=4)


def remote_TAVERN(
        local_path,
        Beethoven: bool = True,
        write_score: bool = False
) -> None:
    """
    Remote scores for the TAVERN variations.

    Args:
        local_path: See notes at remote_scores
        Beethoven (bool): `True` for the Beethoven side of the collection, `False` for Mozart.
        write_score: See notes at remote_scores
    Returns: None
    """

    local_base_path = os.path.join(CORPUS_FOLDER, *local_path)
    remote_base_path = raw_git + "jcdevaney/TAVERN/blob/master/"
    if Beethoven:
        remote_base_path += "Beethoven/"
    else:
        remote_base_path += "Mozart/"

    opus_strings = list_dir_sorted_not_hidden(local_base_path)

    for o in opus_strings:
        local_path = os.path.join(local_base_path, o)
        cat_type = "Opus"
        if Beethoven:
            if o.startswith("Op"):
                # cat_type = "Opus"
                cat_number = int(o[2:])
                remote_URL_path = remote_base_path + f"Opus{cat_number}/Krn/Opus{cat_number}.xml"
            elif o.startswith("WoO"):  # WoO_63 > B063/Krn/Wo063.xml
                cat_type = "Werke ohne Opuszahl"
                cat_number = int(o[4:])
                remote_URL_path = remote_base_path + f"B0{cat_number}/Krn/Wo0{cat_number}.xml"
            else:
                raise ValueError("Invalid opus name")
        else:  # o.startswith("K"):  # "Mozart"
            cat_type = "Köchel-Verzeichnis"
            cat_number = int(o[1:])
            remote_URL_path = remote_base_path + f"{o}/Krn/{o}.krn"  # xml not always there

        if write_score:
            convert_and_write_local(remote_URL_path=remote_URL_path,
                                    local_path=local_path)
        else:
            this_metadata = dict(catalogue_type=cat_type,
                                 catalogue_number=cat_number,
                                 remote_URL_path=remote_URL_path
                                 )

            write_path = os.path.join(local_path, "remote_score.json")
            with open(write_path, "w") as json_file:
                json.dump(this_metadata, json_file, indent=4)


def convert_and_write_local(remote_URL_path,
                            local_path,
                            ):
    """
    Given a remote path (URL) to a score that music21 can convert,
    and a local path to a directory within When in Rome.
    retrieve the remote score, convert, and write a local copy as "score.mxl".

    *** Warning *** this means changing your music21 environment settings while in progress.
    (They will be returned to the previous state at the end).

    Returns: None
    """
    before = environment.Environment()["autoDownload"]  # Get current setting
    during = "allow"

    if before != during:
        print(
            "Warning: temporarily changing music21 environment.Environment() "
            f"autoDownload settings from {before} to {during}."
        )
        environment.set("autoDownload", "allow")  # Change current setting

    score = converter.parse(remote_URL_path)  # And do anything with it
    score.write("mxl", os.path.join(local_path, "score.mxl"))

    if before != during:
        environment.set("autoDownload", before)  # Restore settings as they were


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--DCML_ABC", action="store_true")
    parser.add_argument("--DCML_Mozart", action="store_true")

    parser.add_argument("--DT_analyses", action="store_true")
    parser.add_argument("--DT_base_path", type=str,
                        required=False,
                        default=REPO_FOLDER.parent / "TAOM" / "TAOMfiles" / "Music",
                        help="Local base_path to the DT corpus up to the `Music` directory")

    parser.add_argument("--remote_Beethoven_sonata_list", action="store_true")
    parser.add_argument("--remote_Beethoven_variations_list", action="store_true")
    parser.add_argument("--remote_Mozart_variations_list", action="store_true")

    args = parser.parse_args()

    if args.DCML_ABC:
        convert_DCML_tsv_analyses(corpus="Quartets")
    elif args.DCML_Mozart:
        convert_DCML_tsv_analyses(corpus="Piano_Sonatas")
    elif args.DT_analyses:
        copy_DT_analysis_files(in_path=args.DT_base_path)
    elif args.remote_Beethoven_sonata_list:
        remote_scores()  # default
    elif args.remote_Beethoven_variations_list:
        remote_scores(["Variations_and_Grounds", "Beethoven,_Ludwig_van", "_"])
    elif args.remote_Mozart_variations_list:
        remote_scores(["Variations_and_Grounds", "Mozart,_Wolfgang_Amadeus", "_"])

    else:
        parser.print_help()
