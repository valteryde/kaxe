"""
Unit tests for kaxe.koundTeX number formatting and plot/axis integration.
"""

from decimal import Decimal
from fractions import Fraction
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from kaxe.core.text import Text
from runner import unit


@unit()
def test_koundtex_always_returns_math_str():
    for val in [0, -0.0, 5, -5, 42, -42, 314, -314, 12345, -1000000, 0.005, -0.005]:
        out = kaxe.koundTeX(val)
        assert isinstance(out, str), (val, type(out))
        assert out.startswith("$") and out.endswith("$"), (val, out)


@unit()
def test_koundtex_zero_and_small_integers():
    assert kaxe.koundTeX(0) == "$0$"
    assert kaxe.koundTeX(0.0) == "$0$"
    assert kaxe.koundTeX(-0.0) == "$0$"
    assert kaxe.koundTeX(Decimal("-0.000")) == "$0$"
    assert kaxe.koundTeX(1) == "$1$"
    assert kaxe.koundTeX(1.0) == "$1$"
    assert kaxe.koundTeX(-5) == "$-5$"
    assert kaxe.koundTeX(500.0) == "$500$"
    assert kaxe.koundTeX(-314) == "$-314$"
    assert kaxe.koundTeX(9999) == "$9999$"
    assert kaxe.koundTeX(-9999.25) == "$-9999.25$"


@unit()
def test_koundtex_thousands_grouping():
    assert kaxe.koundTeX(10000) == "$10\\smallSpace000$"
    assert kaxe.koundTeX(-10000) == "$-10\\smallSpace000$"
    assert kaxe.koundTeX(12345) == "$12\\smallSpace345$"
    assert kaxe.koundTeX(12345.67) == "$12\\smallSpace345.67$"
    assert kaxe.koundTeX(-12345.67) == "$-12\\smallSpace345.67$"
    assert kaxe.koundTeX(99999.99999999999) == "$10^{5}$"


@unit()
def test_koundtex_scientific_notation():
    assert kaxe.koundTeX(0.01) == "$0.01$"
    assert kaxe.koundTeX(0.009999999999999998) == "$0.01$"
    assert kaxe.koundTeX(0.00999) == "$9.99\\cdot 10^{-3}$"
    assert kaxe.koundTeX(0.005) == "$5\\cdot 10^{-3}$"
    assert kaxe.koundTeX(-0.005) == "$-5\\cdot 10^{-3}$"
    assert kaxe.koundTeX(0.005252) == "$5.252\\cdot 10^{-3}$"
    assert kaxe.koundTeX(0.001) == "$10^{-3}$"
    assert kaxe.koundTeX(-0.001) == "$-10^{-3}$"
    assert kaxe.koundTeX(100000) == "$10^{5}$"
    assert kaxe.koundTeX(123456) == "$1.23456\\cdot 10^{5}$"
    assert kaxe.koundTeX(732000000) == "$7.32\\cdot 10^{8}$"
    assert kaxe.koundTeX(-1000000) == "$-10^{6}$"
    assert kaxe.koundTeX(5e-324) == "$5\\cdot 10^{-324}$"
    assert kaxe.koundTeX(10**500) == "$10^{500}$"
    assert kaxe.koundTeX(-(10**500)) == "$-10^{500}$"


@unit()
def test_koundtex_ieee754_noise_and_precision():
    assert kaxe.koundTeX(0.1 + 0.2) == "$0.3$"
    assert kaxe.koundTeX(100.1 - 100.0) == "$0.1$"
    assert kaxe.koundTeX(1.23456789, sig_figs=4) == "$1.235$"
    assert kaxe.koundTeX(1.23456789, decimals=2) == "$1.23$"
    assert kaxe.koundTeX(0.004, decimals=2) == "$0$"
    assert kaxe.koundTeX(1234, decimals=-2) == "$1200$"
    assert kaxe.koundTeX(Decimal("0.0001234500"), sig_figs=None) == "$1.2345\\cdot 10^{-4}$"


@unit()
def test_koundtex_special_values_and_types():
    assert kaxe.koundTeX(float("nan")) == "$\\text{NaN}$"
    assert kaxe.koundTeX(float("inf")) == "$∞$"
    assert kaxe.koundTeX(float("-inf")) == "$-∞$"
    assert kaxe.koundTeX(Decimal("NaN")) == "$\\text{NaN}$"
    assert kaxe.koundTeX(Decimal("Infinity")) == "$∞$"
    assert kaxe.koundTeX(Decimal("-Infinity")) == "$-∞$"

    assert kaxe.koundTeX(Fraction(1, 8)) == "$0.125$"
    assert kaxe.koundTeX(Fraction(1, 3), sig_figs=4) == "$0.3333$"
    assert kaxe.koundTeX(np.int64(-42)) == "$-42$"
    assert kaxe.koundTeX(np.float64(0.005)) == "$5\\cdot 10^{-3}$"
    assert kaxe.koundTeX(np.float32(0.1)) == "$0.1$"

    assert kaxe.koundTeX(3 + 4j) == "$3+4i$"
    assert kaxe.koundTeX(3 - 1j) == "$3-i$"
    assert kaxe.koundTeX(0 + 1j) == "$i$"
    assert kaxe.koundTeX(0 - 1j) == "$-i$"
    assert kaxe.koundTeX(5 + 0j) == "$5$"
    assert kaxe.koundTeX(np.complex128(0.005 - 0.001j)) == "$5\\cdot 10^{-3}-10^{-3}i$"

    for bad in [True, False, np.bool_(True), "123", None]:
        try:
            kaxe.koundTeX(bad)
        except TypeError:
            pass
        else:
            raise AssertionError(f"Expected TypeError for {bad!r}")


@unit()
def test_koundtex_renders_with_fondi_text():
    samples = [
        0,
        -5,
        314,
        12345.67,
        0.005,
        -0.001,
        732000000,
        float("nan"),
        float("inf"),
        float("-inf"),
        3 - 1j,
    ]
    for val in samples:
        expr = kaxe.koundTeX(val)
        t = Text(expr, 0, 0, fontSize=24)
        assert t.width > 0 and t.height > 0, (val, expr, t.width, t.height)


@unit()
def test_koundtex_plot_and_logplot_axes():
    p_small = kaxe.Plot([0, 0.005, -0.005, 0.005])
    p_small.showProgressBar = False
    p_small.printDebugInfo = False
    p_small.__bake__()
    x_texts = [m.text for m in p_small.firstAxis.markers]
    assert "$0$" in x_texts
    assert "$5\\cdot 10^{-3}$" in x_texts

    p_large = kaxe.Plot([0, 1e6, 0, 1e6])
    p_large.showProgressBar = False
    p_large.printDebugInfo = False
    p_large.__bake__()
    large_texts = [m.text for m in p_large.firstAxis.markers]
    assert "$10^{6}$" in large_texts

    p_log = kaxe.LogPlot([1, 5, 1e-3, 1e6])
    p_log.showProgressBar = False
    p_log.printDebugInfo = False
    p_log.__bake__()
    log_y_texts = [m.text for m in p_log.secondAxis.markers]
    assert "$5\\cdot 10^{-3}$" in log_y_texts
    assert "$0.01$" in log_y_texts
    assert "$10\\smallSpace000$" in log_y_texts
    assert "$10^{5}$" in log_y_texts
    assert "$5\\cdot 10^{5}$" in log_y_texts
