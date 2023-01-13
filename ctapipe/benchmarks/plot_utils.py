import numpy as np


def decide_on_subplot_layout(num_plots):
    """Decides on subplot layout based on their number using hardcoded heuristic
    Still, try to make less than 20 plots in one call"""
    if num_plots <= 4:
        return (2, 2)
    elif num_plots <= 6:
        return (2, 3)
    elif num_plots <= 8:
        return (2, 4)
    elif num_plots == 9:
        return (3, 3)
    elif num_plots <= 12:
        return (3, 4)
    else:
        nx = 4
        ny = num_plots // nx
        return nx, ny


def get_cameras_in_table(tabload):
    """
    Simple function that returns the telescope numbers and camera types present in a file
    """
    tels_here = {
        str(t): tabload.subarray.get_tel_ids(t)
        for t in tabload.subarray.telescope_types
    }
    return tels_here, tels_here.keys()


def signed_abs_log10(data):
    """Calculate log10 while handling zero an negative entries by using the expression:
    sign(x)*log10(̣|x|+1)"""
    return np.sign(data) * np.log10(np.abs(data) + 1)


def symlogspace(start, stop, steps, lowstop=None, lowstart=None):
    return np.hstack(
        (
            -np.logspace(start, stop, steps)[::-1],
            np.zeros(1),
            np.logspace(start, stop, steps),
        )
    )
