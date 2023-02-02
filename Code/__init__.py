from pathlib import Path

CODE_FOLDER = Path(__file__).parent
REPO_FOLDER = CODE_FOLDER.parent
CORPUS_FOLDER = REPO_FOLDER / "Corpus"

DT_BASE = REPO_FOLDER.parent / "TAOM" / "TAOMfiles" / "Music"
raw_git = "https://raw.githubusercontent.com/"


# ------------------------------------------------------------------------------

def get_corpus_files(sub_corpus_path: Path = CORPUS_FOLDER,
                     file_name: str = "score.mxl",
                     ) -> list:
    """
    Get and return paths to files matching conditions for the given file_name.

    Args:
        sub_corpus_path: the sub-corpus to run.
            Defaults to CORPUS_FOLDER (all corpora).
            Accepts any sub-path of the meta-corpus folder (i.e., "When-in-Rome/Corpus/...")
            Checks ensure both that the path .exists and .is_relative_to(CORPUS_FOLDER)
        file_name (str): select all files matching this file_name. Defaults to "score.mxl".
        Alternatively, specify either an exact file name (e.g., "analysis_automatic.rntxt") or
        use the wildcard "*" to match patterns. Examples:
        - "*.mxl" searches for all .mxl files
        - "slices*" searches for all files starting with "slices"

    Returns: list of file paths.
    """

    assert sub_corpus_path.is_relative_to(CORPUS_FOLDER)
    assert sub_corpus_path.exists()
    return [x for x in sub_corpus_path.rglob(file_name)]
