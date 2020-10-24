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

The OpenScore lieder corpus is a large and growing multi-composer collection.
This script makes a csv file to keep track of the latest list of scores and
(optionally) also of those for which there are corresponding analyses.

Most metadata is retrieved from the directory structure, with the exception of the
lyricist and first time and key signatures.

Adaptable to other collections.

"""

# ------------------------------------------------------------------------------

import fnmatch
import os
import csv

from music21 import converter


# ------------------------------------------------------------------------------

def makeOpenScoreCSV(rootPath: str = '../Corpus/OpenScore-LiederCorpus/',
                     checkForAnalyses: bool = True,
                     additionalInfo: bool = True,
                     outPath: str = ''):
    """
    Make a csv file with the contents of the OpenScore lieder corpus.
    """

    data = []

    for root, dirs, files in os.walk(rootPath):
        for name in files:
            if fnmatch.fnmatch(name, 'lc*.mscx'):
                fullPath = str(os.path.join(root, name))
                thisEntry = fullPath.split('/')[-4:-1]

                if checkForAnalyses:
                    pathToHumanAnalysis = fullPath.replace(name, 'human.txt')
                    if os.path.exists(pathToHumanAnalysis):
                        thisEntry.append('YES')
                    else:
                        thisEntry.append('N')

                try:
                    scorePath = fullPath.replace(name, 'score.mxl')
                    score = converter.parse(scorePath)
                    p0m1 = score.parts[0].measures(0, 3)

                    lyricist = score.metadata.lyricist
                    if not lyricist:
                        lyricist = '[Missing entry]'
                    thisEntry.append(lyricist)

                    firstTS = p0m1.recurse().getElementsByClass('TimeSignature')[0]
                    thisEntry.append(firstTS.ratioString)

                    firstKS = p0m1.recurse().getElementsByClass('KeySignature')[0]
                    thisEntry.append(str(firstKS.sharps))

                    url = 'https://musescore.com/score/'
                    # ossia, longer url = 'https://musescore.com/openscore-lieder-corpus/scores/'
                    lcNumber = name[2:-5]  # cut 'lc' and extension
                    thisEntry.append(url + lcNumber)

                except:  # TODO: investigate and fix these scores!
                    print(f'ERROR with {name}')

                data.append(thisEntry)

    sortedData = sorted(data, key=lambda x: (x[0], x[1], x[2]))

    title = '_OpenScore lieder corpus contents'

    if not outPath:
        outPath = rootPath

    with open(f'{outPath}{title}.csv', 'w') as csvfile:
        csvOut = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        headers = ['COMPOSER', 'COLLECTION (where applicable)', 'SONG NUMBER AND TITLE', 'LYRICIST']
        if checkForAnalyses:
            headers += ['HUMAN ANALYSIS']
        if additionalInfo:
            headers += ['FIRST TS', 'FIRST KS', 'URL']

        csvOut.writerow(headers)
        for entry in sortedData:
            csvOut.writerow([x.replace('_', ' ') for x in entry if x])


# ------------------------------------------------------------------------------

if __name__ == '__main__':

    liederPath = '../Corpus/OpenScore-LiederCorpus/'
    makeOpenScoreCSV(rootPath=liederPath,
                     checkForAnalyses=True,
                     outPath=liederPath)
