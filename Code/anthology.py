# -*- coding: utf-8 -*-
"""

NAME:
===============================
Anthology (anthology.py)

BY:
===============================
Mark Gotham


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Methods for retrieving specific Roman numerals and/or progressions from analyses.

NOTE: musical logic previously here (isNeapolitan and isMixture) now moved to the main
music21 repo [roman.py](https://github.com/cuthbertLab/music21/blob/master/music21/roman.py)

"""

from music21 import bar, converter, instrument, interval, layout, metadata, roman, stream, tempo
from pathlib import Path

import csv
from . import CORPUS_FOLDER, REPO_FOLDER, get_corpus_files, harmonicFunction
from .Pitch_profiles.chord_usage import careful_consolidate


# ------------------------------------------------------------------------------

class RnFinder(object):
    """
    For retrieving specific Roman numerals and/or progressions from analyses.
    Separate methods on this class per search term (e.g., `find_mixtures`).
    Results stored in attributes (e.g., `mixtures`)
    that are lists of dicts returns by dataFromRn.
    """

    def __init__(self,
                 pathToFile: str | Path):

        self.user_progression = []
        self.augmented_chords = []
        self.augmented_sixths = []
        self.neapolitan_sixths = []
        self.applied_chords = []
        self.mixtures = []

        self.analysis = converter.parse(pathToFile, format="romanText")
        self.rns = [x for x in self.analysis.recurse().getElementsByClass("RomanNumeral")]

    def find_mixtures(self):
        """
        NOTE: musical logic previously here now moved to the main music21 repo.
        """

        for rn in self.rns:
            if not rn.secondaryRomanNumeral:
                if rn.isMixture():
                    self.mixtures.append(data_from_Rn(rn))

    def find_applied_chords(self,
                            require_dominant_function: bool = True):
        for rn in self.rns:
            if is_applied_chord(rn, require_dominant_function=require_dominant_function):
                self.applied_chords.append(data_from_Rn(rn))

    def find_Neapolitan_sixths(self):
        """
        NOTE: musical logic previously here now moved to the main music21 repo
        """

        for rn in self.rns:

            if rn.isNeapolitan(require1stInversion=False):
                self.neapolitan_sixths.append(data_from_Rn(rn))

    def find_augmented_sixths(self):
        """
        NOTE:
            includes those literally called `Ger65` etc.,
            but also de facto cases like `V43[b5]`.
        """

        for rn in self.rns:
            #
            if rn.isAugmentedSixth():
                self.augmented_sixths.append(data_from_Rn(rn))

    def find_augmented_chords(self,
                              acceptSevenths: bool = True,
                              requireAugAsTriad: bool = True):

        """
        Finds cases of augmented triads (e.g. III+) in any inversion.

        If acceptSevenths is True (default) then also seeks cases of
        sevenths containing an augmented triad.

        If requireAugAsTriad is True (default), then limit these sevenths to cases
        where the augmented triad is the triad (with an added sevenths), e.g. V+7.
        If not, accept cases where the augmented triad is
        formed by the 3rd, 5th and 7th of the chord (e.g. minor-major sevenths).
        """

        for rn in self.rns:
            if rn.isAugmentedTriad():
                self.augmented_chords.append(data_from_Rn(rn))
            elif acceptSevenths:
                if rn.isSeventh:
                    if rn.isSeventhOfType([0, 4, 8, 11]) or rn.isSeventhOfType([0, 4, 8, 10]):
                        self.augmented_chords.append(data_from_Rn(rn))
                    elif not requireAugAsTriad:
                        if rn.isSeventhOfType([0, 3, 7, 11]):
                            self.augmented_chords.append(data_from_Rn(rn))

    def find_rn_progression(self,
                            rns_list: list[str]):
        """
        Find a specific progression of Roman numerals in a given key input by the user as
        a list of Roman numeral figures like ["I", "V65", "I"]
        """

        lnrns = len(rns_list)

        for overallIndex in range(len(self.rns) - lnrns):
            thisRange = self.rns[overallIndex: overallIndex + lnrns]

            keysInThisRange = [x.key for x in thisRange]
            distinctKeys = set(keysInThisRange)
            if len(distinctKeys) > 1:  # modulates
                break

            figures = [x.figure for x in thisRange]
            if figures == rns_list:
                # Variant on dataFromRn
                info = [thisRange[0].getContextByClass("Measure").measureNumber,
                        figures,
                        thisRange[0].key]

                self.user_progression.append(info)

    def find_prog_by_qual_and_intv(
            self,
            qualitiesList: list,
            intervalList: list[str | interval.Interval] = None,
            bassOrRoot: str = "bass",
    ):
        """
        Find a specific progression of Roman numerals
        searching by chord type quality and (optionally) bass or root motion.

        For instance, to find everything that might constitute a ii-V-I progression
        (regardless of whether those are the exact Roman numerals used), search for
        qualitiesList=["Minor", "Major", "Major"], intervalList=["P4", "P-5"]. bassOrRoot="root")

        This method accepts many input types.
        For the range accepted by qualitiesList,
        see documentation at is_of_type().

        Blank entries are also fine.
        For instance, to find out how augmented chords resolve, search for
        qualitiesList=["Augmented triad", ""].
        To add the preceding chord as well, expand to:
        qualitiesList=["", "Augmented triad", ""].
        Note that intervalList is left unspecified (we are interested in any interval succession.
        Anytime the intervalList is left blank, the search runs on quality only.
        """

        lnQs = len(qualitiesList)

        if intervalList:
            if lnQs != len(intervalList) + 1:
                raise ValueError("There must be exactly one more chord than interval.")

        # 1. Search quality match first: quality is required
        for index in range(len(self.rns) - lnQs):
            theseRns = self.rns[index: index + lnQs]
            for i in range(lnQs):
                if not is_of_type(theseRns[i], qualitiesList[i]):
                    continue  # TODO check
            # 2. Only search for interval match if required and if the qualities already match.
            if intervalList:
                if interval_match(theseRns, intervalList, bassOrRoot):
                    info = data_from_Rn(self.rns[index])
                    info["FIGURE"] = [x.figure for x in theseRns]
                    self.user_progression.append(info)

    def find_Cto_dim7(
            self,
            require_prolongation: bool = True
    ):
        """
        Find a potential instance of the common tone diminished seventh in any form by seeking:
        a diminished seventh,
        which shares at least one pitch with
        the chord before, the one after, or both.

        If require_prolongation is True, the results are limited to cases where the
        diminished seventh is preceded and followed by the same chord.
        """

        for index in range(1, len(self.rns) - 1):

            this_chord = self.rns[index]

            if this_chord.isDiminishedSeventh():

                if is_potential_Cto_Dim_7(
                        self.rns[index - 1],
                        this_chord,
                        self.rns[index + 1],
                        require_prolongation=require_prolongation
                ):
                    self.user_progression.append(data_from_Rn(this_chord))


# ------------------------------------------------------------------------------

# Static functions for progressions

def is_applied_chord(
        rn: roman.RomanNumeral,
        require_dominant_function: bool = True
):
    """
    Applied chords suggest a local tonic chord other than the home tonic.
    (see https://viva.pressbooks.pub/openmusictheory/chapter/tonicization/)

    Typically, these take the form of a
    secondary dominant - i.e., `V(7)/x` - or
    secondary leading-tone - `viio(7)/x` chord,
    where x is the secondary tonality.

    Args:
        rn (roman.RomanNumeral): The roman.RomanNumeral object to consider.
        require_dominant_function (bool): Require that the applied chord has dominant function.
    """
    if not rn.secondaryRomanNumeral:
        return False
    if require_dominant_function:
        f = harmonicFunction.figureToFunction(rn.romanNumeral)  # NB not figure
        return f == "D"

    # TODO: consider options for requiring:
    #     Resolution: rn.next() == rn.secondaryRomanNumeral.figure is diatonic.
    #     Diatonic: rn.secondaryRomanNumeral.figure is diatonic.


def is_potential_Cto_Dim_7(
        chord_before: roman.RomanNumeral,
        diminished_seventh: roman.RomanNumeral,
        chord_after: roman.RomanNumeral,
        require_prolongation: bool = True):
    """
    Find a potential instance of the common tone diminished seventh in any form by seeking:
    a diminished seventh,
    which shares at least one pitch with
    the chord before, the one after, or both.

    This function works entirely by pitch class content and so
    chord spelling is not considered, nor the relation to keys.
    E.g., V in C and I in G are equivalent.

    Args:
        chord_before: the roman.RomanNumeral object immediately preceding.
        diminished_seventh: the roman.RomanNumeral object that is a possible Cto7.
        chord_after: the roman.RomanNumeral object immediately following.
        require_prolongation (bool): diminished seventh is preceded and followed by the same chord
            (as defined by the pitch content, again not inversion or spelling).
    """
    if chord_before.isDiminishedSeventh():
        return False
    if not diminished_seventh.isDiminishedSeventh():
        return False
    if chord_after.isDiminishedSeventh():
        return False

    pcs_before = set([p.pitchClass for p in chord_before.pitches])
    pcs_now = set([p.pitchClass for p in diminished_seventh.pitches])
    pcs_after = set([p.pitchClass for p in chord_after.pitches])

    if require_prolongation:
        if pcs_before != pcs_after:
            return False

    if pcs_now & pcs_before:  # any shared pitch(class)
        return True

    if pcs_now & pcs_after:  # any shared pitch(class)
        return True


# ------------------------------------------------------------------------------

# Other Static

def data_from_Rn(
        rn: roman.RomanNumeral,
        consolidate: bool = True
) -> dict:

    if consolidate:
        fig = careful_consolidate(rn.figure,
                                  major_not_minor=(rn.key.mode == "major"),
                                  rn=rn
                                  )
    else:
        fig = rn.figure

    return {"MEASURE": rn.getContextByClass("Measure").measureNumber,
            "FIGURE": fig,
            "KEY": rn.key.name.replace("-", "b"),
            "BEAT": rn.beat,
            "BEAT STRENGTH": rn.beatStrength,
            "LENGTH": rn.quarterLength}


def is_of_type(this_chord, query_type):
    """
    Tests whether a chord (this_chord) is of a particular type (query_type).

    There are only two match criteria.
    First chords must have the same normal order.
    This means that C major and D major do match (transposition equivalence included),
    but C major and c minor do not (inversion equivalence excluded).
    Second, relevant pitch spelling must also match, so
    dominant sevenths do not match German sixth chords.

    this_chord can be a chord.Chord object
    or a roman.RomanNumeral (which inherits from chord.Chord).
    Raises an error otherwise.

    The query_type can be in almost any format.
    First, it can also be a chord.Chord object, including the same object as this_chord:
    >>> majorTriad = chord.Chord("C E G")
    >>> is_of_type(majorTriad, majorTriad)
    True

    Second, is anything you can use to create a chord.Chord object, i.e.
    string of pitch names (with or without octave), or a list of
    pitch.Pitch objects,
    note.Note objects,
    MIDI numbers, or
    pitch class numbers.
    It bear repeating here that transpositon equivalence is fine:
    >>> is_of_type(majorTriad, [2, 6, 9])
    True

    # TODO: implement chord.fromCommonName then add this:
    # Third, it can be any string returned by music21.chord.commonName.
    # These include fixed strings for
    # single pitch chords (including "note", "unison", "Perfect Octave", ...),
    # dyads (e.g. "Major Third"),
    # triads ("minor triad"),
    # sevenths ("dominant seventh chord"), and
    # other special cases ("all-interval tetrachord"),
    # The full list (based on one by Solomon) can be seen at music.chord.tables.SCREF.
    # TODO >>> is_of_type(majorTriad, "whole tone scale")
    # TODO False
    #
    >>> wholeToneChord = chord.Chord([0, 2, 4, 6, 8, 10])
    #
    # TODO >>> is_of_type(wholeToneChord, "whole tone scale")
    # TODO True
    #
    # Additionally, chord.commonName supports categories of strings like (fill in the <>)
    # "enharmonic equivalent to <>",
    # "<> with octave doublings",
    # "forte class <>", and
    # "<> augmented sixth chord" (and where relevant) "in <> position".
    # TODO >>> is_of_type(wholeToneChord, "forte class <>" )
    # True
    #
    # As with chord.commonName, chords with no common name return the Forte Class
    # so that too is a valid entry (but only in those cases).
    # Any well-formed Forte Class string is acceptable, as is the format "forte class 6-36B",
    # (which chord.commonName returns for cases with no common name):
    # TODO >>> is_of_type(wholeToneChord, "6-35")
    # True

    Raises an error if the query_type is (still!) not valid.
    """
    from music21 import chord

    if "Chord" not in this_chord.classes:
        raise ValueError("Invalid this_chord: must be a chord.Chord object")

    # Make reference (another chord.Chord object) from query_type
    reference = None
    try:
        reference = chord.Chord(query_type)
        # accepts string of pitches;
        # list of ints (normal order), pitches, notes, or strings;
        # even an existing chord.Chord object.
    except:  # can"t make a chord directly. Assume string.
        if isinstance(query_type, str):
            if "-" in query_type:  # take it to be a Forte class.
                f = "forte class "
                if query_type.startswith(f):
                    query_type = query_type.replace(f, "")
                reference = chord.fromForteClass(query_type)
            else:  # a string, not a Forte class, take it to be a common name.
                # TODO
                # reference = chord.fromCommonName(query_type)
                pass
        # else:
        #     raise ValueError(f"Invalid query_type. Cannot make a chord.Chord from {query_type}")
    if not reference:
        raise ValueError(f"Invalid query_type. Cannot make a chord.Chord from {query_type}")

    t = this_chord.commonName == reference.commonName
    return t


def interval_match(rnsList: list,
                   intervalList: list,
                   bassOrRoot: str = "bass"):
    """
    Check whether the intervals (bass or root) between a succession of Roman numerals match a query.
    Requires the creation of interval.Interval objects.
    Minimised here to reduce load on large corpus searches.

    :param rnsList: list of Roman numerals
    :param intervalList: the query list of intervals (interval.Interval objects or directed names)
    :param bassOrRoot: intervals between the bass notes or the roots?
    :return: bool.
    """
    if bassOrRoot == "bass":
        pitches = [x.bass() for x in rnsList]
    elif bassOrRoot == "root":
        pitches = [x.root() for x in rnsList]
    else:
        raise ValueError("The bassOrRoot variable must be either bass or root.")

    if len(pitches) != len(intervalList) + 1:
        raise ValueError("There must be exactly one more RN than interval.")

    for i in range(len(intervalList)):
        sourceInterval = interval.Interval(pitches[i], pitches[i + 1]).intervalClass
        comparisonInterval = interval.Interval(intervalList[i]).intervalClass
        # NOTE: ^ must go through interval.Interval object
        if sourceInterval != comparisonInterval:
            return False  # false as soon as one does not match

    return True


# ------------------------------------------------------------------------------

corpora = ["Early_Choral",
           "Keyboard_Other",
           "OpenScore-LiederCorpus",
           "Orchestral",
           "Piano_Sonatas",
           "Quartets",
           "Variations_and_Grounds"]

valid_searches = ["Modal Mixture",
                  "Augmented Chords",
                  "Augmented Sixths",
                  "Neapolitan Sixths",
                  "Applied Chords",
                  "Common Tone Diminished Sevenths",
                  "Progressions"]


def one_search_one_corpus(corpus: str = "OpenScore-LiederCorpus",
                          what: str = "Modal Mixture",
                          progression: list | None = None,
                          write_summary: bool = True,
                          heads: list | None = None,
                          write_examples: bool = True,
                          ):
    """
    Runs the search methods on a specific pair of corpus and search term.
    Settable to find any of
        "Modal Mixture",
        "Augmented Chords",
        "Augmented Sixths",
        "Neapolitan Sixths",
        "Applied Chords",
        "Common Tone Diminished Sevenths"
        and
        "Progressions".
    Defaults to the "OpenScore-LiederCorpus" and "Modal mixture".
    If searching for a progression, set the progression variable to a list of
    Roman numerals figure strings like ["I", "V65", "I"]
    """

    if heads is None:
        heads = ["COMPOSER",
                 "COLLECTION",
                 "MOVEMENT",
                 "MEASURE",
                 ]
        if what != "Common Tone Diminished Sevenths":
            heads += ["FIGURE", "KEY"]  # single figure and key unhelpful in Cto7 case

    if what not in valid_searches:
        raise ValueError(f"For what, please select from among {valid_searches}.")

    if what == "Progression":
        if not progression:
            raise ValueError("If searching for a progression with the `what` parameter, "
                             "set the 'progression' parameter to a list of Roman numeral figures.")

    if corpus not in corpora:
        raise ValueError(f"Please select a corpus from among {corpora}.")

    lied = False
    if corpus == "OpenScore-LiederCorpus":
        lied = True

    out_data = []
    totalRns = 0
    totalLength = 0

    corpus_path = CORPUS_FOLDER / corpus
    sv_out_path = REPO_FOLDER / "Anthology" / corpus
    eg_out_path = REPO_FOLDER.parent / "Anthology" / corpus  # Now an external repo

    print(f"Searching for {what} within the {corpus} collection:")

    files = get_corpus_files(corpus_path,
                             file_name="analysis.txt"
                             )

    # URLs
    base_url = f'<a href="https://github.com/MarkGotham/'
    wir = base_url + f"When-in-Rome/blob/master/Corpus/{corpus}/"
    ant_online = base_url + f"Anthology/blob/main/{corpus}/"
    eg_url_base = ant_online + what.replace(' ', '_') + "/"
    score_online = '<a href="https://musescore.com/score/'

    for file_path in files:
        try:
            rnf = RnFinder(file_path)
            totalRns += len(rnf.rns)
            totalLength += rnf.analysis.quarterLength
            print(".")
        except:
            print(f"Error with {file_path}")
            continue

        path_to_dir = file_path.parent
        path_parts = path_to_dir.parts[-3:]
        composer, collection, movement = [x.replace("_", " ") for x in path_parts]

        # URL for lieder
        if lied:
            matches = get_corpus_files(path_to_dir, "lc*.mscz")
            if matches:
                lc_num = matches[0].stem[2:]  # NB stem is a string filename w/out extension
                score_url = score_online + f'{lc_num}">{lc_num}</a>'
                download = wir + "/".join(path_parts).replace(",", "%2C")
                mscz_download = download + f'/lc{lc_num}.mscz">.mscz</a>'
                mxl_download = download + '/score.mxl">.mxl</a>'
            else:
                print(f"No <lc*.mscz> file found in {path_to_dir}")
                lc_num = "x_lc_missing"
                score_url = "x_url_missing"
                mscz_download = "mscz_missing"
                mxl_download = "mxl_missing"

        if what == "Modal Mixture":
            rnf.find_mixtures()
            this_work_list = rnf.mixtures
        elif what == "Augmented Chords":
            rnf.find_augmented_chords()
            this_work_list = rnf.augmented_chords
        elif what == "Augmented Sixths":
            rnf.find_augmented_sixths()
            this_work_list = rnf.augmented_sixths
        elif what == "Neapolitan Sixths":
            rnf.find_Neapolitan_sixths()
            this_work_list = rnf.neapolitan_sixths
        elif what == "Applied Chords":
            rnf.find_applied_chords()
            this_work_list = rnf.applied_chords
        elif what == "Common Tone Diminished Sevenths":
            rnf.find_Cto_dim7()
            this_work_list = rnf.user_progression
        elif what == "Progressions":
            rnf.find_rn_progression(rns_list=progression)
            this_work_list = rnf.user_progression

        for x in this_work_list:

            x["COMPOSER"] = composer
            x["COLLECTION"] = collection
            x["MOVEMENT"] = movement

            if lied:
                # For pdf write only (not sv)
                x["source_path"] = path_to_dir
                x["eg_file"] = f'{lc_num}_{x["MEASURE"]}'  # TODO -1 getting added. Review.
                # For sv
                x["SCORE"] = score_url
                if score_url == "x_url_missing":
                    x["DOWNLOAD"] = "x_missing"
                    x["EXAMPLE"] = "x_missing"
                else:
                    x["DOWNLOAD"] = f"{mscz_download} {mxl_download}"
                    x["EXAMPLE"] = eg_url_base + f'{x["eg_file"]}-1.png">{x["eg_file"]}</a>'

        out_data += this_work_list

    sortedList = sorted(out_data, key=lambda x: (x["COMPOSER"],
                                                 x["COLLECTION"],
                                                 x["MOVEMENT"]
                                                 )
                        )

    totalRnLength = sum([x["LENGTH"] for x in sortedList])
    print(f" *** Summary of {what} found in the {corpus} collection:\n"
          f"Number of files: {len(files)}.\n"
          f"Cases (count): {len(sortedList)} from {totalRns} RNs overall.\n"
          f"Length: {totalRnLength} from {totalLength} total.\n")

    if not write_summary and not write_examples:
        return sortedList

    if write_summary:
        with open(sv_out_path / (what + ".csv"), "w") as svfile:
            svOut = csv.writer(svfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)

            if lied:
                heads += ["SCORE", "DOWNLOAD", "EXAMPLE"]

            svOut.writerow(heads)

            for entry in sortedList:
                row = [entry[head] for head in heads]
                svOut.writerow(row)

    if write_examples and corpus == "OpenScore-LiederCorpus" and lc_num:
        what = what.replace(" ", "_")  # TODO higher up?
        v = instrument.Instrument("Voice")  # TODO higher up?
        for item in sortedList:
            in_path = item["source_path"] / "score.mxl"  # TODO consider "analysis_on_score.mxl"
            if not in_path.exists:
                print(f"Warning: {in_path} file does not exist. Skipping.")
                continue

            example_path = eg_out_path / what
            score = converter.parse(in_path)

            # Range to use
            start = item["MEASURE"] - 1
            end = item["MEASURE"] + 1
            example = clean_up(score.measures(start, end))

            example.insert(0, metadata.Metadata())
            example.metadata.composer = item["COMPOSER"]
            example.metadata.title = f'{item["COLLECTION"]}. {item["MOVEMENT"]}. m{item["MEASURE"]}'

            # Currently always the middle of 3 measures. If not, consider:
            # te = expressions.TextExpression(f'{item["KEY"]}: {item["FIGURE"]}')
            # example.parts[0].measure(1).insert( ...

            example.coreElementsChanged()

            try:
                example.write(
                    "musicxml.png",  # sic, this as the format
                    fp=example_path / (item["eg_file"] + ".png")
                )
            except:
                print(f"Warning: unable to write {eg_out_path}")

            # music21 insists on also writing the xml. Remove:
            inadvertent_score_path = example_path / (item["eg_file"] + ".musicxml")
            if inadvertent_score_path.exists():
                inadvertent_score_path.unlink()
            else:
                print(f"Warning: No file found at {inadvertent_score_path}")


def clean_up(
        this_stream: stream,
        lied: bool = True
) -> stream:
    """
    Temporary function for cleaning example score outputs.
    Adapted from my `stream/tools` module for m21.

    Args:
        this_stream: the stream to work on. Note: In place is hard coded in.
        lied (bool): Lied-specific special cases.

    Returns: that same stream, modified.

    # TODO promote higher up the workflow, e.g., for creation of analysis_on_score
    # TODO possibly also remove `bar.Barline type=double` when not last measure
    """

    # for p in this_stream.parts:
    #     p.partAbbreviation = None
    #     # TODO ^ not effective. Resolved elsewhere.
    #
    #     last_measure = p.getElementsByClass(stream.Measure).last()
    #     last_measure.append(bar.Barline(type='final', location='right'))
    #     # TODO ^ not effective. (Partial) terminal double bar added by notation apps.

    if lied:
        i = this_stream.parts[0].getInstrument()
        this_stream.parts[0].replace(i, instrument.Instrument("Voice"))
        # TODO ^ this issue with voice part name is common. Resolve at source. Patch for now.

    remove_dict = {}

    for this_class in [
        layout.PageLayout,
        layout.SystemLayout,
        tempo.MetronomeMark,
        # NB: keep layout.StaffGroup
        bar.Barline,  # TODO Also not effective. See above
    ]:
        for this_state in this_stream.recurse().getElementsByClass(this_class):
            if this_state.activeSite in remove_dict:  # There may be several in same (e.g., measure)
                remove_dict[this_state.activeSite].append(this_state)
            else:
                remove_dict[this_state.activeSite] = [this_state]

    for activeSiteKey, valuesToRemove in remove_dict.items():
        activeSiteKey.remove(valuesToRemove, recurse=True)

    return this_stream


def all_searches_one_corpus(corpus: str = "OpenScore-LiederCorpus"):
    """
    Runs the one_search_one_corpus function for
    one corpus and
    all search terms except "Progressions".
    """

    for w in valid_searches[:-1]:  # omit progressions
        one_search_one_corpus(corpus=corpus, what=w)


def all_searches_all_corpora():
    """
    Runs the one_search_one_corpus function for all pairs of
    corpus and search terms except "Progressions".
    """

    for c in corpora:
        for w in valid_searches[:-1]:  # omit progressions
            one_search_one_corpus(corpus=c, what=w)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest
    doctest.testmod()
