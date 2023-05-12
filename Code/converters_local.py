# -*- coding: utf-8 -*-
"""
NAME:
===============================
Converters Local (converters_local.py)

BY:
===============================
Gianluca Micchi and Mark Gotham

LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/

ABOUT:
===============================
Conversion routines not (yet) promoted up the music21.

Specifically, the following 2-way conversions with rntxt:
- music21 <> DCML
- WiR (here) <> BPS <> Dez.


"""


# ------------------------------------------------------------------------------

from . import REPO_FOLDER

from music21 import converter, pitch, roman, romanText, spanner, stream
import numpy as np

import csv
import json
import logging
import os
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)


# ------------------------------------------------------------------------------

def roman_to_int(roman):
    r2i = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
    }
    return r2i[roman.upper()]


def int_to_roman(n: int):
    """Convert an integer to a Roman numeral."""
    if not 0 < n < 8:
        raise ValueError("Argument must be between 1 and 7")
    ints = (5, 4, 1)
    nums = ("V", "IV", "I")
    result = []
    for i in range(len(ints)):
        count = int(n / ints[i])
        result.append(nums[i] * count)
        n -= ints[i] * count
    return "".join(result)


def merge_dezrann_annotations(
    in_path_1, in_path_2, out_path, layer_1=None, layer_2=None, force_overwrite=False
):
    """
    Merge two dezrann files into a third one.
    The layer field inside dezrann files is used to separate conceptually different annotations.
    For example, it could be set to "automated", "annotator A", "annotator B", "reference", ...

    :param in_path_1: Path to file 1
    :param in_path_2: Path to file 2
    :param out_path: Path to write to
    :param layer_1: If specified, overwrite the content of the layer field inside in_path_1
    :param layer_2: If specified, overwrite the content of the layer field inside in_path_2
    :param force_overwrite:
    :return:
    """
    logger = logging.getLogger(__name__)
    if layer_1 is None:
        logger.info(f"layer_1 was not set, reusing the layer information specified in {in_path_1}")
    if layer_2 is None:
        logger.info(f"layer_2 was not set, reusing the layer information specified in {in_path_2}")
    with open(in_path_1, "r") as f:
        x = json.load(f)
    with open(in_path_2, "r") as f:
        y = json.load(f)

    if not force_overwrite:
        s1 = set([label["layer"] for label in x["labels"]]) if layer_1 is None else set(layer_1)
        s2 = set([label["layer"] for label in y["labels"]]) if layer_2 is None else set(layer_2)
        if not s1.isdisjoint(s2):
            raise AttributeError(
                "The layers in the two files overlap. "
                "This might cause visualization problems in Dezrann."
                "Three possible courses of action: \n"
                "1. set force_overwrite to True, which ignores this error.\n"
                "2. pass the variables layer_1 and layer_2 that overwrite the "
                "(possibly more structured) information inside the dezrann files\n"
                f"3. edit {in_path_1} and {in_path_2} manually."
            )
    if layer_1 is not None:
        for label in x["labels"]:
            label["layer"] = layer_1
    if layer_2 is not None:
        for label in y["labels"]:
            label["layer"] = layer_2

    out_data = {"labels": x["labels"] + y["labels"]}
    with open(out_path, "w") as fp:
        json.dump(out_data, fp, indent=4)

    return


def remove_prima_volta(score: stream.Score,
                       change_measure_number: bool = True):
    """
    Remove first time ("prima volta") from a music21-parsed score.
    Note: Works inplace due to the call to an inplace function in music21.
    TODO: prima and seconda volta only; currenty no support for more complex cases
    """

    for p in score.parts:
        repeat_brackets = [rb for rb in p.getElementsByClass(spanner.RepeatBracket)]
        to_remove = []
        for rb in repeat_brackets:
            if rb.getNumberList() == [1]:
                measures = rb.getSpannedElementsByClass(stream.Measure)
                if len(measures) > 2:
                    for m in measures:
                        to_remove.append(m)
                elif len(measures) == 2:
                    start, end = measures
                    to_remove.append(start)
                    for n in range(start.measureNumber + 1, end.measureNumber + 1):
                        to_remove.append(p.measure(n))
                else:
                    start_end = rb.getSpannedElementsByClass(stream.Measure)[0]
                    to_remove.append(start_end)

        p.remove(to_remove, shiftOffsets=True)
        [p.remove(rb) for rb in repeat_brackets]

        # Change the number of the measures to follow the shift
        if change_measure_number:
            total_measures = p.getElementsByClass(stream.Measure)
            for m in total_measures:  # make sure we change each score element
                for r in reversed(to_remove):
                    if m.measureNumber > r.measureNumber:
                        # TODO Maybe add this condition to check if the measure in prima volta was
                        #  excluded? if str(r.measureNumber) == r.measureNumberWithSuffix()
                        m.number -= 1
    return


class AnnotationConverter(ABC):
    def __init__(self, in_ext=None, out_ext=None):
        self.in_ext = in_ext
        self.out_ext = out_ext
        self.logger = logging.getLogger("converter")
        self.logger.setLevel(logging.INFO)
        self.quality_music21_to_tab = {
            "major triad": "M",
            "minor triad": "m",
            "diminished triad": "d",
            "augmented triad": "a",
            "minor seventh chord": "m7",
            "major seventh chord": "M7",
            "dominant seventh chord": "D7",
            "incomplete dominant-seventh chord": "D7",  # For cases of '75', '73', and [noX]
            "diminished seventh chord": "d7",
            "augmented seventh chord": "+7",
            "half-diminished seventh chord": "h7",
            "German augmented sixth chord": "Gr+6",
            "French augmented sixth chord": "Fr+6",
            "Italian augmented sixth chord": "It+6",

            # Simplifications:
            "dominant-ninth": "D7",
            "augmented major tetrachord": "a",
            "minor-augmented tetrachord": "m",
            "major-second minor tetrachord": "m",
        }
        self.accidental_music21_to_tab = {
            "double-sharp": "++",
            "sharp": "+",
            "natural": "",
            "flat": "-",
            "double-flat": "--",
        }
        self.augmented_sixths = [
            "German augmented sixth chord",
            "French augmented sixth chord",
            "Italian augmented sixth chord",
        ]
        self.inversion_tab2rn = {
            "triad0": "",
            "triad1": "6",
            "triad2": "64",
            "triad3": "wi",
            "seventh0": "7",
            "seventh1": "65",
            "seventh2": "43",
            "seventh3": "42",
        }
        self.quality_tab2rn = {  # (True=uppercase degree, 'triad' or 'seventh', quality)
            "M": (True, "triad", ""),
            "m": (False, "triad", ""),
            "d": (False, "triad", "o"),
            "a": (True, "triad", "+"),
            "M7": (True, "seventh", "M"),
            "m7": (False, "seventh", ""),
            "D7": (True, "seventh", ""),
            "D9": (True, "seventh", ""),  # NB hard coded simplification, as above
            "d7": (False, "seventh", "o"),
            "h7": (False, "seventh", "ø"),
            "Gr+6": (True, "seventh", "Gr"),
            "It+6": (True, "seventh", "It"),
            "Fr+6": (True, "seventh", "Fr"),
        }

        return

    @staticmethod
    def _get_measure_offsets(
            score: stream.Score
    ) -> list:
        """
        The measure_offsets are zero-indexed:
        the first measure in the score will be at index zero, regardless of anacrusis.
        This is implemented by keeping the order of the measure without looking at the keys.

        NOTE: do not consider measures that have been marked as "excluded" in the musicxml.
        NOTE: Only considers the top part (e.g., piano right hand only).

        :param score: a music21 stream.Score object
        :return: a list where at index m there is the offset in quarter length of measure m
        """
        score_mom = score.measureOffsetMap()
        measure_offsets = [k for k in score_mom.keys() if score_mom[k][0].numberSuffix is None]
        measure_offsets.append(score.duration.quarterLength)
        return measure_offsets

    def chord_tab_to_rn(self, degree, quality, inversion):
        """
        Given degree (numerator and denominator), quality of the chord, and inversion,
        return a properly written RN.

        :param num: String with the numerator of the degree in Arabic numerals, e.g., '1', or '+4'
        :param den: Same as num, but for the denominator
        :param quality: Quality of the chord (`major`, `minor`, `dominant seventh`, etc.)
        :param inversion: Inversion as a string
        """

        def interpret_degree(degree):
            """
            Given a degree written in our tabular format, split it into num + den in music21 format.
            For example:
              - interpret_degree('1') = ('I', 'I')
              - interpret_degree('----7/-3') = ('bbbbVII', 'bIII')
              - interpret_degree('+5/5') = ('#V', 'V')
            :param degree:
            :return:
            """
            if "/" in degree:
                num, den = degree.split("/")
            else:
                num, den = degree, "1"

            num_prefix = ""
            while num[0] in ["+", "-"]:
                num_prefix += "b" if num[0] == "-" else "#"
                num = num[1:]
            if num == "1+":
                print("Degree 1+, ignoring the +")
            num = num_prefix + int_to_roman(int(num[0]))

            den_prefix = ""
            while den[0] in ["+", "-"]:
                den_prefix += "b" if den[0] == "-" else "#"
                den = den[1:]
            den = den_prefix + int_to_roman(int(den[0]))

            return num, den

        num, den = interpret_degree(degree)
        upper, triad, qlt = self.quality_tab2rn[quality]
        inv = self.inversion_tab2rn[triad + inversion]
        if upper:
            num_prefix = ""
            while num[0] == "b":
                num_prefix += num[0]
                num = num[1:]
            num = num_prefix + num.upper()
        else:
            num = num.lower()
        if num == "IV" and qlt == "M":  # the fourth degree is by default major seventh
            qlt = ""
        return num + qlt + inv + ("/" + den if den != "I" else "")

    def chord_rn_to_tab(self, chord):
        rn = roman.RomanNumeral(chord, "C")  # arbitrary key, we throw it away later anyway
        _, degree, quality, inversion = self.chord_music21_to_tab(rn)
        return degree, quality, inversion

    def chord_music21_to_tab(self, rn):
        def _get_full_degree(rn):
            def _lower_degree(deg):
                return deg[1:] if deg[0] == "+" else "-" + deg

            def _degree_str_from_rn(rn):
                deg = str(rn.scaleDegreeWithAlteration[0])
                acc = rn.scaleDegreeWithAlteration[1]

                # TODO: check this hack (correct degree +4) still necessary workaround m21.
                if rn.commonName in self.augmented_sixths:
                    deg = "4"
                    acc = pitch.Accidental("sharp")
                # end of hack

                if acc is not None:
                    deg = self.accidental_music21_to_tab[acc.fullName] + deg
                return deg

            degree = _degree_str_from_rn(rn)

            # TODO: review this natural vs harmonic minor handling
            if rn.secondaryRomanNumeral is not None:
                secondary_degree = _degree_str_from_rn(rn.secondaryRomanNumeral)

                if (
                    rn.key.mode == "minor" and "7" in secondary_degree
                ):  # use the harmonic scale on the base key
                    secondary_degree = _lower_degree(secondary_degree)

                if (
                    rn.secondaryRomanNumeralKey.mode == "minor" and "7" in degree
                ):  # use the harmonic scale of the tonicised key
                    degree = _lower_degree(degree)

                # Note: music21 naming convention = "degree1" / "degree2"
                degree = degree + "/" + secondary_degree
            else:
                if rn.key.mode == "minor" and "7" in degree:
                    degree = _lower_degree(degree)

            return degree

        def _get_quality(rn):
            if rn.commonName in self.quality_music21_to_tab.keys():
                return self.quality_music21_to_tab[rn.commonName]

            # Discard extensions or omissions given in brackets
            if "[" in rn.figure:
                fig = str(rn.figure)
                fig = fig.split("[")[0]
                rn = roman.RomanNumeral(fig, rn.key)
                return _get_quality(rn)

            tip_off_quality_pairs = (
                ("9", "D9"),  # TODO Review and document the mapping of all 9ths (sic) to dominants.
                ("Fr", "Fr+6"),
                ("Ger", "Gr+6"),
                ("It", "It+6"),
            )

            for t in tip_off_quality_pairs:
                if t[0] in rn.figure:
                    return t[1]

            self.logger.warning(
                f"Issue with chord quality for chord {rn.figure}, {rn.commonName}"
                f" at measure {rn.measureNumber}. Noting down quality with {quality}"
            )
            return rn.figure

        key = rn.key.tonicPitchNameWithCase
        degree = _get_full_degree(rn)
        quality = _get_quality(rn)
        inversion = min(rn.inversion(), 3)  # fourth inversions on ninths are sent to 3 arbitrarily
        # TODO: Document handling of ninths
        return [key, degree, quality, inversion]

    @abstractmethod
    def load_input(self, in_path):
        pass

    @abstractmethod
    def run(self, in_data, score):
        pass

    @abstractmethod
    def write_output(self, out_data, out_path):
        pass

    def convert_file(self, score_path, in_path, out_path, **kwargs):
        """
        Convert a file in in_path and store it in out_path, using information contained in the score

        :param score_path:
        :param in_path:
        :param out_path:
        :return:
        """

        self.logger.info(
            f"Converting file {os.path.relpath(in_path, os.curdir)} to {os.path.relpath(out_path, os.curdir)}"
        )
        score = converter.parse(score_path)
        in_data = self.load_input(in_path)
        out_data, flag = self.run(in_data, score)
        if flag:
            print(f"{score_path}")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        self.write_output(out_data, out_path)
        return

    # TODO Put an "experimental" decorator here
    def convert_corpus(self, score_folder, in_folder, out_folder, corpus_id, **kwargs):
        """

        :param corpus_id:
        :param score_folder:
        :param in_folder:
        :param out_folder:
        :return:
        """
        os.makedirs(out_folder, exist_ok=True)

        dir_entries = [
            x for x in os.scandir(in_folder) if x.is_file() and x.name.endswith(self.in_ext)
        ]

        for in_file in dir_entries:
            score_file = (
                f"{in_file.name[:-6]}.mxl" if "Tavern" in corpus_id else f"{in_file.name[:-4]}.mxl"
            )
            out_file = ".".join([in_file.name[:-4], self.out_ext])
            self.convert_file(
                os.path.join(score_folder, score_file),
                in_file.path,
                os.path.join(out_folder, out_file),
                **kwargs,
            )
        return


class ConverterRn2Tab(AnnotationConverter):
    def __init__(self):
        super().__init__(in_ext="txt", out_ext="csv")

    def write_output(self, out_data, out_path):
        with open(out_path, "w") as fp:
            w = csv.writer(fp)
            w.writerows(out_data)
        return

    def load_input(self, txt_path):
        """
        Load the rntxt analysis file into a music21 object
        :param txt_path: the path to the rntxt file with the harmonic analysis
        :return:
        """
        analysis = converter.parse(txt_path, format="romanText")
        remove_prima_volta(analysis, change_measure_number=False)
        # NB: recurse for the offsets inside the measure
        return analysis.recurse().getElementsByClass("RomanNumeral")

    def run(self, rntxt, score):
        """
        Convert from rntxt format to tabular format.
        Pay attention to the measure numbers because there are three conventions at play:
          - for python, every list or array is 0-indexed
          - for music21, measures in a score are always 1-indexed
          - for rntxt, measures are 0-indexed if there is anacrusis and 1-indexed if there is not
        We solve by moving everything to 0-indexed and
        adjusting the rntxt output in the retrieve_measure_and_beat function

        Similarly, for the beat,
        convert the 1-index of music21 and rntxt to 0-index and then back at the end.
        """

        def _find_offset(
                rn: roman.RomanNumeral,
                score_measure_offset: list,
                measure_zero: bool
        ):
            """
            Given a roman numeral element from an analysis parsed by music21,
            find its offset in quarter notes length.
            It automatically adapts to the presence of pickup measures thanks to the Boolean measure_zero.

            :param rn: a RomanNumeral object from an rntxt analysis file parsed by music21
            :param score_measure_offset: a list of measure offsets in quarter length
            :param initial_beat_length: Beat length in the first measure;
                e.g. if the piece starts in 4/4, ibl=1; if it starts in 12/8, ibl=1.5
            :param measure_zero: Bool, True if there's a measure counted as zero (pickup measure)
            """
            measure = rn.measureNumber if measure_zero else rn.measureNumber - 1  # 0-indexed
            offset_in_measure = rn.offset
            # if measure == 0:
            #     offset_in_measure -= -score_measure_offset[1] % initial_beat_length
            start = float(score_measure_offset[measure] + offset_in_measure)
            duration = float(rn.quarterLength)
            # TODO: check if we really need to stop the offset at the beginning of the next measure
            # Normally, this should be already implied in the parsing of the rntxt files
            # end = min(start + duration, float(score_measure_offset[measure + 1]))
            end = start + duration
            return round(start, 3), round(end, 3)

        def _correct_final_offset_inplace(out_data, score):
            """
            rntxt files don't repeat the last chord indefinitely, but only give it once.
            This can cause problems because the total length of the score and the analysis differ.
            For tabular representation we need to refer to the total length of the score,
            so we modify the last end_offset to reflect that.
            """
            end_of_analysis = out_data[-1][1]
            end_of_piece = score.duration.quarterLength

            if end_of_analysis != end_of_piece:
                self.logger.warning(
                    f"A gap of {end_of_piece - end_of_analysis} crotchets has been closed at the"
                    f" end of the piece. If > 0, it means that the score is longer than the "
                    f" analysis, which could be due to the final chord lasting several measures."
                )
            out_data[-1][1] = end_of_piece
            return

        out_data = []
        flag = False
        measure_offsets = self._get_measure_offsets(score)

        initial_beat_length = score.flat.getTimeSignatures()[0].beatDuration.quarterLength
        # notice that rntxt can have measureNumber == 0, unlike scores
        measure_zero = rntxt[0].measureNumber == 0

        current_rn, current_label = None, None
        start_offset = 0.0
        for new_rn in rntxt:
            new_label = self.chord_music21_to_tab(new_rn)
            if current_rn is None:  # initialize the system
                current_rn = new_rn
                current_label = self.chord_music21_to_tab(current_rn)

            if any([n != c for n, c in zip(new_label, current_label)]):
                _, end_offset = _find_offset(
                    current_rn,
                    measure_offsets,
                    # initial_beat_length,
                    measure_zero
                )
                if start_offset % 0.5 != 0 or end_offset % 0.5 != 0:
                    self.logger.warning("The chords are not aligned to the quaver's grid")
                out_data.append([start_offset, end_offset, *current_label])
                start_offset, current_rn, current_label = end_offset, new_rn, new_label

            else:  # update the offsets
                current_rn = new_rn

        # write the last chord
        _, end_offset = _find_offset(current_rn,
                                     measure_offsets,
                                     initial_beat_length,
                                     # measure_zero
                                     )
        out_data.append([start_offset, end_offset, *current_label])

        _correct_final_offset_inplace(out_data, score)

        return out_data, flag


datatype_chord = [
    ("onset", "float"),
    ("end", "float"),
    ("key", "<U10"),
    ("degree", "<U10"),
    ("quality", "<U10"),
    ("inversion", "int"),
]


class ConverterTab2Rn(AnnotationConverter):
    def __init__(self):
        super().__init__(in_ext="csv", out_ext="txt")
        self.datatype_chord = datatype_chord

    def write_output(self, out_data, out_path):
        with open(out_path, "w") as f:
            for row in out_data:
                f.write(row + os.linesep)
        return

    def load_input(self, csv_path):
        """
        Load chords of each piece and add chord symbols into the labels.
        :param csv_path: the path to the file with the harmonic analysis
        :return: chord_labels, an array of tuples (start, end, key, degree, quality, inversion)
        """

        chords = []
        with open(csv_path, mode="r") as f:
            data = csv.reader(f)
            for row in data:
                chords.append(tuple(row))
        return np.array(chords, dtype=self.datatype_chord)

    def run(self, tabular, score):
        """
        Convert from tabular format to rntxt format.
        Pay attention to the measure numbers because there are three conventions at play:
          - for python, every list or array is 0-indexed
          - for music21, measures in a score are always 1-indexed
          - for rntxt, measures are 0-indexed if there is anacrusis and 1-indexed if there is not
        We solve by moving everything to 0-indexed and
        adjusting the rntxt output in the retrieve_measure_and_beat function

        TODO DRY documentation.
        """

        def _get_rn_row(datum, in_row=None):
            """
            Write the start of a line of RNTXT.
            To start a new line (one per measure with measure, beat, chord), set in_row = None.
            To extend an existing line (measure already given), set in_row to that existing list.

            :param datum: measure, beat, annotation
            :param in_row: if None, this is a new measure
            """

            measure, beat, annotation = datum

            if in_row is None:  # New line
                in_row = "m" + str(measure)

            beat = (
                int(beat) if int(beat) == beat else round(float(beat), 2)
            )  # just reformat it prettier

            return " ".join([in_row, f"b{beat}", annotation] if beat != 1 else [in_row, annotation])

        def _retrieve_measure_and_beat(
            offset, measure_offsets, time_signatures, ts_measures, beat_zero
        ):
            # find what measure we are by looking at all offsets
            measure = np.searchsorted(measure_offsets, offset, side="right") - 1
            rntxt_measure_number = measure + (
                0 if beat_zero else 1
            )  # the measure number we will write in the output

            offset_in_measure = offset - measure_offsets[measure]
            beat_idx = ts_measures[np.searchsorted(ts_measures, measure, side="right") - 1]
            beat_duration = time_signatures[beat_idx].beatDuration.quarterLength

            beat = (offset_in_measure / beat_duration) + 1  # rntxt format has beats starting at 1
            if rntxt_measure_number == 0:  # add back the anacrusis to measure 0
                beat += beat_zero

            return rntxt_measure_number, beat

        out_data = []
        flag = False  # the flag is used for debugging
        measure_offsets = self._get_measure_offsets(score)

        # Get time signature positions while converting measure numbers given by music21 to 0-indexed
        ts_list = list(
            score.flat.getTimeSignatures()
        )  # we need to call flat to create measure numbers
        first_measure_number = 0 if any([ts.measureNumber == 0 for ts in ts_list]) else 1
        time_signatures = dict(
            [(max(ts.measureNumber - first_measure_number, 0), ts) for ts in ts_list]
        )
        ts_measures = sorted(time_signatures.keys())
        ts_offsets = [measure_offsets[m] for m in ts_measures]

        # if any([ts.measureNumber == 0 for ts in ts_list]) and len(ts_list) > 3:  # debugging tool
        #     flag = True

        # (starting beat == 0) <=> no anacrusis
        starting_beat = ts_list[0].beat - 1  # Convert beats to zero index

        previous_measure, previous_end, previous_key = -1, 0, None
        ts_index = 0  # this runs over the time signatures to find where to put them in the output

        for row in tabular:
            start, end, key, degree, quality, inversion = row
            chord = self.chord_tab_to_rn(degree, str(quality), str(inversion))
            key = key.replace("-", "b")
            annotation = f"{key}: {chord}" if key != previous_key else chord

            # Was there a time signature change?
            while ts_index < len(ts_offsets) and start >= ts_offsets[ts_index]:
                out_data.append("")
                out_data.append(
                    f"Time Signature : {time_signatures[ts_measures[ts_index]].ratioString}"
                )
                out_data.append("")
                ts_index += 1

            # Was there a no-chord passage in between?
            if start != previous_end:
                m, b = _retrieve_measure_and_beat(
                    end, measure_offsets, time_signatures, ts_measures, starting_beat
                )
                if m == previous_measure:
                    out_data[-1] = _get_rn_row([m, b, ""], in_row=out_data[-1])
                else:
                    out_data.append(_get_rn_row([m, b, ""]))
                previous_measure = m

            # Standard annotation conversion
            m, b = _retrieve_measure_and_beat(
                start, measure_offsets, time_signatures, ts_measures, starting_beat
            )
            if m == previous_measure:
                out_data[-1] = _get_rn_row([m, b, annotation], in_row=out_data[-1])
            else:
                out_data.append(_get_rn_row([m, b, annotation]))
            previous_measure, previous_end, previous_key = m, end, key

        return out_data, flag


class ConverterTab2Dez(AnnotationConverter):
    def __init__(self):
        super().__init__(in_ext="csv", out_ext="dez")
        self.datatype_chord = datatype_chord

    def write_output(self, out_data, out_path):
        """

        :param out_data:
        :param out_path:
        :return:
        """
        with open(out_path, "w") as fp:
            json.dump(out_data, fp, indent=4)
        return

    def load_input(self, csv_path):
        """
        Load chords of each piece and add chord symbols into the labels.
        :param csv_path: the path to the file with the harmonic analysis
        :return: chord_labels, an array of tuples (start, end, key, degree, quality, inversion)
        """

        chords = []
        with open(csv_path, mode="r") as f:
            data = csv.reader(f)
            for row in data:
                chords.append(tuple(row))
        return np.array(chords, dtype=self.datatype_chord)

    def run(self, tabular, score, layer="automated"):
        """
        Convert from tabular format to dezrann format.

        :param tabular:
        :param score: This is actually not used in this particular case.
        :param layer: This should be set either to "reference" or to "automated",
            according to the origin of the annotation.
        :return:
        """

        def _get_keys(tabular):
            out_keys = []
            start_previous, end_previous, key_previous, end = None, None, None, None
            for row in tabular:
                start, end, key, degree, quality, inversion = row
                key = key.replace("-", "b")
                if (
                    key != key_previous or start != end_previous
                ):  # the key changes or no-chord passage
                    # TODO: no-chord does not necessarily mean no-key. How to do better?
                    if key_previous is not None:
                        out_keys.append([start_previous, end_previous, key_previous])
                    start_previous, end_previous, key_previous = start, end, key
                else:  # same key
                    end_previous = end

            if key_previous is not None:  # last element
                out_keys.append([start_previous, end, key_previous])

            return out_keys

        def _get_rn(tabular):
            out_rn = []
            start_previous, end_previous, key_previous, rn_previous, end = (
                None,
                None,
                None,
                None,
                None,
            )
            for row in tabular:
                start, end, key, degree, quality, inversion = row
                rn = self.chord_tab_to_rn(degree, str(quality), str(inversion))
                if key != key_previous or rn != rn_previous or start != end_previous:
                    if rn_previous is not None:
                        out_rn.append([start_previous, end_previous, rn_previous])
                    start_previous, end_previous, key_previous, rn_previous = start, end, key, rn
                else:  # same rn
                    end_previous = end

            if rn_previous is not None:  # last element
                out_rn.append([start_previous, end, rn_previous])

            return out_rn

        labels = []
        flag = False

        # The same key can be associated with multiple chords, and therefore multiple lines.
        # We don't want a label that is all broken in Dezrann, so we somehow have to compact the information.
        # We do it by doing two for loops, one to compact the information and one to finally write it out.
        # The same is done also for the RN chord symbols, even if we want a different line for every change in key or rn
        # In fact, this allows us to catch errors in the csv if the same chord is mistakenly broken in several lines
        # The following code is conceptually simple but not efficient at all, as it does 4 loops instead of 1:
        # Two for-loops are apparent below, and one each hides in _get_keys() and _get_rn()
        # However, it is so fast that I prefer to keep it like this, for the moment.
        for start, end, key in _get_keys(tabular):
            labels.append(
                {
                    "type": "Tonality",
                    "layers": [layer],
                    "start": start,
                    "actual-duration": end - start,
                    "tag": key,
                }
            )
        for start, end, rn in _get_rn(tabular):
            labels.append(
                {
                    "type": "Harmony",
                    "layers": [layer],
                    "start": start,
                    "actual-duration": end - start,
                    "tag": rn,
                }
            )

        out_data = {"labels": labels}

        # TODO dez now has "meta" labels for doing layout once only. Update with something like:
        # if include_meta:
        #     out["meta"] = {
        #         "layout": [
        #             {
        #                 "filter": {
        #                     "type": "Harmony"
        #                 },
        #                 "style": {
        #                     "line": "bot.1"
        #                 }
        #             },
        #             {
        #                 "filter": {
        #                     "type": "Tonality"
        #                 },
        #                 "style": {
        #                     "line": "bot.2",
        #                     "color": "#5850be"
        #                 }
        #             }
        #     }

        return out_data, flag


class ConverterDez2Tab(AnnotationConverter):
    def __init__(self):
        super().__init__(in_ext="dez", out_ext="csv")
        self.datatype_chord = datatype_chord

    def write_output(self, out_data, out_path):
        with open(out_path, "w") as fp:
            w = csv.writer(fp)
            w.writerows(out_data)
        return

    def load_input(self, dez_path):
        """
        Load the dezrann file containing the annotations
        """
        with open(dez_path, "r") as f:
            data = json.load(f)
        return data

    def run(self, dezrann, score):
        """
        Convert from dezrann format to tabular format.

        :param dezrann:
        :param score: This is actually not used in this particular case.
        :return:
        """
        out_data = []
        flag = False

        for x in dezrann["labels"]:
            if x["type"] != "Harmony":
                continue
            start, duration, chord = x["start"], x["actual-duration"], x["tag"]
            end = start + duration
            degree, quality, inversion = self.chord_rn_to_tab(chord)
            out_data.append([start, end, degree, quality, inversion])

        i = 0
        for x in dezrann["labels"]:
            if x["type"] != "Tonality":
                continue
            start, duration, key = x["start"], x["actual-duration"], x["tag"]
            end = start + duration
            while (
                i < len(out_data) and out_data[i][0] < end
            ):  # out_data[i] is the start of the annotation
                out_data[i].insert(2, key)
                i += 1
        return out_data, flag


if __name__ == "__main__":
    c = ConverterTab2Dez()


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    base_path = REPO_FOLDER / "Tests" / "Resources" / "Example"

    score_path = base_path / "score.mxl"
    rn_path = base_path / "analysis.txt"
    tab_path = base_path / "analysis_BPS_format.csv"
    dez_path = base_path / "analysis_dez_format.dez"

    c = ConverterRn2Tab()
    c.convert_file(score_path, rn_path, tab_path)

    c = ConverterTab2Dez()
    c.convert_file(score_path, tab_path, dez_path)

    # TODO direct rn <> dez (one step here rather than 2)
