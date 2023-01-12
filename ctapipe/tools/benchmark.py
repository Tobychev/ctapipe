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

    stage = traits.Enum(
        # You'll have to run it for each stage
        ["dl1a", "dl1", "dl2a", "dl2e", "dl2sb", "dl3"],
        help="Stage of the pipeline for which to generate benchmark output",
    ).tag(config=True)

    classes = [DL1aIntensityBenchmark]

    aliases = {
        ("s", "stage"): "BenchmarkTool.stage",
        ("o", "outdir"): "Benchmark.outdir",
        ("n", "name"): "Benchmark.analysis_name",
        ("i", "input"): "Benchmark.input_file",
        "overwrite": "Benchmark.overwrite",
    }

    def start(self):
        self.log.info("Running benchmarks")
        self.plot_maker.make_benchmarks()

    def setup(self):

        if self.stage == "dl1a":
            self.plot_maker = DL1aIntensityBenchmark(
                parent=self,
            )


def main():
    tool = BenchmarkTool()
    tool.run()


if __name__ == "__main__":
    main()
