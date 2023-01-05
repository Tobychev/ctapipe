import os

from ..core import Component  # , Provenance


class Benchmark(Component):
    """
    Produce intensity benchmark plots
    """

    def __init__(self, parent, input_file, analysis_dir, overwrite=False):
        super().__init__(parent=parent)
        self.input = input_file
        self.outdir = analysis_dir
        self.overwrite = overwrite

    def save_figure(self, outname, data):
        self._check_if_exist_and_handle(outname)

    def _check_if_exist_and_handle(self, fname):
        if os.path.isfile(fname) and self.overwrite:
            os.remove(fname)
        if os.path.isfile(fname):
            raise RuntimeError(f"File {fname} already exists")

    def make_plots(self):
        pass


class HistFigure(dict):
    pass
    # TODO: implement something that can hold a figure, some data, and then simply be converted to a table using the
    # __astropy_table__ interface
    """
hist = {"image":img,"truth":timg}
metad = {"image":"Distribution of maximum pixel after camera simulation",
       "truth":"Distribution of maximum pixel after before simulation",
        "bins":bins}
T = Table(hist,meta=metad)
"""
