
from scipy.optimize import fsolve
from ..core.shapes import shapes
from ..objects.point import Points
from ..objects.equation import Equation
from ..plot import identities
import numpy
import cmath
import math

"""
The rootlocus command plots the complex roots of the equation
                        "1 + k*f(s) = 0"

as k runs over the range 
                          "r = a .. b"

 . Since 
                       "f(s) = n(s)/d(s)"

is a rational function in s, this is equivalent to tracing the paths of the complex roots of the polynomial
"""

# https://stackoverflow.com/questions/16927229/evaluating-polynomial-coefficients
# Evaluate a polynomial in reverse order using Horner's Rule,
# for example: a3*x^3+a2*x^2+a1*x+a0 = ((a3*x+a2)x+a1)x+a0
def poly(lst, x):
    total = 0
    for a in reversed(lst):
        total = total*x+a
    return total


class RootLocus:
    def __init__(self, den, num, r=[0, 10**12]):
        """
        Solving 1 + k * f(s) = 0 for k in range(r[0], r[1])
        """

        self.batch = shapes.Batch()
        
        # f(s) = n(s)/d(s)
        # 1 + k * n(s)/d(s) = 0
        # d(s) + k * n(s) = 0


        self.den = numpy.array(den)
        self.num = numpy.array(num)

        self.zeros = numpy.roots(self.num)
        self.poles = numpy.roots(self.den)
        self.points = []
        
        self.zeros = numpy.roots(num)

        self.k1 = r[0]
        self.k2 = r[1]

        self.numpoints = 50
        self.step = (self.k2 - self.k1) / self.numpoints

        # self.points = []
        # for n in range(points):
        #     k = n * step + k1

        #     roots = numpy.roots(self.den + k * self.num)
        #     self.idk.extend(roots)

        self.supports = [identities.XYPLOT]

    
    def __split__(self, a, b, r=0):
        if a < 0 or b < 0:
            return []

        if r > 100000:
            return []

        # accept
        accept = 0.001

        r1 = numpy.roots(self.den + a * self.num)
        r2 = numpy.roots(self.den + b * self.num)

        # find correlation
        foundMatch = False
        for root1 in r1:

            for root2 in r2:

                dr = root1 - root2

                if abs(numpy.real(dr)) < accept and abs(numpy.imag(dr)) < accept:
                    foundMatch = True
                    break
            
            if foundMatch:
                break
        
        if not foundMatch:
            return numpy.concatenate((self.__split__(a, a+(b-a)/2, r+1), self.__split__(a+(b-a)/2, b, r+1)))
        
        else:
            return numpy.concatenate((r1, r2))


    def finalize(self, parent):
        
        # adaptive
        # Next, the code tries to pair up the roots for adjacent values of k by choosing those closest to each other. 
        # If two sets of roots for k = k1 and k = k2
        # are not sufficiently distinguishable from one another, the algorithm will compute a new set of roots for 
        #     "k = k1/2 + k2/2"
        # The optional argument adaptive = false will turn this off.


        a =  self.__split__(self.k1, self.k2)
        for i in a:
            x, y = numpy.real(i), numpy.imag(i)
            px, py = parent.pixel(x, y)

            if not parent.inside(px, py):
                continue

            self.batch.add(shapes.Circle(px, py))


        return


        n = 0
        # iteration

        self.segments = []
        adjacentDiffrence = .05

        for n in range(0, self.numpoints):

            k = self.step * n + self.k1

            roots = numpy.roots(self.den + k * self.num)

            for root in roots:
                
                for segment in self.segments:
                    if cmath.polar(segment[-1] - root)[0] < adjacentDiffrence:
                        segment.append(root)
                        break
                
                else:    
                    self.batch.add(shapes.Circle(*parent.pixel(numpy.real(root), numpy.imag(root))))
                    self.segments.append([root])

                # if ((parent.windowAxis[0] <= numpy.real(root) <= parent.windowAxis[1]) and 
                #     (parent.windowAxis[2] <= numpy.imag(root) <= parent.windowAxis[3])
                #     ):
     
        # segment
        for segment in self.segments:
            
            # for root in segment:
            #     self.batch.add(shapes.Circle(*parent.pixel(numpy.real(root), numpy.imag(root))))

            points = Points([numpy.real(i) for i in segment], [numpy.imag(i) for i in segment])
            parent.add(points)

        poles = Points([numpy.real(i) for i in self.poles], [numpy.imag(i) for i in self.poles]).legend('Poles')
        zeros = Points([numpy.real(i) for i in self.zeros], [numpy.imag(i) for i in self.zeros]).legend('Zeros')

        # parent.add(poles)
        # parent.add(zeros)
        
    
    def draw(self, *args, **kwargs):
        self.batch.draw(*args, **kwargs)

    def push(self, x, y):
        self.batch.push(x, y)


    # def legend(self, text:str):
    #     return
    #     self.legendText = text
    #     return self
    
