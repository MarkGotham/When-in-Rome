import json
from pathlib import Path

USAGE_FOLDER = Path(__file__).parent / "chord_usage"


def import_chord_usage_stats(usage_file_name: str):
    json_path = USAGE_FOLDER / usage_file_name

    with open(json_path) as f:
        return json.load(f)
