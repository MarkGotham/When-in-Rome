# -*- coding: utf-8 -*-
"""
===============================
Updates and Checks (updates_and_checks.py)
===============================

Mark Gotham, 2020-


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Functions for updating entries to the "When in Rome" corpus of harmonic analyses, notably:
- copying, moving, converting scores and analyses;
- creating "slices" and "template" files (from the score)
- producing "feedback" and "analysis_on_score" files (from a score and analysis pair)
- various checks.

See also "contents.py" for updating corpus contents lists.

"""

# ------------------------------------------------------------------------------

import json
import os
import re
import shutil

from pathlib import Path
from typing import Optional, Union

from . import romanUmpire
from . import CORPUS_FOLDER

from music21 import bar, converter, environment, metadata, stream, romanText

# ------------------------------------------------------------------------------

corpora = [
    "Orchestral",
    "Early_Choral",
    "Etudes_and_Preludes",
    "OpenScore-LiederCorpus",
    "Piano_Sonatas",
    "Quartets",
    "Variations_and_Grounds"
]


# ------------------------------------------------------------------------------

# Get file lists

def get_corpus_files(corpus: str = "",
                     file_name: Optional[str] = "*.*",
                     ) -> list:
    """
    Get and return paths to files matching conditions for the given file_name.
    :param corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
    :param file_name: select all files that are compliant with this file_name.
    Specify either the exact files name (e.g., "analysis_automatic.rntxt") or
    use the wildcard "*" to match patterns. Examples:
      - "*.mxl" searches for all .mxl files
      - "slices*" searches for all files starting with slices
    :return: list of file paths.
    """

    if corpus not in ["", *corpora]:
        raise ValueError(f"Invalid corpus: must be one of {corpora} or an empty string (for all)")

    return [str(x) for x in (CORPUS_FOLDER / corpus).rglob(file_name)]


def get_analyses(corpus: str = "OpenScore-LiederCorpus",
                 all_versions: bool = True
                 ) -> list:
    """
    Get analysis files across a corpus.
    (I.e., Convenience function for `get_corpus_files` on analyses.)

    :param corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
    :param all_versions: If True, get all analysis files ("analysis*txt"); if false, only get the
    "analysis.txt" files.
    :return: list of file paths.
    """

    f = "analysis.txt"
    if all_versions:
        f = "analysis*txt"
    return get_corpus_files(corpus=corpus, file_name=f)


def clear_the_decks(corpus: str = "",
                    file_types=None,
                    delete: bool = True
                    ) -> list:
    """
    When in Rome now supports many variant subsidiary files
    but does not include them by default.
    Having created them, use this to reset (delete).

    :param corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
    :param file_types: Which file types to delete or mark for deletion.
    :param delete: Bool. Delete or just report by returning the list.
    :return: list of the marked files.
    """

    if file_types is None:
        file_types = ["analysis_on_score.mxl", "slices.tsv", ]

    to_go = []

    for g in file_types:
        to_go += get_corpus_files(corpus=corpus, file_name=g)

    for f in to_go:
        if delete:
            print("Removing: ", f)
            os.remove(f)

    return to_go


# ------------------------------------------------------------------------------

# Roman Umpire

def process_one_score(path_to_score: str,
                      path_to_analysis,  # NB "On Score" option
                      write_path: str,
                      combine: bool = True,
                      slices: bool = True,
                      feedback: bool = True,
                      overwrite: bool = False):
    """
    Processes one score to produce any or all of the following files:
    "analysis_on_score" (score files with analysis added in musical notation),
    "slices_with_analysis" (tsv representation that is a valid input for the Roman umpire and
    quicker to parse than musicXML), and
    "feedback" (txt written feedback on the score-analysis match).

    :param path_to_score:
    :param path_to_analysis: a string as path, or simply "On score" *** (see romanUmpire).
    :param write_path: where to write any new files to.
    :param combine: create an `analysis_on_score` file with the two combined.
    :param slices: create a "slices.tsv" representation.
    :param feedback: produce feedback on how the analysis matches the score (write to .txt)
    :param overwrite: if False and the file type already exists, don"t replace it.
    """

    if (not combine) and (not slices) and (not feedback):
        print("No action requested: set at least one of combine, slices, or feedback to true.")
        return

    t = romanUmpire.ScoreAndAnalysis(path_to_score,
                                     analysisLocation=path_to_analysis)

    stopping_message = "file exists and overwrite set to False. Stopping"

    if combine:
        if overwrite or not os.path.exists(Path(write_path) / "analysis_on_score.mxl"):
            t.writeScoreWithAnalysis(outPath=write_path,
                                     outFile="analysis_on_score")
        else:
            print("analysis_on_score " + stopping_message)

    if slices:
        t.matchUp()  # Sic, necessary here and only here
        if overwrite or not os.path.exists(Path(write_path) / "slices_with_analysis.tsv"):
            t.writeSlicesFromScore(outPath=write_path,
                                   outFile="slices_with_analysis")
        else:
            print("slices_with_analysis " + stopping_message)

    if feedback:
        if overwrite or not os.path.exists(Path(write_path) / "feedback_on_analysis.txt"):
            t.printFeedback(outPath=write_path,
                            outFile="feedback_on_analysis")
        else:
            print("feedback_on_analysis " + stopping_message)


def process_corpus(corpus: str = "OpenScore-LiederCorpus",
                   combine: bool = True,
                   slices: bool = True,
                   feedback: bool = True,
                   overwrite: bool = False):
    """
    Corpus wide implementation of `process_one_score`. See docs there.
    """
    files = get_corpus_files(corpus=corpus,
                             file_name="analysis.txt")

    for path_to_analysis in files:
        pth = path_to_analysis[:-len("analysis.txt")]
        print(pth)
        analysis_exist = os.path.exists(pth + "analysis_on_score.mxl")
        if overwrite or (not analysis_exist):
            try:
                process_one_score(os.path.join(pth, "score.mxl"),
                                  path_to_analysis,  # i.e. with "analysis"
                                  pth,
                                  combine=combine,
                                  slices=slices,
                                  feedback=feedback,
                                  overwrite=overwrite)
            except Exception as e:
                print(f"Error with: {pth}. {e}")


# ------------------------------------------------------------------------------

# Automated analyses from augmentednet

def make_automated_analyses(corpus: str = "OpenScore-LiederCorpus") -> None:
    """
    Create automated analyses using augmentednet (Nápoles López et al. 2021).
    :param corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
    :return: None

    TODO: untested draft based on (adapted from) https://github.com/MarkGotham/When-in-Rome/pull/47
    """

    from AugmentedNet.inference import batch, predict
    from AugmentedNet.utils import tensorflowGPUHack
    from tensorflow import keras

    tensorflowGPUHack()
    modelPath = "AugmentedNet.hdf5"
    model = keras.models.load_model(modelPath)

    files = get_corpus_files(corpus=corpus,
                             file_name="score.mxl")

    for path in files:
        pathrntxt = path.replace(".mxl", "_annotated.rntxt")
        annotatedScore = path.replace(".mxl", "_annotated.xml")
        annotationCSV = path.replace(".mxl", "_annotated.csv")
        newrntxt = path.replace("score.mxl", "analysis_automatic.rntxt")
        print(path)
        if os.path.isfile(newrntxt):
            print("... Already present, skipping.")
            continue
        try:
            predict(model, inputPath=path)
        except:
            print("... Failure to predict, skipping.")
            pass
        if os.path.isfile(annotatedScore):
            os.remove(annotatedScore)
        if os.path.isfile(annotationCSV):
            os.remove(annotationCSV)
        if os.path.isfile(pathrntxt):
            shutil.move(pathrntxt, newrntxt)


# ------------------------------------------------------------------------------

# Get, convert, move scores and analyses

def convert_musescore_score_corpus(in_path: Union[str, os.PathLike],
                                   out_path: Union[str, os.PathLike],
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
                # Op18_No1
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


def copy_DCML_tsv_analysis_files(in_path: Union[str, os.PathLike],
                                 out_path: Union[str, os.PathLike],
                                 corpus_name: str = "mozart_piano_sonatas",
                                 ) -> None:
    """
    Copy DCML"s analysis files (.tsv) to the relevant
    `working` folder of this repo.

    TODO: DRY - refactor with `convert_musescore_score_corpus`
    """

    valid_corpora = ["ABC", "mozart_piano_sonatas"]
    if corpus_name not in valid_corpora:
        raise ValueError(f"Invalid in_format: must be one of {valid_corpora}")

    out_data = []

    for f in os.listdir(in_path):
        if f.endswith(".tsv"):
            if corpus_name == "ABC":
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
                # Op18_No1
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


def convert_DCML_tsv_analyses(corpus: str = "Quartets",
                              # overwrite: bool = True
                              ) -> None:
    """
    Convert local copies of DCML"s analysis files (.tsv) to rntxt.
    """

    file_paths = get_corpus_files(corpus=corpus, file_name="DCML_analysis.tsv")

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


def remote_scores(local_path: list = ["Piano_Sonatas", "Beethoven,_Ludwig_van"],
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
        ["Variations_and_Grounds", "Mozart,_Wolfgang_Amadeus", "_"]
    ]

    if local_path == valid_local_paths[0]:
        remote_Sapp_Beethoven(local_path=local_path, write_score=write_score)
    elif local_path == valid_local_paths[1]:
        remote_TAVERN(local_path=local_path, Beethoven=True, write_score=write_score)
    elif local_path == valid_local_paths[2]:
        remote_TAVERN(local_path=local_path, Beethoven=False, write_score=write_score)
    else:
        raise ValueError(f"Invalid local_path. Chose one of {valid_local_paths}")


raw_git = 'https://raw.githubusercontent.com/'


def list_dir_sorted_not_hidden(dir: os.PathLike
                               ) -> os.PathLike:
    """
    Convenience function for os.listdir with sorting and ignoring hidden files.
    """
    return sorted([f for f in os.listdir(dir) if not f.startswith(".")])


def remote_Sapp_Beethoven(local_path,
                          write_score: bool = False
                          ) -> None:
    """
    Remote score for the Beethoven piano sonatas from Craig Sapp.
    Returns: None
    """

    local_base_path = os.path.join(CORPUS_FOLDER, *local_path)
    remote_base_path = raw_git + "craigsapp/beethoven-piano-sonatas/master/kern/sonata"
    opus_strings = list_dir_sorted_not_hidden(local_base_path)

    sonata_number = 0

    for o in opus_strings:
        sonata_number += 1
        sonata_path = os.path.join(local_base_path, o)
        movements = list_dir_sorted_not_hidden(sonata_path)

        for movt in movements:
            sonata_string = str(sonata_number).zfill(2)  # zeo-pad sonatas e.g., 01
            remote_URL_path = remote_base_path + f"{sonata_string}-{movt}.krn"
            movement_path = os.path.join(sonata_path, movt)
            this_metadata = {"sonata_number": sonata_number,
                             "movement": int(movt),
                             "remote_URL_path": remote_URL_path
                             }

            if write_score:
                convert_and_write_local(remote_URL_path=remote_URL_path,
                                        local_path=movement_path)
            else:
                write_path = os.path.join(movement_path, "remote_score.json")
                with open(write_path, "w") as json_file:
                    json.dump(this_metadata, json_file)


def remote_TAVERN(local_path,
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
        if Beethoven:
            if o.startswith("Op"):
                opus_numbering_type = "Opus"
                work_number = int(o[2:])
                remote_URL_path = remote_base_path + f"Opus{work_number}/Krn/Opus{work_number}.xml"
            elif o.startswith("WoO"):  # WoO_63 > B063/Krn/Wo063.xml
                opus_numbering_type = "Werke ohne Opuszahl"
                work_number = int(o[4:])
                remote_URL_path = remote_base_path + f"B0{work_number}/Krn/Wo0{work_number}.xml"
            else:
                raise ValueError("Invalid opus name")
        else:  # o.startswith("K"):  # "Mozart"
            opus_numbering_type = "Köchel-Verzeichnis"
            work_number = int(o[1:])
            remote_URL_path = remote_base_path + f"{o}/Krn/{o}.krn"  # xml not always there

        if write_score:
            convert_and_write_local(remote_URL_path=remote_URL_path,
                                    local_path=local_path)
        else:
            this_metadata = {"opus_numbering_type": opus_numbering_type,
                             "work_number": work_number,
                             "remote_URL_path": remote_URL_path
                             }

            write_path = os.path.join(local_path, "remote_score.json")
            with open(write_path, "w") as json_file:
                json.dump(this_metadata, json_file)


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

# Checks

def repeats_are_valid(score: stream.Score, print_all: bool = True) -> None:
    """
    Quick and simple check that start and end repeats match up.
    Specifically, iterates through the barlines on the highest part
    and raises a value error in the case of:
    two starts without an end,
    or two ends without a start.
    """
    last_repeat = ""  # starting condition
    for barline in score.parts[0].recurse().getElementsByClass(bar.Barline):
        measure_num = barline.getContextByClass(stream.Measure).measureNumber
        if str(barline) == str(bar.Repeat(direction="start")):
            if print_all:
                print(f"Start repeat in measure\t{measure_num}")
            if last_repeat == "start":
                raise ValueError(f"Second successive start repeat found in measure {measure_num}.")
            else:
                last_repeat = "start"
        if str(barline) == str(bar.Repeat(direction="end")):
            if print_all:
                print(f"End repeat in measure\t{measure_num}")
            if last_repeat == "end":
                raise ValueError(f"Second successive end repeat found in measure {measure_num}.")
            else:
                last_repeat = "end"
    return


def check_all_parse(corpus: str = "OpenScore-LiederCorpus",
                    analysis_not_score: bool = True,
                    count_files: bool = True,
                    count_rns: bool = True
                    ) -> None:
    """
    Check all files parse successfully
    (throws and error on the first case to fail if not).

    Run on either analyses (analysis_not_score = True, default) or scores (false).
    Optionally count the number of files and (if analyses) also the Roman Numerals therein.

    :param analysis_not_score: If true, check analysis files; if false then scores.
    :param corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
    :param count_files: count+print the total number of analysis files (bool, optional).
    :param count_rns: count+print the total Roman numerals in all analysis files (bool, optional).
    """

    if analysis_not_score:
        files = get_analyses(corpus=corpus)
    else:
        files = get_corpus_files(corpus=corpus, file_name="score.mxl")

    if count_files:
        print(f"{len(files)} files found ... now checking they all parse ...")

    rns = 0

    for f in files:
        if analysis_not_score:
            if count_rns:
                a = converter.parse(f, format="romantext")
                rns += len(a.getElementsByClass("RomanNumeral"))
            else:
                converter.parse(f, format="romantext")
        else:
            converter.parse(f)

    print("All parse")

    if analysis_not_score and count_rns:
        print(f"{rns} total Roman Numerals.")


def anacrusis_number_error(p: stream.Part
                           ) -> bool:
    """
    Check whether anacrustic measures are numbered correctly in a part.
    If the first measure is incomplete (not equal in length to that of the stated time signature)
    then it should be numbered 0; if complete, it should be 1.

    NB:
    - There are known false positives for certain cases like crossing staves (missing events)
    - Multiple voices are untested.

    :param p: a music21.stream.Part, pre-parsed.
    :return: bool, True in the case of an error.
    """
    msrs = p.getElementsByClass("Measure")
    m = msrs[0]

    if m.measureNumber == 0 and m.duration == m.barDuration:
        return True
    elif m.measureNumber == 1 and m.duration != m.barDuration:
        return True


def find_incomplete_measures(part: stream.Part
                             ) -> str:
    """
    Finds cases of "incomplete" measures as defined by a difference between the
    actual length of events in a measure and the nominal (time signature defined) length.

    False positives in cases like crossing staves (missing events)
    Untested: multiple voices. TODO: extract voice 1? Or forget parts and work directly on scores?

    :param part: a music21.stream.Part, pre-parsed
    :return: string with incomplete measure + first and last overall (not necessarily incomplete)
    """
    msrs = part.getElementsByClass("Measure")
    first = msrs[0].measureNumber
    last = msrs[-1].measureNumber
    incomplete = []
    for m in msrs:
        if m.duration != m.barDuration:  # i.e. actual length differs from nominal (ts) length
            incomplete.append(m.measureNumber)

    return f"Incomplete: {incomplete}; first: {first}; last {last}"


def find_incomplete_measures_corpus(corpus: str = "OpenScore-LiederCorpus",
                                    anacrusis_only: bool = True
                                    ) -> dict:
    """
    Run `anacrusis_number_error` or `find_incomplete_measures` on a whole corpus.
    :param corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
    :param anacrusis_only: bool. If True, only consider the first measure
    (i.e., run `anacrusis_number_error`), otherwise run `find_incomplete_measures`.
    :return: dict with file names as the keys.
    """

    # NB: corpus validity check in get_corpus_files
    files = get_corpus_files(corpus=corpus, file_name="score.mxl")
    out_dict = {}
    for file in files:
        print(f"Test: {file}")
        try:
            score = converter.parse(file)
            if anacrusis_only:
                out_dict[file] = anacrusis_number_error(score.parts[0])
            else:
                out_dict[file] = find_incomplete_measures(score.parts[0])
        except:
            print(f"Failed to parse {file}")

    if anacrusis_only:
        titles = [x for x in out_dict if out_dict[x]]
        titles.sort()
        print("ISSUES WITH:")
        [print(x) for x in titles]

    return out_dict


# ------------------------------------------------------------------------------

# script

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild_DCML_ABC", action="store_true")
    parser.add_argument("--rebuild_DCML_Mozart", action="store_true")
    parser.add_argument("--rebuild_remote_Beethoven_sonata_list", action="store_true")
    parser.add_argument("--rebuild_remote_Beethoven_variations_list", action="store_true")
    parser.add_argument("--rebuild_remote_Mozart_variations_list", action="store_true")
    args = parser.parse_args()
    if args.rebuild_DCML_ABC:
        convert_DCML_tsv_analyses(corpus="Quartets")
    elif args.rebuild_DCML_Mozart:
        convert_DCML_tsv_analyses(corpus="Piano_Sonatas")
    elif args.rebuild_remote_Beethoven_sonata_list:
        remote_scores()  # default
    elif args.rebuild_remote_Beethoven_variations_list:
        remote_scores(["Variations_and_Grounds", "Beethoven,_Ludwig_van", "_"])
    elif args.rebuild_remote_Mozart_variations_list:
        remote_scores(["Variations_and_Grounds", "Mozart,_Wolfgang_Amadeus", "_"])
    else:
        parser.print_help()
