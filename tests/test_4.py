
import sys

sys.path.append('./src')

import kaxe
import math

plt = kaxe.Plot()
plt.add(kaxe.HeatMap.fromFunction(lambda x,y: math.sin(x) * math.cos(y), numSamples=100, domain=(-10, 10, -10, 10)))
plt.show()