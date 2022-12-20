# import matplotlib.pyplot as plt
# import numpy as np

from ..core import Component  # , traits

# from ..io import TableLoader


class DL1aIntensityBenchmark(Component):
    """
    Produce intensity benchmark plots
    """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.input = parent.input_file

    def make_plots(self):
        print(self.input)
        print("making plots")
