"""
===============================
Chord Usage (chord_usage.py)
===============================

Mark Gotham, 2022


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


Citation:
===============================

Watch this space!


ABOUT:
===============================

Retrieve usage stats for all chord types in a corpus.

Also includes functionality for simplifying harmonies and
corresponding assessment of that data.

Specifically:
- 2x Corpora: lieder (OpenScore LiederCorpus); Beethoven (Beethoven)
- major and minor handled separately
- expressed as percentages


TODO:
===============================

Currently limited to single chord. Expand to progressions

"""

from . import chord_comparisons
from . import get_distributions
from .. import CORPUS_FOLDER

from typing import Union

from music21.analysis import harmonicFunction as hf
from music21 import roman

# ------------------------------------------------------------------------------

# Collected Data from corpora (each with plateau set at 0.01)
# Later end reads like a Who's Who of extremely marginal chords.

lieder_major = {'I': 31.323, 'V7': 12.959, 'V': 6.585, 'I64': 4.872, 'I6': 3.916, 'IV': 2.469,
                'V65': 2.007, 'vi': 1.918, 'V43': 1.892, 'ii': 1.588, 'V42': 1.483, 'Cad64': 1.438,
                'ii6': 1.429, 'IV6': 0.985, 'V7/V': 0.981, 'V7/IV': 0.949, 'i': 0.831, 'IV64': 0.79,
                'V6': 0.769, 'ii7': 0.685, 'V9': 0.673, 'ii65': 0.671, 'iv': 0.585,
                'viio7/V': 0.516, 'V65/V': 0.48, 'vi6': 0.474, 'Ger65': 0.464, 'viio43/ii': 0.442,
                'viio42': 0.386, 'viio7': 0.337, 'V7/vi': 0.32, 'iiø42': 0.294, 'V7/ii': 0.294,
                'iiø65': 0.285, 'V/vi': 0.285, 'V42/IV': 0.261, 'V43/V': 0.243, 'iv6': 0.236,
                'iii6': 0.234, 'V65/IV': 0.234, 'viio7/ii': 0.215, 'i64': 0.212, 'vi42': 0.208,
                'viio6': 0.203, 'vi7': 0.196, 'iiø7': 0.186, 'viio7/v': 0.183, 'i6': 0.183,
                '#iio42': 0.183, 'V64': 0.182, 'viiø7/V': 0.176, 'Fr43': 0.17, 'I42': 0.17,
                'V+': 0.167, 'viio43': 0.163, 'viiø65': 0.157, 'V43/ii': 0.157, 'V65/ii': 0.154,
                'viio42/iii': 0.154, 'iii': 0.15, 'viio65/ii': 0.147, 'V65/vi': 0.144, 'V+6': 0.142,
                'V+7': 0.141, 'ii42': 0.138, 'viiø7': 0.135, 'bII': 0.129, 'V43/vi': 0.128,
                'iio6': 0.128, 'viio43/V': 0.125, 'I54': 0.125, 'I7': 0.125, 'Ger43': 0.121,
                'V7/II': 0.115, 'iv64': 0.115, 'viio65': 0.115, 'vi65': 0.106, 'V7[no5]': 0.103,
                'V/V': 0.099, 'I[add6]': 0.096, 'IV7': 0.093, 'iio64': 0.09, 'v': 0.086,
                'viio65/v': 0.086, 'viio': 0.083, 'V42/ii': 0.082, 'vi64': 0.08, 'V43[no3]': 0.08,
                'V6/V': 0.08, 'III': 0.077, 'I+': 0.077, 'IV6/4': 0.074, 'Vb9': 0.071,
                'V9[no5]': 0.071, 'viio65/V': 0.071, 'viiø43': 0.07, 'viio43/III': 0.067,
                'ii64': 0.067, 'I43': 0.067, 'II': 0.064, 'viiø65/V': 0.064, 'II43': 0.064,
                'iiø43': 0.064, 'iv6/ii': 0.064, '#V': 0.064, 'V42/V': 0.064, 'viio6/V': 0.064,
                'iio42': 0.062, 'V6/ii': 0.061, 'viio7/vi': 0.058, 'III+/vi': 0.058, 'II42': 0.058,
                'IV43': 0.051, 'Ger65/IV': 0.051, 'viø7': 0.051, 'bIII': 0.051, 'viio7/III': 0.051,
                'V9/v': 0.051, 'viio43[no3]': 0.051, 'VI/ii': 0.051, 'iv64[no1]': 0.051,
                'viio6/ii': 0.051, 'V6/vi': 0.051, 'V43/IV': 0.048, 'viio65/vi': 0.048,
                'viiø42': 0.048, 'viio64/V': 0.048, 'viio7/iii': 0.048, 'V7/iv': 0.048,
                'vi43': 0.045, 'bII7': 0.045, 'Ger65/II': 0.045, 'iio65': 0.045, 'II6': 0.042,
                'V[no3]': 0.04, 'viio64': 0.038, 'I+64': 0.038, 'I6[no5]': 0.038, 'viio42/V': 0.038,
                'V9/IV': 0.038, 'viio43/vii': 0.038, 'V6/5': 0.038, 'v7': 0.038, 'bVI6': 0.038,
                'V9/ii': 0.038, 'viio42/ii': 0.038, 'V43[add4][no3]': 0.038, 'Cad64/V': 0.038,
                'viio6/bi': 0.038, 'viio/bIV': 0.038, 'It6': 0.038, 'V6/iii': 0.038, 'V/ii': 0.038,
                'viio7/vii': 0.035, 'iio': 0.035, 'Ger7': 0.032, 'II65': 0.032, 'ii43': 0.032,
                'viio/ii': 0.032, 'I+6': 0.032, 'V[add6]': 0.032, 'VI6/v': 0.032,
                'viio65/#I': 0.032, 'viio6/vii': 0.032, 'IV42': 0.029, 'iii65[add9]': 0.029,
                'viio42/vii': 0.029, 'I65': 0.026, 'Ger65/ii': 0.026, 'V+/IV': 0.026,
                'viio6/iii': 0.026, 'viio64/ii': 0.026, 'viio43/v': 0.026, 'viio/v': 0.026,
                'V65/iv': 0.026, 'ii6/4': 0.026, 'III+42/vi': 0.026, 'viiø6': 0.026,
                'V42/II': 0.026, 'IV7[no5]': 0.026, 'bVI42': 0.026, 'V64/ii': 0.026, 'V2': 0.026,
                'V[add9]': 0.026, 'iv6/vi': 0.026, 'V[add9]/vi': 0.025, 'bVI': 0.025, 'iio7': 0.022,
                'iio7/ii': 0.019, 'III+/ii': 0.019, 'IV65': 0.019, 'V+642': 0.019,
                'V43[add4][add9]': 0.019, 'I[add#6]': 0.019, 'V65[add9]': 0.019, 'V43/iv': 0.019,
                'V+6/vi': 0.019, 'vi6/4': 0.019, 'viio7/IV': 0.019, 'V64/vi': 0.019, 'V6/v': 0.019,
                'V/IV': 0.019, 'V54': 0.019, 'V7b9': 0.019, 'IV6b5': 0.019, 'V9/iv': 0.019,
                '#iio2': 0.019, 'i54': 0.019, 'V7/iii': 0.016, 'viio6/IV': 0.016, 'viio7/iv': 0.016,
                'viio/V': 0.016, 'V65/iii': 0.016, 'iv/vi': 0.013, 'viio7[no5]/vi': 0.013,
                'viio/iii': 0.013, 'V+43': 0.013, 'Fr7': 0.013, 'IV9/iv': 0.013, 'viiø2': 0.013,
                'v6': 0.013, 'bVII6': 0.013, 'V43[add9]': 0.013, 'viio/42': 0.013, 'ii65/IV': 0.013,
                'iv64/ii': 0.013, 'viiø7/v': 0.013, 'iv6/IV': 0.013, 'iii42[no5]': 0.013,
                'vi65[no5]': 0.013, 'iiiø7': 0.013, 'III+6/ii': 0.013, 'VI/vi': 0.013,
                'III+64/vi': 0.013, 'V/iii': 0.013, '#iio7': 0.013, 'viio6/iv': 0.013,
                'It6/vi': 0.013, 'iiø': 0.013, 'i[add4]': 0.013, 'ii43[no3]': 0.013,
                'I[add4]': 0.013, 'bVI64': 0.013, 'iii64': 0.013, 'vi2': 0.013, 'ii2': 0.013,
                'Ger65/I': 0.013, 'viio7/II': 0.013, 'V43/iii': 0.013, 'v64': 0.012,
                'V7[no3]': 0.01, 'viio65/iii': 0.01, 'It6/iv': 0.01, 'bVI+': 0.01,
                'I[no3][add2][add4]': 0.01, 'bII6#5': 0.01, 'V+64/IV': 0.01, 'V7[no5]/iii': 0.01,
                'I+42[b7]': 0.01, 'I64/V': 0.01, 'viiø42/IV': 0.01, 'bVI+64': 0.01, 'IV4b3': 0.01,
                'Ger6': 0.01}

lieder_major_simple = {'I': 42.541, 'V': 33.535, 'ii': 5.932, 'IV': 4.589, 'vii': 3.209, 'vi': 3.13,
                       '#vii': 1.86, 'i': 1.261, 'iv': 1.119, 'Ger': 0.764, 'iii': 0.453,
                       'II': 0.261, '#ii': 0.215, 'III': 0.206, 'bII': 0.184, 'Fr': 0.183,
                       'v': 0.149, 'bVI': 0.122, 'VI': 0.096, '#V': 0.064, 'It': 0.061,
                       'bIII': 0.051, 'bVII': 0.013}

lieder_minor = {'i': 27.055, 'V': 10.725, 'V7': 7.152, 'i64': 5.032, 'i6': 4.687, 'VI': 2.059,
                'iv': 1.957, 'V65': 1.898, 'I': 1.851, 'V43': 1.541, 'iv6': 1.514, 'V42': 1.398,
                'viio43': 1.396, 'viio7': 1.388, 'Ger65': 1.337, 'iiø65': 1.127, 'V9': 1.055,
                'V6': 1.053, 'viio43/V': 0.894, 'viio65': 0.889, 'Cad64': 0.871, 'viio42': 0.846,
                'iio6': 0.767, 'III': 0.705, 'iiø42': 0.63, 'VI6': 0.622, 'iiø7': 0.599,
                'viio7/V': 0.545, 'iiø43': 0.49, 'iv64': 0.476, 'viio6': 0.452, 'V7/iv': 0.435,
                'V64': 0.407, 'V7/V': 0.368, 'VI7': 0.354, 'iv7': 0.349, 'It6': 0.347, 'v6': 0.343,
                'viio': 0.294, 'bII6': 0.289, 'Fr43': 0.282, 'viio7/iv': 0.257, 'viio7/v': 0.252,
                'V65/iv': 0.245, 'iio': 0.242, 'I6': 0.24, 'V65/V': 0.239, 'iio64': 0.218,
                'i54': 0.214, 'VI64': 0.211, 'III+6': 0.208, 'ii7': 0.196, 'ii': 0.187, 'v7': 0.184,
                'III7': 0.183, 'viø65': 0.172, 'v': 0.172, 'viø7': 0.166, 'iio43': 0.165,
                'IV64': 0.159, 'bII': 0.153, 'V/V': 0.153, 'VI42': 0.147, 'V7/iii': 0.147,
                'i42': 0.147, 'V43[b5]': 0.147, 'V6/V': 0.147, 'bII65': 0.146, 'V7/III': 0.14,
                'I64': 0.138, 'ii65': 0.135, 'i7': 0.129, 'V43/V': 0.129, 'III+': 0.123,
                'VII': 0.123, 'V65/IV': 0.122, 'IV': 0.12, 'V42/iv': 0.117, 'viio65/V': 0.117,
                'viio43/iv': 0.116, 'bII6#5': 0.116, 'VI+': 0.11, 'ivb7': 0.11, 'iio7': 0.11,
                'viio65/v': 0.11, 'V7[no3]': 0.107, 'viio64': 0.104, 'V43/iv': 0.101,
                'viio64/ii': 0.098, 'bVI6': 0.098, 'IV6': 0.098, 'bII4#3': 0.098, 'iio65': 0.098,
                'bvi': 0.097, 'III+64': 0.096, 'V7/v': 0.092, 'vi': 0.09, 'viio42/V': 0.086,
                'viio/V': 0.086, 'III64': 0.086, 'V[no3no5]': 0.085, 'V42/IV': 0.077,
                'V42/bII': 0.074, 'iv65': 0.074, 'bV[add#6]': 0.074, 'viio42/v': 0.074,
                'bII42[#7]': 0.074, 'V2': 0.073, 'bII#7': 0.067, 'Ger42': 0.067, 'viio42/iv': 0.067,
                'III+7': 0.064, 'V65/VI': 0.061, 'V7/VI': 0.061, 'IV9': 0.061, 'ii6': 0.061,
                'V64[no3]': 0.061, 'iv43': 0.061, 'Ger43': 0.055, 'III6': 0.055, 'iv6[add4]': 0.055,
                'viio6/iv': 0.055, 'IV43': 0.05, 'vi64': 0.049, 'V42/V': 0.049, 'VII6': 0.049,
                'i64/V': 0.049, 'viio43/VI': 0.049, 'viio6/V': 0.049, 'i64[no3]': 0.049,
                'Ger7': 0.049, 'bvii': 0.049, 'V6-5': 0.049, 'iio42': 0.049, 'IV/64': 0.049,
                'V9[no3]': 0.049, 'vii/V': 0.043, 'viio/v': 0.04, 'Fr7': 0.037, 'Fr42': 0.037,
                'III+65': 0.037, 'V42/III': 0.037, 'III+43': 0.037, 'i532': 0.037,
                'viiø7/IV': 0.037, 'bVI42[b7]': 0.037, 'bVII7': 0.037, 'III+63': 0.037,
                'V642': 0.037, 'V7[no5]/V': 0.037, 'V7[add4]': 0.037, 'V65/VII': 0.037, 'N6': 0.037,
                'vo6': 0.037, 'Fr43/iv': 0.037, 'viio7/ii': 0.037, 'V42/VI': 0.037,
                'vo64[no3]': 0.037, 'III42/iv': 0.037, 'It': 0.037, 'Fr6': 0.037, 'VIb7': 0.037,
                'V7/IV': 0.037, 'iiø64': 0.037, 'vø7': 0.037, 'iv9': 0.037, 'viø42': 0.031,
                'V7[no5]': 0.031, 'i6[no1]': 0.031, 'V+': 0.028, 'Ger6': 0.025,
                'viio43[no3]': 0.025, 'viiø43': 0.025, 'bII9': 0.025, 'II42': 0.025, 'vio6': 0.025,
                'ii42': 0.025, 'V43/VI': 0.025, 'i[no3][add2][add4]': 0.025,
                'i[no3][no5][add2][add4][add6]': 0.025, 'It64': 0.025, 'V9/V': 0.025, 'V4': 0.025,
                'viio65/IV': 0.025, 'I64/VI': 0.025, 'viio7/IV': 0.025, 'V9/IV': 0.025,
                'vi43': 0.025, 'V65/III': 0.025, 'III42[no3]': 0.025, 'VI42[no3]': 0.025,
                'iio65[no5]': 0.025, 'i:': 0.025, 'V+6': 0.025, 'IV7': 0.025, 'V42[no3no5]': 0.025,
                'bVI': 0.025, 'bVI+': 0.025, 'bII64': 0.025, 'vii64/v': 0.025, 'It53': 0.025,
                'iio/V': 0.025, 'V9/iv': 0.025, 'II7': 0.024, 'v4': 0.024, 'v43': 0.024,
                'iiø2': 0.024, 'iiø7/III': 0.024, 'V+65': 0.024, 'ii64': 0.019, 'It6/iv': 0.018,
                'V+7': 0.018, 'V[add6]': 0.018, 'ii9': 0.018, 'iv7[no3]': 0.018, 'V65/v': 0.018,
                'III42[b7]': 0.018, 'viio65/ii': 0.018, 'It53[add4]': 0.018, 'iiø7/V': 0.013,
                'V7/ii': 0.013, 'ib7': 0.012, 'viø43': 0.012, 'bvi43': 0.012, 'i65': 0.012,
                'bVI42': 0.012, 'bVII': 0.012, 'bVIb7': 0.012, 'vo43': 0.012, 'VI43': 0.012,
                'VI65': 0.012, 'V43/v': 0.012, 'iiø6': 0.012, 'V[no3][no5]': 0.012, 'IV65': 0.012,
                'VI+6': 0.012, 'iio43[no3]': 0.012, 'viio2/v': 0.012, 'V/VI': 0.012,
                'viiø7/iv': 0.012, 'viiø7/V': 0.012, 'V6/iv': 0.012, 'III+42': 0.012}

lieder_minor_simple = {'i': 37.567, 'V': 29.244, 'vii': 7.394, 'ii': 5.313, 'iv': 4.656,
                       'VI': 3.605, 'I': 3.128, 'III': 1.725, 'Ger': 1.535, '#vii': 1.174,
                       'bII': 1.031, 'v': 0.871, 'IV': 0.575, 'vi': 0.571, 'It': 0.47, 'Fr': 0.43,
                       'bVI': 0.209, 'VII': 0.172, 'bvi': 0.109, 'bV': 0.074, 'bvii': 0.049,
                       'bVII': 0.049, 'II': 0.049}

lieder_both = {'I': 21.202, 'V7': 10.965, 'i': 9.836, 'V': 8.006, 'I64': 3.246, 'I6': 2.653,
               'V65': 1.97, 'i64': 1.867, 'V43': 1.772, 'i6': 1.729, 'IV': 1.662, 'V42': 1.454,
               'vi': 1.29, 'Cad64': 1.243, 'ii': 1.107, 'iv': 1.056, 'ii6': 0.96, 'V6': 0.867,
               'V9': 0.804, 'V7/V': 0.77, 'Ger65': 0.764, 'VI': 0.707, 'viio7': 0.698, 'IV6': 0.681,
               'iv6': 0.675, 'V7/IV': 0.636, 'viio43': 0.586, 'iiø65': 0.575, 'IV64': 0.574,
               'viio42': 0.544, 'viio7/V': 0.526, 'ii7': 0.517, 'ii65': 0.487, 'iiø42': 0.409,
               'V65/V': 0.397, 'viio43/V': 0.389, 'viio65': 0.381, 'iio6': 0.347, 'iiø7': 0.328,
               'vi6': 0.313, 'III': 0.293, 'viio43/ii': 0.29, 'viio6': 0.288, 'V64': 0.26,
               'iv64': 0.239, 'VI6': 0.214, 'V7/vi': 0.212, 'iiø43': 0.21, 'Fr43': 0.208,
               'viio7/v': 0.207, 'V43/V': 0.204, 'V42/IV': 0.198, 'V7/ii': 0.198, 'V65/IV': 0.196,
               'V/vi': 0.187, 'V7/iv': 0.181, 'viio': 0.156, 'iii6': 0.154, 'viio7/ii': 0.154,
               'It6': 0.144, 'bII': 0.137, 'vi42': 0.137, 'iio64': 0.134, 'vi7': 0.128, 'v6': 0.126,
               'iv7': 0.124, 'VI7': 0.122, '#iio42': 0.12, 'viiø7/V': 0.12, 'V+': 0.119,
               'V/V': 0.118, 'v': 0.116, 'I42': 0.111, 'iio': 0.106, 'viiø65': 0.103,
               'V43/ii': 0.103, 'V6/V': 0.103, 'viio65/ii': 0.103, 'V+6': 0.101, 'V65/iv': 0.101,
               'V65/ii': 0.101, 'viio42/iii': 0.101, 'bII6': 0.099, 'V+7': 0.099, 'ii42': 0.099,
               'viio7/iv': 0.099, 'iii': 0.099, 'Ger43': 0.098, 'V65/vi': 0.097, 'viio65/v': 0.094,
               'viø7': 0.091, 'v7': 0.088, 'viiø7': 0.088, 'viio65/V': 0.086, 'i54': 0.086,
               'V43/vi': 0.084, 'I54': 0.082, 'I7': 0.082, 'V7[no5]': 0.078, 'V7/II': 0.076,
               'VI64': 0.072, 'III+6': 0.072, 'vi64': 0.07, 'IV7': 0.069, 'vi65': 0.069,
               'I[add6]': 0.063, 'iio65': 0.063, 'III7': 0.063, 'V7/iii': 0.061, 'viio64': 0.061,
               'bVI6': 0.059, 'viø65': 0.059, 'V42/V': 0.059, 'viio6/V': 0.059, 'iio42': 0.057,
               'iio43': 0.057, 'viio42/V': 0.055, 'V43[no3]': 0.055, 'viiø43': 0.055,
               'V42/ii': 0.054, 'VI42': 0.053, 'V7/III': 0.052, 'iio7': 0.052, 'IV43': 0.051,
               'ii64': 0.051, 'viio64/ii': 0.051, 'i42': 0.051, 'V43[b5]': 0.051, 'I+': 0.051,
               'bII65': 0.05, 'IV6/4': 0.048, 'V43/iv': 0.047, 'Vb9': 0.046, 'II42': 0.046,
               'V9[no5]': 0.046, 'bII6#5': 0.046, 'V42/iv': 0.044, 'viio43/III': 0.044, 'i7': 0.044,
               'I43': 0.044, 'V7[no3]': 0.043, 'viio43[no3]': 0.042, 'II': 0.042, 'III+': 0.042,
               'VII': 0.042, 'viiø65/V': 0.042, 'II43': 0.042, 'iv6/ii': 0.042, '#V': 0.042,
               'V2': 0.042, 'viio7/vi': 0.04, 'V6/ii': 0.04, 'viio/V': 0.04, 'viio43/iv': 0.04,
               'vi43': 0.038, 'VI+': 0.038, 'Ger7': 0.038, 'ivb7': 0.038, 'III+/vi': 0.038,
               'V6/vi': 0.036, 'Ger65/IV': 0.034, 'V43/IV': 0.034, 'bIII': 0.034,
               'viio7/III': 0.034, 'III64': 0.034, 'V9/IV': 0.034, 'V9/v': 0.034, 'VI/ii': 0.034,
               'iv64[no1]': 0.034, 'bII4#3': 0.034, 'viio6/ii': 0.034, 'bvi': 0.033,
               'III+64': 0.033, 'viio65/vi': 0.032, 'V7/v': 0.032, 'viiø42': 0.032,
               'viio64/V': 0.032, 'viio7/iii': 0.032, 'viio/v': 0.031, 'bII7': 0.029,
               'Ger65/II': 0.029, 'V[no3]': 0.029, 'V[no3no5]': 0.029, 'II6': 0.027,
               'V[add6]': 0.027, 'viio6/iv': 0.027, 'V42/bII': 0.025, 'iv65': 0.025, 'I+64': 0.025,
               'bV[add#6]': 0.025, 'I6[no5]': 0.025, 'viio43/vii': 0.025, 'viio42/v': 0.025,
               'V6/5': 0.025, 'V9/ii': 0.025, 'viio42/ii': 0.025, 'bII42[#7]': 0.025,
               'V43[add4][no3]': 0.025, 'Cad64/V': 0.025, 'viio6/bi': 0.025, 'viio/bIV': 0.025,
               'V6/iii': 0.025, 'V/ii': 0.025, 'bVI': 0.025, 'viio/ii': 0.023, 'viio7/vii': 0.023,
               'bII#7': 0.023, 'Ger42': 0.023, 'viio42/iv': 0.023, 'III+7': 0.022, 'Fr7': 0.021,
               'V65/VI': 0.021, 'V7/VI': 0.021, 'IV9': 0.021, 'bVI42': 0.021, 'II65': 0.021,
               'viio7/IV': 0.021, 'ii43': 0.021, 'I+6': 0.021, 'V9/iv': 0.021, 'VI6/v': 0.021,
               'viio65/#I': 0.021, 'V64[no3]': 0.021, 'iv43': 0.021, 'viio6/vii': 0.021,
               'IV42': 0.019, 'III6': 0.019, 'iv6[add4]': 0.019, 'iii65[add9]': 0.019,
               'viio42/vii': 0.019, 'I65': 0.017, 'Ger65/ii': 0.017, 'V+/IV': 0.017,
               'viio6/iii': 0.017, 'viio43/v': 0.017, 'IV65': 0.017, 'VII6': 0.017, 'i64/V': 0.017,
               'viio43/VI': 0.017, 'ii6/4': 0.017, 'i64[no3]': 0.017, 'III+42/vi': 0.017,
               'bvii': 0.017, 'V6-5': 0.017, 'viiø6': 0.017, 'V42/II': 0.017, 'IV7[no5]': 0.017,
               'V64/ii': 0.017, 'IV/64': 0.017, 'V9[no3]': 0.017, 'V[add9]': 0.017, 'iv6/vi': 0.017,
               'V[add9]/vi': 0.017, 'Ger6': 0.015, 'bVI+': 0.015, 'vii/V': 0.015, 'Fr42': 0.013,
               'iio7/ii': 0.013, 'III+/ii': 0.013, 'III+65': 0.013, 'V42/III': 0.013,
               'III+43': 0.013, 'i532': 0.013, 'viiø7/IV': 0.013, 'bVI42[b7]': 0.013,
               'V+642': 0.013, 'bVII7': 0.013, 'III+63': 0.013, 'V642': 0.013,
               'V43[add4][add9]': 0.013, 'It6/iv': 0.013, 'I[add#6]': 0.013, 'V65[add9]': 0.013,
               'V7[no5]/V': 0.013, 'V7[add4]': 0.013, 'V65/VII': 0.013, 'V+6/vi': 0.013,
               'vi6/4': 0.013, 'N6': 0.013, 'vo6': 0.013, 'Fr43/iv': 0.013, 'V64/vi': 0.013,
               'V42/VI': 0.013, 'vo64[no3]': 0.013, 'V6/v': 0.013, 'III42/iv': 0.013, 'It': 0.013,
               'V/IV': 0.013, 'Fr6': 0.013, 'VIb7': 0.013, 'iiø64': 0.013, 'V54': 0.013,
               'V7b9': 0.013, 'vø7': 0.013, 'IV6b5': 0.013, '#iio2': 0.013, 'iv9': 0.013,
               'ii9': 0.011, 'viø42': 0.011, 'viio6/IV': 0.011, 'i6[no1]': 0.01, 'V65/iii': 0.01}

lieder_both_simple = {'V': 32.168, 'I': 29.136, 'i': 13.78, 'ii': 5.679, 'vii': 4.638, 'IV': 3.215,
                      'iv': 2.322, 'vi': 2.237, '#vii': 1.591, 'VI': 1.284, 'Ger': 1.026,
                      'III': 0.704, 'bII': 0.46, 'v': 0.372, 'iii': 0.274, 'Fr': 0.27, 'II': 0.179,
                      'It': 0.171, '#ii': 0.134, 'bVI': 0.134, 'VII': 0.059, '#V': 0.042,
                      'bIII': 0.034, 'bvi': 0.033, 'bV': 0.025, 'bvii': 0.017, 'bVII': 0.013}


# ------------------------------------------------------------------------------

# Code

def get_usage(base_path: str = str(CORPUS_FOLDER / 'OpenScore-LiederCorpus'),
              weight_by_length: bool = True,
              sort_dict: bool = True,
              percentages: bool = True,
              mode: str = 'major',
              plateau: float = 0.01
              ):
    """
    For a given corpus, iterate over all figures and return 
    a dict for each chord and its usage.
    
    Choose mode = 'major', 'minor', 'both'.
    It usually makes sense to separate by mode 
    (e.g. usage of 'i' varies signifiantly between major and minor).
    
    Optionally set a plateau for minimum usage, ignoring one-offs.
    By default this value is 0.0 (i.e. there is no such plateau). 
    Set at a higher value to cut off at that level. 
    This applies to both percentage and otherwise.
    E.g. 0.01 for low percentages or 
    1 for single quarterLength usage (or equivalent).
    """

    if mode not in ['major', 'minor', 'both']:
        raise ValueError("Invalid mode: chose one of 'major', 'minor', 'both'.")

    files = chord_comparisons.get_files(base_path)  # file_name = 'slices_with_analysis.tsv')

    working_dict = {}

    for path_to_file in files:
        try:
            data = get_distributions.DistributionsFromTabular(path_to_file)
        except ValueError:
            raise ValueError(f"Cannot load {path_to_file}")  # .split('/')[-4:-1]}")
            # print(f"failing to load {path_to_file.split('/')[-4:-1]}")

        data.get_profiles_by_chord()

        for d in data.profiles_by_chord:
            # Mode
            if mode == 'major' and not d['key'][0].isupper():  # Major e.g. 'C', 'Ab'.
                continue
            elif mode == 'minor' and d['key'][0].isupper():  # Should be lower e.g. ab'.
                continue

            # Init new entries
            if d['chord'] not in working_dict:
                working_dict[d['chord']] = 0

                # Length or count:
            if weight_by_length:
                working_dict[d['chord']] += d['quarter length']
            else:
                working_dict[d['chord']] += 1

    if sort_dict:
        working_dict = sort_this_dict(working_dict)

    if percentages:
        working_dict = dict_in_percentages(working_dict)

    if plateau:

        pop_keys = []
        for key in list(working_dict.keys()):
            if working_dict[key] < plateau:
                pop_keys.append(key)

        for key in pop_keys:  # iterate all as it might not be sorted
            working_dict.pop(key)

    return working_dict


def simplify_usage_dict(this_usage_dict: dict = lieder_both,
                        # TODO simplification options here.
                        sort_dict: bool = True,
                        percentages: bool = True):
    """
    For a full usage dict (with separate entries for each exact figure),
    return a simplified form, joining items together figures according to 
    the types of simplification set out in simplify_chord.
    
    a dict for each chord and its usage.
    """
    working_dict = {}
    for k, v in this_usage_dict.items():
        simpler_key = simplify_chord(k)  # TODO simplification options here.
        if simpler_key not in working_dict:
            working_dict[simpler_key] = 0  # init
        working_dict[simpler_key] += v  # in any case

    if sort_dict:
        working_dict = sort_this_dict(working_dict)

    if percentages:
        working_dict = dict_in_percentages(working_dict)

    return working_dict


usage_dict_simplified = {'V': 32.067, 'I': 29.11, 'i': 13.717, 'ii': 5.808, 'vii': 4.684,
                         'IV': 3.237, 'iv': 2.312, 'vi': 2.228, '#vii': 1.623, 'VI': 1.228,
                         # TODO fix '#vii'
                         'Ger': 0.897, 'III': 0.763, 'bII': 0.446, 'v': 0.4, 'iii': 0.316,
                         'Fr': 0.274, 'It': 0.193, 'II': 0.158, 'bVI': 0.151, '#ii': 0.142,
                         'VII': 0.059, '#V': 0.042, 'bvi': 0.038, 'bIII': 0.034, 'bVII': 0.029,
                         'bV': 0.025, 'bvii': 0.017}


def sort_this_dict(working_dict):
    """
    Sorts a dict by the values, high to low.
    """
    return {k: v for k, v in sorted(working_dict.items(),
                                    key=lambda item: item[1],
                                    reverse=True)}


def dict_in_percentages(working_dict):
    """
    Convert a dict into expression the values as percentages of the total.
    """
    total = sum([working_dict[x] for x in working_dict])
    for x in working_dict:
        working_dict[x] *= (100 / total)
        working_dict[x] = round(working_dict[x], 3)

    return working_dict


# ------------------------------------------------------------------------------

def simplify_chord(rn: Union[roman.RomanNumeral, str],
                   hauptHarmonicFunction: bool = False,
                   fullHarmonicFunction: bool = False,
                   ignoreInversion: bool = False,
                   ignoreRootAlt: bool = False,
                   ignoreOtherAlt: bool = True,
                   ):
    """
    Given a chord (expressed as a roman.RomanNumeral or figure str),
    simplify that chord in one or more ways:

    hauptHarmonicFunction:
        returns the basic function like T, S, D.
        E.g., 'I' becomes 'T'.
        See notes at music21.analysis.harmonicFunction

    fullHarmonicFunction:
        Likewise, but supports Nebenfunktionen, e.g. Tp.
        E.g., 'vi' in a major key becomes 'Tp'.
        Again, see notes at music21.analysis.harmonicFunction

    ignoreInversion:
        E.g., '#ivo65' becomes '#ivo'.

    ignoreRootAlt:
        E.g., '#ivo' becomes 'ivo'.
        (NB: Not usually desirable!)

    ignoreOtherAlt:
        Ignore modifications of and added, removed, or chromatically altered tones.
        So '#ivo[add#6]' becomes '#ivo'.

    These are all settable separately, and so potentially combinable, 
    but note that there is a hierarchy here.
    For instance, anything involving the function labels currently makes all the others
    reductant.

    >>> rn = roman.RomanNumeral('#ivo65[add4]/v')
    >>> rn.figure
    '#ivo65[add4]/v'

    >>> rn.primaryFigure
    '#ivo65[add4]'

    >>> rn = roman.RomanNumeral('#ivo65[add4]')
    >>> rn.romanNumeral
    '#iv'

    >>> rn.romanNumeralAlone
    'iv'

    """

    if isinstance(rn, str):
        rn = roman.RomanNumeral(rn)

    if hauptHarmonicFunction or fullHarmonicFunction:
        return hf.romanToFunction(rn, hauptHarmonicFunction=hauptHarmonicFunction)

    if any([ignoreInversion, ignoreRootAlt, ignoreOtherAlt]):
        # TODO fully, separate handling. Make a convenience fx in m21
        # See doc notes above on .romanNumeral, .romanNumeralAlone, etc
        # HOw to handle secondary? rn.primaryFigure - follow m21 conventions
        # ignoreAdded = rn.romanNumeral
        # ignore # vs .figure vs .romanNumeralAlone
        if ignoreRootAlt:
            return rn.romanNumeralAlone
        else:
            if ignoreOtherAlt:  # added etc., but keep root alt
                return rn.romanNumeral
