"""
===============================
Get Distributions (get_distributions.py)
===============================

Mark Gotham, 2020-21


LICENCE:
===============================

Creative Commons Attribution-NonCommercial 4.0 International License.
https://creativecommons.org/licenses/by-nc/4.0/


ABOUT:
===============================

Retrieves pitch usage distributions from
'slice'-based tabular score representations (.tsv / .csv).

A 'slice' is a momentary cross-section during which none of the notes change.
The tabular representation stores a score (optionally with an analysis)
as a succession of slices, with one slice per row.
(See the 'scoreSVs.py' functionality of https://github.com/MarkGotham/Moments/).

The corresponding import methods for chroma representations derived from audio frames (.mat)
are currently in a separate module.

In both cases, the goal is to return structured lists of dicts with keys for at least:
- distribution
and timing information as appropriate to the data source with start, end and length for:
- offset (usually for symbolic sources)
- measure (")
- seconds (usually for audio sources)
- frames (")

"""

# ------------------------------------------------------------------------------

import unittest
import os
import csv

import normalisation_comparison

from typing import Optional


# ------------------------------------------------------------------------------

class DistributionsFromTabular:
    """
    For making usage distributions from tabular representations of scores.
    """

    def __init__(self,
                 path_to_tab: str,

                 columns_from_source: bool = False,

                 offset_column: int = 0,
                 measure_column: int = 1,
                 beat_column: float = 2,
                 # beat_strength_column: float = 3,
                 length_column: int = 4,
                 pitch_column: int = 5,
                 key_column: int = 6,
                 chord_column: int = 7,

                 norm: bool = False,
                 norm_type: str = 'Sum',
                 round_places: int = 3
                 ):

        self.data = normalisation_comparison.importSV(path_to_tab)

        if columns_from_source:
            self._get_headers()
        else:
            self.offset_column = offset_column
            self.measure_column = measure_column
            self.beat_column = beat_column
            self.length_column = length_column
            self.pitch_column = pitch_column
            self.key_column = key_column
            self.chord_column = chord_column

        self.slices = []
        self.distributions_by_measure = {}
        self.distributions_by_key = None
        self.distributions_by_chord = None
        self.overall_distribution = [0] * 12

        # Normalisation
        self.norm = norm
        self.norm_type = norm_type
        self.round_places = round_places

        self._get_slices_distributions()

    def _get_headers(self):
        """
        Attempts to retrieve current columns for measure etc from headers.
        By default this does not run (default values or user-defined).
        """
        self.headers = self.data[0]

        self.pitch_column = None
        self.length_column = None
        self.measure_column = None
        self.offset_column = None
        self.beat_column = None
        self.key_column = None
        self.chord_column = None

        for index in range(len(self.headers)):
            this_header = self.headers[index].lower()
            if 'pitch' in this_header:
                self.pitch_column = index
            elif 'length' in this_header:
                self.length_column = index
            elif 'measure' in this_header:
                self.measure_column = index
            elif 'offset' in this_header:
                self.offset_column = index
            elif ('beat' in this_header) and not ('strength' in this_header):
                self.beat_column = index
            elif 'key' in this_header:
                self.key_column = index
            elif 'chord' in this_header:
                self.chord_column = index

        self.data = self.data[1:]  # remove header row

    def _get_slices_distributions(self):
        """
        Process slices including making distributions for each.
        """

        self.slices = []

        for row in self.data:
            if len(row) > self.pitch_column:

                # Obligatory entries (fail if missing)
                this_slice = {'measure': int(row[self.measure_column]),
                              'beat': float(row[self.beat_column]),
                              'length': float(row[self.length_column])}

                if self.offset_column is not None:  # often column 0
                    this_slice['offset'] = float(row[self.offset_column])

                if self.pitch_column:
                    this_slice['pitch_names'] = row[self.pitch_column][2:-2].split("', '")
                    this_slice['pitch_classes'] = [
                        normalisation_comparison.pitch_class_from_name(x[:-1]) for x in
                        this_slice['pitch_names']]
                    # NB: -1 is a hack to remove octave

                if self.key_column and (len(row) > self.key_column):
                    this_slice['key'] = row[self.key_column]
                else:
                    this_slice['key'] = '.'  # no change, continuation

                if self.chord_column and (len(row) > self.chord_column):
                    this_slice['chord'] = row[self.chord_column]
                else:
                    this_slice['chord'] = '.'  # no change, continuation

                this_slice['distribution'] = normalisation_comparison.pc_list_to_distribution(
                    this_slice['pitch_classes'])

                self.slices.append(this_slice)

    # ------------------------------------------------------------------------------

    # Overall

    def get_overall_distributions(self):
        """
        Retrieve a single distribution for the piece overall.
        Uses distributions_by_measure() as an intermediary step (runs if not already).
        """

        self.overall_distribution = [0] * 12

        if not self.distributions_by_measure:
            self.get_distributions_by_measure()

        for m in self.distributions_by_measure.keys():
            m_dist = self.distributions_by_measure[m]
            for pc in range(12):
                self.overall_distribution[pc] += m_dist[pc]

        if self.norm:
            self.overall_distribution = normalisation_comparison.normalise(
                self.overall_distribution,
                normalisation_type=self.norm_type,
                round_output=True,
                round_places=self.round_places)
        else:
            rounded = [round(x, self.round_places) for x in self.overall_distribution]
            self.overall_distribution = rounded

    # ------------------------------------------------------------------------------

    # Measures

    def get_distributions_by_measure(self):
        """
        Sort slice distributions into a dict where
        the keys are the measure numbers and the corresponding
        values the distributions for that range.

        Normalisation is optional (default = False), set at the Class init.
        """

        # Get
        for s in self.slices:
            msr = s['measure']
            if msr not in self.distributions_by_measure.keys():
                self.distributions_by_measure[msr] = [0] * 12

            for pc in s['pitch_classes']:
                self.distributions_by_measure[msr][pc] += s['length']

        # Round and (optionally) normalise
        for msr in self.distributions_by_measure.keys():
            if self.norm:
                self.distributions_by_measure[msr] = normalisation_comparison.normalise(
                    self.distributions_by_measure[msr],
                    normalisation_type=self.norm_type,
                    round_output=True,
                    round_places=self.round_places
                )
            else:
                rounded = [round(x, self.round_places) for x in self.distributions_by_measure[msr]]
                self.distributions_by_measure[msr] = rounded

    def measure_range(self,
                      start_measure: int = 1,
                      end_measure: int = 100):
        """
        Return the combined distributions for all measure in a given range
        from start measure to (ending at, i.e. <) end measure.
        """
        combined = [0] * 12
        for this_measure in self.distributions_by_measure.keys():
            if start_measure <= this_measure < end_measure:
                for y in range(12):
                    combined[y] += self.distributions_by_measure[this_measure][y]

        return self.round_and_norm(combined)

    # ------------------------------------------------------------------------------

    # Keys and chords

    def get_distributions_by_key(self):
        """
        Sort the list of slices into separate segments for each key.
        This method populates the self.distributions_by_key list with
        separate entries for each passage the analyst has determined to be in a single key.

        Each entry takes the form of a dict where with the following keys:
        - key
        - distribution

        - start offset
        - end offset
        - quarter length

        - start measure
        - end measure
        - measure length

        Normalisation is optional (default = False), set at the Class init.
        """

        if self.distributions_by_key:
            return
        self.distributions_by_key = []
        self.group_by_key_or_chord(key_or_chord='key')

    def get_distributions_by_chord(self):
        """As for get_distributions_by_key"""

        if self.distributions_by_chord:
            return
        self.distributions_by_chord = []
        self.group_by_key_or_chord(key_or_chord='chord')

    def group_by_key_or_chord(self, key_or_chord: str = 'key'):
        """
        Shared method for
        get_distributions_by_key
        and
        get_distributions_by_chord
        """

        if key_or_chord not in ['key', 'chord']:
            raise ValueError("Arg 'key_or_chord' must be 'key' or 'chord'.")

        list_of_list_of_all_slices = []

        first_slice = self.slices[0]
        this_group = [first_slice]
        prevailing_key = first_slice[key_or_chord]

        for s in self.slices[1:]:  # NB
            if s[key_or_chord] in [prevailing_key, '.', '']:
                this_group.append(s)
            else:  # change, so new group
                list_of_list_of_all_slices.append(this_group)
                prevailing_key = s[key_or_chord]
                this_group = [s]

        # Once more for the final group
        list_of_list_of_all_slices.append(this_group)

        for this_group in list_of_list_of_all_slices:
            combined = self.combine_slice_group(this_group)
            if key_or_chord == 'key':
                self.distributions_by_key.append(combined)
            elif key_or_chord == 'chord':
                self.distributions_by_chord.append(combined)

    def combine_slice_group(self,
                            list_of_slices: list):
        """
        Shared method for synthesising a list of slice dicts into one dict with values for

         From the first slice:
             'start offset'
             'start measure'
             'key'
             'chord': note pop'd when grouping by key

         From the last slice:
             'end offset'
             'end measure' *

         From all the slices:
             'distribution'
             'quarter length'

        Also 'measure length' from the difference. *

        * NB: end measure and measure length only reliable in so far as the original slices data
             includes splits at the start of each measure. Potentially off by one otherwise.

        Abstracted enough to support grouping by:
        - changes of key (get_distributions_by_key > self.distributions_by_key)
        - changes of chord (get_distributions_by_chord > self.distributions_by_chord)
        """

        first_slice = list_of_slices[0]
        last_slice = list_of_slices[-1]

        entry = {'key': first_slice['key'],
                 'chord': first_slice['chord'],  # NB: pop'd when grouping by key

                 'start offset': first_slice['offset'],
                 'start measure': first_slice['measure'],

                 'end offset': last_slice['offset'] + last_slice['length'],
                 'end measure': last_slice['measure'],

                 'distribution': [0] * 12,  # init
                 'quarter length': 0,  # init
                 }

        for s in list_of_slices:
            for pc in range(12):
                entry['distribution'][pc] += s['distribution'][pc] * s['length']

            entry['quarter length'] += s['length']
            # Note: ^ Alternatively, sum([s['quarter length'] for s in list_of_slices]
            # Note: Likewise distributions

        # Finishing up
        entry['quarter length'] = round(entry['quarter length'], self.round_places)
        entry['distribution'] = self.round_and_norm(entry['distribution'])
        entry['measure length'] = entry['end measure'] - entry['start measure']

        return entry

    # ------------------------------------------------------------------------------

    # Write: same method for measures, keys, chords

    def write_distributions(self,
                            by_what: str = 'measure',
                            out_path: str = '.',
                            out_file: Optional[str] = None):
        """
        Optional, subsidiary method for writing out the distribution information
        to a tsv file.

        Support all grouping methods on this class through the by_what argument:
            'measure': writes a row for each measure with the measure number and distribution;
            'keys': does so for each change of key with additional information for start / end;
            'chord': as for 'keys' but while 'keys' does not include an account of the chords
            within that span; 'chord' does include the corresponding 'key'.

        """

        possible_headers = ['distribution',
                            'start offset',
                            'end offset',
                            'quarter length',
                            'start measure',
                            'end measure',
                            'measure length'
                            ]

        if by_what == 'measure':

            if not self.distributions_by_measure:
                self.get_distributions_by_measure()

            headers = ['Measure', 'Distribution']

            if not out_file:
                out_file = 'Distributions_by_measure'

        elif by_what == 'key':

            if not self.distributions_by_key:
                self.get_distributions_by_key()

            headers = ['key'] + possible_headers

            if not out_file:
                out_file = 'Keys_and_distributions'

        elif by_what == 'chord':

            if not self.distributions_by_chord:
                self.get_distributions_by_chord()

            headers = ['key', 'chord'] + possible_headers

            if not out_file:
                out_file = 'Chords_and_distributions'

        else:
            raise ValueError(f'Invalid `by_what` argument: {by_what}')

        with open(f'{os.path.join(out_path, out_file)}.tsv', "w") as sv_file:
            svOut = csv.writer(sv_file, delimiter='\t',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)

            svOut.writerow(headers)

            if by_what == 'measures':
                for k in self.distributions_by_measure:
                    svOut.writerow([k, self.distributions_by_measure[k]])
            elif by_what in ['key', 'chord']:
                for entry in getattr(self, 'distributions_by_' + by_what):
                    svOut.writerow([entry[h] for h in headers])

    def round_and_norm(self,
                       dist: list):
        """
        Wraps up one combined distribution with
        rounding and (optionally) normalisation.
        """
        if self.norm:
            return normalisation_comparison.normalise(dist,
                                                      normalisation_type=self.norm_type,
                                                      round_output=True,
                                                      round_places=self.round_places)
        else:
            return [round(x, self.round_places) for x in dist]


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def test_two_songs(self):
        base_path = '../../Corpus/OpenScore-LiederCorpus/'

        p = base_path + 'Reichardt,_Louise/Zwölf_Gesänge,_Op.3/01_Frühlingsblumen/'
        test_p = DistributionsFromTabular(path_to_tab=p + 'slices_with_analysis.tsv')
        test_p.get_distributions_by_key()
        self.assertEqual(len(test_p.distributions_by_key), 1)  # i.e. only one key

        q = base_path + 'Schumann,_Clara/Lieder,_Op.12/04_Liebst_du_um_Schönheit/'
        test_q = DistributionsFromTabular(path_to_tab=q + 'slices_with_analysis.tsv')
        test_q.get_distributions_by_key()
        self.assertEqual(len(test_q.distributions_by_key), 9)  # i.e. 9 local key areas
        self.assertEqual(test_q.distributions_by_key[0]['key'], 'Db')  # Starting in Db
        self.assertEqual(test_q.distributions_by_key[-1]['key'], 'Db')  # And ending there too


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
