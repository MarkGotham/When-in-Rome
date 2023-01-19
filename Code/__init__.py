from pathlib import Path

CODE_FOLDER = Path(__file__).parent
REPO_FOLDER = CODE_FOLDER.parent
CORPUS_FOLDER = REPO_FOLDER / "Corpus"


# ------------------------------------------------------------------------------

corpora = [
    "Orchestral",
    "Early_Choral",
    "Etudes_and_Preludes",
    "OpenScore-LiederCorpus",
    "Piano_Sonatas",
    "Quartets",
    "Variations_and_Grounds"
]


def get_corpus_files(corpus: str = "",
                     file_name: str = "score.mxl",
                     ) -> list:
    """
    Get and return paths to files matching conditions for the given file_name.

    Args:
        corpus: the sub-corpus to run. Leave blank ("") to run all corpora.
        file_name (str): select all files matching this file_name. Defaults to "score.mxl".
        Alternatively, specify either an exact file name (e.g., "analysis_automatic.rntxt") or
        use the wildcard "*" to match patterns. Examples:
        - "*.mxl" searches for all .mxl files
        - "slices*" searches for all files starting with "slices"

    Returns: list of file paths.
    """

    if corpus not in ["", *corpora]:
        raise ValueError(f"Invalid corpus: must be one of {corpora} or an empty string (for all)")

    return [str(x) for x in (CORPUS_FOLDER / corpus).rglob(file_name)]
