import os

import numpy as np
from astropy.table import Table

from ..core import Component, Provenance


class Benchmark(Component):
    """
    Produce intensity benchmark plots
    """

    def __init__(self, parent, input_file, analysis_dir, overwrite=False):
        super().__init__(parent=parent)
        self.input = input_file
        self.outdir = analysis_dir
        self.overwrite = overwrite

    def save_figure(self, outname, figure, figure_data):
        self._check_if_exist_and_handle(outname)
        Provenance().add_output_file(outname, role="benchmark plot")
        # fig.savefig(outname)

    def _check_if_exist_and_handle(self, fname):
        if os.path.isfile(fname) and self.overwrite:
            os.remove(fname)
        if os.path.isfile(fname):
            raise RuntimeError(f"File {fname} already exists")

    def make_benchmarks(self):
        pass


class BenchmarkPlot:
    def __init__(self, name, xlabel, ylabel, description=""):
        self.name = name
        self.description = description
        self.xlabel = xlabel
        self.ylabel = ylabel

    def make_plot(self):
        self.prepare_data()
        self.prepare_display()
        return self.make_figure()

    def make_data_container(self, type):
        # Here we call the apropriate figure data container and set its properties
        pass


class HistFigureData:
    """Simple container to hold a number of histograms with common binning used to make a figure, metadata about each histogram, and facilities to serialise to and from an astropy table"""

    def __init__(self, fig=None, bins=None, hist_dic=None, meta_dic=None):
        self.bins = bins
        self.hists = hist_dic
        self.meta = meta_dic

    def to_table(self):
        """
        Return an astropy Table containing the bincounts and the bin edges.
        The bincounts are padded with an extra -1 to equalize lengths.
        """
        hist_names = self.hists.keys()
        self.hists["bins"] = self.bins
        for name in hist_names:
            h = np.zeros_like(self.bins)
            h[-1] = -1
            self.hists[name] = h.copy()
        return Table(meta=self.meta)

    def from_table(self, table):
        # TODO: decide if this is really a useful thing to have
        pass
