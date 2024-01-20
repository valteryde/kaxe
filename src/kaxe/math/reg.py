
from scipy.optimize import curve_fit
import numpy
from typing import Callable

def regression(func:Callable, x:list, y:list):
    """
    dont use math
    use e. g. numpy.power(x, 2)
    
    func: e.g: lambda x,a,b: a*x+b
    x goes first
    """

    params = curve_fit(func, numpy.array(x), numpy.array(y))
    return params
