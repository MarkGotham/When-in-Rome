import unittest

from music21 import common
from music21 import key
from music21 import metadata
from music21 import meter
from music21 import pitch
from music21 import chord
from music21 import roman
from music21 import stream

from numpy import array
from copy import deepcopy
import csv

#------------------------------------------------------------------------------

class M21: # M21 > TSV
    '''
    Convertions starting with a music21 harmonic analysis stream.
    '''
    def __init__(self, m21HarmonicAnalysis):
        self.m21HarmonicAnalysis = m21HarmonicAnalysis
        self.M21Array = self.toM21Array()

    def toM21Array(self):
        '''
        Convertion from a music21 harmonic analysis to an intermediary array format.
        '''

        headers = ['chord', # 0
                    'altchord',
                    'measure',
                    'beat',
                    'totbeat',
                    'timesig', # 5
                    'op',
                    'no',
                    'mov',
                    'length',
                    'global_key', # 10
                    'local_key',
                    'pedal',
                    'numeral',
                    'form',
                    'figbass', # 15
                    'changes',
                    'relativeroot',
                    'phraseend']

        info = [headers]

        inputHarmonicAnalysis = self.m21HarmonicAnalysis

        # MD
        opn = inputHarmonicAnalysis.metadata.opusNumber
        no = inputHarmonicAnalysis.metadata.number
        mvmt = inputHarmonicAnalysis.metadata.movementNumber

        romans = []

        for item in inputHarmonicAnalysis.recurse():
            if 'RomanNumeral' in item.classes:
                romans.append(item) # Still a m21 object at this stage
            if 'TimeSignature' in item.classes:
                ts = item.ratioString # Check for changes of ts during piece. TODO***

        globalKey = str(romans[0].key).split()[0] # From key of first fig. Most reliable option available.

        for item in romans: # Intermediary list because global needed in advance.

            # Relative root (NB duplicates vLocalKey method). TODO***
            relativeroot = None
            fig = item.figure
            if '/' in fig:
                position = fig.index('/')
                try:
                    int(fig[position+1]) # If it's an int then format of e.g. I6/4 rather than V/ii
                except:
                    relativeroot = fig[position+1:]

            # Local key. An ugly solution to be sure. TODO***
            pitches = item.key.pitches
            thisChord = chord.Chord([pitches[0], pitches[2], pitches[4]])
            rn = roman.romanNumeralFromChord(thisChord, key.Key(globalKey))
            localKey = rn.figure

            thisEntry = [item.figure, # TODO: combine key for key changes.
                        None, #'altchord',
                        item.measureNumber,
                        item.offset, # beat
                        None, # 'totbeat',
                        ts, # 'timesig', # 5 #TODO***
                        opn,# 'op',
                        no,# 'no',
                        mvmt,# 'mov',
                        item.quarterLength, # 'length',
                        globalKey, # 'global_key', # 10. Set below
                        localKey, # local_key
                        None, # 'pedal',
                        item.figure, # 'numeral',
                        None, # 'form',
                        None, # 'figbass', # 15
                        None, # 'changes',
                        relativeroot, # 'relativeroot',
                        None, # 'phraseend'
                        ]     # TODO: Review these and fill remaining columns using.
            info.append(thisEntry)

        harmonicArray = array(info)

        return harmonicArray

    def toABCArray(self):
        '''
        Makes an ABC-format version of a music21-format array by swapping
        equivalent text representations for the same Roman Numeral.
        '''

        ABC_Array = deepcopy(self.M21Array)

        globalKey = ABC_Array[1][10]

        for row in ABC_Array[1:]: # Leave header.
            if globalKey == globalKey.lower(): # If the global key is minor ...
                row[11] = characterSwaps(row[11], minor=True, direction='m21-ABC')
            else:
                row[11] = characterSwaps(row[11], minor=False, direction='m21-ABC')

            if row[11] == row[11].lower(): # If the local key is minor ...
                if row[17]: # If there's a relative root
                    if row[17] == row[17].lower(): # ... and it's minor too change it and the figure
                        row[17] = characterSwaps(row[17], minor=True, direction='m21-ABC')
                        row[13] = characterSwaps(row[13], minor=True, direction='m21-ABC')
                    else: # ... rel. root but not minor
                        row[17] = characterSwaps(row[17], minor=False, direction='m21-ABC')
                else: # No relative root
                    row[13] = characterSwaps(row[13], minor=True, direction='m21-ABC')
            else: # local Key not minor
                if row[17]: # If there's a relative root
                    if row[17] == row[17].lower(): # ... and it's minor
                        row[17] = characterSwaps(row[17], minor=False, direction='m21-ABC')
                        row[13] = characterSwaps(row[13], minor=True, direction='m21-ABC')
                    else: # ... rel. root but not minor
                        row[17] = characterSwaps(row[17], minor=False, direction='m21-ABC')
                else: # No relative root
                    row[13] = characterSwaps(row[13], minor=False, direction='m21-ABC')

        self.ABC_Array = ABC_Array

        return ABC_Array

    def toTSV(self, type='ABC', outFilePath='./', outFileName='TSV_FILE.tsv',):
        '''
        Makes a TSV file from a data array.
        '''

        if type=='ABC':
            harmonicInfo = self.ABC_Array
        elif type=='music21':
            harmonicInfo = self.M21Array

        tsvOut = arrayToTSV(harmonicInfo, outFilePath=outFilePath, outFileName=outFileName)

#------------------------------------------------------------------------------

class TSV:
    '''
    Conversion starting an ABC TSV file.
    '''
    def __init__(self, TSV_FILE):
       self.TSV_FILE = TSV_FILE
       self.ABC_Array = self.toABCArray()
       self.M21Array = self.toM21Array()

    def toABCArray(self):
        '''
        Takes an ABC TSV file and returns an array of the same data.
        '''

        fileName = self.TSV_FILE

        f = open(fileName, 'r')
        data = []
        for row_num, line in enumerate(f):
            values = line.strip().split('\t')
            # if row_num != 0: # Ignore first line (header)
            data.append([v.strip('\"') for v in values]) # Remove the extra set of quotes
        harmonicArray = array(data)
        f.close()

        return harmonicArray

    def toM21Array(self):
        '''
        Makes an m21-format version of the ABC-format data by swapping
        equivalent text representations for the same Roman Numeral.
        Also adds a column specifying the pitches entailed by the RN.
        ''' # Combine with above? TODO***

        M21Array = deepcopy(self.ABC_Array)

        globalKey = M21Array[1][10]

        for row in M21Array[1:]: # Ignore headers here

            # As above, but direction='ABC-m21'. TODO Make into a separate, static function

            # Global - local
            if globalKey == globalKey.lower():
                row[11] = characterSwaps(row[11], minor=True, direction='ABC-m21')
            else:
                row[11] = characterSwaps(row[11], minor=False, direction='ABC-m21')

            # Local - rel and figure
            if row[11] == row[11].lower():
                if row[17]:
                    if row[17] == row[17].lower():
                        row[17] = characterSwaps(row[17], minor=True, direction='ABC-m21')
                        row[13] = characterSwaps(row[13], minor=True, direction='ABC-m21')
                    else:
                        row[17] = characterSwaps(row[17], minor=False, direction='ABC-m21')
                else:
                    row[13] = characterSwaps(row[13], minor=True, direction='ABC-m21')
            else: # local key not minor
                if row[17]:
                    if row[17] == row[17].lower(): # ... and it's minor
                        row[17] = characterSwaps(row[17], minor=False, direction='ABC-m21')
                        row[13] = characterSwaps(row[13], minor=True, direction='ABC-m21')
                    else: # ... rel. root but not minor
                        row[17] = characterSwaps(row[17], minor=False, direction='ABC-m21')
                else: # No relative root
                    row[13] = characterSwaps(row[13], minor=False, direction='ABC-m21')


            numeral = str(row[13])
            form = str(row[14])
            figbass = str(row[15])
            # changes = str(row[16]). TODO***
            relativeRoot = str(row[17])

            # Combined figure for column[0] (though NB no key in the m21 case).
            combined = ''.join([numeral, form, figbass]) # , changes]). conversion TODO***
            if relativeRoot: # special case requiring '/'.
                combined = ''.join([combined, '/', relativeRoot])
            row[0] = combined

        self.M21Array = M21Array

        return M21Array

    def reduce(self):
        '''
        Takes an m21 array and returns a simplifed harmonic reduction with specific pitch classes
        ''' # Option to integate specific pitches back into array? TODO***

        headers = ['measure', 'beat', 'totbeat', 'pitchClasses']
        reducedData = [headers]

        harmonicArray = self.M21Array
        for row in harmonicArray[1:]:

            thisMeasure = int(row[2])
            beat =  float(row[3])
            totbeat = float(row[4])

            global_key = row[10]
            local_key = row[11]

            local_key_V2 = getLocalKey(local_key, global_key)
            local_key_V3 = key.Key(local_key_V2)

            try: # Some RNs missing
                rn = roman.RomanNumeral(row[0], local_key_V3) # e.g. ('VI', 'd')
                pitches = [x.pitchClass for x in rn.pitches]
                newRow = [thisMeasure, beat, totbeat, pitches]
                reducedData.append(newRow)
            except:
                continue

        return reducedData

    def toM21(self):
        '''
        Takes chords from an array and inserts them into a music21 stream prepared by .prepStream().
        '''

        self.prepStream()

        s = self.prepdStream # copy.Deepcopy?
        p = s.parts[0] # Just to get to the part, not that there are necessarily several.

        harmonicArray = self.M21Array

        for row in harmonicArray[1:]: # Ignore headers again ...

            # Get info.
            firstColumn = str(row[0])
            # altchord =
            thisMeasure = int(row[2])
            beat =  float(row[3]) # NB beat = offset + 1, so add extra variable for ...
            offsetInMeasure = beat - 1
            totbeat = float(row[4]) # music21's 'offset' but again, + 1 (starts on 1)
            # timesig = # Needed to check changes TODO
            # op, no, mov = 4, 5, 6 # Dealt with in metadata.
            length = float(row[9]) # music21's 'quarterLength'
            global_key = str(row[10])
            local_key = getLocalKey(str(row[11]), global_key)
            # pedal =
            numeral = str(row[13])
            form = str(row[14])
            figbass = str(row[15])
            changes = str(row[16])
            relativeRoot = str(row[17])
            # phraseend = #

            # Insert the rn to the relevant measure
            if numeral:
                combined = ''.join([numeral, form, figbass])
                # Simply omit 'changes' columns for now -- more conversion needed. TODO***
                if relativeRoot: # special case requiring '/'.
                    combined = ''.join([combined, '/', relativeRoot])

                rn = roman.RomanNumeral(combined, local_key)
                rn.quarterLength = length
                try:
                    p.measure(thisMeasure).insert(offsetInMeasure, rn)
                except:
                    raise ValueError('No such measure number %i in this piece' %thisMeasure)

        self.M21stream = s
        return s

    def prepStream(self):
        '''
        Prepares a music21 stream for the harmonic analysis to go into.
        Specifically: creates the score, part, and measure streams,
        as well as some (the available) metadata based on the orginal TSV data.
        '''

        s = stream.Score()
        p = stream.Part()

        harmonicArray = self.M21Array

        # Transfer metadatafrom within array. Check no in-doc changes (one doc, two mvmts). TODO***
        s.insert(0, metadata.Metadata())
        s.metadata.opusNumber = harmonicArray[1][6]
        s.metadata.number = harmonicArray[1][7]
        s.metadata.movementNumber = harmonicArray[1][8]
        # Would use int() except they sometimes include text like 'op2', 'no1'.

        startingKeySig = str(harmonicArray[1][10])
        ks = key.Key(startingKeySig)
        p.insert(0, ks)

        startingTimeSig = str(harmonicArray[1][5])
        ts = meter.TimeSignature(startingTimeSig)
        p.insert(0, ts) # Check for ts changes later. TODO***

        numerator = ts.numerator

        measures = list([int(row[2]) for row in harmonicArray[1:]]) # Headers again ...
        firstMeasure = measures[0]
        #
        last = measures[-1]
        #
        difference = 0 # initialise. 0 where no anacrusis (piece starts at the beginning of m1).
        if firstMeasure == 0:
            measure1index = measures.index(1)
            difference += (harmonicArray[measure1index][4] - harmonicArray[0][4]) # totbeat

        # Insert all measures into stream.
        for eachMeasureNo in range(measures[0], measures[-1]+1): # From start (0 or 1) to end.
            m = stream.Measure(number=eachMeasureNo)
            m.offset = (eachMeasureNo-1)*numerator + difference
            # Check for timesig changes. TODO***
            # Generalise for all timesig types (compound). TODO***
            p.insert(m)

        s.append(p)

        self.prepdStream = s

        return s

#------------------------------------------------------------------------------

# No class -- static functions needed in both directions.

def arrayToTSV(infoArray, outFilePath, outFileName):
    '''
    Takes an array (of any kind) and writes a TSV file.
    '''

    with open(outFilePath+outFileName, 'a') as csvfile: # 'a' to allow multiple works
        csvOut = csv.writer(csvfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for sublist in infoArray:
            csvOut.writerow([x for x in sublist])

def characterSwaps(preString, minor=True, direction='m21-ABC'):
    '''
    Character swap function to coordinate between the two notational versions.
    In all cases, swapping between '%' and '/o' for the notation of half diminished (for example).

    >>> testStr = 'ii%'
    >>> characterSwaps(testStr, minor=False, direction='ABC-m21')
    'ii/o'

    In the case of minor key, additional swaps for the different default 7th degrees:
    - raised in m21 (natural minor)
    - not raised in ABC (melodic minor)

    >>> testStr = '.f.vii'
    >>> characterSwaps(testStr, minor=True, direction='m21-ABC')
    '.f.#vii'

    >>> testStr = '.f.#vii'
    >>> characterSwaps(tstr, minor=True, direction='ABC-m21')
    '.f.vii'

    '''

    # For both major & minor. TODO: Expand and ensure that keys legitimate in all cases.
    characterDict = {'/o':'%',
                    }
    if direction=='ABC-m21': # Reverse direction. By default, direction='m21-ABC'
        characterDict = {'%': '/o', # Notation of half diminished
                        'M7':'7', # 7th types not specified in m21
                        # More? TODO***
                        }

    for key in characterDict: # Both major and minor
        preString = preString.replace(key, characterDict[key])

    if minor==True:

        if direction=='m21-ABC':
            search = 'b'
            insert = '#'
        elif direction=='ABC-m21':
            search = '#'
            insert = 'b'
        else:
            raise ValueError("Direction must be 'm21-ABC' or 'ABC-m21'.")

        if 'vii' in preString.lower():
            position = preString.lower().index('vii')
            prevChar = preString[position-1] # the previous character, # / b.
            if prevChar == search:
                postString = preString[:position-1]+preString[position:]
            else:
                postString = preString[:position]+insert+preString[position:]
        else:
            postString = preString

    else:
        postString = preString

    return postString

def getLocalKey(local_key, global_key, convert=False):
    '''
    Re-casts comparative local key (e.g. 'V of G major') in its own terms ('D').
    >>> getLocalKey('V', 'G')
    'D'
    >>> getLocalKey('ii', 'C')
    'd'
    By default, assumes an m21 input, and operates as such:
    >>> getLocalKey('vii', 'a')
    'g#'
    Set convert=True to convert from TSV to m21 formats. Hence;
    >>> getLocalKey('vii', 'a', convert=True)
    'g'
    '''

    if convert==True:
        if global_key[0] == global_key[0].lower(): # Minor. Given by first character (e.g. D, d, F#, f#, Bb, bb)
            local_key = characterSwaps(local_key, minor=True, direction='ABC-m21')
        else:
            local_key = characterSwaps(local_key, minor=False, direction='ABC-m21')

    asRoman = roman.RomanNumeral(local_key, global_key)
    rt = asRoman.root().name
    if asRoman.isMajorTriad():
        newKey = rt.upper()
    elif asRoman.isMinorTriad():
        newKey = rt.lower()

    return newKey

def vLocalKey(rn, local_key):
    '''
    Separates comparative roman numeral for tonicisiations like 'V/IV' into the component parts of
    - a roman numeral (V) and
    - a (very) local key (IV)
    and expresses that very local key in relation to the local key also called (ABC column 11).

    >>> getLocalKey(vi, C)
    'a'
    >>> vLocalKey(V/vi, C)
    'a'
    '''

    if '/' not in rn:
        very_local_as_key = local_key
        # raise ValueError("Only call this method to seperate a comparative roman numeral like 'V/V'")
    else:
        position = rn.index('/')
        very_local_as_roman = rn[position+1:]
        very_local_as_key = getLocalKey(very_local_as_roman, local_key)

    return very_local_as_key

# NB: not used

def extricateRoman(col0String):
    '''
    Retrieves the roman numeral (with inversions etc) from the column 0 value,
    cutting the key information which is more easily retrievable from local_key.
    '''

    if '.' not in col0String:
        raise ValueError("Only call this function on a string with '.' to indicate key changes.")
    else:
        lastDotIndex = finalOccurence(col0String, '.')
        extricatedRoman = col0String[lastDotIndex+1:]

    return extricatedRoman

def finalOccurence(haystack, needle):
    '''
    Returns the final occurence of one string in another.
    '''

    flippedHaystack = haystack[::-1]
    negIndex = flippedHaystack.find(needle)
    realIndex = len(haystack) - (negIndex + 1)

    return realIndex

#------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def testM21toTSV(self):

        testMonteverdiHarmony = corpus.parse('monteverdi/madrigal.3.1.rntxt')

        initial = M21(monteverdiHarmony) #
        m21Monteverdi = initial.toM21Array()
        TSVMonteverdi = initial.toTSVArray()

        self.assertEqual(m21Monteverdi[5][0], 'I')
        self.assertEqual(TSVMonteverdi[5][0], 'I')

        self.assertEqual(m21Monteverdi[175][13], 'viio6')
        self.assertEqual(TSVMonteverdi[175][13], '#viio6')

    # def testTSVtoM21(self): # TODO

    def testOfCharacter(self):

        startText = 'before%after'
        newText = [characterSwaps(x) for x in startText]
        # '%' > '/o'

        self.assertIsInstance(startText, str)
        self.assertIsInstance(newText, str)
        self.assertEqual(len(startText), 12)
        self.assertEqual(len(newText), 13)
        self.assertEqual(startText[6], '%')
        self.assertEqual(newTextMin[6], '/')

        testStr1in = 'ii%'
        testStr1out = characterSwaps(testStr, minor=False, direction='ABC-m21')

        self.assertEqual(testStr1in, 'ii%')
        self.assertEqual(testStr1out, 'ii/o')

        testStr2in = 'vii'
        testStr2out = characterSwaps(testStr, minor=True, direction='m21-ABC')

        self.assertEqual(testStr2in, 'vii')
        self.assertEqual(testStr2out, '#vii')

        testStr3in = '#vii'
        testStr3out = characterSwaps(testStr, minor=True, direction='ABC-m21')

        self.assertEqual(testStr2in, '#vii')
        self.assertEqual(testStr2out, 'vii')

    def testGetLocalKey(local_key, global_key, convert=False):

        test1 = getLocalKey('V', 'G')
        self.assertEqual(test1, 'D')

        test2 = getLocalKey('ii', 'C')
        self.assertEqual(test2, 'd')

        test3 = getLocalKey('vii', 'a')
        self.assertEqual(test3, 'g#')

        test4 = getLocalKey('vii', 'a', convert=True)
        self.assertEqual(test3, 'g')

    def testvLocalKey(self):

        testRN = 'V/vi'
        testLocalKey = 'D'

        veryLocalKey = vLocalKey(testRN, testLocalKey)

        self.assertIsInstance(veryLocalKey, str)
        self.assertEqual(veryLocalKey, 'b')

    def testExtricateRoman(self):

        col0String = 'ii.#viio2'
        extricatedRoman = extricateRoman(col0String)

        self.assertIsInstance(extricatedRoman, str)
        self.assertEqual(extricatedRoman[0], '#')

    def testFinalOccurence(self):

        haystack = 'je.nrtjer34jweqw39iodjsd'
        index = finalOccurence(haystack, '.')

        self.assertIsInstance(index, int)
        self.assertEqual(index, 2)
