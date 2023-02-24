import os
import re
from pathlib import Path

import unittest
from Code.Resources import metadata
from . import TEST_FOLDER

DCML_base = TEST_FOLDER.parent.parent


def test_DCML_Mozart_analyses(
        theirs: Path = DCML_base / "mozart_piano_sonatas",
) -> None:
    """
    Check DCML "mozart_piano_sonatas" files names have
    corresponding folders in WiR in the expected pattern.
    """

    ours = TEST_FOLDER.parent / "Corpus"
    for x in metadata.sonatas_Mozart["path_within_WiR"]:
        ours = ours / x

    for f in os.listdir(theirs):
        if f.endswith(".tsv"):
            cln, mvt = f.split("-")  # e.g., K279-1.mscx >>> K279, 1.mcsx
            cln = cln[1:]  # drop the K
            mvt = mvt.split(".")[0]  # e.g.,  1.mcsx >>> 1

            test_path = ours / cln / mvt

            assert (test_path.exists())


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


class Test(unittest.TestCase):

    def test_metadata(self):
        for md in (
                # metadata.chorales,  # special case items = 371
                metadata.chopin_mazurkas,
                metadata.madrigals,
                metadata.sonatas_Mozart,
                metadata.sonatas_Beethoven,
        ):
            k = len(md["item_keys"])
            for i in md["items"]:
                if isinstance(i, int):  # Mozart ssa items = 371
                    assert(k == 1)
                else:
                    assert(len(i) == k)


if __name__ == "__main__":
    # Not unittests because the local copy is required.

    test_DCML_Mozart_analyses()

    # Chopin
    assert(get_DCML_Chopin_analyses() == metadata.chopin_mazurkas["items"])
