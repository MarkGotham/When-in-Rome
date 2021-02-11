# -*- coding: utf-8 -*-
"""
===============================
Contents (contents.py)
===============================

Mark Gotham, 2020


LICENCE:
===============================

Creative Commons Attribution-NonCommercial 4.0 International License.
https://creativecommons.org/licenses/by-nc/4.0/


ABOUT:
===============================

A simple script for keeping track of the 'When in Rome' corpus collection.

As this corpus builds up incrementally from a range of sources:

1. collections may or may not be complete
(e.g. Chen and Su's BPS dataset took on Beethoven Piano sonatas, but the first movements only),

2. scores may or may not be included
(they are present for Open Score corpora like the lieder corpus, but not for some others),

3. where a full set of scores is available those scores may not have been analysed
(only a fraction the 1,000 lieder have analyses).

Most metadata is retrieved from the directory structure, with optional extras which
require score parsing to retrieve (movement length and initial time and key signatures).

"""


# ------------------------------------------------------------------------------

import fnmatch
import os
import csv

from music21 import converter


# ------------------------------------------------------------------------------

def makeContentsSV(corpus: str = 'OpenScore-LiederCorpus',
                   checkForScores: bool = True,
                   additionalInfo: bool = False):
    """
    Make a csv file with the contents of a corpus.
    Specifically, finds all 'analysis.txt' files, and optionally
    checks for whether there's a corresponding score hosted locally (checkForScores, default True),
    retrieves additional metadata from that score.
    """

    corpora = ['Early_Choral',
               'Etudes_and_Preludes',
               'OpenScore-LiederCorpus',
               'Orchestral',
               'Piano_Sonatas',
               'Quartets',
               'Variations_and_Grounds']

    if corpus not in corpora:
        raise ValueError(f'Corpus (currently {corpus}) must be one of {corpora}.')

    data = []
    rootPath = os.path.join('..', 'Corpus')
    corpusPath = os.path.join(rootPath, corpus)

    for root, dirs, files in os.walk(corpusPath):
        for name in files:
            if fnmatch.fnmatch(name, 'analysis.txt') or fnmatch.fnmatch(name, 'analysis_A.txt'):

                scoreAvailable = False

                analysisPath = str(os.path.join(root, name))
                thisEntry = analysisPath.split('/')[-4:-1]

                if checkForScores:
                    scorePath = analysisPath.replace(name, 'score.mxl')
                    if os.path.exists(scorePath):
                        scoreAvailable = True
                        thisEntry.append('YES')
                    else:
                        thisEntry.append('N')

                if additionalInfo:

                    if scoreAvailable:
                        score = converter.parse(scorePath)
                    else:
                        score = converter.parse(analysisPath, format='Romantext')

                    thisEntry.append(str(score.parts[0].quarterLength))

                    p0m1 = score.parts[0].measures(0, 3)
                    firstTS = p0m1.recurse().getElementsByClass('TimeSignature')[0]
                    thisEntry.append(firstTS.ratioString)
                    firstKS = p0m1.recurse().getElementsByClass('KeySignature')[0]
                    thisEntry.append(str(firstKS.sharps))

                    if corpus == 'OpenScore-LiederCorpus':  # Lieder-specific entries

                        lyricist = score.metadata.lyricist
                        if not lyricist:
                            lyricist = '[Missing entry]'
                        thisEntry.append(lyricist)

                        url = 'https://musescore.com/score/'
                        lcPath = analysisPath.replace(name, 'lc*.mscz')
                        if os.path.exists(lcPath):
                            lcNumber = name[2:-5]  # cut 'lc' and extension
                            thisEntry.append(url + lcNumber)
                        else:  # generic url for the set
                            url = 'https://musescore.com/openscore-lieder-corpus/scores/'
                            thisEntry.append(url)

                data.append(thisEntry)

    sortedData = sorted(data, key=lambda x: (x[0], x[1], x[2]))

    title = corpus + '_contents' + '.tsv'

    with open(os.path.join(rootPath, title), 'w') as csvfile:
        csvOut = csv.writer(csvfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        headers = ['COMPOSER', 'COLLECTION', 'MOVEMENT']
        if checkForScores:
            headers += ['SCORE']
        if additionalInfo:
            headers += ['QUARTER LENGTH', '1ST TIME SIG', '1ST KEY SIG']
            if corpus == 'OpenScore-LiederCorpus':  # Lieder-specific entries
                headers += ['LYRICIST', 'URL']

        csvOut.writerow(headers)
        for entry in sortedData:
            csvOut.writerow([x.replace('_', ' ') for x in entry if x])


def runAll():
    for corpus in ['Early_Choral',
                   'Etudes_and_Preludes',
                   'OpenScore-LiederCorpus',
                   'Orchestral',
                   'Piano_Sonatas',
                   'Quartets',
                   'Variations_and_Grounds']:
        makeContentsSV(corpus, checkForScores=True, additionalInfo=False)


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    runAll()
