# When in Rome

This repo provides Roman numeral analysis corpora and related material including the supplementary resources promised in:

[Dmitri Tymoczko, Mark Gotham, Michael Scott Cuthbert, Christopher Ariza. “The Romantext Format: a Flexible and Standard Method for Representing Roman Numeral Analyses”, 20th International Society for Music Information Retrieval Conference, Delft, The Netherlands, 2019.](http://archives.ismir.net/ismir2019/paper/000012.pdf )

See also:
- https://github.com/cuthbertLab/music21/tree/master/music21/romanText
- http://web.web.mit.edu/music21/doc/moduleReference/moduleRoman.html
- http://web.mit.edu/music21/doc/usersGuide/usersGuide_23_romanNumerals.html

## Corpora

The corpora provided include those mentioned in the paper as well as other created or converted since going to press, totaling around 250 scores and 80,000 Roman numerals.
These analyses are hosted here or on music21 as listed in the following subsections.

Note: As the paper attests, harmonic analysis is fundamentally, necessarily, and intentionally a reductive act that includes a good degree of subjective reading.
These are not in any sense, 'definitive' analyses to the exclusion of other possibilities.
Quite the opposite: part of the point of having a representation format like this is to enable the recording of variant readings.
Please feel free to re-analyse these works by using the existing analysis as a template and changing the parts you disagree with.
In that case, perhaps credit the original analyst too in the format: 'Analyst: [Your name] after [their name]'

### Hosted on music21
- Bach Chorales: A sample of 20 analyses. [Hosted on music21: all files in this folder](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/bach/choraleAnalyses).
- Monteverdi madrigals: Complete scores and analyses for books 3--5 of the Monteverdi madrigals (48 works). [Hosted on music21: all .rntxt files in this folder](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/monteverdi).

### Conversions of existing corpora
- ['BPS-FH'](/Corpus/BPS-FH/): Complete first movements of the Beethoven Piano Sonatas (32 movments), from [Tsung-Ping Chen and Li Su, ISMIR 2018](https://github.com/Tsung-Ping/functional-harmony).
- ['TAVERN'](/Corpus/TAVERN/): 27 sets of Variations by Mozart and Beethoven, from [Devaney et al, ISMIR 2015](https://github.com/jcdevaney/TAVERN)
- ['ABC'](/Corpus/ABC/): Complete Beethoven string quartets (16 string quartets, 70 movements), from the [DCMLab](https://github.com/DCMLab/ABC), with a small amount of error-correction and proof-reading to ensure parsing. (Proof-read version coming soon).

### New corpora by MG and colleagues
- [Bach Preludes](/Corpus/Bach_Preludes/): Complete preludes from the first book of Bach's Well Tempered Clavier (24 analyses)
- [Grounds](/Corpus/Grounds/): Examples of ground bass compositions from Purcell and Bach.
- [Nineteenth-century French and German songs](/Corpus/Songs/): A sample of 48 songs from the ['Scores of Scores' corpus](https://github.com/MarkGotham/ScoresOfScores), including Schubert's complete _Winterreise_ cycle.

## Templates

The templates folder contains templates for analyses of every song in the ['Scores of Scores' corpus](https://github.com/MarkGotham/ScoresOfScores).
These rntxt template files include the:
- metadata,
- time signatures, and
- measure range equalities

... but no actual analysis.
You can download these templates and fill them in with your take on the work.

The file names correspond exactly to the auto-updating corpus mirror [hosted here](https://github.com/shoogle/OpenScore-LiederCorpus) enabling easy pairing with the original scores.
That repo provides details of the file naming system.
The only modification here is to replace the '/' for subdirectories with '\_-\_'.

## Lists

To assist with the task of undertaking a Roman numerals, the 'Lists' folder spells out which pitches are associated with numerals.

This encompasses music21's default reading of:
- Every combination of the figures 2–9 (= 255 total, the number of files)
- Major/minor key (= 2),
- Root accidental ['b', '', '#'] (= 3)
- Scale degree, I-VII (= 7)
- Chord type (o, m, M, +; e.g. ['io', 'i', 'I', 'I+',]).  (= 4)

'Make-list.py' provides the (very simple) code for generating these list anew.

## Minor Mode

The lists were generated with music21's 'quality' default for handling the 6th / 7th degrees in minor mode.

Music21 has four settable options for handling minor key variation.
- Quality: the status of the triad as major or minor (upper or lower case, not accounting for diminished / augmented at this stage) alters the output chord’s root. In this case, ‘vii’ in a minor returns g# minor and the same holds for a diminished alteration (’viio’ = g# diminished). ‘VII’ sets the root to G natural, so ‘VII’ = G major and VII+ is G augmented.
- Cautionary: like 'quality', except that the ‘cautionary’ option ignores one chromatic alteration in the ‘sensible’ direction. So, ‘#vii’ would return g# minor, and not g## minor. Likewise, ‘bVII’ would be G major and not Gb major. This is useful to accommodating cases much of the realistic variation in minor mode conventions — the single, ‘sensible' sharp or flat is like a ‘cautionary accidental’. Further sharps and flats in the ‘sensible’ direction, and any sharps / flats in the opposite direction do change the root.
- Sharp / Raised: explicitly sets the 6th and / or 7th degrees to ‘Sharp / Raised’ (F# and G# in a minor).
- Flat / Lowered: the same for flatten / lowered roots (F and G in a minor).

The following tables set out how these options relate to each other in a minor. The first moves in a logical direction for  sharp / flat direction modifications. The second sets out the opposite direction, largely for the sake of completeness.

|“Right” direction|##vii|#vii|vii|VII|bVII|bbVII|
|---|---|---|---|---|---|---|
|Quality|g###|g##|g#|G|Gb|Gbb|
|Cautionary|g##|g#|g#|G|G|Gb|
|Sharp / Raised|g###|g##|g#|G#|G|Gb|
|Flat / Lowered|g##|g#|g|G|Gb|Gbb|

|“Wrong” direction|bbvii|bvii|vii|VII|VII#|VII##|
|---|---|---|---|---|---|---|
|Quality|gb|g|g#|G|G#|G##|
|Cautionary|gb|g|g#|G|G#|G##|
|Sharp / Raised|gb|g|g#|G#|G##|G###|
|Flat / Lowered|gbb|gb|g|G|G#|G##|

## Acknowledging and Contributing

Please see [music21](https://github.com/cuthbertLab/music21/) for details of the licensing for music21 code and corpora.

You are welcome to use the materials hosted here in your own work.
For research and other public-facing projects, please cite or otherwise acknowledge the above paper.

We welcome pull requests, including corrections and additions to the corpus. For any clear error there may be, please suggest a correction; for alternative readings, please submit a separate analysis.
