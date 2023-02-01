import os
import re
from pathlib import Path

from Code.Resources import metadata
from . import TEST_FOLDER

DCML_base = TEST_FOLDER.parent.parent


def get_DCML_Chopin_analyses(
        in_path: Path = DCML_base / "romantic_piano_corpus" / "chopin_mazurkas"
) -> list:
    """
    Check DCML Chopin files names match the expected pattern.
    Returns a list.
    Each list has two sub-tuples: BI and Opus.
    Each of BI and Opus is len 2.
    All entries may be None except the first BI.
    """
    all_out = []

    for path in (in_path / "harmonies").glob("*.tsv"):

        parts = str(path.parts[-1]).split("op")  # give my modest regex skills a chance ...

        # With or without opus number.
        m = re.search(f"BI(?P<bi_a>\d+)-?(?P<bi_b>\d+)?", parts[0])
        bi_parts = (
            int(m.group("bi_a")),
            int(m.group("bi_b")) if m.group("bi_b") else None
            )

        if len(parts) == 2:  # With opus number. E.g., "BI18op68-2.tsv" and "BI60-1op06-1.tsv"
            n = re.search(f"(?P<op_a>\d+)-?(?P<op_b>\d+)?.tsv", parts[1])
            opus_parts = (
                int(n.group("op_a")) if n.group("op_a") else None,
                int(n.group("op_b")) if n.group("op_b") else None
                )
        else:
            opus_parts = (None, None)

        all_out.append((bi_parts, opus_parts))

    return tuple(sorted(all_out, key=lambda ind: ind[0]))


if __name__ == "__main__":
    # Not unittests because the local copy is required.

    # Chopin
    assert(get_DCML_Chopin_analyses() == metadata.chopin["items"])
