from Code import data_by_heading
import unittest
from pathlib import Path

TEST_FOLDER = Path(__file__).parent
TEST_RESOURCES_FOLDER = TEST_FOLDER / "Resources"


class Test(unittest.TestCase):

    def test_import_SV(self):

        corpus_data_pairs = (
            ("OpenScore-LiederCorpus",
                (
                    21 / 24,
                    30 / 42,
                    31 / 42,
                    60 / 79,
                    4 / 45,
                    30 / 45,
                    3 / 14,
                    11 / 43,
                    25 / 43,
                    39 / 43,
                    8 / 11,
                    13 / 62,
                    52 / 62,
                    11 / 17,
                    16 / 35,
                    1 / 15,
                    18 / 31,
                    32 / 36,
                    34 / 36
                )
             ),
            ("Piano_Sonatas",
                (
                    42 / 332,
                    44 / 332,
                    94 / 343,
                    98 / 343,
                    102 / 343,
                    275 / 343,
                    279 / 343,
                    283 / 343,
                    12 / 309,
                    14 / 309,
                    20 / 309,
                    22 / 309,
                    122 / 309,
                    124 / 309,
                    196 / 309,
                    198 / 309,
                    204 / 309,
                    206 / 309,
                    286 / 309,
                    288 / 309,
                    300 / 309,
                    302 / 309,
                    6 / 199,
                    16 / 199,
                    18 / 199,
                    133 / 199,
                    146 / 199,
                    147 / 199,
                    149 / 199,
                    119 / 216,
                    79 / 84,
                    99 / 460,
                    140 / 460,
                    148 / 460,
                    152 / 460,
                    373 / 460,
                    416 / 460,
                    424 / 460,
                    428 / 460,
                    105 / 109,
                    224 / 257,
                    2 / 105,
                    25 / 157,
                    151 / 157,
                    153 / 157,
                    13 / 98,
                    14 / 98,
                    3 / 144,
                    85 / 144,
                    103 / 144,
                    39 / 162,
                    41 / 162,
                    64 / 162,
                    136 / 162,
                    138 / 162,
                    23 / 36,
                    51 / 120,
                    52 / 120,
                    118 / 120,
                    25 / 276,
                    29 / 276,
                    196 / 276,
                    200 / 276,
                    9 / 127,
                    80 / 127,
                    111 / 259,
                    128 / 259,
                    23 / 86,
                    29 / 86,
                    30 / 86,
                    84 / 86,
                    85 / 86,
                    54 / 268,
                    219 / 268,
                    51 / 165,
                    149 / 165,
                    153 / 165,
                    85 / 224,
                    156 / 224,
                    195 / 224,
                    67 / 184,
                    69 / 184,
                    71 / 236,
                    198 / 236,
                    13 / 188,
                    77 / 188,
                    175 / 188,
                )
             )
        )

        base_path = TEST_FOLDER.parent / "Anthology"

        for pair in corpus_data_pairs:
            quiescenzas = data_by_heading(base_path / pair[0] / "Quiescenzas.csv")
            positions = [x["MEASURE"] for x in quiescenzas]
            for i in range(len(positions)):
                x, y = positions[i].split("/")
                self.assertEqual(int(x) / int(y), pair[1][i])
