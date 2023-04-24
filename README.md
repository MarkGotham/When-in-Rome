![GitHub top language](https://img.shields.io/github/languages/top/MarkGotham/When-in-Rome)
![GitHub issues](https://img.shields.io/github/issues-raw/MarkGotham/When-in-Rome)
![GitHub last commit](https://img.shields.io/github/last-commit/MarkGotham/When-in-Rome)
![GitHub repo size](https://img.shields.io/github/repo-size/MarkGotham/When-in-Rome)
![License](https://img.shields.io/badge/license-CC%20BY--SA%204.0-9)

# When in Rome

'When in Rome' brings together the world's functional harmonic analyses in encoded formats 
into a single, consistent repository.
This enables musicians and developers to interact with that great body of work at scale, 
with minimal overheads.

In total, there are now approximately 2,000 analyses of 1,500 distinct works.

Additionally, 'When in Rome' provides code for working with these corpora, 
building on the [music21](https://github.com/cuthbertLab/music21/) library for music analysis.

## Is it for me?

This is best thought of as primarily a corpus of _analyses_ which secondarily provide code for working with them and include the _score_ where possible.
I.e., the focus is on the analyses.
There is a very great deal we can do with those analyses alone.
Clearly there are also certain questions to require analysis-source alignment.
We do our best to cater for that by including the _score_ wherever possible, and as reliably aligned as possible (as anyone in the field knows, this is a significant challenge).

We're proud of how useful this is.
All the same, it might not serve your needs.
Might we suggest that if you're looking for:
- scores only in a permissive licence, then try the [OpenScore Lieder Corpus (1,300 songs, CC0 licence)](https://github.com/OpenScore/Lieder).
- a small corpus of perfectly aligned scores + analyses (i.e., your priority is alignment, not overall size or diversity of content) then a single (not meta-) corpus like one of the DCML corpora listed below.

## Corpus Directory Structure

### Overall

```
<genre>/<composer>/<set>/<movement>/<files>
```


- `<genre>`: A top level classification of the works by approximate genre or repertoire. As most corpora are prepared in relation to this categorisation, this top level division also reflects something of the corpora's origins. (For the avoidance of doubt, every analysis includes an attribution.)

- `<composer>`: composer's name in the form `Last,_First`.

- `<set>`: extended work (e.g. a song cycle or piano sonata) where applicable. Stand-alone scores are placed in a set called `_` (i.e. a single underscore) for the sake of consistency.

- `<movement>`: name and/or number of the movement. In the case of a piano sonata, folder names are generally number-only: e.g. `1`. Most songs include both the name of the song and its position in the set (e.g. `1_Nach_Süden`)

- `<files>`: See the following sub-sections.

The [Key Modulations and Tonicizations](Corpus/Textbooks/) corpus is a slight exception: we preserve the organisation of that corpus by author, title, example number, e.g., `Corpus/Textbooks/Aldwell,_Edward/Harmony_and_Voice_Leading/2a/`. So the `<genre>` is `Textbooks`, the `<composer>` is the author, the `<set>` is the title, and the `<movement>` is the example number.
We find this more logical that re-organisation by composer.

### All folders include:

- `score.mxl` or a `remote.json` file including links to external score files 
  - What: `score.mxl` is a copy of the score in the compressed musicXML format. 
    This is provided for all new scores, as well as all originating elsewhere  
    where that original is _in a format which music21 cannot parse_.
  - How to use: Open in any software for music notation (e.g., [MuseScore](https://musescore.org/)).
  - Where there is no local `score.mxl`, there is a `remote.json` instead. Please note:
    - This file points to an externally hosted score _in a format which music21 can parse_. 
    - This is designed to prevent duplication and automatically include source updates.
    - Note that MuseScore files are included in a local conversion (`.mxl`) rather than remote.
      - This is because music21 cannot parse them and conversion requires the `mscore` package 
        (see `Code.updates_and_checks.convert_musescore_score_corpus`).
    - For downloading a local copy of remote files, see `Code.updates_and_checks.remote_scores` 
      and the argument `convert_and_write_local`. Read those docs for details and warnings.
    - Please check and observe the licence of all scores, especially those hosted externally.

- `analysis.txt`
  - What: A human analysis in plain text.
  - How to use: Open in any text editor. 
    You can also use these analyses as a kind of template for your own, 
    by creating a copy and editing only the moments you disagree with.
 
- `analysis_automatic.rntxt`.
  - What: An automatic analysis made by [AugmentedNet](https://github.com/napulen/AugmentedNet) - 
    a machine learning architecture which, in turn, is built on this meta-corpus' data.
  - How to use: In exactly the same way as a human analysis, e.g., as a template (same format, same parsing routines).

### Some folders include:

- `remote.json` files 
  - What: this provides additional information about remote content including paths to external 
    scores as discussed above.
  - Additionally, we take the opportunity to provide metadata including composer name and one or 
    more sets of catalogue information (`Opus` and/or equivalent).

- `analysis_<analyst>.txt`
  - What: An alternative analysis. This takes one of two forms:
    - A copy of an original analysis exactly as converted for cases where significant changes 
      have been made to that analysis. See, for example,
      [this edit](/Corpus/Piano_Sonatas/Beethoven,_Ludwig_van/Op010_No1/1/analysis.txt)
      [of this "original"](/Corpus/Piano_Sonatas/Beethoven,_Ludwig_van/Op010_No1/1/analysis_BPS.txt)
    - A second analysis of the same work. The ['TAVERN'](https://github.com/jcdevaney/TAVERN) 
      dataset includes pairs of analyses of the same work. In order to ensure there is exactly 
      one `analysis.txt` throughout, we name the pair `analysis.txt` (note not 
      `analysis_A.txt`) and `analysis_B.txt`.
    - We likewise organise cases of two separate corpora of analyses of the same music this way.
      - The set which is complete takes precedence for the `analysis.txt` name.
  - How to use: All such text files can be opened in the normal way. "Original conversions" 
    serve as a point of reference for full disclosure on the conversion process.

### Optional extra files (not included but easy to generate):

This repo. includes code and clear instructions for creating any or all of the following additional files for the whole meta-corpus, or for a specific sub-corpus.

The [example folder](./Tests/Resources/Example/) contains all of these files for one example score: 
Clara Schumann's Lieder, Op.12, No.4, 'Liebst du um Schönheit'.
Most of the variants derive from the options for pitch class profile generations, creating files in the form: `profiles_<and_features_>by_<segmentation_type>.<format>`
- `<and_features_>` (optional) includes harmonic feature information. See notes at [Code/Pitch_profiles/chord_features.py](Code/Pitch_profiles/chord_features.py)
- `<segmentation_type>` options group by moments of change to the `chord`, `key`, or `measure`.
- `<format>` options are `.arff`, `.csv`, `.json`, and `.tsv`.

Apart from these, the example folder also contains the files which are included in all folders by default (see above) as well as others that can likewise be generated across the meta-corpus:
- `analysis_on_score.mxl`: the analysis rendered in musical notation alongside the score (as an additional 'part').
- `feedback_on_analysis.txt`: automatically generated feedback on any analysis complete with an overall rating. Useful for proofreading. See [Code/romanUmpire.py](Code/romanUmpire.py) for more details on what it can and can't do.
- `<Keys_or_chords>_and_distributions.tsv`: pitch class distributions for each range delimited by a single key or chord. See notes at [Code/Pitch_profiles/get_distributions.py](Code/Pitch_profiles/get_distributions.py)
- `slices.tsv` and/or `slices_with_analysis.tsv`: a tabular representation of the score in 'slices' - vertical cross-sections of the score, with one entry for each change of pitch.
This is useful for various tasks, both human (at-a-glance checks) and automatic (much quicker to load and process than parsing musicXML).
The columns from left to right set out the:
  - `Offset` from the start (a time stamp measured in terms of quarter notes),
  - `Measure` number,
  - `Beat`,
  - `Beat 'Strength'` (from relative metrical position),
  - `Length` (also measured in quarter notes),
  - `Pitches`,
  - and where the analysis is included, also `Key`, `Chord`
- `template.txt`: a proto-analysis text file with only the metadata, time signatures, measures, and measure equality ranges as a template - i.e. all the information you need from the score with space to enter your own analysis from scratch.

This is clearly too much to include for every entry.
Use the example folder to see the options and 'try before you' commit to a corpus-wide generation.

## Corpus Overview

This corpus involves the combination of new analyses with conversions of those originating elsewhere.

### Corpora originating elsewhere

Converted from other formats:
- the [DCMLab's](https://github.com/DCMLab/) standard
  ([conversion code here](https://github.com/cuthbertLab/music21/blob/master/music21/romanText/tsvConverter.py)):
  - [Beethoven string quartets](/Corpus/Quartets/Beethoven,_Ludwig_van/) 
    (complete, 16 string quartets, 70 movements): originating from the
    ['ABC' corpus](https://github.com/DCMLab/ABC).
  - [Mozart Piano Sonatas](/Corpus/Piano_Sonatas/Mozart,_Wolfgang_Amadeus/) (complete, 18 sonatas): 
    originating from ['The Annotated Mozart Sonatas' corpus](https://github.com/DCMLab/mozart_piano_sonatas).
  - Several collections including the 
    [Chopin Mazurkas](/Corpus/Keyboard_Other/Chopin,_Frédéric/Mazurkas) (56 works):
    originating from DCML's ['romantic_piano_corpus'](https://github.com/DCMLab/romantic_piano_corpus).
- krn format (with thanks to [@napulen](https://github.com/napulen)):
  - 27 sets of keyboard Variations by 
    [Mozart,_Wolfgang_Amadeus](/Corpus/Variations_and_Grounds/Mozart,_Wolfgang_Amadeus/) and 
    [Beethoven](/Corpus/Variations_and_Grounds/Beethoven,_Ludwig_van/), from 
    [The 'TAVERN' project, (Devaney et al. ISMIR 2015)](https://github.com/jcdevaney/TAVERN)
  - [Haydn Op. 20 String Quartets](/Corpus/Quartets/Haydn,_Franz_Joseph/): 
    Complete annotations of Haydn's Op. 20 (6 string quartets, 24 movements), from the  
    [MTG dataset](https://zenodo.org/record/1095630#.X8AbrcJyZhE)
  - [Key Modulations and Tonicizations](Corpus/Textbooks/): Modulation examples annotated from 
    five music theory textbooks.
    Published in [Nápoles López et al. 2020](https://dl.acm.org/doi/10.1145/3424911.3425515).
- other:
  - [Beethoven Piano Sonata](/Corpus/Piano_Sonatas/Beethoven,_Ludwig_van/) 
    (complete first movements, 32 movements), from Tsung-Ping Chen and Li Su's
    ['BPS-FH' dataset, ISMIR 2018](https://github.com/Tsung-Ping/functional-harmony).

Analyses originally in the 'RomanText' format (no conversion needed), 
analysed by Dmitri Tymoczko and colleagues, and forming part of the supplementary to Tymoczko's 
forthcoming "TAOM", include:
- [Monteverdi madrigals](/Corpus/Early_Choral/Monteverdi,_Claudio/): Complete scores and 
  analyses for books 3–5 of the Monteverdi madrigals (48 works) also to be seen in 
  [this part](https://github.com/cuthbertLab/music21/tree/master/music21/corpus/monteverdi)  
  of the music21 corpus (but updated since that version).
- [Bach Chorales](/Corpus/Early_Choral/Bach,_Johann_Sebastian/Chorales): 371 chorales, of which 
  a subset of 20 was first released on music21.
- Several further collections including a second set of analyses for most of the  
  [ChopinMazurkas](/Corpus/Keyboard_Other/Chopin,_Frédéric/Mazurkas)

### Mixed sources

Several corpora have full or partial coverage from more than one source.
The most complex case is the 
the [Beethoven Piano Sonata](/Corpus/Piano_Sonatas/Beethoven,_Ludwig_van/) collection
for which there are 3 external corpora, all of them incomplete:
1. 64 movements from DCML's 
   ['romantic_piano_corpus'](https://github.com/DCMLab/romantic_piano_corpus).
2. 36 movements from Dmitri Tymoczko's TAOM collection
3. 32 movements (complete first movements) as converted from the  
  ['BPS-FH' dataset, ISMIR 2018](https://github.com/Tsung-Ping/functional-harmony).


### New corpora by MG and colleagues
- [Bach Preludes](/Corpus/Etudes_and_Preludes/Bach,_Johann_Sebastian/The_Well-Tempered_Clavier_I/):
  Complete preludes from the first book of Bach's Well Tempered Clavier (24 analyses)
- [Ground bass works](/Corpus/Variations_and_Grounds/) by Bach and Purcell.
- [Nineteenth-century songs](/Corpus/OpenScore-LiederCorpus/): A sample of songs from the 
  OpenScore / 'Scores of Scores' lieder corpus  
  ([mirroring the public-facing score collection hosted here](https://musescore.
  com/openscore-lieder-corpus/sets)), including analyses for the complete
  [_Winterreise_](/Corpus/OpenScore-LiederCorpus/Schubert,_Franz/Winterreise,_D.911/) and  
  [_Schwanengesang_](/Corpus/OpenScore-LiederCorpus/Schubert,_Franz/Schwanengesang,_D.957/) cycles (Schubert),  
  [_Dichterliebe_](/Corpus/OpenScore-LiederCorpus/Schumann,_Robert/Dichterliebe,_Op.48/) (Schumann), 
- and many of the songs by women composers that constitute a key part of and motivation for that collection.

## Code and Lists

For developers, please see the individual code files for details of what they do and how.

Run code scripts from the repo's base directory (`When-in-Rome`) using the format:

`>>> python3 -m Code.<name_of_file>`

For example, this is the syntax for processing one score (feedback, slices, etc.):

`>>> python3 -m Code.updates_and_checks --process_one_score OpenScore-LiederCorpus/Bonis,
_Mel/_/Allons_prier!`

Briefly, this repo. includes:
- [The Roman Umpire](/Code/romanUmpire.py) for providing automatic 'feedback' files.
It takes in a harmonic analysis and the corresponding score to assess how well they match.
[Working in Harmony](https://fourscoreandmore.org/working-in-harmony/analysis/) is an initial attempt at an interactive app for making use of this code online (no downloads, coding, dependency).
- [Anthology](/Code/anthology.py) for retrieving instances of specific chords and progression from the analyses.
- [Pitch_profile](/Code/Pitch_profiles/) for producing the profile and feature information discussed above.

## Licence, Citation, External Apps, Contribution

### Licence

New content in this repository, including the new analyses, code, and the conversion 
(specifically) of existing analyses is available under the
[CC BY-SA licence](https://creativecommons.org/licenses/by-sa/4.0/) (a free culture licence).

For analyses that originated elsewhere and have been converted into the format used here,
please refer to the original source for licence.
Links are provided to those original sources throughout the repository including the 
itemised list above and within every `analysis.txt` file.

These external licences vary.
As far as we can tell, all the content here is either original to this repo,  
or properly credited and fair to use in this way.
If you think you see an issue please let us know.
Again, if you are simply looking for a scores in a maximally permissive licence, then head to the 
[OpenScore collections](https://github.com/openscore) which are notable for using CC0.

For research and other public-facing projects making use of this work, 
please cite or otherwise acknowledge one or more of the papers listed below as appropriate to your project.

### Citation

The materials provided in this repo includes supplementary resources promised in:
- [Dmitri Tymoczko, Mark Gotham, Michael Scott Cuthbert, Christopher Ariza. “The Romantext Format: a Flexible and Standard Method for Representing Roman Numeral Analyses”, 20th International Society for Music Information Retrieval Conference, Delft, The Netherlands, 2019.](http://archives.ismir.net/ismir2019/paper/000012.pdf )
- [Gianluca Micchi, Mark Gotham, and Mathieu Giraud (2020). "Not All Roads Lead to Rome: Pitch Representation and Model Architecture for Automatic Harmonic Analysis", Transactions of the International Society for Music Information Retrieval, 3(1), pp. 42–54. DOI: https://doi.org/10.5334/tismir.45](https://transactions.ismir.net/articles/10.5334/tismir.45/)
- [Néstor Nápoles López, Mark R H Gotham, & Ichiro Fujinaga. (2021). AugmentedNet: A Roman Numeral Analysis Network with Synthetic Training Examples and Additional Tonal Tasks. Proceedings of the 22nd International Society for Music Information Retrieval Conference, 404–411](https://doi.org/10.5281/zenodo.5624533)
- [Mark R H Gotham, Rainer Kleinertz, Christof Weiss, Meinard Müller, & Stephanie Klauk. (2021). What if the 'When' Implies the 'What'?: Human harmonic analysis datasets clarify the relative role of the separate steps in automatic tonal analysis. Proceedings of the 22nd International Society for Music Information Retrieval Conference, 229–236](https://doi.org/10.5281/zenodo.5676067)

### External Apps and More

'When in Rome' data is also used in external research projects and apps including the:
- ["Open Music Theory" (OMT) textbook's harmony anthology](https://viva.pressbooks.pub/openmusictheory/chapter/anthology-harmony/)
- ["RAWL" app](https://rawl.vercel.app)
- ["VIMU" (Visual Musicology) app](https://vimu.app) via [AugmentedNet](https://github.com/napulen/AugmentedNet)

Using 'When in Rome' in your project? Let us know!

### Syntax and Contributing

As the papers attest, harmonic analysis is fundamentally, necessarily, and intentionally a reductive act that includes a good degree of subjective reading.
As such, these analyses are not in any sense 'definitive', to the exclusion of other possibilities.
Quite the opposite: part of the point of having a representation format like this is to enable the recording of variant readings.
Please feel free to re-analyse these works by using the existing analysis as a template and changing the parts you disagree with.
- For minor changes, consider integrating your edits into the existing file using the variant (`var`) option that rntxt provides. E.g. `m1 I b2 IV` followed by a new line with `m1var1 I b2 ii6`
- For more thoroughly divergent analyses, a new file may be warranted. In that case, perhaps credit the original analyst too in the format - `Analyst: [Your name] after [their name]`
- For any cases of clear errors, please submit a pull request with the correction.

For more details of the RomanText format used to encode analyses here, see:
- the [technical specification paper](http://archives.ismir.net/ismir2019/paper/000012.pdf), or 
- the relevant corners of the music21's
  - [code](https://github.com/cuthbertLab/music21/tree/master/music21/romanText),
  - [module reference](http://web.web.mit.edu/music21/doc/moduleReference/moduleRoman.html), or 
  - (if in doubt) [user guide](http://web.mit.edu/music21/doc/usersGuide/usersGuide_23_romanNumerals.html)
- this repository's own ["quick start" guide to writing in RomanText](syntax.md).
