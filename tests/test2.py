
import sys

import scipy.stats
sys.path.append('./src')

# test
import math
import kaxe
from random import randint, random, choice
import numpy as np
import string
import scipy.interpolate
import time
import pylab
import scipy.stats as stats
import statistics

import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def randomObject(legend=True):
    
    pointLength = randint(50, 1000)

    a = randint(-1000000,1000000)
    b = randint(-1000000,1000000)

    l = min(a, b)
    u = max(a, b)

    x = [randint(l, u) for i in range(pointLength)]
    y = [randint(l, u) for i in range(pointLength)]

    point = kaxe.Points2D(x, y)
    
    if legend:
        point.legend(str(a))
    
    return point
    

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(choice(letters) for i in range(length))


class Test:
    def argument():
        if len(sys.argv) == 1:
            Test.run()
        else:
            eval('Test.test{}()'.format(sys.argv[1]))

    def run():        
        startTime = time.time()
        kaxe.setSetting(removeInfo=True)
        count = 0
        failed = 0
        for i in dir(Test):
            if 'test' in i:
                count += 1
                print('\033[94m' + 'Running {}'.format(i) + '\033[0m')
                try:
                    now = time.time()
                    with HiddenPrints():
                        eval('Test.{}()'.format(i))
                    print('\033[92m'+ 'Ran {} successfull in {} s'.format(i, round(time.time() - now, 3)))
                except Exception as e:
                    print('\033[91m' + 'Error in test {}: {}'.format(i, e) + '\033[0m')
                    failed += 1
        print('\033[93m' + '{} tests ran in {} min [{} failed]'.format(count, round((time.time() - startTime)/60, 3), failed) + '\033[0m')

    def testTransparent3DPlot():
        plt = kaxe.Plot3D()
        
        plt.add(kaxe.Function3D(lambda x,y:0, numPoints=10))
        plt.add(kaxe.Function3D(lambda x,y:6, numPoints=10, color=kaxe.Colormaps.blue.setAlpha(150)))
        plt.add(kaxe.Function3D(lambda x,y:3, numPoints=10, color=kaxe.Colormaps.blue.setAlpha(150)))

        plt.show()


if __name__ == '__main__':
    import os
    try:
        os.mkdir('tests/images')
    except FileExistsError:
        pass
    
    Test.testTransparent3DPlot()

    # Test.testBubbles()
    # Test.testDobuleAxisPlot()
    # Test.testHistogram()
    
    # Test.argument()
