# RomanText Syntax Notes

This is a "quick start" guide to writing in RomanText.
For more details of the RomanText format used to encode analyses here, see:
- the [technical specification paper](http://archives.ismir.net/ismir2019/paper/000012.pdf), or 
- the relevant corners of the music21's
  - [code](https://github.com/cuthbertLab/music21/tree/master/music21/romanText),
  - [module reference](http://web.web.mit.edu/music21/doc/moduleReference/moduleRoman.html), or
  - (if in doubt) [user guide](http://web.mit.edu/music21/doc/usersGuide/usersGuide_23_romanNumerals.html)

## Annotation basics

Basically the analyst's job is to:
- Decide where each chord change occurs;
- Enter a Roman numeral (in the format described below).

Be sure to:
- Note down the measure (`m1`) and beat (`b1`) carefully, and
- Start your analysis at the start of the piece (measure 1, or 0 in the case of anacruses) - the templates can help with this.

## Simple RomanText Example

Here's a simple harmonic analysis in RomanText for the beginning of Bach's The Well-Tempered Clavier:

```
Composer: J.S. Bach
Title: Prelude No.1 (BWV846)
Analyst: Mark Gotham [feel free to leave this blank]

m1 C: I
m2 ii42
m3 V65
m4 I
m5 vi6
m6 G: V42
m7 I6
m8 IV42
m9 ii7
m10 V7
m11 I
```

## Format of each Roman numeral entry

- New chord: For each new chord, specify the Roman numeral in relation to the prevailing key, for instance `I` for the tonic.
- New key:
  - For the start of a new key area (including, necessarily, the start of the piece), specify that key followed by a colon (`:`) and the Roman numeral (e.g. `G: I` for a move to G major and a tonic chord in that key).
  - For a continuation of the prevailing key, there's no need to specify the key: just write in the Roman numeral alone (`I`). That said, you may want to put in reminders of the prevailing key occasionally. That's fine and doesn't make any difference to the analysis.
  - Tonicization (e.g., `viio/V`) are supported. Changes of key remain in effect until the next marking, but changes of tonicization don’t so you need to reiterate them at every entry. That should help keep their use suitably fleeting!
- Chord quality:
  - use upper case for Major (e.g. `I`),
  - lower case for minor (`i`), and 
  - add the symbols for a diminished triad (`o`) or augmented triad (`+`) as necessary.
  - The `ø` symbol (or, equivalently, `/o`) can be used for half-diminished sevenths.
- Additional and/or altered notes can be specified in square brackets with `add`, `#`, `b`, or `no` as required.

In summary, enter a Roman numeral (that’s required), along with any or all of the other annotations (all optional) in the following order:
- OPTIONAL: key: (e.g. `d: `),
- OPTIONAL: root accidental (`#`),
- REQUIRED: Roman numeral (`iv`),
- OPTIONAL: quality (`o`),
- OPTIONAL: inversion figure (`6`),
- OPTIONAL: additions and/or alterations `[add9]`.

For instance, the convoluted entry `d: #ivo6[add9]` indicates:
- `d: ` - the key of d minor and ...
- `#iv` - a chord on the raised fourth degree (G#) ...
- `o` - that is diminished (so G#, B, D) ...
- `6` - in first inversion (so with B in the bass, below the G# and D)..
- `6[add9]` - with an added 9th (2nd) above the root (sic, so the pitch A).

## Convoluted RomanText Example

Here's a hypothetical analysis with lots of symbols and notes for illustration:

```
Composer: No one in their right mind
Title: 'Study in RomanText'
Analyst: It could be you!


Time Signature: 4/4
Note: Use a new line with 'Note:' to enter a free comment any time you like.

m0 b3 Ab: I 
Note: As normal, if the score begins with an anacrusis, the first (incomplete) measure is numbered 0.

m1 ii b3 IV b4 viiø7
Note: Enter beat-chord pairs each time something happens (here on beats 1, 3 and 4 but not 2). 
Note: The 'ø' symbol is for half-diminished chords. If you prefer, '/o' also works.

Pedal: Ab m1 b1 m2 b1 
Note: Pedals like this ^ are set out on their own line, before or after the measure in question

m2 I || f: III b2 III+  b3 viio6 b4 i
Note: The '||' is used for pivot chords: put the numeral in the prevailing key before (here 'I') and the new key:chord pair after.

Time Signature: 6/8
Note: This ^ is the format for time signatures changes though they should be in the template provided.

m3 viio7 b1.33 i b1.66 viio7 b2 i b2.66 iv6
Note: 6/8 is counted in 2 beats, hence beats 1.33 and 1.66.

m4 It6 b1.33 V b1.66 Fr43 b2 V b2.33 Ger65 b2.66 V 
Note: These are the shorthands for augmented 6th chords. Other inversion can be set in the normal way (e.g. 'Fr65') but no other shorthands are accepted (e.g. 'Gr').

m5-6 = m3-4
Note: This syntax repeats measures 3 and 4 exactly including all chords. 
Note: Use EITHER this repeat format OR a measure entry (not both).
Note: It'd easy to get this slightly wrong, don't do so check you 

m7 viio43 b2 i6
Note: Slashes between figures are optional ('viio43' is fine, as is 'viio4/3').

m8 viio/V b2 V
Note: Slashes are required for tonicizations.

m9 Cad64 b2 V7
Note: Both 'I64' and 'Cad64' are supported (note the capital C); the resolution to V is required.

m10 I
Note: Picardy thirds and other mixture chords work fine.
```

## Additional syntax hints

Pro tips for advanced users, including updates and clarifications on top of the 2019 release.

The template files should handle all of the necessary header, metadata information, but you can of course write and/or edit this yourself. E.g., for `Time Signature`, all strings supported by music21 are supported here. In addition to the typical `X/Y` format entries, this also includes:
  - `C` for "common time" (similar to `4/4`),
  - `Cut` for "cut common time" (similar to `2/2`),
  - the distinction between `Slow` and `Fast` compound meters (e.g., `Slow 6/8` has 6 beats; `Fast 6/8` has 2)

For Suspensions the safest and best-tested method is to explicitly add and/or remove notes from the chord with the `V[add4][no3]` syntax.
  - Alternatives like `V54` are equivalent in that specific case, and are accepted, but are less tested, and not as flexible.
  - Note that at cadence, it's `V54`: We support `I64` or `Ca64` for the 64 suspension, then when it's 54, definitely use `V54`.

### Spotlight on 6^ and 7^ in minor mode

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
