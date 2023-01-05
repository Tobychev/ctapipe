# import astropy.table as tab
import matplotlib.pyplot as plt
import numpy as np

from ..core import Provenance
from ..io import TableLoader
from .benchmark import Benchmark
from .plot_utils import decide_on_subplot_layout

__all__ = ["DL1aIntensityBenchmark"]


class DL1aIntensityBenchmark(Benchmark):
    """
    Produce intensity benchmark plots
    """

    def make_plots(self):
        self.log.info(self.input)
        self.log.info("making plots")
        self.make_pixel_noise_signal_plot()

    def make_pixel_noise_signal_plot(self):
        tab = TableLoader(
            self.input,
            load_dl1_images=True,
            load_true_images=True,
            load_simulated=False,
        )
        tels, cams = get_cameras_in_file(self.input)
        # For performance reasons we only fetch a few thousand events
        events = tab.read_telescope_events_by_id(start=0, stop=7000)

        bins = np.linspace(-0.9, 4.1, 72)
        for camera in cams:
            outname = f"{camera}_Pixels_Noise_Signal"
            fig, hists = tel_pixel_noise_signal_plot(tels[camera], events, bins)
            self.save_figure(outname, fig, hists)
            Provenance().add_output_file(outname, role="benchmark plot")
            fig.savefig(outname)


def get_cameras_in_file(tabload):
    """
    Simple function that returns the telescope numbers and camera types present in a file
    """
    tels_here = {
        str(t): tabload.subarray.get_tel_ids(t)
        for t in tabload.subarray.telescope_types
    }
    return tels_here, tels_here.keys()


def signed_abs_log10(data):
    """Calculate log10 while handling zero an negative entries by using the expression:
    sign(x)*log10(̣|x|+1)"""
    return np.sign(data) * np.log10(np.abs(data) + 1)


def tel_pixel_noise_signal_plot(tels, table, bins, size_x_inch=11, size_y_inch=10):
    nx, ny = decide_on_subplot_layout(len(tels))
    fig, axs = plt.subplots(nx, ny)
    fig.set_size_inches(size_x_inch, size_y_inch)
    hists = {}
    for tel in tels:
        pixels = table[tel]["true_image"].data.flatten()
        truth = table[tel]["true_image"].data.flatten()
        noise = table[tel]["image"].data.flatten()[truth == 0]
        trans = np.sign(pixels) * np.log10(np.abs(pixels) + 1)
        noist = np.sign(noise) * np.log10(np.abs(noise) + 1)
        s_count, _ = np.histogram(trans, bins=bins)
        n_count, _ = np.histogram(noist, bins=bins)
        hists[tel] = (s_count, n_count)

    for tel, ax in zip(tels, axs.ravel()):
        s_count, n_count = hists[tel]
        make_pixel_noise_signal_plot_from_hists(
            ax,
            s_count,
            n_count,
            bins,
            f"Telescope {tel}",
            "log10 PE",
            "Counts",
            "Signal",
            "Noise",
        )

    # TODO: make hists into a list of HistFigure filled as apropriate
    plt.tight_layout()
    return fig, hists


def make_pixel_noise_signal_plot_from_hists(
    ax, s_count, n_count, bins, title, xlabel, ylabel, s_label, n_label
):
    ax.stairs(s_count, bins, fill=False, edgecolor="C2", label=s_label)
    ax.stairs(n_count, bins, fill=False, edgecolor="C1", label=n_label)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_yscale("log")
    ax.legend(loc="upper right")
    return ax
