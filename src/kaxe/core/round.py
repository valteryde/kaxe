
import math

def countZeros(s:str):
    c = 0
    for i in s:
        if i != "0":
            break
        c += 1
    return c

def forceround(n:float) -> float:
    return round(n, 13)


def koundTeX(num: float) -> str:
    """Format a number for axis labels using LaTeX-style notation.

    Small integers are returned as plain numbers. Very small or very large
    values use scientific notation. Thousands separators use ``\\smallSpace``.

    Parameters
    ----------
    num : float
        Numeric value to format.

    Returns
    -------
    str
        LaTeX math string, e.g. ``"$5*10^{-4}$"`` or ``"$314$"``.

    Examples
    --------
    >>> koundTeX(0.005)
    '$5.0*10^{-3}$'
    >>> koundTeX(314)
    '$314$'
    """
    if num == 0: return "$0$"

    if num < 100 and math.floor(int(num) - num) == math.ceil(int(num) - num):
        return int(num)

    n = abs(num)
    ori = n / num > 0

    s = ''
    if n < 0.01:
        
        c = math.floor(math.log10(n))
        s = '{}*10^<{}>'.format(forceround(n/10**(c)), c)

    elif n >= 10000:
        
        a = str(n).split('.')[0]
        l = []
        for j in range(0, len(a)):
            i = len(a) - j - 1

            if j % 3 == 0 and j > 0:
                l.append('\\smallSpace')
                #l.append('\\,')
            
            l.append(a[i])
        l.reverse()
        s = ''.join(l)

    elif n > 100000:

        c = math.floor(math.log10(n))
        s = '{}*10^<{}>'.format(forceround(n/(10**(c))), c)

    else:
        s = str(forceround(n))

    s = s.replace('<', '{').replace('>', '}')
    if not ori:
        s = '-' + s

    return '${}$'.format(s)

# koundTeX(0.005) #-> 5*10^(-4)
# koundTeX(732000000) #-> 732*10^(6)
# koundTeX(314) #-> 732*10^(6)
# koundTeX(0.005252) #-> 5*10^(-4)
