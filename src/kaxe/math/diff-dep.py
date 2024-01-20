
# https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html

# CHECK FOR REVERSE
def getCorrospondingParentheses(s, reverse:bool=False):
    if reverse: s.reverse()

    depth = 0
    for i, c in enumerate(s):
        depth += c == '(' * (-1)**reverse
        depth -= c == ')' * (-1)**reverse

        if depth == 0:
            break

    return i

def getCorrospondingParenthesesStr(s, i, reverse:bool=False): # DITTO
    r = getCorrospondingParentheses(s[i:], reverse)
    return s[i+1:i+r]


def getArguments(f, i):
    if f[i-1] == ')':
        a = getCorrospondingParenthesesStr(f, i+1, True)

    else:
        a = f[i-1]
            
    if f[i+1] == '(':
        b = getCorrospondingParenthesesStr(f, i+1)
            
    else:
        b = f[i+1]

    return a, b

    

# class MathFunction:
    
#     def __init__(self, name, inner):
#         self.name = name
#         self.inner = inner

#     def diff(self):
#         pass


#     def __str__(self):
#         pass

slotSymbolCount = [0,0,0]
def resetSlotSymbolCount():
    global slotSymbolCount
    slotSymbolCount = [0,0,0]


class Slot:

    def __init__(self, value, symbol):
        global slotSymbolCount

        self.value = value
        self.function = False
        print(value)

        if value == symbol:
            self.symbol = 'x' + str(slotSymbolCount[0])
            slotSymbolCount[0] += 1
        elif symbol in value:
            self.symbol = 'f' + str(slotSymbolCount[1])
            slotSymbolCount[1] += 1
            self.function = True
        else:
            self.symbol = 'a' + str(slotSymbolCount[2])
            slotSymbolCount[2] += 1

    def __repr__(self):
        return self.symbol

    def __str__(self):
        return self.__repr__()


def symbolize(f:str, symbol:str) -> list:
    resetSlotSymbolCount()
    
    pointer = 0
    l = []
    depth = 0
    for i, c in enumerate(f):
        depth += c == '('
        depth -= c == ')'

        if c in ["*", '/', '^'] and depth == 0:
            l.append(Slot(f[pointer:i], symbol))
            l.append(c)
            pointer = i

    if len(l) == 0:
        pointer = -1

    l.append(Slot(f[pointer+1:], symbol))

    return l


BASEDIFFRULES = {
    ("a0", "^", "x0"): ("(", "a0", ")", "^", "(", "x0", ")", "*", "ln", "(", "a0", ")"),
    ("a0", "*", "x0"): ("a0",),
    ("a0","/", "x0"):("-", "a0", "/", "(", "x0", "^", "2", ")"),
    ("a0",): ("",),
    ("x0",): ("1",),
    ("x0","^","a0"): ("a0", "*", "x", "^", "(", "a0", "-", "1", ")")
}

def rule(f, symbol): # +use rule
    
    orgsymb = symbolize(f, symbol)
    pattern = tuple(str(i) for i in orgsymb)
    appendix = []

    if pattern not in BASEDIFFRULES: # chain rule
        
        symb = orgsymb
        for s in symb:
            if type(s) is not Slot: continue
            
            if s.function:
                s.symbol = s.symbol.replace('f', 'x')
                appendix = ['*', '(', bdiff(join(s.value), symbol), ')']

        pattern = tuple(str(i) for i in symb)
        
    symb = [i for i in orgsymb if type(i) is Slot]

    # product rule
    if join(pattern) == 'x0*x1':
        return join(('(', diff(symb[0].value, symbol), '*', symb[1].value, '+', diff(symb[1].value, symbol), '*', symb[0].value, ')'))

    # base diff
    rule = [i for i in BASEDIFFRULES[pattern]]

    for s in symb:        
        rule = [s.value if x==s.symbol else x for x in rule]
    
    return join(["("] + rule + appendix + [")"])

    # print('->',join(rule))

    # print(pattern,rule)
    

# recursive diff
def bdiff(f, symbol, prefix:str='+'):
    
    # jeg mangler at lave tokens på de forskellige. Så vi kører ud fra en liste. Er lidt 
    # usikker på hvordan jeg skal lave funktioner som sin, da de ikke overholder normale regler.

    # parse line and addition rule for diff.
    line = []
    pointer = -1
    depth = 0
    for i,c in enumerate(f):
        depth += c == '('
        depth -= c == ')'

        if c in ['+', '-'] and depth == 0:
            sub = (f[pointer+1:i], c)
            line.append(sub)
            pointer = i

    if pointer != len(f)-1:
        line.append((f[pointer+1:], f[pointer]))

    if len(line) > 1:
        res = ''
        for f, pre in line:
            res += bdiff(f, symbol, pre)
        return prefix + res
    
    return rule(f, symbol)


def join(l):
    return ''.join(l)


def prettify(s):
    
    # remove superfluous + and -
    res = ''
    for i, c in enumerate(s):
        
        # remove double
        if s[i-1] == c and c in ['-', '+']:
            continue
            
        res += c
    
    s = res
    res = ''
    for i, c in enumerate(s):
        
        # remove + 
        if i == 0 and c == '+':
            continue

        if s[i-1] in ['(', '*'] and c == '+':
            continue
        
        res += c

    return res


def diff(s, symbol):
    return prettify(bdiff(s, symbol))

