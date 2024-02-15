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

from music21 import bar, converter
from music21 import instrument, interval
from music21 import layout, metadata
from music21 import roman, stream, tempo

from pathlib import Path

import csv
from . import CORPUS_FOLDER, REPO_FOLDER, chords_and_progs, get_corpus_files, mixture
from .Pitch_profiles.chord_usage import careful_consolidate


# ------------------------------------------------------------------------------

class RnFinder(object):
    """
    For retrieving specific Roman numerals and/or progressions from analyses.
    Separate methods on this class per search term (e.g., `find_mixtures`).
    All such results stored in the `.results` attributes:
    that are lists of dicts returns by data_from_Rn.
    """

    def __init__(self,
                 pathToFile: str | Path):

        self.analysis = converter.parse(pathToFile, format="romanText")
        self.rns = [x for x in self.analysis.recurse().getElementsByClass("RomanNumeral")]
        self.results = []

    def find_mixtures(self):
        """
        NOTE: musical logic previously here now moved to the main music21 repo.
        """

        for rn in self.rns:
            if not rn.secondaryRomanNumeral:
                if mixture.is_mixture(rn):
                    self.results.append(data_from_Rn(rn))

    def find_applied_chords(self,
                            require_dominant_function: bool = True):
        for rn in self.rns:
            if chords_and_progs.is_applied_chord(rn, require_dominant_function=require_dominant_function):
                self.results.append(data_from_Rn(rn))

    def find_Neapolitan_sixths(self):
        """
        NOTE: musical logic previously here now moved to the main music21 repo
        """

        for rn in self.rns:

            if rn.isNeapolitan(require1stInversion=False):
                self.results.append(data_from_Rn(rn))

    def find_augmented_sixths(self):
        """
        NOTE:
            includes those literally called `Ger65` etc.,
            but also de facto cases like `V43[b5]`.
        """

        for rn in self.rns:
            #
            if rn.isAugmentedSixth():
                self.results.append(data_from_Rn(rn))

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
                self.results.append(data_from_Rn(rn))
            elif acceptSevenths:
                if rn.isSeventh:
                    if rn.isSeventhOfType([0, 4, 8, 11]) or rn.isSeventhOfType([0, 4, 8, 10]):
                        self.results.append(data_from_Rn(rn))
                    elif not requireAugAsTriad:
                        if rn.isSeventhOfType([0, 3, 7, 11]):
                            self.results.append(data_from_Rn(rn))

    def find_rn_progression(self,
                            rns_list: list[str]):
        """
        Find a specific progression of Roman numerals in a given key input by the user as
        a list of Roman numeral figures like ["I", "V65", "I"]
        """

        lnrns = len(rns_list)

        for index in range(len(self.rns) - lnrns):
            thisRange = self.rns[index: index + lnrns]

            if chords_and_progs.changes_key(thisRange):
                break

            figures = [x.figure for x in thisRange]
            if figures == rns_list:
                self.results.append(data_from_Rn_list(rns_list))

    def find_prog_by_qual_and_intv(
            self,
            qualities: list | None = None,
            intervals: list[interval.GenericInterval | interval.Interval] | None = None,
            # TODO qualities, intervals or both. Neither = error.
            # TODO accept generic intervals too
            bass_not_root: bool = True
    ):
        """
        Find a specific progression of Roman numerals
        searching by chord type quality and (optionally) bass or root motion.

        For instance, to find everything that might constitute a ii-V-I progression
        (regardless of whether those are the exact Roman numerals used), search for
        qualities=["Minor", "Major", "Major"],
        intervals=["P4", "P-5"].
        bass_not_root=False.

        This method accepts many input types.
        For the range accepted by qualities,
        see documentation at is_of_type().

        Blank entries are also fine.
        For instance, to find out how augmented chords resolve, search for
        qualities=["Augmented triad", ""].
        To add the preceding chord as well, expand to:
        qualities=["", "Augmented triad", ""].
        Note that intervals is left unspecified (we are interested in any interval succession).
        Anytime the intervals is left blank, the search runs on quality only
        (and vice versa).
        """
        if not qualities and not intervals:
            raise ValueError("Pick at least one of qualities and intervals")

        lnQs = len(qualities)

        if intervals:
            if lnQs != len(intervals) + 1:
                raise ValueError("There must be exactly one more chord than interval.")

        # 1. Search quality match first: quality is required
        for index in range(len(self.rns) - lnQs):
            theseRns = self.rns[index: index + lnQs]
            for i in range(lnQs):
                if not chords_and_progs.is_of_type(theseRns[i], qualities[i]):
                    continue  # TODO check
            # 2. Only search for interval match if required and if the qualities already match.
            if intervals:
                if chords_and_progs.interval_match(
                        theseRns,
                        intervals,
                        bass_not_root
                ):
                    self.results.append(data_from_Rn_list(theseRns))

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

                if chords_and_progs.is_potential_Cto_Dim_7(
                        self.rns[index - 1],
                        this_chord,
                        self.rns[index + 1],
                        require_prolongation=require_prolongation
                ):
                    self.results.append(
                        data_from_Rn_list(
                            [self.rns[index - 1],
                             this_chord,
                             self.rns[index + 1]
                             ]
                        )
                    )

    def find_quiescenzas(self):
        """
        Find specific cases of the "Quiescenza".
        Basically this is of the kind V/IV to IV,
        with or without 7th on the V and heading to either IV (typical in major) or iv (minor).
        Partimenti tradition considers this suitable for the end.
        There are examples of that in the corpus (Bach Prelude no1 in C).
        ... but it also often appears at the start.
        That being the case, this method differs from others on the class by returning
        not only the specific progression, but also the location

        See is_quiescenza for more info.
        """

        last_measure = self.rns[-1].getContextByClass("Measure").measureNumber

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if chords_and_progs.changes_key(this_range):
                continue

            if chords_and_progs.is_quiescenza(this_range):
                info = data_from_Rn_list(this_range)
                info["MEASURE"] += f"/{last_measure}"  # interested in position in work.
                self.results.append(info)

    def find_descending_fifths(self):
        """
        Find cases of
        descending_fifths()
        as defined at that functions below.
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if chords_and_progs.descending_fifths(this_range):
                self.results.append(data_from_Rn_list(this_range))

    def find_ascending_fifths(self):
        """
        Find cases of the
        ascending_fifths()
        as defined at that functions below.
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if chords_and_progs.ascending_fifths(this_range):
                self.results.append(data_from_Rn_list(this_range))

    def find_aufsteigender_Quintfall(self):
        """
        Find specific cases of the
        aufsteigender_Quintfall()
        as defined at that functions below.

        Apologies for the mixed languages.
        The long form of this method can be called:
        "Ich frage mich, ob das ein aufsteigender Quintfall ist."
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if chords_and_progs.aufsteigender_Quintfall(this_range):
                self.results.append(data_from_Rn_list(this_range))

    def find_fallender_Quintanstieg(self):
        """
        Find specific cases of the
        fallender_Quintanstieg()
        as defined at that function below.
        """

        for index in range(len(self.rns) - 4):
            this_range = self.rns[index: index + 4]

            if chords_and_progs.fallender_Quintanstieg(this_range):
                self.results.append(data_from_Rn_list(this_range))


# ------------------------------------------------------------------------------

# Static functions for progressions now moved to separate file
# Other Static:

def data_from_Rn(
        rn: roman.RomanNumeral,
        consolidate: bool = True
) -> dict:
    if consolidate:
        fig = careful_consolidate(
            rn.figure,
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


def data_from_Rn_list(
        rn_list: list[roman.RomanNumeral],
        consolidate: bool = True
) -> dict:

    # figures
    if consolidate:
        figs = [careful_consolidate(
            rn.figure,
            major_not_minor=(rn.key.mode == "major"),
            rn=rn
        ) for rn in rn_list]
    else:
        figs = [rn.figure for rn in rn_list]
    figures = "-".join(figs)

    # keys
    keys = [rn_list[0].key.name]
    for rn in rn_list[1:]:
        if rn.key.name not in keys:
            keys.append(rn.key.name)
    keys = "-".join([k.replace("-", "b") for k in keys])

    measure_start = rn_list[0].getContextByClass("Measure").measureNumber
    measure_end = rn_list[-1].getContextByClass("Measure").measureNumber

    return {"MEASURE": f"{measure_start}-{measure_end}",
            "FIGURE": figures,
            "KEY": keys,
            "BEAT": rn.beat,
            "BEAT STRENGTH": rn.beatStrength,
            "LENGTH": rn.quarterLength}


# ------------------------------------------------------------------------------

corpora = [
    "Chamber_Other",
    "Early_Choral",
    "Keyboard_Other",
    "OpenScore-LiederCorpus",
    "Orchestral",
    "Piano_Sonatas",
    "Quartets",
    "Variations_and_Grounds"
]

valid_searches = [
    "Modal Mixture",
    "Augmented Chords",
    "Augmented Sixths",
    "Neapolitan Sixths",
    "Applied Chords",
    "Common Tone Diminished Sevenths",
    "Quiescenzas",
    "ascending_fifths",
    "descending_fifths",
    "aufsteigender_Quintfall",
    "fallender_Quintanstieg",
    "Progressions",
]


def one_search_one_corpus(corpus: str = "OpenScore-LiederCorpus",
                          what: str = "Modal Mixture",
                          progression: list | None = None,
                          write_summary: bool = True,
                          heads: list | None = None,
                          write_examples: bool = False,
                          ):
    """
    Runs the search methods on a specific pair of corpus and search term.
    Settable to find any of the `valid_searches` ("Modal Mixture", ...).
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
    raw_url = f'<a href="https://raw.githubusercontent.com/MarkGotham/'
    wir = base_url + f"When-in-Rome/blob/master/Corpus/{corpus}/"
    ant_online = raw_url + f"Anthology/main/{corpus}/"
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
        elif what == "Augmented Chords":
            rnf.find_augmented_chords()
        elif what == "Augmented Sixths":
            rnf.find_augmented_sixths()
        elif what == "Neapolitan Sixths":
            rnf.find_Neapolitan_sixths()
        elif what == "Applied Chords":
            rnf.find_applied_chords()
        elif what == "Common Tone Diminished Sevenths":
            rnf.find_Cto_dim7()
        elif what == "Quiescenzas":
            rnf.find_quiescenzas()
        elif what == "ascending_fifths":
            rnf.find_ascending_fifths()
        elif what == "descending_fifths":
            rnf.find_descending_fifths()
        elif what == "fallender_Quintanstieg":
            rnf.find_fallender_Quintanstieg()
        elif what == "aufsteigender_Quintfall":
            rnf.find_aufsteigender_Quintfall()
        elif what == "Progressions":
            rnf.find_rn_progression(rns_list=progression)

        for x in rnf.results:

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

        out_data += rnf.results

    sortedList = sorted(out_data, key=lambda x: (x["COMPOSER"],
                                                 x["COLLECTION"],
                                                 x["MOVEMENT"]
                                                 )
                        )

    totalRnLength = sum([x["LENGTH"] for x in sortedList])
    print(f"*** Summary of {what} found in the {corpus} collection:\n"
          f"\tFiles: {len(files)}.\n"
          f"\tCases (count): {len(sortedList)} from {totalRns} RNs overall.\n"
          f"\tLength: {totalRnLength} from {totalLength} total.\n")

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
        for item in sortedList:
            in_path = item["source_path"] / "score.mxl"  # TODO consider "analysis_on_score.mxl"
            if not in_path.exists:
                print(f"Warning: {in_path} file does not exist. Skipping.")
                continue

            example_path = eg_out_path / what
            score = converter.parse(in_path)

            # Range to use
            if what in [
                "Quiescenzas",
                "ascending_fifths",
                "descending_fifths",
                "aufsteigender_Quintfall",
                "fallender_Quintanstieg"
            ]:
                # ^ special handling of progressions
                start = int(item["MEASURE"].split("/")[0])
                end = start + 2
                item["eg_file"] = item["eg_file"].split("/")
            else:
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


def all_corpora_one_search(what: str = "fallender_Quintanstieg"):
    """
    Runs the one_search_one_corpus function for
    one corpus and
    all search terms except "Progressions".
    """

    for c in corpora:
        one_search_one_corpus(corpus=c, what=what)


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
