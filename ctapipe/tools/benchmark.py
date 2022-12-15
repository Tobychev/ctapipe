# import os

from ..core import Tool, traits

# from ..core import Provenance, Tool, ToolConfigurationError, traits


class BenchmarksTool(Tool):
    """
    Create benchmark plots and tables for different stages of the cta-pipe
    workflow.

    The resulting files are saved to a user specified root-directory
    following a fixed hierachy
    """

    name = "ctapipe-benchmark"
    description = traits.Unicode(__doc__)

    outdir = traits.Path(
        exists=True,
        directory_ok=True,
        help="The root directory in which to output results",
    ).tag(config=True)

    analysis_name = traits.Unicode(
        help="Name used when saving the benchmark output"
    ).tag(config=True)

    #    aliases = dict(outdir="Benchmarks.outdir", analysis_name="Analysis name")
    aliases = {
        ("o", "outdir"): "BenchmarksTool.outdir",
        ("n", "name"): "BenchmarksTool.analysis_name",
    }

    def setup(self):
        pass

    def start(self):
        print(self.outdir)


"""
    def setup(self):
        if self.outdir is None:
            raise ToolConfigurationError("You need to provide an --output file")

        if self.outdir.exists() and not self.overwrite:
            raise ToolConfigurationError(
                "Outputfile {self.output} already exists, use `--overwrite` to overwrite"
            )
"""


def main():
    tool = BenchmarksTool()
    tool.run()


if __name__ == "__main__":
    main()
