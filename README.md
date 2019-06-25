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
- Complete preludes from the first book of Bach's Well Tempered Clavier (24 analyses). [Hosted here, coming soon]
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

The lists were generated in 2018; please let me know if you find changes and I'll re-make them.

Additionally/alternatively, 'Make-list.py' provides the (very simple) code for generating these list anew.

## Acknowledging and Contributing

Please see [music21](https://github.com/cuthbertLab/music21/) for details of the licensing for music21 code and corpora.

You are welcome to use the materials hosted here in your own work.
For research and other public-facing projects, please cite or otherwise acknowledge the above paper.

We welcome pull requests, including corrections and additions to the corpus. For any clear error there may be, please suggest a correction; for alternative readings, please submit a separate analysis.
