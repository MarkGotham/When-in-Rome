# -*- coding: utf-8 -*-
"""
NAME:
===============================
Updates and Checks (updates_and_checks.py)

BY:
===============================
Mark Gotham

LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/

ABOUT:
===============================
Functions for updating entries to the "When in Rome" corpus of harmonic analyses, notably:
- creating "slices" and "template" files (from the score)
- producing "feedback" and "analysis_on_score" files (from a score and analysis pair)
- various checks.
See also "contents.py" for updating corpus contents lists.

"""

# ------------------------------------------------------------------------------

import os
import shutil

from pathlib import Path

from . import romanUmpire
from . import CORPUS_FOLDER
from . import get_corpus_files

from music21 import bar, converter, romanText, stream


# ------------------------------------------------------------------------------

def get_analyses(
        corpus: Path = CORPUS_FOLDER,
        all_versions: bool = True
) -> list:
    """
    Get analysis files across a corpus.
    (I.e., Convenience function for `get_corpus_files` on analyses.)

    :param corpus: the sub-corpus to run. Leave blank to run all corpora.
    :param all_versions: If True, get all analysis files ("analysis*txt"); if false, only get the
    "analysis.txt" files.
    :return: list of file paths.
    """

    f = "analysis.txt"
    if all_versions:
        f = "analysis*txt"
    return get_corpus_files(sub_corpus_path=corpus, file_name=f)


def rename_analyses(corpus: Path = CORPUS_FOLDER,
                    name_before: str = "analysis.txt",
                    name_after: str = "analysis_with_name.txt",
                    ) -> None:
    f = get_corpus_files(corpus, name_before)
    for file in f:
        shutil.move(file, file.parent / name_after)


def clear_the_decks(
        corpus: Path = CORPUS_FOLDER,
        file_types=None,
        delete: bool = True
) -> list:
    """
    When in Rome now supports many variant subsidiary files
    but does not include them by default.
    Having created them, use this to reset (delete).

    :param corpus: the sub-corpus to run. Leave blank to run all corpora.
    :param file_types: Which file types to delete or mark for deletion.
    :param delete: Bool. Delete or just report by returning the list.
    :return: list of the marked files.
    """

    if file_types is None:
        file_types = ["analysis_on_score.mxl", "slices.tsv", ]

    to_go = []

    for g in file_types:
        to_go += get_corpus_files(sub_corpus_path=corpus, file_name=g)

    for f in to_go:
        if delete:
            print("Removing: ", f)
            os.remove(f)

    return to_go


# ------------------------------------------------------------------------------

# Roman Umpire

def process_one_score(
        path_to_score: str | os.PathLike,
        path_to_analysis: str | os.PathLike | None = None,
        write_path: str | os.PathLike | None = None,
        combine: bool = True,
        slices: bool = True,
        feedback: bool = True,
        overwrite: bool = False
) -> None:
    """
    Processes one score to produce any or all of the following files:
    "analysis_on_score" (score files with analysis added in musical notation),
    "slices_with_analysis" (tsv representation that is a valid input for the Roman umpire and
    quicker to parse than musicXML), and
    "feedback" (txt written feedback on the score-analysis match).

    :param path_to_score: path to a file or simply the string
    :param path_to_analysis: path to a file or simply the string "On score" *** (see romanUmpire).
    :param write_path: where to write any new files to.
    :param combine: create an `analysis_on_score` file with the two combined.
    :param slices: create a "slices.tsv" representation.
    :param feedback: produce feedback on how the analysis matches the score (write to .txt)
    :param overwrite: if False and the file type already exists, don"t replace it.
    """

    if (not combine) and (not slices) and (not feedback):
        print("No action requested: set at least one of combine, slices, or feedback to true.")
        return

    if Path(path_to_score).exists():
        path_to_score = Path(path_to_score)
        if not path_to_score.is_relative_to(CORPUS_FOLDER):
            raise ValueError("The `path_to_score` argument must be within the corpus")
    elif (CORPUS_FOLDER / path_to_score).exists():
        path_to_score = CORPUS_FOLDER / path_to_score
    else:
        raise ValueError("The `path_to_score` argument is invalid.")

    if path_to_analysis is None:
        path_to_analysis = path_to_score
    if write_path is None:
        write_path = path_to_score

    t = romanUmpire.ScoreAndAnalysis(path_to_score / "score.mxl",
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


def process_corpus(
        corpus_name: str = "OpenScore-LiederCorpus",
        combine: bool = True,
        slices: bool = True,
        feedback: bool = True,
        overwrite: bool = False
) -> None:
    """
    Corpus wide implementation of `process_one_score`. See docs there.
    """
    analysis_paths = get_corpus_files(sub_corpus_path=CORPUS_FOLDER / corpus_name,
                                      file_name="analysis.txt")

    for p in analysis_paths:
        pth_to_dir = p.parent
        print("Processing: ", pth_to_dir)
        already_exist = os.path.exists(Path(pth_to_dir) / "analysis_on_score.mxl")
        if overwrite or (not already_exist):
            try:
                process_one_score(pth_to_dir,
                                  combine=combine,
                                  slices=slices,
                                  feedback=feedback,
                                  overwrite=overwrite)
                print("... done.")
            except Exception as e:
                print(f"... error: {e}")


# ------------------------------------------------------------------------------

# Automated analyses from augmentednet

def make_automated_analyses(
        corpus: Path = CORPUS_FOLDER
) -> None:
    """
    Create automated analyses using augmentednet (Nápoles López et al. 2021).
    :param corpus: the sub-corpus to run. Leave blank to run all corpora.
    :return: None

    TODO: untested draft based on (adapted from) https://github.com/MarkGotham/When-in-Rome/pull/47
    """

    from AugmentedNet.inference import batch, predict
    from AugmentedNet.utils import tensorflowGPUHack
    from tensorflow import keras

    tensorflowGPUHack()
    modelPath = "AugmentedNet.hdf5"
    model = keras.models.load_model(modelPath)

    files = get_corpus_files(sub_corpus_path=corpus,
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

# Checks

def repeats_are_valid(
        score: stream.Score,
        print_all: bool = True
) -> None:
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


def check_all_parse(
        corpus: Path = CORPUS_FOLDER,
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
    :param corpus: the sub-corpus to run. Leave blank to run all corpora.
    :param count_files: count+print the total number of analysis files (bool, optional).
    :param count_rns: count+print the total Roman numerals in all analysis files (bool, optional).
    """

    if analysis_not_score:
        files = get_analyses(corpus=corpus, all_versions=True)
    else:
        files = get_corpus_files(sub_corpus_path=corpus, file_name="score.mxl")

    if count_files:
        print(f"{len(files)} files found ... ")
        distinct_works = set([x.parts[:-1] for x in files])
        print(f"... on {len(distinct_works)} distinct works ...")

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


def anacrusis_number_error(
        p: stream.Part
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


def find_incomplete_measures(
        part: stream.Part
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


def find_incomplete_measures_corpus(
        corpus: Path = CORPUS_FOLDER,
        anacrusis_only: bool = True
) -> dict:
    """
    Run `anacrusis_number_error` or `find_incomplete_measures` on a whole corpus.
    :param corpus: the sub-corpus to run. Leave blank to run all corpora.
    :param anacrusis_only: bool. If True, only consider the first measure
    (i.e., run `anacrusis_number_error`), otherwise run `find_incomplete_measures`.
    :return: dict with file names as the keys.
    """

    # NB: corpus validity check in get_corpus_files
    files = get_corpus_files(sub_corpus_path=corpus, file_name="score.mxl")
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


def retrieve_unprocessed(
        s: stream.Score,
        tag: str = "Form"
) -> str:
    """
    Retrieve tagged but unprocessed information from a romanText file.

    Note that this complements the processed metadata.Metadata information
    which includes not only composer, title, etc.
    but also the "analyst" and "proofreader".

    Args:
        s (stream.Score): only makes sense if this stream is a parsed romantext analysis.
        tag (str): the tag to find. Defaults to "Form" for retrieving formal labels.
        Other options include further analyst annotations ("Note").

    Returns: str

    """
    unprocessed = s.recurse().getElementsByClass(romanText.translate.RomanTextUnprocessedMetadata)
    for u in unprocessed:
        if "tag" in u.__dict__:
            if u.__dict__["tag"] == tag:
                return u.__dict__["data"]


# ------------------------------------------------------------------------------

# script

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--process_one_score", action="store_true", )
    parser.add_argument("--process_corpus", action="store_true", )
    parser.add_argument("--check_all_parse", action="store_true", )
    parser.add_argument("--anthology", action="store_true", )

    parser.add_argument("--path_to_score", type=str,
                        required=False,
                        help="Path to score-analysis pair directory. "
                             "This can be specified entirely to the CORPUS_FOLDER.")
    parser.add_argument("--corpus", type=str,
                        required=False,
                        default="OpenScore-LiederCorpus",
                        help="Process all cases within this corpus path.")

    args = parser.parse_args()
    if args.process_one_score:
        process_one_score(path_to_score=args.path_to_score)
    elif args.process_corpus:
        process_corpus(corpus_name=args.corpus)
    elif args.check_all_parse:
        check_all_parse(corpus=args.corpus)
    elif args.anthology:
        from . import anthology
        anthology.all_searches_one_corpus(corpus=args.corpus)
    else:
        parser.print_help()
