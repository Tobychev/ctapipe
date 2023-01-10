# import astropy.table as tab
import matplotlib.pyplot as plt
import numpy as np
from visualisers import plot_histograms

# from ..core import Provenance
from ..core import traits
from ..io import TableLoader
from .benchmark import Benchmark, BenchmarkPlot
from .plot_utils import decide_on_subplot_layout, get_cameras_in_file, signed_abs_log10

__all__ = ["DL1aIntensityBenchmark"]


class DL1aIntensityBenchmark(Benchmark):
    """
    Produce intensity benchmark plots
    """

    camera_type = traits.String(help="the type of camera").tag(config=True)

    def make_benchmarks(self):
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


class PixelNoisePlot(BenchmarkPlot):
    pass


def tel_pixel_noise_signal_plot(tels, table, bins, size_x_inch=11, size_y_inch=10):
    nx, ny = decide_on_subplot_layout(len(tels))
    fig, axs = plt.subplots(nx, ny)
    fig.set_size_inches(size_x_inch, size_y_inch)
    hists = {}
    for tel in tels:
        pixels = table[tel]["true_image"].data.flatten()
        truth = table[tel]["true_image"].data.flatten()
        noise = table[tel]["image"].data.flatten()[truth == 0]
        trans = signed_abs_log10(pixels)
        noist = signed_abs_log10(noise)
        s_count, _ = np.histogram(trans, bins=bins)
        n_count, _ = np.histogram(noist, bins=bins)
        hists[tel] = (s_count, n_count)

    for tel, ax in zip(tels, axs.ravel()):
        s_count, n_count = hists[tel]
        plot_histograms(
            ax,
            list(hists[tel]),
            bins,
            f"Telescope {tel}",
            "log10 PE",
            "Counts",
            ["Signal", "Noise"],
        )

    # TODO: make hists into a list of HistFigure filled as apropriate
    plt.tight_layout()
    return fig, hists
