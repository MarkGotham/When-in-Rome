"""
===============================
Get Distributions (get_distributions.py)
===============================

Mark Gotham, 2020-21


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


Citation:
===============================

Gotham et al. "What if the 'When' Implies the 'What'?". ISMIR, 2021
(see README.md)


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

import os
import csv
from functools import cached_property

from . import normalisation_comparison
from . import chord_features

from typing import Optional
import numpy as np

# ------------------------------------------------------------------------------

features_list = [
    'chordQualityVector',
    'thirdTypeVector',
    'fifthTypeVector',
    'seventhTypeVector',
    'rootPitchClassVector',
    'hauptFunctionVector',
    'functionVector',
    'chosenChordPCPVector',
    'bestFitChordPCPVector',
    'chordTypeMatchVector',
    'chordRotationMatchVector',
    'distanceToBestFitChordPCPVector',
    'distanceToChosenChordVector',
    'fullChordCommonnessVector',
    'simplifiedChordCommonnessVector',
]


# ------------------------------------------------------------------------------

class DistributionsFromTabular:
    """
    For making usage distributions from tabular representations of scores.
    """

    def __init__(self,
                 path_to_tab: str,

                 columns_from_source: bool = False,

                 norm: bool = False,
                 norm_type: str = 'Sum',
                 round_places: int = 3,

                 include_features: bool = True,
                 features_to_use: Optional[list] = None
                 ):

        self.include_features = include_features
        if features_to_use and not self.include_features:
            raise ValueError('You have attempted to define features_to_use'
                             'but have set include_features to false. ')
        if features_to_use:
            self.features_to_use = features_to_use
        else:
            self.features_to_use = features_list

        self.path_to_dir = os.path.dirname(path_to_tab)
        self.data = normalisation_comparison.importSV(path_to_tab)

        if columns_from_source:
            self._get_headers()
        else:
            self.headers = ["offset", "measure", "beat", "beat_strength", "length", "pitch", "key", "chord"]

        # Normalisation
        self.norm = norm
        self.norm_type = norm_type
        self.round_places = round_places

    def _get_headers(self):
        """
        Attempts to retrieve current columns for measure etc from headers.
        By default this does not run (default values or user-defined).
        """
        self.headers = self.data[0]
        self.data = self.data[1:]  # remove header row

    @cached_property
    def slices(self):
        """
        Process slices including making distributions for each.
        """
        slices = []
        for row in self.data:
            if len(row) > self.headers.index('pitch'):

                # Obligatory entries (fail if missing)
                this_slice = {'measure': int(row[self.headers.index('measure')]),
                              'beat': float(row[self.headers.index('beat')]),
                              'length': float(row[self.headers.index('length')])}

                if 'offset' in self.headers:  # often column 0
                    this_slice['offset'] = float(row[self.headers.index('offset')])

                if 'pitch' in self.headers:
                    this_slice['pitch_names'] = row[self.headers.index('pitch')][2:-2].split("', '")
                    this_slice['pitch_classes'] = [
                        normalisation_comparison.pitch_class_from_name(x[:-1]) for x in
                        this_slice['pitch_names'] if x]
                    # -1 to remove octave
                    # and 'if x' because of occasional blank '' (no pitch) slice

                if 'key' in self.headers and (len(row) > self.headers.index('key')):
                    this_slice['key'] = row[self.headers.index('key')]
                else:
                    this_slice['key'] = '.'  # no change, continuation

                if 'chord' in self.headers and (len(row) > self.headers.index('chord')):
                    this_slice['chord'] = row[self.headers.index('chord')]
                else:
                    this_slice['chord'] = '.'  # no change, continuation

                this_slice['profile'] = normalisation_comparison.pc_list_to_distribution(
                    this_slice['pitch_classes'])

                slices.append(this_slice)
        return slices

    # ------------------------------------------------------------------------------

    # Overall

    @cached_property
    def overall_distribution(self):
        """
        Retrieve a single distribution for the piece overall.
        Uses profiles_by_measure() as an intermediary step (runs if not already).
        """
        overall_distribution = np.zeros(12)
        for m, m_dist in self.profiles_by_measure.items():
            overall_distribution += np.array(m_dist)

        return self.round_and_norm(list(overall_distribution))

    # ------------------------------------------------------------------------------

    # Measures
    @cached_property
    def profiles_by_measure(self):
        """
        Sort slice distributions into a dict where
        the keys are the measure numbers and the corresponding
        values the distributions for that range.

        Normalisation is optional (default = False), set at the Class init.
        """
        profiles_by_measure = {}
        for s in self.slices:
            msr = s['measure']
            if msr not in profiles_by_measure.keys():
                profiles_by_measure[msr] = [0] * 12

            for pc in s['pitch_classes']:
                profiles_by_measure[msr][pc] += s['length']

        # Round and (optionally) normalise
        for msr in profiles_by_measure.keys():
            if self.norm:
                profiles_by_measure[msr] = normalisation_comparison.normalise(
                    profiles_by_measure[msr],
                    normalisation_type=self.norm_type,
                    round_output=True,
                    round_places=self.round_places
                )
            else:
                rounded = [round(x, self.round_places) for x in profiles_by_measure[msr]]
                profiles_by_measure[msr] = rounded
        return profiles_by_measure

    def measure_range(self,
                      start_measure: int = 1,
                      end_measure: int = 100):
        """
        Return the combined distributions for measure in a given range
        from start_measure to (ending at, i.e. <) end_measure.
        """
        combined = [0] * 12
        for this_measure in self.profiles_by_measure.keys():
            if start_measure <= this_measure < end_measure:
                for y in range(12):
                    combined[y] += self.profiles_by_measure[this_measure][y]

        return self.round_and_norm(combined)

    # ------------------------------------------------------------------------------

    # Keys and chords

    @cached_property
    def profiles_by_key(self):
        """
        Sort the list of slices into separate segments for each key.
        This method populates the self.profiles_by_key list with
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
        return self._group_by_key_or_chord(key_or_chord='key')

    @cached_property
    def profiles_by_chord(self):
        """As for get_profiles_by_key"""
        return self._group_by_key_or_chord(key_or_chord='chord')

    def _group_by_key_or_chord(self, key_or_chord):
        """
        Shared method for
        get_profiles_by_key
        and
        get_profiles_by_chord
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
        return [self.combine_slice_group(this_group) for this_group in list_of_list_of_all_slices]

    def combine_slice_group(self,
                            list_of_slices: list,):
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
             'profile'
             'quarter length'

        Also 'measure length' from the difference. *

        * NB: end measure and measure length only reliable in so far as the original slices data
             includes splits at the start of each measure. Potentially off by one otherwise.

        Abstracted enough to support grouping by changes of:
        - key (get_profiles_by_key > self.profiles_by_key)
        - chord (get_profiles_by_chord > self.profiles_by_chord)
        - measure (get_profiles_by_measure > self.profiles_by_measure)

        This method also gathers feature information as described in chord_features.get_features
        if self.include_features is set to True (at the class init)

        Note how this relates to arguments at
        the class init:
        - self.include_features must be True for this information to be collected
        - self.features_to_use defines which.
        and in write_distributions (option to write that information).
        """

        first_slice = list_of_slices[0]
        last_slice = list_of_slices[-1]

        entry = {'key': first_slice['key'],
                 'chord': first_slice['chord'],  # NB: pop'd when grouping by key

                 'start offset': first_slice['offset'],
                 'start measure': first_slice['measure'],

                 'end offset': last_slice['offset'] + last_slice['length'],
                 'end measure': last_slice['measure'],

                 'profile': [0] * 12,  # init
                 'quarter length': 0,  # init
                 }

        for s in list_of_slices:
            for pc in range(12):
                entry['profile'][pc] += s['profile'][pc] * s['length']

            entry['quarter length'] += s['length']
            # Note: ^ Alternatively, sum([s['quarter length'] for s in list_of_slices]
            # Note: Likewise distributions

        # Finishing up
        entry['quarter length'] = round(entry['quarter length'], self.round_places)
        entry['profile'] = self.round_and_norm(entry['profile'])
        entry['measure length'] = entry['end measure'] - entry['start measure']

        if self.include_features:
            from music21 import roman
            rn = roman.RomanNumeral(entry['chord'], entry['key'])
            features = chord_features.SingleChordFeatures(rn, entry['profile'])
            for feat in self.features_to_use:  # see below for list
                entry[feat] = getattr(features, feat)

        return entry

    # ------------------------------------------------------------------------------

    # Write: same method for measures, keys, chords

    def write_distributions(self,
                            by_what: str = 'measure',
                            out_path: Optional[str] = None,
                            out_file: Optional[str] = None,
                            write_features: bool = False,
                            out_format: str = '.tsv'
                            ):
        """
        Optional, subsidiary method for writing out the distribution information
        to one of '.csv', '.tsv', '.arff' and '.json'
        which are all well-known with the possible exception of
        .arff for recording features (documented in Vatolkin et al. ***).

        Support all grouping methods on this class through the by_what argument:
            'measure':  writes a row for each measure with the measure number and distribution;
            'keys':     does so for each change of key with additional information for start / end;
            'chord':    as for 'keys' but while 'keys' does not include an account of the chords
                        within that span; 'chord' does include the corresponding 'key'.

        Set write_features to True (bool, default is False) to include feature information.
        Note how this relates to arguments at the class init:
        - self.include_features must be True for this information to be collected at all.
        - self.features_to_use defines which features.
        """

        # Check valid

        valid_formats = ['.csv', '.tsv', '.arff', '.json']
        if out_format not in valid_formats:
            raise ValueError(f'Invalid out_format: must one of {valid_formats}')

        valid_by_what = ['measure', 'key', 'chord']
        if by_what not in valid_by_what:
            raise ValueError(f'Invalid `by_what` argument: must be one of {valid_by_what}')

        # Headers
        if by_what == 'measure':
            headers = ['measure', 'profile']
        else:  # 'key', 'chord'
            headers = ['profile',
                       'start offset',
                       'end offset',
                       'quarter length',
                       'start measure',
                       'end measure',
                       'measure length'
                       ]

        if write_features:
            headers += features_list

        # Data: get_ / profiles_by_ / measure, key, chord, / ()
        # NB: don't need 'if not getattr('. There's a check / return at the start of each method
        getattr(self, 'get_profiles_by_' + by_what)()  # Note to self, () outside
        data = getattr(self, 'profiles_by_' + by_what)

        # 'key', 'chord'
        if out_format != '.arff' and by_what != 'measure':
            if by_what == 'chord':
                headers = ['chord'] + headers
            headers = ['key'] + headers  # in both cases 'key', 'chord'

        # Write

        if not out_path:
            out_path = self.path_to_dir  # i.e. same as source

        if not out_file:
            out_file = 'profiles'
            if write_features:
                out_file += '_and_features'
            out_file += f'_by_{by_what}'
        full_path = str(os.path.join(out_path, out_file)) + out_format

        if out_format == '.json':
            import json
            with open(full_path, 'w') as f:
                json.dump(data, f)
            return
        else:
            delimiter = ','  # Init for '.csv' or '.arff'
            if out_format == '.tsv':  # Alter for '.tsv'
                delimiter = '\t'
            with open(full_path, "w") as sv_file:
                svOut = csv.writer(sv_file, delimiter=delimiter,
                                   quotechar='"', quoting=csv.QUOTE_MINIMAL)

                # Headers
                if out_format == '.arff':
                    svOut.writerow([f"@RELATION \'Chord features for {out_file}\'"])
                    for h in headers:
                        svOut.writerow([f"@ATTRIBUTE \'{h}\' NUMERIC"])  # TODO check types
                    svOut.writerow([f"@DATA"])
                else:  # tsv, csv
                    svOut.writerow(headers)

                # Data
                if by_what == 'measure':
                    for k in self.profiles_by_measure:
                        svOut.writerow([k, self.profiles_by_measure[k]])
                elif by_what in ['key', 'chord']:
                    for entry in data:
                        # svOut.writerow([entry[h] for h in headers])
                        svOut.writerow([str(entry[h]) for h in headers])

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
            return list(np.round(dist, self.round_places))
