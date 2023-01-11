# import astropy.table as tab
import matplotlib.pyplot as plt
import numpy as np
from visualisers import plot_histograms

# from ..core import Provenance
from ..core import traits
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


class PixelNoisePlot(BenchmarkPlot):

    input_file = traits.Path(help="Input file to process").tag(config=True)

    bin_start = traits.Float(
        help="Lowest bin edge in log10 pe", default_value=-0.9
    ).tag(config=True)
    bin_stop = traits.Float(help="Higest bin edge in log10 pe", default_value=4.1).tag(
        config=True
    )
    bin_num = traits.Int(help="Number of bins to use", default_value=72).tag(
        config=True
    )
    size_x_inch = traits.Float(help="Figure length in inches", default_value=11)
    size_y_inch = traits.Float(help="Figure height in inches", default_value=10)

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

        self.data = hists
        self.bins = bins

    def layout_figures(self):
        for camera in self.cameras:
            nx, ny = decide_on_subplot_layout(len(self.tels[camera]))
            fig, axs = plt.subplots(nx, ny)
            fig.set_size_inches(self.size_x_inch, self.size_y_inch)
            hists = {tel: (s, n) for tel, s, n in self.data[camera]}
            for tel, ax in zip(self.tels[camera], axs.ravel()):
                plot_histograms(
                    ax,
                    list(hists[tel]),
                    self.bins,
                    f"Telescope {tel}",
                    "log10 PE",
                    "Counts",
                    ["Signal", "Noise"],
                )

            fig.set_layout_engine("tight")
            self.figure.append(fig)
