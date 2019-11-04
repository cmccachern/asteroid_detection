"""
This is an example module.  Every module should have a descriptive docsting.
"""

import numpy as np

def sum_list(data):
    """
    Sum a list of numbers.

    Each function should have a short description optionally followed, optionally by
    a longer description.  Docstrings should follow the numpydoc format.  For more
    information, see the numpy docstring guide at
    https://numpydoc.readthedocs.io/en/latest/format.html.


    Parameters
    ----------
    data : list of int or float
        Numbers to be summed.

    Returns
    -------
    sum : float
        Sum of input list
    """
    return np.sum(data)
