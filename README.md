# When in Rome

This repo provides Roman numeral analysis code, corpora and related material including supplementary resources promised in:
- [Gianluca Micchi, Mark Gotham, and Mathieu Giraud (2020). "Not All Roads Lead to Rome: Pitch Representation and Model Architecture for Automatic Harmonic Analysis", Transactions of the International Society for Music Information Retrieval, 3(1), pp. 42–54. DOI: https://doi.org/10.5334/tismir.45](https://transactions.ismir.net/articles/10.5334/tismir.45/)
- [Dmitri Tymoczko, Mark Gotham, Michael Scott Cuthbert, Christopher Ariza. “The Romantext Format: a Flexible and Standard Method for Representing Roman Numeral Analyses”, 20th International Society for Music Information Retrieval Conference, Delft, The Netherlands, 2019.](http://archives.ismir.net/ismir2019/paper/000012.pdf )
- Other papers forthcoming

See also:
- https://github.com/cuthbertLab/music21/tree/master/music21/romanText
- http://web.web.mit.edu/music21/doc/moduleReference/moduleRoman.html
- http://web.mit.edu/music21/doc/usersGuide/usersGuide_23_romanNumerals.html

The corpora provided include those mentioned in the papers above and continues to grow.
The total provision now exceeds 250 scores and 80,000 Roman numerals.
Directions to these corpora are given in the following subsection.

Note: As the papers attest, harmonic analysis is fundamentally, necessarily, and intentionally a reductive act that includes a good degree of subjective reading.
As such, these analyses are not in any sense 'definitive', to the exclusion of other possibilities.
Quite the opposite: part of the point of having a representation format like this is to enable the recording of variant readings.
Please feel free to re-analyse these works by using the existing analysis as a template and changing the parts you disagree with.
In that case, perhaps credit the original analyst too in the format: 'Analyst: [Your name] after [their name]'

## Human Analysis Corpora

### Hosted on music21
- Bach Chorales: A sample of 20 analyses. [Hosted on music21: all files in this folder](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/bach/choraleAnalyses).
- Monteverdi madrigals: Complete scores and analyses for books 3–5 of the Monteverdi madrigals (48 works). [Hosted on music21: all .rntxt files in this folder](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/monteverdi).

### Conversions of existing corpora
- ['BPS-FH'](/Corpus/BPS-FH/): Complete first movements of the Beethoven Piano Sonatas (32 movements), from [Tsung-Ping Chen and Li Su, ISMIR 2018](https://github.com/Tsung-Ping/functional-harmony).
- ['TAVERN'](/Corpus/TAVERN/): 27 sets of Variations by Mozart and Beethoven, from [Devaney et al, ISMIR 2015](https://github.com/jcdevaney/TAVERN)
- ['ABC'](/Corpus/ABC/): Complete Beethoven string quartets (16 string quartets, 70 movements), from the [DCMLab](https://github.com/DCMLab/ABC), with a small amount of error-correction and proof-reading to ensure parsing. (Proof-read version coming soon).

### New corpora by MG and colleagues
- [Bach Preludes](/Corpus/Bach_Preludes/): Complete preludes from the first book of Bach's Well Tempered Clavier (24 analyses)
- [Grounds](/Corpus/Grounds/): Examples of ground bass compositions from Purcell and Bach.
- [Nineteenth-century French and German songs](/Corpus/OpenScore-LiederCorpus/): A sample of songs from the OpenScore / 'Scores of Scores' lieder corpus ([mirroring the public-facing score collection hosted here](https://musescore.com/openscore-lieder-corpus/sets)), including analyses for the complete _Winterreise_ and _Schwanengesang_ cycles (Schubert), _Dichterliebe_ (Schumann), and many of the songs by women composers that constitute a key part of and motivation for that collection.
- [Haydn Op. 20 String Quartets](/Corpus/HaydnOp20/): Complete annotations of Haydn's Op. 20 (6 string quartets, 24 movements), from the [MTG](https://zenodo.org/record/1095630#.X8AbrcJyZhE).

The new corpora (Bach Preludes, Grounds, and 'Scores of Scores' lieder) also include the corresponding scores, templates, and feedback files.
(Please see the original corpora for score to the converted analyses.)
This is intended to support future contributors to this collection, making the study of these analyses and / or the submission of alternative readings as easy as possible.
[This page](https://fourscoreandmore.org/working-in-harmony/analysis/) provides full instructions for formatting your analysis.

### Most folders include the following files:

1. 'score.mxl'
- What: A conversion of the corpus score into `.mxl`  format such that you can open it in any software editor.
- How to use: To add an analysis, enter it as lyrics to the bottom part. Note that lyrics must be affixed to a note, so in many or most cases it will be best to add a new part especially for this (e.g. press 'i' in Musescore) so that you can change the rhythm as needed.
2. 'slices.tsv'
- What: a tabular representation of the score in 'slices' - vertical cross-sections of the score, with one for each change of pitch. The columns from left to right set out the:
  - `Offset` from the start (a time stamp measured in terms of quarter notes),
  - `Measure` number,
  - `Beat`,
  - `Beat 'Strength'` (from relative metrical position),
  - `Length` (also measured in quarter notes), and
  - `Pitches`.
- How to use: as a half-way house for the automatic comparisons (the slicing method is an intermediary step of that process).
3. 'template.txt'
- What: a text file with only the metadata, time signatures, measures, and measure equality ranges as a template - i.e. all the information you need from the score with space to enter your own analysis.
- How to use: type in your analysis from scratch.
4. lc*.mscz
- What: The score as it appears in the lieder corpus, in its original MuseScore format.
- How to use: Open in MuseScore if you want to reference the original. We also use this to keep track of the 'lc' code number. You can find this score online by adding the lc number to the following URL: https://musescore.com/score/. Alternatively, click through from the '_OpenScore lieder corpus contents' in the root directory.

### Folders with human analyses include the following files:
1. 'analysis.txt'
- What: A human analysis in plain text.
- How to use: As a way to view the analysis, or else to make your own analysis by creating a copy and editing moments you disagree with.
2. 'analysis_onscore.mxl'
- What: The score with the human analysis added as an additional lowest part.
- How to use: Open in any notation software to view. Analysts may like to use this as a template for their own analysis. If so, edit the file in place. Code provided will extract the adjusted analysis and write it to Roman text format. Specifically, make changes to the lyrics. Don’t worry about the chords — they are there to illustrate the implications of the Roman numeral in question. Alternative (forthcoming) code is available for working directly with chords.
3. 'feedback_on_analysis.txt'
- What: This is a text document providing feedback on the analysis generated by the 'romanUmpire' script.
- How to use: This helps direct attention to possible errors in the analysis. See [Code/romanUmpire.py](Code/romanUmpire.py) for more details on what it can and can't do.

## Code and Lists

For developers, please see the individual code files for details of what they do and how.

### The Roman Umpire (romanUmpire.py)

This code generates the 'feedback' files.
It takes in a harmonic analysis and the corresponding score to assess how well they match.
Stay tuned for an interactive app with a friendly interface for making use of this code.

### Make List (makeList.py)

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
This is one aspect of roman numeral analysis that is particularly liable to inconsistency and in need of a clear protocol.
Here, we follow the music21 default of 'quality', which is among four supportde options:
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
