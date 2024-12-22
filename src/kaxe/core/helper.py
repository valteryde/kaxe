
import math
import numbers

# math
def intersectLines(n1, p1, n2, p2):
    """
    n1: hat vector
    p1: position
    n2: hat vector
    p2: position
    """

    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]
    a1 = n1[0]
    a2 = n2[0]
    b1 = n1[1]
    b2 = n2[1]

    #x = ((-y1 + y2)*b1*b2 - b2*a1*x1 + x2*b1*a2)/(-a1*b2 + a2*b1)
    
    try:
        x = (a1*b2*x1 - a2*b1*x2 + b1*b2*y1 - b1*b2*y2)/(a1*b2 - a2*b1)
    except ZeroDivisionError: #parrallel
        return None
    try:
        y = (n1[0]*(x-p1[0]))/(-n1[1]) + p1[1]
    except ZeroDivisionError:
        y = (n2[0]*(x-p2[0]))/(-n2[1]) + p2[1]

    return x, y


def vdiff(v1, v2):
    return [v2[i]-v1[i] for i in range(len(v1))]


def vlen(v):
    return math.sqrt(sum([i**2 for i in v]))


def vectorScalar(v, s):
    return [i*s for i in v]


def addVector(*vs):
    return [sum([vs[j][i] for j in range(len(vs))]) for i in range(len(vs[0]))]


def vectorMultipliciation(*vs):

    l = []
    for i in range(len(vs[0])):
        
        r = 1
        for n in vs:
            r *= n[i]

        l.append(r)

    return l


def angleBetweenVectors(v1, v2):
    return math.degrees(math.acos((v1[0]*v2[0]+v1[1]*v2[1])/(vlen(v1)*vlen(v2))))


# window math
def boxIntersectWithLine(box, nvector, pos):

    # special cases
    if nvector[0] == 0:
        return (box[0], pos[1]), (box[2],pos[1])

    if nvector[1] == 0:
        return (pos[0],box[1]), (pos[0],box[3])

    # general case
    p1 = intersectLines(nvector, pos, (1, 0), (box[0], 0))

    if p1[1] < box[1]:
        p1 = intersectLines(nvector, pos, (0, 1), (0, box[1]))
    elif p1[1] > box[3]:
        p1 = intersectLines(nvector, pos, (0, 1), (0, box[3]))

    p2 = intersectLines(nvector, pos, (1, 0), (box[2], 0))

    if p2[1] < box[1]:
        p2 = intersectLines(nvector, pos, (0, 1), (0, box[1]))
    elif p2[1] > box[3]:
        p2 = intersectLines(nvector, pos, (0, 1), (0, box[3]))

    return p1, p2

    # right = intersectLines(nvector, pos, (1, 0), (box[2], 0))
    
    # top = intersectLines(nvector, pos, (0, 1), (0, box[3]))
    
    # return 

def distPointLine(n, pos, point):
    c = -n[0] * pos[0] - n[1] * pos[1]

    return abs(n[0] * point[0] + n[1] * point[1] + c) / math.sqrt(n[0]**2+n[1]**2)


def halfWay(v1, v2):
    return addVector(v1, vectorScalar(vdiff(v1, v2), 1/2))



def insideBox(box, point):
    if round(point[0]) < box[0]:
        return False
    if round(point[0]) > box[2]:
        return False
    if round(point[1]) < box[1]:
        return False
    if round(point[1]) > box[3]:
        return False
    return True


def shell(a):
    def __shell__():
        return a

    return __shell__

def closeToZero(v, epsilon=0.001):
    return -epsilon < v < epsilon


def isRealNumber(x):
    if not isinstance(x, numbers.Real):
        return False
    if math.isnan(x):
        return False
    return True
