"""
This script is a starting point to do any kinds of analysis one might want.
It stores the information on each piece inside a pandas dataframe.
Therefore, it requires the pandas package to be installed
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from Code import CORPUS_FOLDER
from Code.Pitch_profiles.get_distributions import DistributionsFromTabular
from Code.updates_and_checks import get_corpus_files


def plot_key_over_time(df, name):
    df.plot.scatter("offset", "key")
    plt.title(name)
    plt.show()
    return


if __name__ == '__main__':
    files = get_corpus_files(file_name="slices_with_analysis.tsv")
    names = [Path(f).parent.relative_to(CORPUS_FOLDER) for f in files]

    distributions = {f: DistributionsFromTabular(path_to_tab=f) for f in files}
    data = [pd.DataFrame(v.data, columns=v.headers).fillna(method="ffill") for k, v in distributions.items()]
