# import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm


def plot_hist2D(
    ax,
    hist,
    xedges,
    yedges,
    xlabel,
    ylabel,
    title="",
    xscale="linear",
    yscale="linear",
    norm="log",
    cmap="viridis",
):
    """Convenience function for drawing a 2D histogram produced by numpy hisogram2D on an axis supplied by the user."""
    if norm == "log":
        norm = LogNorm(vmax=hist.max())

    xg, yg = np.meshgrid(xedges, yedges)
    ax.pcolormesh(xg, yg, hist.T, norm=norm, cmap=cmap)
    ax.set_title(title)
    ax.set_xscale(xscale)
    ax.set_xlabel(xlabel)
    ax.set_yscale(yscale)
    ax.set_ylabel(ylabel)


def plot_hist2D_as_contour(
    ax,
    hist,
    xedges,
    yedges,
    xlabel,
    ylabel,
    levels=5,
    xscale="linear",
    yscale="linear",
    norm="log",
    cmap="reds",
):
    """Convenience function for drawing a contour plot using output from numpy hisogram2D on an axis supplied by the user."""
    if norm == "log":
        norm = LogNorm(vmax=hist.max())
    xg, yg = np.meshgrid(xedges[1:], yedges[1:])
    ax.contour(xg, yg, hist.T, norm=norm, cmap=cmap, levels=levels)
    ax.set_xscale(xscale)
    ax.set_xlabel(xlabel)
    ax.set_yscale(yscale)
    ax.set_ylabel(ylabel)


def plot_histograms(
    ax,
    counts,
    bins_list,
    title,
    xlabel,
    ylabel,
    hist_labels,
    yscale="log",
    xscale="linear",
    legend=True,
    legend_loc="upper right",
    fill=False,
):
    """Function for plotting up to five histograms with same x-dimension into the same, user supplied, axis"""
    colors = ["C1", "C2", "C3", "C4", "C5"]
    if isinstance(counts, list) and (len(counts) > 5):
        raise RuntimeError(
            f"plot_histograms can only plot at most 5 histograms at once, got {len(counts)}"
        )
    if not isinstance(bins_list, list) and isinstance(counts, list):
        bins_list = len(counts) * [bins_list]
    if not isinstance(bins_list, list) and not isinstance(counts, list):
        bins_list = [bins_list]
        counts = [counts]

    for count, bins, color, label in zip(counts, bins_list, colors, hist_labels):
        ax.stairs(count, bins, fill=fill, edgecolor=color, label=label)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_yscale("log")
    if legend:
        ax.legend(loc=legend_loc)
