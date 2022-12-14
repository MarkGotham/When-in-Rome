"""
Process all the available corpora and generate three files for each entry:
 - analysis_on_score.mxl
 - slices_with_analysis.tsv
 - feedback_on_analysis.txt
By default, do not overwrite existing files.
"""
from Code.updates_and_checks import process_corpus, corpora

if __name__ == '__main__':
    overwrite = False
    for c in corpora:
        process_corpus(c, combine=True, slices=True, feedback=True, overwrite=overwrite)
