
import sys

sys.path.append('./src')

import kaxe

plt = kaxe.Plot()

f = lambda x,y: (x - 1) ** 2 + (y - 2) ** 2
g = lambda x,y: x + y - 3

plt.add(kaxe.Contour(f))
plt.add(kaxe.Inequality(g, lambda x,y: 0, hatch_spacing=50))
plt.show()
