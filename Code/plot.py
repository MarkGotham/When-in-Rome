# -*- coding: utf-8 -*-
"""
NAME:
===============================
Plot (plot.py)


BY:
===============================
Mark Gotham


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================
Plot

"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from typing import Callable, Union
from music21 import roman

from . import CODE_FOLDER, data_by_heading, load_json

from .Pitch_profiles import chord_usage

ANTHOLOGY_PATH = CODE_FOLDER.parent / "Anthology"


# ------------------------------------------------------------------------------

# Linear, Polynomials (quadratic + cubic), and more

def linear(x, a, b):
    return a * x + b


def quadratic(x, a, b, c):
    return a * x ** 2 + b * x + c


def cubic(x, a, b, c, d):
    return a * x ** 3 + b * x ** 2 + c * x + d


def arc_tan(x, a, b, c, d):
    return a * np.arctan(b * x + c) + d


def exponential_decay(x, a, b, c):
    return a * np.exp(-b * x) + c


def log_decay(x, a, b, c):
    return -a * np.log(b * x) + c


# ------------------------------------------------------------------------------

def plot_dist(
        values_list_of_lists: list,
        name_list_of_lists: list,
        labels: list | None = None,
        plot_type: str = "bar",  # or "line"
        xlabel: str = "Position",
        ylabel: str = "Weight",
        title: str = "Profile weighting",
        width: float = 0.5,
        savefig: bool = False,
        out_path: Path | str | None = CODE_FOLDER / "test.png"
) -> plt:
    """
    Plot (bars or line) usage distribution
    whether for a source or a model (or anything else!)

    `values_list_of_lists` and `name_list_of_lists` are
    lists of lists to support any number of value / name pairs.
    There must be at least one sublist to each, and the same number as each other.
    """

    if not labels:
        labels = [str(x) for x in range(len(values_list_of_lists[0]))]
    elif len(labels) != len(values_list_of_lists[0]):
        raise ValueError("The length of variable labels "
                         f"(currently {len(labels)}) "
                         "must be equal to that of the values "
                         f"(currently {len(values_list_of_lists[0])}.")

    for x in values_list_of_lists:
        assert (len(x) == len(values_list_of_lists[0]))  # all the same length

    indexes = range(len(labels))

    # fig, ax = plt.subplots()
    # plt.figure()
    # plt.figure(figsize=(15, 6))

    # plot_type
    if plot_type == "bar":
        f = plt.bar
    elif plot_type == "line":
        f = plt.plot
    else:
        raise ValueError(f"plot_type {plot_type} not supported. Chose `bar` or `line`.")

    for i in range(len(values_list_of_lists)):
        f(indexes, values_list_of_lists[i], width, label=name_list_of_lists[i])

    plt.legend()  # loc="upper left")
    # plt.gcf().subplots_adjust(left=0.15)

    # plt.title(title)
    plt.xlabel(xlabel)  # , fontsize=14)
    plt.ylabel(ylabel)  # , fontsize=14)
    plt.xticks(indexes, labels)

    plt.ylim(0, 0.5)

    plt.tight_layout()

    if not title:
        title = "Plot"
    if savefig:
        plt.savefig(Path(out_path) / f"{title}.pdf", facecolor="w", edgecolor="w", format="pdf")
    else:
        return plt.figure


def plot_hist(
        data_list: list,
        bins: int | None = None,
        xlabel: str = "",
        ylabel: str = "Frequency",
        title: str = "",
        min_max_bin_from_data: bool = False,
        save_fig: bool = True
) -> plt:
    """
    Plotting data in the form of a list of integer values.
    Binning supported within the plot.
    """

    if min_max_bin_from_data:
        mn = min(data_list)
        mx = max(data_list)
        if bins is None:
            bins = int(mx) + 1 - int(mn)
    else:
        mn = 0
        mx = 100
        if bins is None:
            bins = 20

    incr = (mx - mn) / bins

    plt.figure(figsize=(15, 6))

    plt.hist(data_list,
             bins=bins,
             width=incr * 0.8,
             range=(mn, mx),
             align="mid",
             )

    plt.title(title, fontsize=20, family="serif")
    plt.xlabel(xlabel, fontsize=14, family="serif")
    plt.ylabel(ylabel, fontsize=14, family="serif")
    plt.xticks(np.arange(mn, mx, incr))
    plt.yticks(np.arange(0, 10, 1))

    if not title:
        title = "Plot"

    if save_fig:
        plt.savefig(title + ".pdf",
                    facecolor="w",
                    edgecolor="w",
                    format="pdf")
    else:
        return plt.figure


def plot_scatter_best_fit(
        xs: Union[list, np.array],
        ys: Union[list, np.array],
        fit_function: str | Callable = "exponential",
        p0: tuple | None = (2000, .1, 50),
        xscale: str | None = "log",
        xlabel: str = "Length (quarter notes)",
        ylabel: str = "Distance to prototype",
        title: str = "scatter_fit",
        savefig: bool = False
):
    """
    Make a scatter plot of 2D data and include a
    line (e.g. fit_function = "linear"), or
    curve (e.g. fit_function = "exponential"),
    of best fit.

    p0 argument is a tuple with starting estimate for fit function
    """

    if type(xs) == list:
        xs = np.array(xs)
    if type(ys) == list:
        ys = np.array(ys)

    # in case of multiple plots
    fig, ax = plt.subplots()
    ax.scatter(xs, ys, marker="x", linewidths=0.5)
    # plt.plot(xs, ys)  # , ".", label="data")

    if xscale:
        plt.xscale(xscale)

    x_fit = np.linspace(min(xs), max(xs), 10)  # issues with np.array(xs) for some reason

    squared_diffs = None

    if type(fit_function) == str:
        fit_function = fit_function.lower()

    if fit_function in ["lin", "linear", linear]:
        b, a = np.polynomial.polynomial.polyfit(xs, ys, 1)  # NB

        xs = np.array(xs)
        ys = np.array(ys)

        # params, cv = curve_fit(linear, xs, ys, p0)
        # a, b = params

        squared_diffs = np.square(ys - linear(xs, a, b))

        eq = f"{a}x + {b}"
        y_fit = a * x_fit + b

    elif fit_function in ["exp", "exponential", exponential_decay]:

        xs = np.array(xs)
        ys = np.array(ys)

        params, cv = curve_fit(exponential_decay, xs, ys, p0)
        a, b, c = params

        squared_diffs = np.square(ys - exponential_decay(xs, a, b, c))

        eq = f"y = {round(a, 3)}e^(-{round(b, 3)}x) + {round(c, 3)}"
        y_fit = exponential_decay(x_fit, a, b, c)

    elif fit_function in ["log", log_decay]:  # TODO compress

        xs = np.array(xs)
        ys = np.array(ys)

        # Fit
        params, cv = curve_fit(log_decay, xs, ys, p0)
        a, b, c = params

        # r^2 (quality of the fit from min 0 to max fit 1). TODO apply to all
        squared_diffs = np.square(ys - log_decay(xs, a, b, c))

        eq = f"y = -{round(a, 3)} * log({round(b, 3)}x) + {round(c, 3)}"
        y_fit = log_decay(x_fit, a, b, c)

    else:
        raise ValueError("Invalid fit_function")

    if squared_diffs is not None:
        r2_from_squared_diffs(ys, squared_diffs)

    plt.plot(x_fit, y_fit, "--", color="green", label=eq)
    plt.legend()

    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    if savefig:
        plt.savefig(title + ".png", facecolor="w", edgecolor="w", format="png")
    else:
        plt.show()


def r2_from_squared_diffs(
        ys: np.array,
        squared_diffs: np.square,
        print_r2: bool = True
):
    squared_diffs_from_mean = np.square(ys - np.mean(ys))
    r2 = 1 - np.sum(squared_diffs) / np.sum(squared_diffs_from_mean)
    if print_r2:
        print(f"R² = {round(r2 * 100, 3)}%")
    return r2


# ------------------------------------------------------------------------------

def plot_with_best_fit(
        x: list,
        y: list,
        fit_function=exponential_decay,
        a: float = None,  # Initial guesses for the variables
        b: float = None,  # ... as needed for the fx ...
        c: float = None,
        xlabel: str = "Position",
        ylabel: str = "Weight",
        title: str = "Distribution weighting",
        savefig: bool = False
):
    # Check fit_function legit + number of variables

    popt, pcov = curve_fit(fit_function, x, y, p0=(a, b, c))

    # Calculate new x and y values for the curve of best fit
    x_new = np.linspace(x[0], x[-1], 50)  # first, last, step
    # y_new = f(x_new)  # quad
    y_new = fit_function(x_new, *popt)  # exp

    # Plot
    plt.plot(x, y, "o", x_new, y_new)
    plt.xlim(x[0], x[-1])  # min / max
    # plt.plot(x, np.poly1d(np.polyfit(x, nums, 1))(y))
    # plt.plot(x, np.poly1d(np.polyfit(x, y, 1))(y))
    # plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))  # for unsorted
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    if savefig:
        plt.savefig(title + ".png", facecolor="w", edgecolor="w", format="png")
    else:
        plt.show()
        return plt


# TODO integrate above ^
def exp_with_fit(
        xs: np.array,
        ys: np.array,
        title: str = "Test"
) -> plt:
    plt.plot(xs, ys, ".")
    plt.title(title)

    # Fit
    p0 = (2000, .1, 50)  # start with plausible values
    params, cv = curve_fit(exponential_decay, xs, ys, p0)
    a, b, c = params

    # r^2 (quality of the fit from min 0 to max fit 1)
    squared_diffs = np.square(ys - exponential_decay(xs, a, b, c))
    squared_diffsFromMean = np.square(ys - np.mean(ys))
    rSquared = 1 - np.sum(squared_diffs) / np.sum(squared_diffsFromMean)
    print(f"R² = {rSquared}")

    eq = f"Y = {round(a, 3)} * e^(-{round(b, 3)} * x) + {round(c, 3)}"

    # plot the results
    plt.plot(xs, ys, ".", label="data")
    plt.plot(xs, exponential_decay(xs, a, b, c), "--", label=f"fit: {eq}")
    plt.legend()

    plt.show()


# ------------------------------------------------------------------------------

def plot_prog_by_positions(
        corpus_name: str = "OpenScore-LiederCorpus",
        what: str = "Quiescenzas"
) -> plt:
    data = data_by_heading(ANTHOLOGY_PATH / corpus_name / (what + ".csv"))
    position_strings = [x["MEASURE"] for x in data]
    positions = []
    for i in range(len(position_strings)):
        x, y = position_strings[i].split("/")
        positions.append(100 * int(x) / int(y))

    plot_hist(
        positions,
        xlabel="Position in work (%, binned)",
        ylabel="Frequency",
        title=f"{what}_{corpus_name}",
    )


def plot_usage(
        corpus_name: str = "OpenScore-LiederCorpus",
        what: str = "Aug6",
        user_list: list | None = ["bII", "bII6", "bII64", "bII7", "bII65", "bII43", "bII2"],
        save_fig: bool = True,
        out_path: Path | None = None
) -> plt:
    """
    Plot the usage of single chords by category.
    E.g., if "what" = "Aug6",
    plots all augmented 6ths in a sub-corpus by mode (maj/min) and
    3 "Nationality" labels ignoring inversion.

    Args:
        corpus_name: one of the sub-corpora
        what: str. What chord type. Currently, "Aug6", "N6", "User" in which last case use ...
        user_list: list. Optional. A user-defined list of figures to plot (in order).
            This is ignored unless "what" is "User".
            The default provides an alternative way of plotting the Neapolitans.
        save_fig: bool. Save a copy
        out_path: Path | None. Path to write to. If None, use ANTHOLOGY_PATH / corpus_name.

    Returns: plt

    """
    minor_data = None
    major_data = None
    all_keys = None

    if what == "Aug6":
        minor_data = chord_usage.get_Aug6s(this_mode="minor", corpus_name=corpus_name)
        major_data = chord_usage.get_Aug6s(this_mode="major", corpus_name=corpus_name)
        all_keys = ("Ger", "It", "Fr")
    elif what == "N6":
        minor_data = chord_usage.get_N6s(this_mode="minor", corpus_name=corpus_name)
        major_data = chord_usage.get_N6s(this_mode="major", corpus_name=corpus_name)
        all_keys = list(minor_data.keys()) + list(major_data.keys())
    elif what == "User":
        chord_usage_dir = CODE_FOLDER / "Resources" / "chord_usage"
        minor_data = load_json(chord_usage_dir / f"minor_{corpus_name}_simple.json")
        major_data = load_json(chord_usage_dir / f"major_{corpus_name}_simple.json")
        all_keys = user_list
        pass

    for k in all_keys:
        if k not in minor_data:
            minor_data[k] = 0
        if k not in major_data:
            major_data[k] = 0

    by_mode = {"minor": tuple([round(minor_data[x], 2) for x in all_keys]),
               "major": tuple([round(major_data[x], 2) for x in all_keys])
               }
    max_val = max(list(by_mode["minor"]) + list(by_mode["major"]))

    x = np.arange(len(all_keys))
    bar_width = 0.25
    count = 0

    fig, ax = plt.subplots(layout='constrained')

    for k, v in by_mode.items():
        offset = bar_width * count
        rects = ax.bar(x + offset, v, bar_width, label=k)
        ax.bar_label(rects, padding=2)
        count += 1

    ax.set_ylabel("Frequency (%)")
    ax.set_xticks(x + bar_width / 2, all_keys)
    ax.legend(loc="upper right", ncols=2)

    ax.set_ylim(0, round(max_val, 2) + 0.04)
    ax.set_xlabel("Figure")

    if what == "Aug6":
        ax.set_xlabel('"Nationality" (any inversion)')
        ax.set_title(f'Aug 6ths in the {corpus_name.replace("_", " ")} by so-called "nationality"')

    if not out_path:
        out_path = ANTHOLOGY_PATH / corpus_name

    if save_fig:
        plt.savefig(out_path / (what + ".png"), facecolor="w", edgecolor="w", format="png")
    else:
        plt.show()

    return plt


def plot_counts(
        corpora: list | None = None,
        what: list | None = None,
        save_fig: bool = True,
        out_path: Path | None = None
) -> plt:
    """
    Plot the usage of chords and/or progressions by category.
    E.g., "what" defaults to
    ["ascending_fifths",
    "descending_fifths",
    "aufsteigender_Quintfall",
    "fallender_Quintanstieg"
    ],
    and plots the number of each appearing
    in each of the sub-corpora listed by `corpora`.

    Args:
        corpora: list of which sub-corpora
        what: list of what chord / progressions type.
        save_fig: bool. Save a copy
        out_path: Path | None. Path to write to. If None, use ANTHOLOGY_PATH.

    Returns: plt

    """
    if corpora is None:
        corpora = ["OpenScore-LiederCorpus",
                   "Keyboard_Other",
                   "Early_Choral"
                   ]
    if what is None:
        what = ["ascending_fifths",
                "descending_fifths",
                "aufsteigender_Quintfall",
                "fallender_Quintanstieg"
                ]

    import csv

    by_mode = {}
    max_val = 0
    for corpus in corpora:
        this_list = []
        for w in what:
            this_path = str(ANTHOLOGY_PATH / corpus / f"{w}.csv")
            with open(this_path) as csvfile:
                data = csv.reader(csvfile)
                row_count = sum(1 for row in data)  # sum() w generator to avoid storing whole file
            this_list.append(row_count - 1)
            if row_count > max_val:
                max_val = row_count
        by_mode[corpus] = this_list

    x = np.arange(len(what))
    bar_width = 0.25
    count = 0

    fig, ax = plt.subplots(layout='constrained')

    for k, v in by_mode.items():
        offset = bar_width * count
        rects = ax.bar(x + offset, v, bar_width, label=k)
        ax.bar_label(rects, padding=2)
        count += 1

    ax.set_ylabel("Count")
    ax.set_xlabel("Progression type")
    ax.set_xticks(x + bar_width / 2,
                  [x.split("_")[0] for x in what]  # shorthand
                  )
    ax.legend(loc="upper right", ncols=1)

    ax.set_ylim(0, round(max_val, 2) + 0.04)

    if not out_path:
        out_path = ANTHOLOGY_PATH

    if save_fig:
        plt.savefig(out_path / ("?" + ".png"), facecolor="w", edgecolor="w", format="png")
    else:
        plt.show()

    return plt


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--plot_prog_by_positions", action="store_true")
    parser.add_argument("--plot_N6_usage", action="store_true")
    parser.add_argument("--plot_Aug6_usage", action="store_true")
    parser.add_argument("--plot_counts", action="store_true")

    parser.add_argument(
        "--corpus",
        type=str,
        required=False,
        default="OpenScore-LiederCorpus",
        help="Process all cases within this sub-corpus."
    )

    parser.add_argument(
        "--what",
        type=str,
        required=False,
        default="Quiescenzas",
        help="Which of the anthology cases.")

    args = parser.parse_args()

    if args.plot_prog_by_positions:
        plot_prog_by_positions(
            corpus_name=args.corpus,
            what=args.what
        )
    elif args.plot_N6_usage:
        plot_usage(corpus_name=args.corpus, what="N6")
    elif args.plot_Aug6_usage:
        plot_usage(corpus_name=args.corpus, what="Aug6")
    elif args.plot_counts:
        plot_counts()
    else:
        parser.print_help()
