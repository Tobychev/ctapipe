# import astropy.table as tab
import matplotlib.pyplot as plt
import numpy as np

# from ..core import Provenance
from ..core import traits
from .benchmark import Benchmark, BenchmarkPlot
from .plot_utils import (
    decide_on_subplot_layout,
    get_cameras_in_file,
    signed_abs_log10,
    symlogspace,
)
from .visualisers import plot_hist2D, plot_histograms

__all__ = ["DL1aIntensityBenchmark"]


class DL1aIntensityBenchmark(Benchmark):
    """
    Produce intensity benchmark plots
    """

    camera_type = traits.Unicode(help="the type of camera").tag(config=True)

    def __init__(self, parent=None, config=None, **kwargs):
        super().__init__(parent=parent, config=config, **kwargs)
        self.plots = []
        self.plots.append(PixelNoisePlot(parent=self))
        self.plots.append(ChargeResolutionPlot(parent=self))

    def make_benchmarks(self):
        self.log.info(self.input_file)
        self.log.info("making plots")
        for plot in self.plots:
            plot.run(stage="dl1a")


class PixelNoisePlot(BenchmarkPlot):
    name = "PixelNoisePlot"

    bin_start = traits.Float(
        help="Lowest bin edge in log10 pe", default_value=-0.9
    ).tag(config=True)
    bin_stop = traits.Float(help="Higest bin edge in log10 pe", default_value=4.1).tag(
        config=True
    )
    bin_num = traits.Int(help="Number of bins to use", default_value=72).tag(
        config=True
    )

    def prepare_data(self):
        tab = self.fetch_table(self.input_file, dl1_images=True, true_images=True)
        tels, cams = get_cameras_in_file(self.input_file)
        self.tels = tels
        self.cameras = cams
        # For performance reasons we only fetch a few thousand events
        events = tab.read_telescope_events_by_id(start=0, stop=7000)

        bins = np.linspace(self.bin_start, self.bin_stop, self.bin_num)
        hists = {}

        for camera in cams:
            hists[camera] = []
            for tel in tels[camera]:
                pixels = events[tel]["true_image"].data.flatten()
                truth = events[tel]["true_image"].data.flatten()
                noise = events[tel]["image"].data.flatten()[truth == 0]
                trans = signed_abs_log10(pixels)
                noist = signed_abs_log10(noise)
                s_count, _ = np.histogram(trans, bins=bins)
                n_count, _ = np.histogram(noist, bins=bins)
                hists[camera].append((tel, s_count, n_count))
                self.book_hist1d(
                    "signal", "log10 PE", bins, s_count, key=f"{camera} tel {tel}"
                )
                self.book_hist1d(
                    "noise", "log10 PE", bins, n_count, key=f"{camera} tel {tel}"
                )

        self.data = hists
        self.bins = bins

    def layout_figures(self):
        self.figures = {}
        for camera in self.cameras:
            nx, ny = decide_on_subplot_layout(len(self.tels[camera]))
            fig, axs = plt.subplots(nx, ny)
            fig.set_size_inches(self.size_x_inch, self.size_y_inch)
            hists = {tel: (s, n) for tel, s, n in self.data[camera]}
            for tel, ax in zip(self.tels[camera], axs.ravel()):
                plot_kwd = {
                    "norm": "log",
                    "cmap": "viridis",
                    "xlabel": "log10 PE",
                    "ylabel": "Counts",
                    "hist_labels": ["Signal", "Noise"],
                    "title": f"Telescope {tel}",
                }
                plot_histograms(ax, list(hists[tel]), self.bins, **plot_kwd)

            fig.set_layout_engine("tight")
            self.figures[camera] = (fig, plot_kwd)


class ChargeResolutionPlot(BenchmarkPlot):
    name = "ChargeResolution"

    x_bin_start = traits.Float(help="Lowest bin edge in log10 pe", default_value=0).tag(
        config=True
    )
    x_bin_stop = traits.Float(
        help="Higest bin edge in log10 pe", default_value=4.5
    ).tag(config=True)
    x_bin_num = traits.Int(help="Number of bins to use", default_value=80).tag(
        config=True
    )
    y_bin_start = traits.Float(
        help="Lowest bin edge in log10 pe", default_value=-0.7
    ).tag(config=True)
    y_bin_stop = traits.Float(help="Higest bin edge in log10 pe", default_value=2).tag(
        config=True
    )
    y_bin_num = traits.Int(help="Number of bins to use", default_value=60).tag(
        config=True
    )

    def prepare_data(self):
        tab = self.fetch_table(self.input_file, dl1_images=True, true_images=True)
        events = tab.read_telescope_events(start=0, stop=8000)

        x_bin_edges_counts = np.logspace(
            self.x_bin_start, self.x_bin_stop, self.x_bin_num
        )
        y_bin_edges_counts = symlogspace(
            self.y_bin_start, self.y_bin_stop, self.y_bin_num
        )

        bins = (x_bin_edges_counts, y_bin_edges_counts)

        X = events["true_image"].data.flatten()
        Y = events["image"].data.flatten()
        mask = X > 0
        reldif = Y[mask] / X[mask]
        self.data = np.histogram2d(X[mask], reldif, bins=bins)

        self.book_hist2d("charge resolution", "True PE", "Reco/Truth", *self.data)

    def layout_figures(self):
        fig, axs = plt.subplots(figsize=(self.size_x_inch, self.size_y_inch))
        H, xedges, yedges = self.data
        plot_kwd = {
            "xscale": "symlog",
            "yscale": "symlog",
            "norm": "log",
            "cmap": "viridis",
            "xlabel": "True PE",
            "ylabel": "Reco/Truth",
        }
        plot_hist2D(axs, H, xedges, yedges, **plot_kwd)
        self.figures = (fig, plot_kwd)
