from ..core import Tool
from ..core.traits import Path


class ExampleTool(Tool):
    name = "example"
    outdir = Path(file_ok=False, exists=True).tag(config=True)
    infile = Path(file_ok=True, exists=True).tag(config=True)

    aliases = {
        ("o", "outdir"): "ExampleTool.outdir",
        ("i", "infile"): "ExampleTool.infile",
    }

    def setup(self):
        pass

    def start(self):
        print(self.outdir)


def main():
    tool = ExampleTool()
    tool.run()


if __name__ == "__main__":
    main()
