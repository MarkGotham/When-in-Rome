from tempfile import NamedTemporaryFile

from Tests import TEST_RESOURCES_FOLDER
from Code.converters_local import ConverterRn2Tab, ConverterRn2Dez, rn2dez

fld = TEST_RESOURCES_FOLDER / "Example"
score_path = fld / "score.mxl"
tab_path = fld / "analysis_BPS_format.csv"
dez_path = fld / "analysis_dez_format.dez"
rn_path = fld / "analysis.txt"


def test_rn2tab():
    c = ConverterRn2Tab()
    with open(tab_path, "r") as f:
        ref = f.readlines()
    with NamedTemporaryFile() as f:
        c.convert_file(score_path, rn_path, f.name)
        pred = [x.decode().replace("\r", "") for x in f.readlines()]
    assert ref == pred


def test_rn2dez():
    c = ConverterRn2Dez()
    ref = c._load_dez(dez_path)
    with NamedTemporaryFile() as f:
        rn2dez(rn_path, f.name)
        pred = c._load_dez(f.name)
    assert ref == pred
