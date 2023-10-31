
from .reg import regression
import sympy
import logging
from .math import parseMath

# for more advanced stuff please visit sympy, scipy or matplotlib

def diff(f):
    logging.info('Using sympy ({}) (https://sympy.org)'.format(sympy.__version__))
    return sympy.diff(f)

def int(f):
    logging.info('Using sympy ({}) (https://sympy.org)'.format(sympy.__version__))
    return sympy.integrate(f)

def prepEq(eqs):
    eqs = list(eqs) # make mutable
    symbols = dict({})
    for i, eq in enumerate(eqs):
        if '=' in eq: eqs[i] = eq.replace('=', '-(') + ')'
        eqs[i] = sympy.parse_expr(eq)
        symbols = {*symbols, *eqs[i].free_symbols}
    return eqs, symbols

def solve(*eqs):
    eqs, _ = prepEq(eqs)
    
    logging.info('Using sympy ({}) (https://sympy.org)'.format(sympy.__version__))
    
    return sympy.solve(eqs, dict=True)


def nsolve(*eqs, guess:dict=None):
    eqs, symbols = prepEq(eqs)

    guessList = []
    if guess is None:
        #guess = {i:0 for i in symbols}
        guessList = tuple(0 for _ in symbols)
    else:
        
        for symbol in symbolList:
            guessList.append(guessList[symbol])

    symbolList = []
    for s in symbols:
        symbolList.append(s)

    logging.info('Using sympy ({}) (https://sympy.org)'.format(sympy.__version__))
    return sympy.nsolve(eqs, symbolList, guessList, dict=True)


class math:

    regression = regression
    diff = diff
    int = int
    solve = solve
    nsolve = nsolve

    def __init__(self, script:str):
        parseMath(script)

    def __call__(self, script:str):
        parseMath(script)

