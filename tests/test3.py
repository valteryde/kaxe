

import sys

sys.path.append('./src')

# test
import kaxe
import numpy as np

plt = kaxe.Plot([0, 4*np.pi, -1, 1])
plt.add(kaxe.Function2D(lambda x: np.sin(x)))  # main plot only

zoom = plt.zoom(2.5, 4, -0.4, -0.1, position=(5, -0.5), size=(600, 600))
zoom.add(kaxe.Points2D([3.2], [-0.2], symbol=kaxe.symbol.CIRCLE, color=(255, 0, 0, 255)))

plt.save('tests/images/zoom_inset.png')
plt.show()
