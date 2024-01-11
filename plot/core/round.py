
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


def koundTeX(num:float) -> str:
    #num = round(num, 5)
    if num == 0: return "$0$"

    if num < 100 and math.floor(int(num) - num) == math.ceil(int(num) - num):
        return int(num)

    n = abs(num)
    ori = n / num > 0

    s = ''
    if n < 0.1:
        
        c = countZeros(str(n).split('.')[-1]) + 1
        s = '{}*10^<-{}>'.format(forceround(n*10**(c)), c)

    elif n > 1000:

        c = countZeros(reversed(str(int(n))))
        s = '{}*10^<{}>'.format(forceround(n/(10**(c))), c)

    else:
        s = str(round(n, 2))

    s = s.replace('<', '{').replace('>', '}')
    if not ori:
        s = '-' + s

    return '${}$'.format(s)

# koundTeX(0.005) #-> 5*10^(-4)
# koundTeX(732000000) #-> 732*10^(6)
# koundTeX(314) #-> 732*10^(6)
# koundTeX(0.005252) #-> 5*10^(-4)
