from pathlib import Path
import json
import csv


# ------------------------------------------------------------------------------

CODE_FOLDER = Path(__file__).parent
REPO_FOLDER = CODE_FOLDER.parent
CORPUS_FOLDER = REPO_FOLDER / "Corpus"

DT_BASE = REPO_FOLDER.parent / "TAOM" / "TAOMfiles" / "Music"
raw_git = "https://raw.githubusercontent.com/"


# ------------------------------------------------------------------------------

def get_corpus_files(sub_corpus_path: Path = CORPUS_FOLDER,
                     file_name: str = "score.mxl",
                     ) -> list[Path]:
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


def load_json(
    json_path: Path
) -> list:
    """
    Read in json format data.
    Never remember to open / close again.
    """
    with open(json_path, "r") as f:
        return json.load(f)


def write_json(
        this_data: dict,
        json_path: Path
) -> None:
    """
    Write the metadata in json format to the specified path
    """
    with open(json_path, "w") as json_file:
        json.dump(this_data, json_file, indent=4, sort_keys=True)


# ------------------------------------------------------------------------------

# Tabular

def import_SV(
        path_to_file: Path,
        split_marker: str | None = None
) -> list:
    """
    Import SV file data for further processing.
    """

    if split_marker is None:
        ext = path_to_file.suffix
        if ext == ".tsv":
            split_marker = "\t"
        elif ext == ".csv":
            split_marker = ","
        else:
            raise ValueError(f"Format {ext} invalid: must be `.tsv` or `.csv`.")

    if split_marker not in ["\t", ","]:
        raise ValueError(f"split_marker {split_marker} invalid: must be `\t` or `,`.")

    with open(path_to_file, "r") as f:
        return [x for x in csv.reader(f, delimiter=split_marker)]


def data_by_heading(
        file_path: Path,
        headings_row: int = 0
) -> list[dict]:
    """
    Imports an SV file from the provided `file_path`
    and converts the data to a directly to list of dicts
    with headers given by the data in the `headings_row`.
    """

    table = import_SV(file_path)
    headings = table[headings_row]
    out_list = []
    for entry in table[headings_row + 1:]:
        data = {}
        for i, col in enumerate(entry):
            data[headings[i]] = col
        out_list.append(data)
    return out_list


# ------------------------------------------------------------------------------
