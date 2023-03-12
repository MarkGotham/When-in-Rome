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
from . import CODE_FOLDER
from . import data_by_heading


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

def plot_quiescenza_positions(
        corpus_name: str = "OpenScore-LiederCorpus",
) -> plt:

    base_path = CODE_FOLDER.parent / "Anthology"

    quiescenzas = data_by_heading(base_path / corpus_name / "Quiescenzas.csv")
    position_strings = [x["MEASURE"] for x in quiescenzas]
    positions = []
    for i in range(len(position_strings)):
        x, y = position_strings[i].split("/")
        positions.append(100 * int(x) / int(y))

    plot_hist(
        positions,
        xlabel="Position in work (%, binned)",
        ylabel="Frequency",
        title=f"Quiescenzas_{corpus_name}",
    )


# ------------------------------------------------------------------------------

plot_quiescenza_positions("Piano_Sonatas")
