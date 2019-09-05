# When in Rome

This repo provides corpora and supplementary material for the following paper:

Dmitri Tymoczko, Mark Gotham, Michael Scott Cuthbert, Christopher Ariza. “The Romantext Format: a Flexible and Standard Method for Representing Roman Numeral Analyses”, 20th International Society for Music Information Retrieval Conference, Delft, The Netherlands, 2019.

See also:
- https://github.com/cuthbertLab/music21/tree/master/music21/romanText
- http://web.web.mit.edu/music21/doc/moduleReference/moduleRoman.html
- http://web.mit.edu/music21/doc/usersGuide/usersGuide_23_romanNumerals.html

## Corpora

The corpora mentioned in the paper are hosted here or on music21 as follows:

- Complete scores and analyses for books 3--5 of the Monteverdi madrigals (48 works). [Hosted on music21: all .rntxt files in this folder](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/monteverdi).
- Complete preludes from the first book of [Bach's Well Tempered Clavier (24 analyses)](/Corpus/Bach Preludes/)
- A sample of Bach chorale analyses (20 analyses). [Hosted on music21: all files in this folder](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/bach/choraleAnalyses).
- The complete Beethoven string quartets, converted from the DCMLab's ABC corpus and with some manual error-correction (16 string quartets, 70 movements). [Hosted here, coming soon]
- A sample of Nineteenth-century French and German songs from the ['Scores of Scores' corpus](https://github.com/MarkGotham/ScoresOfScores), including Schubert's complete Winterreise cycle (50 songs). [Hosted here, coming soon]

## Lists

These lists spell out which pitches are associated with Roman numerals.

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
