import os
import re
import unittest
from pathlib import Path

from Code.Resources import metadata


def get_DCML_Chopin_analyses(
        in_path: Path = metadata.DCML_Chopin
) -> list:
    """
    Check DCML Chopin files names match the expected pattern.
    Returns a tuple.
    Each tuple has two sub-tuples: BI and Opus.
    Each of BI and Opus is len 2.
    All entries may be None except the first BI.
    """
    all_out = []
    for file_name in os.listdir(in_path / "harmonies"):
        if file_name.endswith(".tsv"):

            parts = file_name.split("op")  # give my modest regex skills a chance ...

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
            all_out.append((bi_parts, opus_parts))
    return sorted(all_out, key=lambda ind: ind[0])


class Test(unittest.TestCase):

    def test_Chopin(self) -> list:
        data = get_DCML_Chopin_analyses()
        self.assertEqual(data, metadata.chopin["items"])
