# When in Rome

'When in Rome' brings together all of the world's harmonic analyses in encoded formats into a single, consistent repository.
This enables musicians and developers to interact with that great body of work at scale, with minimal overheads.

In total, there are now approximately 450 analyses and 100,000 Roman numerals in here.

Additionally, 'When in Rome' provides code for working with this corpora, building on top of the [music21](https://github.com/cuthbertLab/music21/) library for music analysis.

## Corpus Directory Structure

```
<genre>/<composer>/<set>/<movement>/<files>
```

Directories:

- `<genre>`: A top level classification of the works by approximate genre or repertoire. As most corpora are prepared in relation to this categorisation, this top level division also reflects something of the corpora's origins. (For the avoidance of doubt, every analysis includes an attribution.)

- `<composer>`: composer's name in the form `Last,_First`.

- `<set>`: extended work (e.g. a song cycle or piano sonata) where applicable. Stand-alone scores are placed in a set called `_` (i.e. a single underscore) for the sake of consistency.

- `<movement>`: name and/or number of the movement. In the case of a piano sonata, folder names are generally number-only: e.g. `1`. Most songs include both the name of the song and its position in the set (e.g. `1_Nach_Süden`)

## Corpus Overview

This corpus involves the combination of new analyses with conversions of those originating elsewhere.

### Corpora originating elsewhere

Converted from other formats:
- 27 sets of keyboard Variations by [Mozart,_Wolfgang_Amadeus](/Corpus/Variations_and_Grounds/Mozart) and [Beethoven](/Corpus/Variations_and_Grounds/Beethoven,_Ludwig_van/), from [Devaney et al.'s 'TAVERN' project, ISMIR 2015](https://github.com/jcdevaney/TAVERN)
- [Beethoven string quartets](/Corpus/Quartets/Beethoven,_Ludwig_van/) (complete, 16 string quartets, 70 movements): originating from the [DCMLab's 'ABC' corpus](https://github.com/DCMLab/ABC), with a small amount of error-correction and proof-reading to ensure parsing. (Proof-read version coming soon).
- [Beethoven Piano Sonata](/Corpus/Piano_Sonatas/Beethoven,_Ludwig_van/) (complete first movements, 32 movements), from Tsung-Ping Chen and Li Su's ['BPS-FH' dataset, ISMIR 2018](https://github.com/Tsung-Ping/functional-harmony).

Originally in the 'RomanText' format (no conversion needed):
- [Monteverdi madrigals](/Corpus/Early_Choral/Monteverdi,_Claudio/): Complete scores and analyses for books 3–5 of the Monteverdi madrigals (48 works), from [this part](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/monteverdi) of the music21 corpus.
- [Bach Chorales](/Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales): the sample of 20 analyses in [this part](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/bach/choraleAnalyses) of the music21 corpus.


### New corpora by MG and colleagues
- [Bach Preludes](/Corpus/Etudes_and_Preludes/Bach,_Johann_Sebastian/The_Well-Tempered_Clavier_I/): Complete preludes from the first book of Bach's Well Tempered Clavier (24 analyses)
- Ground bass examples from Purcell and Bach (within [this folder](/Corpus/Variations_and_Grounds/))
- [Nineteenth-century songs](/Corpus/OpenScore-LiederCorpus/): A sample of songs from the OpenScore / 'Scores of Scores' lieder corpus ([mirroring the public-facing score collection hosted here](https://musescore.com/openscore-lieder-corpus/sets)), including analyses for the complete [_Winterreise_](/Corpus/OpenScore-LiederCorpus/Schubert,_Franz/Winterreise,_D.911/) and [_Schwanengesang_](/Corpus/OpenScore-LiederCorpus/Schubert,_Franz/Schwanengesang,_D.957/) cycles (Schubert), [_Dichterliebe_](/Corpus/OpenScore-LiederCorpus/Schumann,_Robert/Dichterliebe,_Op.48/) (Schumann), and many of the songs by women composers that constitute a key part of and motivation for that collection.
- [Haydn Op. 20 String Quartets](/Corpus/Quartets/Haydn,_Franz_Joseph/): Complete annotations of Haydn's Op. 20 (6 string quartets, 24 movements), from the [MTG dataset](https://zenodo.org/record/1095630#.X8AbrcJyZhE).

The new corpora (Bach Preludes, Grounds, and 'Scores of Scores' lieder) also include the corresponding scores, templates, and feedback files.
(Please see the original corpora for score to the converted analyses.)
This is intended to support future contributors to this collection, making the study of these analyses and / or the submission of alternative readings as easy as possible.
[This page](https://fourscoreandmore.org/working-in-harmony/analysis/) provides full instructions for formatting your analysis.

### Folders with scores (most) include:

1. `score.mxl`
- What: A conversion of the corpus score into `.mxl`  format such that you can open it in any software editor.
- How to use: To add an analysis, enter it as lyrics to the bottom part. Note that lyrics must be affixed to a note, so in many or most cases it will be best to add a new part especially for this (e.g. press 'i' in Musescore) so that you can change the rhythm as needed.
2. `slices.tsv`
- What: a tabular representation of the score in 'slices' - vertical cross-sections of the score, with one for each change of pitch. The columns from left to right set out the:
  - `Offset` from the start (a time stamp measured in terms of quarter notes),
  - `Measure` number,
  - `Beat`,
  - `Beat 'Strength'` (from relative metrical position),
  - `Length` (also measured in quarter notes), and
  - `Pitches`.
- How to use: as a half-way house for the automatic comparisons (the slicing method is an intermediary step of that process).
3. `template.txt`
- What: a text file with only the metadata, time signatures, measures, and measure equality ranges as a template - i.e. all the information you need from the score with space to enter your own analysis.
- How to use: type in your analysis from scratch.
4. `lc*.mscz`
- What: For the songs, this is the score as it appears in the original lieder corpus, in its original MuseScore format.
- How to use: Open in MuseScore if you want to reference the original. We also use this to keep track of the 'lc' code number. You can find this score online by adding the lc number to the following URL: https://musescore.com/score/. Alternatively, click through from the '_OpenScore lieder corpus contents' in the root directory.

### Folders with human analyses (most) include:
1. `analysis.txt`
- What: A human analysis in plain text.
- How to use: As a way to view the analysis, or else to make your own analysis by creating a copy and editing moments you disagree with.
2. `analysis_on_score.mxl`
- What: The score with the human analysis added as an additional lowest part.
- How to use: Open in any notation software to view. Analysts may like to use this as a template for their own analysis. If so, edit the file in place. Code provided will extract the adjusted analysis and write it to Roman text format. Specifically, make changes to the lyrics. Don’t worry about the chords — they are there to illustrate the implications of the Roman numeral in question. Alternative (forthcoming) code is available for working directly with chords.
3. `feedback_on_analysis.txt`
- What: This is a text document providing feedback on the analysis generated by the 'romanUmpire' script.
- How to use: This helps direct attention to possible errors in the analysis. See [Code/romanUmpire.py](Code/romanUmpire.py) for more details on what it can and can't do.

## Code and Lists

For developers, please see the individual code files for details of what they do and how.

### [The Roman Umpire](/Code/romanUmpire.py)

This code generates the 'feedback' files.
It takes in a harmonic analysis and the corresponding score to assess how well they match.
Stay tuned for an interactive app with a friendly interface for making use of this code.

### [Anthology](/Code/anthology.py)

Methods for retrieving instances of specific chords and progression from the analyses.

### [Contents](/Code/contents.py)

A short script for keeping track of the ever growing corpus' contents.

### [Make List](/Code/makeList.py)

To assist with the task of undertaking a Roman numerals, the 'Lists' folder spells out which pitches are associated with numerals.

This encompasses music21's default reading of:
- Every combination of the figures 2–9 (= 255 total, the number of files)
- Major/minor key (= 2),
- Root accidental ['b', '', '#'] (= 3)
- Scale degree, I-VII (= 7)
- Chord type (o, m, M, +; e.g. ['io', 'i', 'I', 'I+',]).  (= 4)

'Make-list.py' provides the (very simple) code for generating these list anew.

## Minor Mode

This is one aspect of roman numeral analysis that is particularly liable to inconsistency and in need of a clear protocol.
Here, we follow the music21 default of 'quality', which is among four supported options:
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

## Licence, Acknowledging, Contribution

### Licence

New content in this repository, including the new analyses, most code, and the conversion (specifically) of existing analyses is available under the [CC BY-SA licence](https://creativecommons.org/licenses/by-sa/3.0/).
The [Roman Umpire](Code/romanUmpire.py) and [Anthology](Code/anthology.py) scripts are subject to the slightly more restrictive [CC BY-NC](https://creativecommons.org/licenses/by-nc/3.0/).
If you wish to use these scripts in a commercial context then please get in touch to discuss your plans.

For analyses that originated elsewhere and have been converted into the format used here, please refer to the original source for licence.
Links are provided to those original sources throughout the repository including the itemised list above and within every `analysis.txt` file.

For research and other public-facing projects making use of this work, please cite or otherwise acknowledge one or more of the papers listed below as appropriate to your project.

### Citeable Papers

The materials provided in this repo includes supplementary resources promised in:
- [Dmitri Tymoczko, Mark Gotham, Michael Scott Cuthbert, Christopher Ariza. “The Romantext Format: a Flexible and Standard Method for Representing Roman Numeral Analyses”, 20th International Society for Music Information Retrieval Conference, Delft, The Netherlands, 2019.](http://archives.ismir.net/ismir2019/paper/000012.pdf )
- [Gianluca Micchi, Mark Gotham, and Mathieu Giraud (2020). "Not All Roads Lead to Rome: Pitch Representation and Model Architecture for Automatic Harmonic Analysis", Transactions of the International Society for Music Information Retrieval, 3(1), pp. 42–54. DOI: https://doi.org/10.5334/tismir.45](https://transactions.ismir.net/articles/10.5334/tismir.45/)
- [Néstor Nápoles López, Mark R H Gotham, & Ichiro Fujinaga. (2021). AugmentedNet: A Roman Numeral Analysis Network with Synthetic Training Examples and Additional Tonal Tasks. Proceedings of the 22nd International Society for Music Information Retrieval Conference, 404–411](https://doi.org/10.5281/zenodo.5624533)
- [Mark R H Gotham, Rainer Kleinertz, Christof Weiss, Meinard Müller, & Stephanie Klauk. (2021). What if the 'When' Implies the 'What'?: Human harmonic analysis datasets clarify the relative role of the separate steps in automatic tonal analysis. Proceedings of the 22nd International Society for Music Information Retrieval Conference, 229–236](https://doi.org/10.5281/zenodo.5676067])

### Contributing to / new analyses

As the papers attest, harmonic analysis is fundamentally, necessarily, and intentionally a reductive act that includes a good degree of subjective reading.
As such, these analyses are not in any sense 'definitive', to the exclusion of other possibilities.
Quite the opposite: part of the point of having a representation format like this is to enable the recording of variant readings.
Please feel free to re-analyse these works by using the existing analysis as a template and changing the parts you disagree with.
- For minor changes, consider integrating your edits into the existing file using the variant (`var`) option that rntxt provides. E.g. `m1 I b2 IV` followed by a new line with `m1var1 I b2 ii6`
- For more thoroughly divergent analyses, a new file may be warranted. In that case, perhaps credit the original analyst too in the format - `Analyst: [Your name] after [their name]`
- For any cases of clear errors, please submit a pull request with the correction.

For details of the RomanText format used to encode analyses here, see our [technical specification paper](http://archives.ismir.net/ismir2019/paper/000012.pdf) or the relevant corners of the music21's [code](https://github.com/cuthbertLab/music21/tree/master/music21/romanText), [module reference](http://web.web.mit.edu/music21/doc/moduleReference/moduleRoman.html), or (if in doubt) [user guide](http://web.mit.edu/music21/doc/usersGuide/usersGuide_23_romanNumerals.html)
