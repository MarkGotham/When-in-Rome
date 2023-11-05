from Code import data_by_heading, updates_and_checks
import unittest
from pathlib import Path

TEST_FOLDER = Path(__file__).parent
TEST_RESOURCES_FOLDER = TEST_FOLDER / "Resources"


class Test(unittest.TestCase):

    def test_q(self):
        """Test the `data_by_heading` and `import_SV` fxs using some Quiescenza data"""

        corpus_data_pairs = (
            ("OpenScore-LiederCorpus",
             (21, 21, 24)
             ),
            ("Piano_Sonatas",
             (27, 27, 195)
             )
        )

        base_path = TEST_FOLDER.parent / "Anthology"

        for pair in corpus_data_pairs:
            quiescenzas = data_by_heading(base_path / pair[0] / "Quiescenzas.csv")
            position = quiescenzas[0]["MEASURE"]
            x, z = position.split("/")
            x, y = x.split("-")
            self.assertEqual(
                (int(x), int(y), int(z)),
                pair[1]
            )
