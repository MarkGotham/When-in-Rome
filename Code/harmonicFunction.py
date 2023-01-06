# -*- coding: utf-8 -*-
"""
===============================
HARMONIC FUNCTION (harmonicFunction.py)
===============================

Mark Gotham, 2021


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Mapping between Roman numeral figures and harmonic function labels.

TODO
This is a first draft with simple Functional labels
(total of 18, with max. 1 Haupt-, 1 Neben-, no inversions),
working mostly at the level of strings,
and with some assumptions (e.g., pairing Sp and ii in all cases).


"""


from music21 import roman
from typing import Union


# ------------------------------------------------------------------------------

functionFigureTuples = (
    # Scale degrees (major)
    # 1:
    ('T', 'I'), 
    ('t', 'i'),
    # b2:
    ('sL', 'bII'),
    # 2:
    ('Sp', 'ii'),
    # b3:
    ('tP', 'III'),  # Note first: tP generally preferred over dL
    ('dL', 'III'),
    # 3:
    ('Dp', 'iii'),  # Note first: Dp generally preferred over tL
    ('Tl', 'iii'),
    # 4:
    ('S', 'IV'),
    ('s', 'iv'),
    # 5:
    ('D', 'V'),
    ('d', 'v'),
    # b6:
    ('sP', 'VI'),  # Note first: sP generally preferred over tL
    ('tL', 'VI'),
    # 6:
    ('Tp', 'vi'),  # Note first: Tp generally preferred over Sl
    ('Sl', 'vi'),
    # b7:
    ('dP', 'VII'),
    # 7:
    ('D', 'vii'),
    ('Dl', '#VII'),
    )


def functionToFigure(harmonicFunctionLabel: str):
    '''
    Takes a Roman numeral figure (e.g., 'I') and
    returns the corresponding functional label (here, 'T' for major tonic).

    >>> functionToFigure('T')
    'I'

    Note that this is case sensitive.

    >>> functionToFigure('t')
    'i'

    The reverse operation is handled by the complementary
    `figureToFunction`.

    There are 18 main functional label supported in all, for
    the three functional categories
    (T for tonic,
    S for subdominant,
    and D for dominant) and
    three relevant transformation types (none, P, and L)
    all in upper and lower case (for major/minor):
    T, Tp, Tl, t, tP, tL,
    S, Sp, Sl, s, sP, sL,
    D, Dp, Dl, d, dP, dL.

    Some of the 18 main functions overlap, with two functional labels 
    referring to the same Roman numeral figure.
    That makes no difference to this function, 
    for instance both 'Tl' and 'Dp'simply map to 'iii':
        
    >>> functionToFigure('Tl')
    'iii'

    >>> functionToFigure('Dp')
    'iii'

    In the reverse case, `figureToFunction`
    follows the convention of dispreferring the L-version.
    For this example, 'iii' will return 'Dp' (i.e. not 'Tl').

    >>> figureToFunction('iii')
    'Dp'
    
    Finally, both functions return False if the input is not recognised 
    (i.e. in this case, not one of those functional label listed above).
    '''

    for entry in functionFigureTuples:
        if harmonicFunctionLabel == entry[0]:
            return entry[1]
    return False


def figureToFunction(romanNumeralFigure: Union[str, roman.RomanNumeral],
                     simplified: bool = False):
    '''
    Maps a Roman numeral figure to an harmonic function label.
    >>> figureToFunction('VI')
    'sP'
    
    Returns False in the case of no match.
        
    Optionally, return a simplified version which excludes any modications of 
    the basic set of 6: t, T, s, S, d, D 
    (major and minor forms of tonic, subdominant and dominant functions).
    >>> figureToFunction('VI', simplified=True)
    's'
    
    Inversions are not considered.
    If the input is a string, then no match will be found (returns False).
    If the input is a roman.RomanNumeral object they will be ignored 
    (using the romanNumeralAlone attribute).
    >>> rn = roman.RomanNumeral('VI65')
    >>> figureToFunction(rn)
    'sP'
    
    See further notes on the complementary `functionToFigure`.
    '''

    secondary = False

    returnString = ''

    if isinstance(romanNumeralFigure, roman.RomanNumeral):
        if romanNumeralFigure.secondaryRomanNumeral:
            secondary = True
        # Special case override:
        if romanNumeralFigure.figure == 'Cad64':
            romanNumeralFigure = 'V'
        else:
            romanNumeralFigure = romanNumeralFigure.romanNumeralAlone

    # Special case override. TODO D.R.Y.
    if romanNumeralFigure == 'Cad64':
        returnString = 'D'
    else:
        for entry in functionFigureTuples:
            if romanNumeralFigure == entry[1]:
                returnString = entry[0]
                if simplified:
                    returnString = returnString[0]
                break

    if secondary:
        returnString = f'({returnString})'

    if returnString:
        return returnString
    else:
        return False
    

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    import doctest
    doctest.testmod()
