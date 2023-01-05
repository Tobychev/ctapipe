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
