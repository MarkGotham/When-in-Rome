# -*- coding: utf-8 -*-
"""
===============================
SKELETON HARMONY (skeletonHarmony.py)
===============================

Mark Gotham, 2020


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

To facilitate various Roman numeral analysis tasks.

Input options:
- a full analysis in the lyrics of a score, or
- a reduced score annotated with:
    Reduced chords given in lowest part(s);
    Lyrics explicitly labelling keys (modulation) and tonizations (secondary keys)

Output options:
1. analysis as data;
2. analysis as score with annotated analysis added;
3. analysis in Romantext format;
4. simple template from the score in Romantext format (no analysis at all);
in either Romantext cases (3, 4), this can be with or without a shorthand for measure equivalences.

"""

from copy import deepcopy
import fractions
import re

from music21 import chord
from music21 import key
from music21 import roman
from music21 import repeat


# ------------------------------------------------------------------------------

class RnAnalysis:
    """
    Roman numeral analysis.

    Takes in a score, and optionally:
        Roman numeral analysis from lyrics on that score (getAnnotationsAndLocations);
        or annotated reduction score (getAnnotationsAndLocations + chfyChordAndLabel);

    Returns:
        data;
        score (writeScore); or
        Romantext format (writeRomanText).

    Summary of all options:

    1.
    FROM: Score only
    TO: Romantext template directly;

    2.
    FROM: Score + full annotations (eg as lyrics)
    VIA: getAnnotationsAndLocations (ie full analysis)
    TO: Any output format (score, Romantext);

    3.
    FROM: Score + annotated reduction (keys and tonicizations only)
    VIA: getAnnotationsAndLocations and chfyChordAndLabel
    TO: Any output format (score, Romantext)
    """

    def __init__(self,
                 score,
                 analysisPartNo: int = -1,
                 templateParts="all",
                 # Annotations:
                 annotationTextClass: str = "Lyric",
                 adaptText: bool = True,
                 # Metadata:
                 composer: str = "",
                 title: str = "",
                 analyst: str = "",
                 proofreader: str = "",
                 notes: list = []
                 ):

        self.combinedList = []

        # Score, location of analysis, total measures
        self.score = score
        self.analysisPartNo = analysisPartNo  # Part number
        self.templateParts = templateParts
        measures = self.score.parts[0].getElementsByClass("Measure")
        self.firstMeasureNumber = measures[0].measureNumber
        if self.firstMeasureNumber not in [0, 1]:
            raise ValueError("The first measure number should be 1, or 0 for anacruses. "
                             f"It is currently {self.firstMeasureNumber}.")
        self.lastMeasureNumber = measures[-1].measureNumber

        self.timeSignatures = None
        self.timeSigMeasureDict = None
        self.getTSs()

        self.deducedAnalysis = None

        self.tempScore = None

        # Textual annotations
        self.annotationsAndLocations = None
        if annotationTextClass in ["Lyric", "TextExpression"]:
            self.annotationTextClass = annotationTextClass
        else:
            raise ValueError(f"The annotationTextClass (currently {annotationTextClass}) must be "
                             "either \"Lyric\" (default), or \"TextExpression\".")
        self.adaptText = adaptText

        # Metadata / preamble
        self.composer = composer
        self.title = title
        self.analyst = analyst
        self.proofreader = proofreader
        self.notes = notes
        self.preamble = []
        self.prepPreamble()

    def getTSs(self):
        """
        Retrieve all time signatures and make timeSignatures dict.
        """

        self.timeSignatures = self.score.parts[0].recurse().getElementsByClass("TimeSignature")
        self.timeSigMeasureDict = {}
        for x in self.timeSignatures:
            self.timeSigMeasureDict[x.measureNumber] = x.ratioString

    def prepPreamble(self):
        """
        Metadata for the filename and (if applicable) writeRoman. Priority order:
        1. User defined takes priority (no action here or below),
        2. Then anything retrievable from the score (see prepPreamble),
        3. Failing 1 and 2, placeholders.
        """

        if self.composer:  # default unless set
            self.preamble.append(f"Composer: {self.composer}")
        else:

            if self.score.metadata.composer:
                self.composer = self.score.metadata.composer  # overwrite
                self.preamble.append(f"Composer: {self.composer}")
            else:
                self.composer = "Unknown"
                self.preamble.append("Composer: ")

        if self.title:
            self.preamble.append(f"Title: {self.title}")

        else:
            workingTitle = []

            if self.score.metadata.title:
                workingTitle.append(self.score.metadata.title)
            if self.score.metadata.movementNumber:
                workingTitle.append(f"- No.{self.score.metadata.movementNumber}:")  # Spaces later
            if self.score.metadata.movementName:
                if self.score.metadata.movementName != self.score.metadata.title:
                    workingTitle.append(self.score.metadata.movementName)

            if len(workingTitle) > 0:
                self.title = " ".join(workingTitle)
                self.preamble.append(f"Title: {self.title}")
                # then adjustments for use as filename:
                self.title = self.title.replace(".", "")
                self.title = self.title.replace(":", "")
                self.title = self.title.replace(" ", "_")
            else:
                self.title = "Unknown"
                self.preamble.append("Title: ")

        self.preamble.append(f"Analyst: {self.analyst}")
        self.preamble.append(f"Proofreader: {self.proofreader}")

        if self.notes:
            for nt in self.notes:
                self.preamble.append(f"Note: {nt}")

    # ------------------------------------------------------------------------------

    # For on-score analysis

    def getAnnotationsAndLocations(self):
        """
        Retrieve analytical text from a user-specified:
            part (self.analysisPartNo, the lowest part of a score by default); and
            class (lyrics on notes in that part by default, alternatively text expressions).
        Used whether the input is a full analysis or just a reduction.
        """

        self.annotationsAndLocations = []

        if self.annotationTextClass == "Lyric":
            for n in self.score.parts[self.analysisPartNo].recurse().notes:
                if n.lyric:
                    txt = n.lyric
                    if self.adaptText:
                        txt = fixTextRn(txt)

                    self.annotationsAndLocations.append([n.measureNumber, n.beat, txt])

        else:  # self.annotationTextClass == "TextExpression":
            for elem in self.score.parts[self.analysisPartNo].recurse():
                if "TextExpression" in elem.classes:
                    txt = elem.content  # Note
                    if self.adaptText:
                        txt = fixTextRn(txt)

                    self.annotationsAndLocations.append([elem.measureNumber, elem.beat, txt])

    # ------------------------------------------------------------------------------

    # For partial analysis (deductions)

    def chfyChordAndLabel(
            self,
            ignoreParts: int = 2,
            tonicizationsRemainInEffect: bool = False,
            prefer_secondary: bool = False
    ):
        """
        To use in the case of a partial analysis with chords and key information.

        Takes each successive chord and key/tonicization labelling lyric,
        works out the chord, and either
        returns that as data, or
        as appended to the score in question.

        Note that changes of key remain in effect until the next marking, but
        changes of tonicizations do not by default (settable with tonicizationsRemainInEffect).

        That said, you may want to put in reminders of the prevailing key occasionally
        (after a tonicization, or indeed elsewhere);
        that is fine and does not make any different to the analysis.
        """

        self.deducedAnalysis = []

        reduction = deepcopy(self.score)
        for x in range(ignoreParts):
            reduction.remove(reduction.parts[0])  # Top parts of the original score

        self.chfyScore = reduction.stripTies().chordify()
        self.chfyScore.partName = "Roman"

        currentIndex = 0  # Index
        currentKey = "FAKE KEY"  # Initialise empty for inclusion of the first key
        currentTonicization = None

        if not self.annotationsAndLocations:
            self.getAnnotationsAndLocations()

        keyData = self.annotationsAndLocations
        lenKeyData = len(keyData)

        for ch in self.chfyScore.recurse().notes:

            startKey = currentKey
            if not tonicizationsRemainInEffect:
                currentTonicization = None  # reset for each chord

            # Key Changes and Tonicization
            if lenKeyData > currentIndex and [ch.measureNumber, ch.beat] == keyData[currentIndex][
                                                                            0:2]:
                stringInQuestion = keyData[currentIndex][2]  # Before updating current index
                currentIndex += 1
                if "/" in stringInQuestion:  # Indicates a local tonicization (X/Y)
                    rnFigureString, currentTonicization = stringInQuestion.split("/")
                    # TODO make use of any rnFigureString specified?
                    # TODO support e.g. "/g" as well as (and converting it to) relative ("/ii")
                elif ":" in stringInQuestion:  # modulation
                    currentKey, rnFigureString = stringInQuestion.split(":")
                    # TODO make use of any rnFigureString specified?
                else:
                    x = re.search("[a-gA-G]", stringInQuestion[0])
                    if x:  # modulation without RN. Note we don't suport Fr43 or Ger65 (start F, G)
                        currentKey = stringInQuestion
                        currentTonicization = None
                    else:
                        # TODO accept anything else as a full, user-defined Roman numeral?
                        raise ValueError(f"Unrecognised entry {stringInQuestion} "
                                         f"in measure {ch.measureNumber}, "
                                         f"beat {ch.beat}")

            if not currentTonicization:
                rn = roman.romanNumeralFromChord(ch,
                                                 key.Key(currentKey),
                                                 preferSecondaryDominants=prefer_secondary)
            else:  # currentTonicization
                localKey = getLocalKey(currentTonicization, currentKey)
                rn = roman.romanNumeralFromChord(ch,
                                                 key.Key(localKey),
                                                 # sixthMinor=roman.Minor67Default.CAUTIONARY,
                                                 # seventhMinor=roman.Minor67Default.CAUTIONARY,
                                                 )  # TODO: issues with sixth and seventh minor

            lyric = str(rn.figure)

            # Lyric modifications. Otherwise the lyric is unchanged
            if startKey != currentKey:
                lyric = currentKey + ": " + lyric
            elif currentTonicization:
                lyric = lyric + stringInQuestion

            ch.lyric = lyric

            thisData = [ch.measureNumber, ch.beat, lyric]
            self.deducedAnalysis.append(thisData)

    # ------------------------------------------------------------------------------

    def makeMeasureStrings(self):
        """
        Takes information from lists of [measure, beat, chord]
        retrieved by either getAnnotationsAndLocations or chfyChordAndLabel
        and converts it into separate rntxt strings to print for each measure
        stored in a dict such that dict[measureNumber] = string.
        """

        if self.deducedAnalysis:  # Not doing the deductions here.
            infoToUse = self.deducedAnalysis
        else:  # If not self.deducedAnalysis, then we are not doing the deductions ...
            if not self.annotationsAndLocations:
                self.getAnnotationsAndLocations()  # ... and that the full analysis is on score
            infoToUse = self.annotationsAndLocations

        firstMeasure = infoToUse[0][0]

        currentMeasure = firstMeasure
        currentString = None

        self.analysisDict = {}

        for item in infoToUse:
            measureX = item[0]

            if measureX == currentMeasure:  # continue an existing string
                currentString = rnString(item, inString=currentString)
            else:
                self.analysisDict[currentMeasure] = currentString  # Save previous string ...
                currentString = rnString(item)  # ... and start a new one.
            currentMeasure = measureX

        # Special case of last entry. Note currentMeasure = measureX so either is fine.
        self.analysisDict[currentMeasure] = currentString

    # ------------------------------------------------------------------------------

    # From rntxtTemplate

    def getRepeats(self,
                   threshold: int = 1):
        """
        Finds equivalent passages (e.g. song verses) to avoid duplicating the same material
        and to encourage (but not require!) parallel analyses for identical passages.

        Works by comparing measures of the whole score using music21"s RepeatFinder.

        Optionally: reduce the parts to consider in the comparison by specifying "partsToRemove".
        This removes parts from the bottom of the score (in the expectation of parts
        corresponding to the "analysis" parts of the romanUmpire.ScoreAndAnalysis).

        Notes for using the RepeatFinder:
        1.
        Key changes not preserved for the part following a measure range equality.
        This can lead to errors if the key changes in the latter case but is not specified in the
        former (continues prevailing), or if
        they both change to the same key from different previous keys.
        In that case either:
        - adjust the moment of repetition to include the key change explicitly, or
        - reiterate (specify the apparently redundant) key at the start of the compared from entry.
        Best to just make a habit of specifying the key at the start of and after every measure
        range equality.
        2.
        Similar issues with TimeSignature changes during the measure range.

        Here, getRepeats sets measureRangeEqualities.
        """

        self.processTemplateParts()

        simMGs = repeat.RepeatFinder(self.tempScore).getSimilarMeasureGroups(threshold=threshold)

        # Separate into static function def simplify() for getting
        # from list of contiguous measures to "From-to = from-to" pairs
        self.measureRangeEqualities = {}
        for rangeComp in simMGs:
            simplified = [rangeComp[1][0], rangeComp[1][-1], rangeComp[0][0], rangeComp[0][-1]]
            self.measureRangeEqualities[simplified[0]] = simplified

    def processTemplateParts(self):
        """
        Checks the parts to consider for the template and processes them if necessary and valid.
        """

        msg = f"The templateParts (currently {self.templateParts}) " \
              "must be either the string \"all\" (default) or a list of non-negative integers " \
              "corresponding to the part number in the score (counting from 0)."

        if self.templateParts == "all":
            self.tempScore = self.score  # No adjustment, so avoid (no need to) deepcopy
            return
        else:
            if not isinstance(self.templateParts, list):
                raise ValueError(msg)
            else:  # It is a list
                for x in self.templateParts:
                    if not isinstance(x, int):
                        raise ValueError(msg)
                    if x < 0:
                        raise ValueError(msg)

            self.tempScore = deepcopy(self.score)

            partsToRemove = []
            for x in range(len(self.score.parts)):  # TODO: part number attribute?
                if x not in self.templateParts:
                    partsToRemove.append(x)

            for x in partsToRemove[::-1]:  # Note: reverse order is important
                self.tempScore.remove(self.score.parts[x])

    def prepList(self,
                 template: bool = True):
        """
        Prepares a list of text lines that will be written to rntxt by writeRomanText().
        Both methods are used for both full analyses and templates.

        In either case, this integrates score information including:
        - timeSignatures (including changes)
        - repeat ranges (if getRepeats has been called and only as `Notes:`)

        Args:
            template (bool): If True, write a template file with metadata, measures, but no more.
                             If False, full analysis extracted from the score.
        """
        # TODO: option for removing duplicate analysis from repeat passages
        # TODO: similar option for recurring harmonies (repeats on the rntxt)?

        tsMeasures = self.timeSigMeasureDict.keys()

        self.getRepeats()  # Sets measureRangeEqualities
        measureRangeEqualityStarts = self.measureRangeEqualities.keys()

        if not template:
            self.makeMeasureStrings()

        for x in range(self.firstMeasureNumber, self.lastMeasureNumber + 1):

            # Time signatures (whether a template or not)
            if x in tsMeasures:  # First, before corresponding measure analysis
                ts = self.timeSigMeasureDict[x]
                self.combinedList.append(f"\nTime Signature: {ts}")

            # Measure range equalities (currently a duplicate)
            if x in measureRangeEqualityStarts:
                entry = self.measureRangeEqualities[x]
                if entry[0] == entry[1]:  # Single measure comparison
                    self.combinedList.append(f"Note: m{entry[0]} = m{entry[2]}")
                else:  # Measure range comparison
                    self.combinedList.append(
                        f"Note: m{entry[0]}-{entry[1]} = m{entry[2]}-{entry[3]}")

            # Measure lines (analysis where provide; empty for template)
            if template:
                self.combinedList.append(f"m{x} b1")
            else:
                if x in self.analysisDict.keys():
                    self.combinedList.append(self.analysisDict[x])
                # else:  # Not template and annotation in this measure, leave blank

    # ------------------------------------------------------------------------------

    # To write

    def writeRomanText(self,
                       outPath: str = "./",
                       fileName: str = ""):
        """
        Writes the combined information to a .txt file.
        Use for both full analyses and templates.
        """

        if not self.combinedList:
            self.prepList()

        if not fileName:  # Never an empty string: placeholders set by prepPreamble as needed.
            fileName = f"{self.composer}_-_{self.title}"

        text_file = open(f"{outPath}{fileName}.txt", "w")
        [text_file.write(entry + "\n") for entry in self.preamble]
        [text_file.write(entry + "\n") for entry in self.combinedList]
        text_file.close()

    def writeScore(self,
                   outPath: str = "./",
                   fileName: str = ""):
        """
        Writes a score.
        Intended for the score with Roman numeral analysis added.
        Note: chfyChordAndLabel() will run if it has not run already.
        """

        if not self.chfyScore:
            self.chfyChordAndLabel()
        self.score.insert(self.chfyScore)

        if not fileName:
            fileName = self.title
        self.score.write(fp=f"{outPath}{fileName}.musicxml")


# ------------------------------------------------------------------------------

# Static functions

def getLocalKey(local_key: chord.Chord,
                global_key: key.Key):
    """
    Works out the quality (major / minor) of a local key relative to a global one
    Note similar to a function in romanText.tsvConverter.
    """
    asRoman = roman.RomanNumeral(local_key, global_key)
    rt = asRoman.root().name
    if asRoman.isMajorTriad():
        return rt.upper()
    elif asRoman.isMinorTriad():
        return rt.lower()
    else:  # TODO check redundancy - keys checks (and potential fails) in roman.RomanNumeral
        raise ValueError(f"The local_key (currently {local_key}) must be a major or minor triad.")


def fixTextRn(textRn: str):
    """
    Adjusts a prospective Roman numeral string such that music21 will accept it.

    Mainly, this serves to remove any characters other than
    a-g, A-G, "i", "I", "v", "V",
    "#", "b", "-", ":", and
    Arabic numerals (0-9).
    This includes removing hidden non-printing characters like the non-breaking space ("\xc2\xa0").

    This also includes swaps that would be covered in music21, such as:
    "/o" for ø and "°" for "o".

    Finally, it also ensures that there is exactly one space after a colon.
    Music21"s Roman text reader can handle excessive spaces, but not a missing one.
    """
    # TODO: regex instead?

    swapDict = {"/o": "ø",  # e.g. vii/o7 >  viiø7
                "°": "o",  # e.g. ii°6 > iio6
                "(": "[",  # For [no5] style additions
                ")": "]",  # "
                }

    legalCharacters = ["#", "b", "-",
                       "+", "o", "ø",
                       ":", "[", "]", "/",

                       "a", "b", "c", "d", "e", "f", "g",
                       "i", "v",
                       "n",  # for "[no3]"

                       "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    # Swaps, replacements, and removals
    for k in swapDict.keys():
        if k in textRn:
            textRn = textRn.replace(k, swapDict[k])

    for char in textRn:
        if char.lower() not in legalCharacters:
            textRn = textRn.replace(char, "")

    # Exactly one space after any colons, all previous spaces having being removed
    textRn = textRn.replace(":", ": ")

    return textRn


def rnString(measureBeatStringList: list,
             inString: str = ""):
    """
    Write the start of a line of RNTXT.
    To start a new line (one per measure with measure, beat, chord),
    set inString = None.
    To extend an existing line (measure already given),
    set inString to that existing list.
    """

    if not inString:  # New line
        inString = "m" + str(measureBeatStringList[0])

    bt = measureBeatStringList[1]
    bt = intBeat(bt)
    if bt == 1:
        return " ".join([inString, str(measureBeatStringList[2])])
    else:
        return inString + " b" + str(bt) + " " + str(measureBeatStringList[2])


def intBeat(beat,
            roundValue: int = 2):
    """
    Converts beats to integers if possible, and otherwise to rounded decimals.
    Accepts input as string, int or float.
    """

    options = [str, int, float, fractions.Fraction]

    if type(beat) not in options:
        raise ValueError(f"Beat, (currently {beat}) must be one of {options}.")

    if type(beat) in [str, fractions.Fraction]:
        beat = float(beat)

    if int(beat) == beat:
        return int(beat)
    else:
        return round(float(beat), roundValue)


# ------------------------------------------------------------------------------

if __name__ == "__main__":

    import argparse
    from music21 import converter

    parser = argparse.ArgumentParser()

    parser.add_argument("--process_one_score", action="store_true", )
    parser.add_argument("path_to_score",
                        type=str,
                        required=False,
                        help="Path to a skeletal analysis within the meta-corpus.")

    args = parser.parse_args()

    if args.process_one_score:
        score = converter.parse(args.path_to_score)
        analysis = RnAnalysis(score)
        analysis.chfyChordAndLabel(ignoreParts=2)
        analysis.prepList(template=False)
        analysis.writeRomanText()

    else:
        parser.print_help()
