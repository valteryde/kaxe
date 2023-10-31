
from scipy.optimize import curve_fit
import numpy
from typing import Callable

def regression(func:Callable, x:list, y:list):
    """
    dont use math
    use e. g. numpy.power(x, 2)
    """

    params = curve_fit(func, numpy.array(x), numpy.array(y))
    return params