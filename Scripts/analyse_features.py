from music21 import converter, roman

from Code.updates_and_checks import get_corpus_files
from Code.Pitch_profiles.chord_features import SingleChordFeatures

# Check the tests in test_get_distributions and restart from there

if __name__ == '__main__':
    files = get_corpus_files(file_name="analysis.txt")
    # for f in files:
    #     print(f)
    #     analyses = converter.parse(f, format="romantext")
    analyses = [converter.parse(f, format="romantext") for f in files]
    for a in analyses:
        rns = a.recurse().getElementsByClass(roman.RomanNumeral)
        for rn in rns:
            SingleChordFeatures(rn)

    # files = get_corpus_files(file_name="slices_with_analysis.tsv")
    print("hi")




# SingleChordFeatures()
