# -*- coding: utf-8 -*-
"""
===============================
ANTHOLOGY (anthology.py)
===============================

Mark Gotham, 2020


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Methods for retrieving specific Roman numerals and/or progressions from analyses.

NOTE: musical logic previously here (isNeapolitan and isMixture) now moved to the main
music21 repo's [roman.py](https://github.com/cuthbertLab/music21/blob/master/music21/roman.py)

"""

from music21 import converter
from music21 import interval
from music21 import roman

from typing import List, Union

import csv
import fnmatch
import os


# ------------------------------------------------------------------------------

class RnFinder(object):
    """
    For retrieving specific Roman numerals and/or progressions from analyses.
    """

    def __init__(self,
                 pathToFile: str):

        self.userRnProgressionList = []
        self.augmentedChords = []
        self.augmentedSixths = []
        self.neapolitanSixths = []
        self.appliedChords = []
        self.mixtures = []

        self.analysis = converter.parse(pathToFile, format='romanText')
        self.rns = [x for x in self.analysis.recurse().getElementsByClass('RomanNumeral')]

    def findMixtures(self):

        for rn in self.rns:
            # NOTE: musical logic previously here now moved to the main music21 repo
            if not rn.secondaryRomanNumeral:
                if rn.isMixture():
                    self.mixtures.append(dataFromRn(rn))

    def findAppliedChords(self):

        for rn in self.rns:
            if rn.secondaryRomanNumeral:
                self.appliedChords.append(dataFromRn(rn))

    def findNeapolitanSixths(self):

        for rn in self.rns:
            # NOTE: musical logic previously here now moved to the main music21 repo
            if rn.isNeapolitan(require1stInversion=False):
                self.neapolitanSixths.append(dataFromRn(rn))

    def findAugmentedSixths(self):

        for rn in self.rns:
            if rn.isAugmentedSixth():
                self.augmentedSixths.append(dataFromRn(rn))

    def findAugmentedChords(self,
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
                self.augmentedChords.append(dataFromRn(rn))
            elif acceptSevenths:
                if rn.isSeventh:
                    if rn.isSeventhOfType([0, 4, 8, 11]) or rn.isSeventhOfType([0, 4, 8, 10]):
                        self.augmentedChords.append(dataFromRn(rn))
                    elif not requireAugAsTriad:
                        if rn.isSeventhOfType([0, 3, 7, 11]):
                            self.augmentedChords.append(dataFromRn(rn))

    def findProgressionByRns(self,
                             rns_list: List[str]):
        """
        Find a specific progression of Roman numerals in a given key input by the user as
        a list of Roman numeral figures like ['I', 'V65', 'I']
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
                info = [thisRange[0].getContextByClass('Measure').measureNumber,
                        figures,
                        thisRange[0].key]

                self.userRnProgressionList.append(info)

    def findProgressionByTypeAndIntv(self,
                                     qualitiesList: List,
                                     intervalList: List[Union[str, interval.Interval]] = None,
                                     bassOrRoot: str = 'bass',
                                     ):
        """
        Find a specific progression of Roman numerals
        searching by chord type quality and (optionally) bass or root motion.

        For instance, to find everything that might constitute a ii-V-I progression
        (whether or not those are the Roman numerals used), search for
        qualitiesList=['Minor', 'Major', 'Major'], intervalList=['P4', 'P-5']. bassOrRoot='root')

        This method accepts many input types.
        For the range accepted by qualitiesList,
        see documentation at isOfType().

        Blank entries are also fine.
        For instance, to find out how augmented chords resolve, search for
        qualitiesList=['Augmented triad', ''].
        To add the preceding chord as well, expand to:
        qualitiesList=['', 'Augmented triad', ''].
        Note that intervalList is left unspecified (we are interested in any interval succession.
        Anytime the intervalList is left blank, the search runs on quality only.
        """

        lnQs = len(qualitiesList)

        if intervalList:
            if lnQs != len(intervalList) + 1:
                raise ValueError('There must be exactly one more chord than interval.')

        # 1. Search quality match first: quality is required
        for index in range(len(self.rns) - lnQs):
            theseRns = self.rns[index: index + lnQs]
            for i in range(lnQs):
                if not isOfType(theseRns[i], qualitiesList[i]):
                    continue  # TODO check
            # 2. Only search for interval match if required and if the qualities already match.
            if intervalList:
                if intervalMatch(theseRns, intervalList, bassOrRoot):
                    info = dataFromRn(self.rns[index])
                    info['FIGURE'] = [x.figure for x in theseRns]
                    self.userRnProgressionList.append(info)

    def findPotentialCommonToneDiminishedSeventh(self,
                                                 requireProlongation: bool = True):
        """
        Find a potential instance of the common tone diminished seventh in any form by seeking:
        a diminished seventh,
        which shares at least one pitch with
        the chord before, the one after, or both.

        If requireProlongation is True, the results are limited to cases where the
        diminished seventh is preceded and followed by the same chord.
        """

        for index in range(1, len(self.rns) - 1):

            info = []

            thisChord = self.rns[index]

            if thisChord.isDiminishedSeventh():

                previousChord = self.rns[index - 1]
                nextChord = self.rns[index + 1]
                if requireProlongation:
                    if previousChord != nextChord:
                        break

                pitchesNow = set([p.name for p in thisChord.pitches])

                if previousChord.key == thisChord.key:  # currently required, may change
                    if previousChord.figure != thisChord.figure:  # TODO handling of repeating RNs
                        pitchesBefore = set([p.name for p in previousChord.pitches])
                        if pitchesNow & pitchesBefore:  # any shared pitch(class)
                            info = [previousChord.getContextByClass('Measure').measureNumber,
                                    [previousChord.figure, thisChord.figure],
                                    previousChord.key.name,
                                    ]
                        else:
                            if requireProlongation:
                                continue  # can't be without the previous chord

                nextChord = self.rns[index + 1]
                if nextChord.key == thisChord.key:
                    if nextChord.figure != thisChord.figure:
                        if requireProlongation and (nextChord.figure != previousChord.figure):
                            # info = []
                            continue
                        pitchesAfter = set([p.name for p in previousChord.pitches])
                        if pitchesNow & pitchesAfter:
                            if info:  # before and after, add to existing (combine all three)
                                info[1].append(nextChord.figure)
                            else:
                                info = [thisChord.getContextByClass('Measure').measureNumber,
                                        [thisChord.figure, nextChord.figure],
                                        thisChord.key.name,
                                        ]

                if info:
                    self.userRnProgressionList.append(info)


# ------------------------------------------------------------------------------

# Static

def dataFromRn(rn: roman.RomanNumeral):
    return {'MEASURE': rn.getContextByClass('Measure').measureNumber,
            'FIGURE': rn.figure,
            'KEY': rn.key.name.replace('-', 'b'),
            'BEAT': rn.beat,
            'BEAT STRENGTH': rn.beatStrength,
            'LENGTH': rn.quarterLength}


# TODO possible candidate for a new music21.chord.isOfType() function
def isOfType(thisChord, queryType):
    """
    Tests whether a chord (thisChord) is of a particular type (queryType).

    There are only two match criteria.
    First chords must have the same normal order.
    This means that C major and D major do match (transposition equivalence included),
    but C major and c minor do not (inversion equivalence excluded).
    Second, relevant pitch spelling must also match, so
    dominant sevenths do not match German sixth chords.

    thisChord can be a chord.Chord object
    or a roman.RomanNumeral (which inherits from chord.Chord).
    Raises an error otherwise.

    The queryType can be in almost any format.
    First, it can also be a chord.Chord object, including the same object as thisChord:
    >>> majorTriad = chord.Chord('C E G')
    >>> isOfType(majorTriad, majorTriad)
    True

    Second, is anything you can use to create a chord.Chord object, i.e.
    string of pitch names (with or without octave), or a list of
    pitch.Pitch objects,
    note.Note objects,
    MIDI numbers, or
    pitch class numbers.
    It bear repeating here that transpositon equivalence is fine:
    >>> isOfType(majorTriad, [2, 6, 9])
    True

    # TODO: implement chord.fromCommonName then add this:
    # Third, it can be any string returned by music21's chord.commonName.
    # These include fixed strings for
    # single pitch chords (including 'note', 'unison', 'Perfect Octave', ...),
    # dyads (e.g. 'Major Third'),
    # triads ('minor triad'),
    # sevenths ('dominant seventh chord'), and
    # other special cases ('all-interval tetrachord'),
    # The full list (based on Solomon's) can be seen at music.chord.tables.SCREF.
    # TODO >>> isOfType(majorTriad, 'whole tone scale')
    # TODO False
    #
    >>> wholeToneChord = chord.Chord([0, 2, 4, 6, 8, 10])
    #
    # TODO >>> isOfType(wholeToneChord, 'whole tone scale')
    # TODO True
    #
    # Additionally, chord.commonName supports categories of strings like (fill in the <>)
    # 'enharmonic equivalent to <>',
    # '<> with octave doublings',
    # 'forte class <>', and
    # '<> augmented sixth chord' (and where relevant) 'in <> position'.
    # TODO >>> isOfType(wholeToneChord, 'forte class <>' )
    # True
    #
    # As with chord.commonName, chords with no common name return the Forte Class
    # so that too is a valid entry (but only in those cases).
    # Any well-formed Forte Class string is acceptable, as is the format 'forte class 6-36B',
    # (which chord.commonName returns for cases with no common name):
    # TODO >>> isOfType(wholeToneChord, '6-35')
    # True

    Raises an error if the queryType is (still!) not valid.
    """
    from music21 import chord

    if not 'Chord' in thisChord.classes:
        raise ValueError('Invalid thisChord: must be a chord.Chord object')

    # Make reference (another chord.Chord object) from queryType
    reference = None
    try:
        reference = chord.Chord(queryType)
        # accepts string of pitches;
        # list of ints (normal order), pitches, notes, or strings;
        # even an existing chord.Chord object.
    except:  # can't make a chord directly. Assume string.
        if isinstance(queryType, str):
            if '-' in queryType:  # take it to be a Forte class.
                f = 'forte class '
                if queryType.startswith(f):
                    queryType = queryType.replace(f, '')
                reference = chord.fromForteClass(queryType)
            else:  # a string, not a Forte class, take it to be a common name.
                # TODO
                # reference = chord.fromCommonName(queryType)
                pass
        # else:
        #     raise ValueError(f'Invalid queryType. Cannot make a chord.Chord from {queryType}')
    if not reference:
        raise ValueError(f'Invalid queryType. Cannot make a chord.Chord from {queryType}')

    t = thisChord.commonName == reference.commonName
    return t


def intervalMatch(rnsList: list,
                  intervalList: list,
                  bassOrRoot: str = 'bass'):
    """
    Check whether the intervals (bass or root) between a succession of Roman numerals match a query.
    Requires the creation of interval.Interval objects.
    Minimised here to reduce load on large corpus searches.

    :param rnsList: list of Roman numerals
    :param intervalList: the query list of intervals (interval.Interval objects or directed names)
    :param bassOrRoot: intervals between the bass notes or the roots?
    :return: bool.
    """
    if bassOrRoot == 'bass':
        pitches = [x.bass() for x in rnsList]
    elif bassOrRoot == 'root':
        pitches = [x.root() for x in rnsList]
    else:
        raise ValueError('The bassOrRoot variable must be either bass or root.')

    if len(pitches) != len(intervalList) + 1:
        raise ValueError('There must be exactly one more RN than interval.')

    for i in range(len(intervalList)):
        sourceInterval = interval.Interval(pitches[i], pitches[i + 1]).intervalClass
        comparisonInterval = interval.Interval(intervalList[i]).intervalClass
        # NOTE: ^ Make sure to go through interval.Interval object
        if sourceInterval != comparisonInterval:
            return False  # false as soon as one doesn't match

    return True


# ------------------------------------------------------------------------------

corpora = ['Early_Choral',
           'Etudes_and_Preludes',
           'OpenScore-LiederCorpus',
           'Orchestral',
           'Piano_Sonatas',
           'Quartets',
           'Variations_and_Grounds']

validSearches = ['Modal Mixture',
                 'Augmented Chords',
                 'Augmented Sixths',
                 'Neapolitan Sixths',
                 'Applied Chords',
                 'Common Tone Diminished Sevenths',
                 'Progressions']


def oneSearchOneCorpus(corpus: str = 'OpenScore-LiederCorpus',
                       what: str = 'Modal Mixture',
                       progression: list = None,
                       write: bool = True,
                       heads: list = None
                       ):
    """
    Runs the search methods on a specific pair of corpus and serach term.
    Settable to find any of
        'Modal Mixture',
        'Augmented Chords',
        'Augmented Sixths',
        'Neapolitan Sixths',
        'Applied Chords',
        'Common Tone Diminished Sevenths'
        and
        'Progressions'.
    Defaults to the 'OpenScore-LiederCorpus' and 'Modal mixture'.
    If searching for a progression, set the progression variable to a list of
    Roman numerals figure strings like ['I', 'V65', 'I']
    """

    if heads is None:
        heads = ['COMPOSER',
                 'COLLECTION',
                 'MOVEMENT',
                 'MEASURE',
                 'FIGURE',
                 'KEY']

    if what not in validSearches:
        raise ValueError(f'For what, please select from among {validSearches}.')

    if what == 'Progression':
        if not progression:
            raise ValueError("If searching for a progression with the 'what' parameter, "
                             "set the 'progression' parameter to a list of Roman numeral figures "
                             "like ['I', 'V65', 'I'].")

    if corpus not in corpora:
        raise ValueError(f'Please select a corpus from among {corpora}.')

    lied = False
    if corpus == 'OpenScore-LiederCorpus':
        lied = True
        url = ''

    totalList = []
    totalRns = 0
    totalLength = 0

    corpusPath = os.path.join('..', 'Corpus', corpus)
    outPath = os.path.join('..', 'Anthology', corpus)

    print(f'Searching for {what} within the {corpus} collection:')

    for dpath, dname, fname in os.walk(corpusPath):
        for name in fname:
            if name == "analysis.txt":

                fullPath = str(os.path.join(dpath, name))
                pathtoFolder = fullPath[:-len(name)]
                print(pathtoFolder)

                idsDraft = pathtoFolder.split('/')[-4:-1]
                ids = [x.replace('_', ' ') for x in idsDraft]

                # URL for lieder
                if lied:
                    for fileName in os.listdir(pathtoFolder):
                        if fnmatch.fnmatch(fileName, 'lc*.mscx'):
                            lc = fileName[2:-5]
                            url = f'<a href="https://musescore.com/score/{lc}">{lc}</a>'
                            break
                    if not url:
                        print(f'No <lc*.mscx> file found in {pathtoFolder}')

                rnf = RnFinder(fullPath)
                totalRns += len(rnf.rns)
                totalLength += rnf.analysis.quarterLength

                if what == 'Modal Mixture':
                    rnf.findMixtures()
                    tempList = rnf.mixtures
                elif what == 'Augmented Chords':
                    rnf.findAugmentedChords()
                    tempList = rnf.augmentedChords
                elif what == 'Augmented Sixths':
                    rnf.findAugmentedSixths()
                    tempList = rnf.augmentedSixths
                elif what == 'Neapolitan Sixths':
                    rnf.findNeapolitanSixths()
                    tempList = rnf.neapolitanSixths
                elif what == 'Applied Chords':
                    rnf.findAppliedChords()
                    tempList = rnf.appliedChords
                elif what == 'Common Tone Diminished Sevenths':
                    rnf.findPotentialCommonToneDiminishedSeventh()
                    tempList = rnf.userRnProgressionList
                elif what == 'Progressions':
                    rnf.findProgressionByRns(rns_list=progression)
                    tempList = rnf.userRnProgressionList

                for x in tempList:
                    x['COMPOSER'] = ids[0]
                    x['COLLECTION'] = ids[1]
                    x['MOVEMENT'] = ids[2]
                    if lied:
                        x['URL'] = url

                totalList += tempList

    sortedList = sorted(totalList, key=lambda x: (x['COMPOSER'],
                                                  x['COLLECTION'],
                                                  x['MOVEMENT']))

    totalRnLength = sum([x['LENGTH'] for x in sortedList])
    print(f'{len(sortedList)} cases from {totalRns} RNs searched overall with a '
          f'combined length of {totalRnLength} from {totalLength}.')

    if not write:
        return sortedList

    with open(os.path.join(outPath, what + '.csv'), "w") as svfile:
        svOut = csv.writer(svfile, delimiter=',',
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)

        if lied:
            heads.append('URL')

        svOut.writerow(heads)

        for entry in sortedList:
            row = [entry[head] for head in heads]
            svOut.writerow(row)


def allSearchesOneCorpus(corpus: str = 'OpenScore-LiederCorpus'):
    """
    Runs the oneSearchOneCorpus function for
    one corpus and
    all search terms except 'Progressions'.
    """

    for w in validSearches[:-1]:  # omit progressions
        oneSearchOneCorpus(corpus=corpus, what=w)


def processAll():
    """
    Runs the oneSearchOneCorpus function for all pairs of
    corpus and search terms except 'Progressions'.
    """

    for c in corpora:
        for w in validSearches[:-1]:  # omit progressions
            oneSearchOneCorpus(corpus=c, what=w)


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod()
