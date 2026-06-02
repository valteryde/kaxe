
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sympy import *
import kaxe
null = lambda *a, **b: 0

x_1, x_2 = symbols("x_1 x_2")

f = (x_1 + 1)**2 + (1 - x_2)**2

# min f(x) when 

g_1 = x_1 + 0.5 * x_2 - 2 # <= 0
g_2 = -x_1 + 1 # <= 0


f_lambda = lambdify([x_1, x_2], f)
g_1_lambda = lambdify([x_1, x_2], g_1)
g_2_lambda = lambdify([x_1, x_2], g_2)

plt = kaxe.Plot()
plt.add(kaxe.Contour(f_lambda))
#plt.add(kaxe.Inequality(g_1_lambda, null))
# plt.add(kaxe.Inequality(g_2_lambda, null))
plt.show()
