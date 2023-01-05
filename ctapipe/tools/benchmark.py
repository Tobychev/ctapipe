# import os
# import pathlib

from ..benchmarks import DL1aIntensityBenchmark
from ..core import Tool, traits

# from ..core import Provenance, Tool, ToolConfigurationError, traits


class BenchmarkTool(Tool):
    """
    Create benchmark plots and tables for different stages of the cta-pipe
    workflow.

    The resulting files are saved to a user specified root-directory
    following a fixed hierachy
    """

    name = "ctapipe-benchmark"
    description = traits.Unicode(__doc__)

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
        help="Name used when saving the benchmark output"
    ).tag(config=True)

    overwrite = traits.Bool(
        default_value=False, help="If true, overwrite outputfile without asking"
    ).tag(config=True)

    stage = traits.Enum(
        # You'll have to run it for each stage
        ["dl1a", "dl1", "dl2a", "dl2e", "dl2sb", "dl3"],
        help="Stage of the pipeline for which to generate benchmark output",
    ).tag(config=True)

    classes = [DL1aIntensityBenchmark]

    aliases = {
        ("o", "outdir"): "BenchmarkTool.outdir",
        ("n", "name"): "BenchmarkTool.analysis_name",
        ("s", "stage"): "BenchmarkTool.stage",
        ("i", "input"): "BenchmarkTool.input_file",
        "overwrite": "BenchmarkTool.overwrite",
    }

    def start(self):
        self.log.info(self.outdir)
        self.plot_maker.make_plots()

    #        if self.result_dir.exists() and not self.overwrite:
    #            raise ToolConfigurationError(
    #                f"Result directory {self.result_dir} already exists, use `--overwrite` to overwrite"
    #            )

    def setup(self):
        self.analysis_dir = self.outdir / self.analysis_name
        self.analysis_dir.mkdir(exist_ok=True, parents=True)

        if self.stage == "dl1a":
            self.plot_maker = DL1aIntensityBenchmark(
                parent=self,
                input_file=self.input_file,
                analysis_dir=self.analysis_dir,
                overwrite=self.overwrite,
            )


def main():
    tool = BenchmarkTool()
    tool.run()


if __name__ == "__main__":
    main()
