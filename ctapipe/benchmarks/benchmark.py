import os

from astropy.table import Table

from ..core import Component, Provenance, traits
from ..io import TableLoader


class Benchmark(Component):
    """
    Produce intensity benchmark plots
    """

    input_file = traits.Path(
        help="Location and name of input file",
        allow_none=False,
        exists=True,
        directory_ok=False,
        file_ok=True,
    ).tag(config=True)

    outdir = traits.Path(
        exists=True,
        directory_ok=True,
        help="The root directory in which to collect results",
    ).tag(config=True)

    analysis_name = traits.Unicode(
        help="Name used to separate the benchmark output"
    ).tag(config=True)

    overwrite = traits.Bool(
        default_value=False, help="If true, overwrite outputfile without asking"
    ).tag(config=True)


class BenchmarkPlot(Benchmark):
    """
    Produce intensity benchmark plots
    """

    size_x_inch = traits.Float(help="Figure length in inches", default_value=11).tag(
        config=True
    )
    size_y_inch = traits.Float(help="Figure height in inches", default_value=10).tag(
        config=True
    )
    figure_format = traits.Unicode(
        help="Format to save figure in", default_value="png"
    ).tag(config=True)

    def run(self, stage):
        self.stage = stage
        self.out_data = {"main": []}
        self.figures = None
        self.data = None
        self.prepare_data()
        self.layout_figures()
        self._get_analysis_dir()
        self._save_data()
        self._save_figures()

    def fetch_table(self, infile, dl1_images=False, true_images=False, simulated=False):
        tab = TableLoader(
            self.input_file,
            load_dl1_images=dl1_images,
            load_true_images=true_images,
            load_simulated=simulated,
        )
        Provenance().add_input_file(infile, role=f"Source file for {self.name} plot")
        return tab

    def _get_analysis_dir(self):
        self.analysis_dir = self.outdir / self.analysis_name / self.stage
        self.analysis_dir.mkdir(exist_ok=True, parents=True)

    def _check_if_exist_and_handle(self, fname):
        if os.path.isfile(fname) and self.overwrite:
            os.remove(fname)
        if os.path.isfile(fname):
            raise RuntimeError(f"File {fname} already exists")

    def _save_figures(self):
        """If the figures are saved in a dictionary, this conveys one figure should be saved per key"""
        if isinstance(self.figures, dict):
            names = [f"{self.name}_{key}" for key in self.figures.keys()]
            for name in names:
                outname = self.analysis_dir / name
                self._check_if_exist_and_handle(outname)
                fig, plot_kwd = self.figures[name]
                fig.savefig(outname, self.figure_format)
                Provenance().add_output_file(outname, role=f"{name} plot")
        else:
            outname = self.analysis_dir / self.name
            self._check_if_exist_and_handle(outname)
            fig, plot_kwd = self.figures
            fig.savefig(outname, self.figure_format)
            Provenance().add_output_file(outname, role=f"{self.name} plot")

    def _save_data(self):
        for data_key in self.out_data.keys():
            hist1d = {"name": [], "bins": [], "counts": []}
            hist2d = {"name": [], "xbins": [], "ybins": [], "counts": []}
            for data in self.out_data[data_key]:
                kind = data[0]
                if kind == "hist1d":
                    hist1d["name"] = data[1]
                    hist1d["xlabel"] = data[2]
                    hist1d["bins"] = data[3]
                    hist1d["counts"] = data[4]
                elif kind == "hist2d":
                    hist2d["name"] = data[1]
                    hist2d["xlabel"] = data[2]
                    hist2d["ylabel"] = data[3]
                    hist2d["counts"] = data[4]
                    hist2d["xbins"] = data[5]
                    hist2d["ybins"] = data[6]

            kinds = {"hist1d": hist1d, "hist2d": hist2d}
            for kind_key in kinds.keys():
                itm = kinds[kind_key]
                if len(itm["name"]):
                    data_table = Table(itm)
                    outname = (
                        self.analysis_dir / f"{self.name}_{data_key}_{kind_key}.fits"
                    )
                    data_table.write(outname, overwrite=self.overwrite)
                    Provenance().add_output_file(
                        outname, role=f"Data for {data_key} {self.name} plot"
                    )

    def book_hist1d(self, name, xlabel, bins, counts, key="main"):
        if not self.out_data.get(key):
            self.out_data[key] = []

        self.out_data[key].append(("hist1d", (name, xlabel, bins, counts)))

    def book_hist2d(self, name, xlabel, ylabel, xbins, ybins, counts, key="main"):
        if not self.out_data.get(key):
            self.out_data[key] = []

        self.out_data[key].append(
            ("hist2d", (name, xlabel, ylabel, counts, xbins, ybins))
        )
