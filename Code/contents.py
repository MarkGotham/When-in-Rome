# -*- coding: utf-8 -*-
"""
===============================
Contents (contents.py)
===============================

Mark Gotham, 2020


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

A simple script for keeping track of the "When in Rome" corpus collection.
See also `updates_and_checks.py` for populating the corpus.

As this corpus builds up incrementally from a range of sources:

1. collections may or may not be complete
e.g., The BPS dataset (Chen and Su, 2018) covers the first movements of Beethoven Piano sonatas.

2. scores may or may not be included
If not, "remote_score.json" files are provided instead.

3. where a full set of scores is available those scores may not have been analysed
(only a fraction the > 1,000 lieder have analyses).

Most metadata is retrieved from the directory structure, with optional extras which
require score parsing to retrieve (movement length and initial time and key signatures).

"""


# ------------------------------------------------------------------------------

import fnmatch
import os
import csv

from music21 import converter
from typing import Optional, List


# ------------------------------------------------------------------------------

def makeContentsSV(corpus: str = "OpenScore-LiederCorpus",
                   startWithAnalyses: bool = True,
                   checkForBothScoreAndAnalysis: bool = True,
                   additionalInfo: bool = False,
                   composers: Optional[List] = [],
                   write: bool = True):
    """
    Create a list of lists with the contents of a corpus and (optionally) write to an SV file.

    :param corpus: one of the corpora in the "When in Rome" repository, so one of
        "Early_Choral",
        "Etudes_and_Preludes",
        "OpenScore-LiederCorpus",
        "Orchestral",
        "Piano_Sonatas",
        "Quartets",
        "Variations_and_Grounds".
    :param startWithAnalyses: by default, find all "analysis.txt" files, and (optionally)
        check for whether there"s a corresponding "score.mxl" file hosted locally.
        Setting this parameter to False flips this search, i.e.
        start with scores, optionally find analyses.
    :param checkForBothScoreAndAnalysis: set to False to ignore the "other" file type
        (score or analysis as defined by startWithAnalyses).
    :param additionalInfo: Retrieve additional metadata from the score.
        In all cases, this means the first time and key signatures.
        For the lieder, it will also retrieve the lyricist (stored in score metadata).
    :param composers: (Optionally) restrict the search to this list of composers.
    :param write: Create an SV file and write to the corpus (note: paths hard coded).
    """

    corpora = ["Early_Choral",
               "Etudes_and_Preludes",
               "OpenScore-LiederCorpus",
               "Orchestral",
               "Piano_Sonatas",
               "Quartets",
               "Variations_and_Grounds"]

    if corpus not in corpora:
        raise ValueError(f"Corpus (currently {corpus}) must be one of {corpora}.")

    lied = False
    if corpus == "OpenScore-LiederCorpus":  # Lieder-specific entries, checked several times
        lied = True

    data = []
    rootPath = os.path.join(os.path.dirname((os.path.realpath(__file__))), "..", "Corpus")
    corpusPath = os.path.join(rootPath, corpus)

    primary, secondary = "analysis.txt", "score.mxl"
    if startWithAnalyses:
        additionalHeader = "SCORE"
    else:
        primary, secondary = secondary, primary
        additionalHeader = "ANALYSIS"

    for root, dirs, files in os.walk(corpusPath):
        for name in files:
            if fnmatch.fnmatch(name, primary):
                primaryPath = str(os.path.join(root, name))
                thisEntry = primaryPath.split("/")[-4:-1]

                if checkForBothScoreAndAnalysis:
                    secondaryPath = primaryPath.replace(name, secondary)
                    if os.path.exists(secondaryPath):
                        thisEntry.append("YES")
                    else:
                        remotePath = secondaryPath.replace(secondary, "remote_score.json")
                        if os.path.exists(remotePath):
                            thisEntry.append("REMOTE")
                        else:
                            thisEntry.append("N")

                if additionalInfo:
                    analysisPath, scorePath = primaryPath, secondaryPath
                    if not startWithAnalyses:
                        scorePath, analysisPath = analysisPath, scorePath
                    if os.path.exists(scorePath):
                        score = converter.parse(secondaryPath)
                    else:
                        score = converter.parse(analysisPath, format="Romantext")

                    thisEntry.append(str(score.parts[0].quarterLength))

                    p0m1 = score.parts[0].measures(0, 3)
                    firstTS = p0m1.recurse().getElementsByClass("TimeSignature")[0]
                    thisEntry.append(firstTS.ratioString)
                    firstKS = p0m1.recurse().getElementsByClass("KeySignature")[0]
                    thisEntry.append(str(firstKS.sharps))

                    if lied:
                        lyricist = score.metadata.lyricist
                        if not lyricist:
                            lyricist = "[Missing entry]"
                        thisEntry.append(lyricist)

                if lied:
                    url = ""
                    pathtoFolder = primaryPath[:-len(primary)]
                    for fileName in os.listdir(pathtoFolder):
                        if fnmatch.fnmatch(fileName, "lc*.mscx"):
                            lcNumber = fileName[2:-5]  # cut "lc" and extension
                            url = "https://musescore.com/score/" + lcNumber
                            break
                    if not url:  # failed to find one, use generic url for the set instead
                        url = "https://musescore.com/openscore-lieder-corpus/scores/"
                    thisEntry.append(url)

                data.append(thisEntry)

    if composers:
        data = [x for x in data if x[0] in composers]

    sortedData = sorted(data, key=lambda x: (x[0], x[1], x[2]))

    if write:

        title = corpus + "_contents" + ".tsv"

        with open(os.path.join(rootPath, title), "w") as csvfile:
            csvOut = csv.writer(csvfile, delimiter="\t",
                                quoting=csv.QUOTE_MINIMAL)

            headers = ["COMPOSER", "COLLECTION", "MOVEMENT"]
            if checkForBothScoreAndAnalysis:
                headers += [additionalHeader]
            if additionalInfo:
                headers += ["QUARTER LENGTH", "1ST TIME SIG", "1ST KEY SIG"]
                if lied:
                    headers.append("LYRICIST")
            if lied:
                headers.append("URL")

            csvOut.writerow(headers)
            for entry in sortedData:
                csvOut.writerow([x.replace("_", " ") for x in entry if x])

    return sortedData


def runAll():
    for corpus in ["Early_Choral",
                   "Etudes_and_Preludes",
                   "OpenScore-LiederCorpus",
                   "Orchestral",
                   "Piano_Sonatas",
                   "Quartets",
                   "Variations_and_Grounds"]:
        makeContentsSV(corpus,
                       startWithAnalyses=True,
                       checkForBothScoreAndAnalysis=True,
                       additionalInfo=False)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    runAll()
