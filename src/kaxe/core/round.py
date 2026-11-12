from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from fractions import Fraction
import math
import numbers
from typing import Optional, Tuple, Union

_SCIENTIFIC_LOW_EXP = -2   # |x| < 10^-2 (0.01) uses scientific notation
_SCIENTIFIC_HIGH_EXP = 5   # |x| >= 10^5 (100 000) uses scientific notation
_GROUPING_EXP = 4          # 10 000 <= |x| < 100 000 uses \smallSpace grouping


def forceround(n: float) -> float:
    """Round a float to 13 decimal places."""
    return round(n, 13)


def _is_bool(value) -> bool:
    return isinstance(value, bool) or type(value).__name__ == "bool_"


def _to_decimal(num, sig_figs: Optional[int]) -> Decimal:
    """Convert a real numeric value to an exact Decimal."""
    if _is_bool(num):
        raise TypeError(f"Expected a numeric value, got {type(num).__name__}")

    if isinstance(num, Decimal):
        return num

    if isinstance(num, numbers.Integral):
        return Decimal(int(num))

    if isinstance(num, Fraction):
        with localcontext() as ctx:
            ctx.prec = max(64, (sig_figs or 10) + 20)
            return Decimal(num.numerator) / Decimal(num.denominator)

    if isinstance(num, float):
        if math.isnan(num):
            return Decimal("NaN")
        if math.isinf(num):
            return Decimal("-Infinity") if num < 0 else Decimal("Infinity")
        return Decimal(str(num))

    if isinstance(num, numbers.Real):
        # Covers NumPy floats (including float16/float32/longdouble) and other Real types
        try:
            return Decimal(str(num))
        except InvalidOperation:
            f = float(num)
            if math.isnan(f):
                return Decimal("NaN")
            if math.isinf(f):
                return Decimal("-Infinity") if f < 0 else Decimal("Infinity")
            return Decimal(str(f))

    raise TypeError(f"Expected a numeric value, got {type(num).__name__}")


def _round_decimal(
    d: Decimal,
    sig_figs: Optional[int],
    decimals: Optional[int],
) -> Decimal:
    """Apply decimal-place or significant-figure rounding to a finite Decimal."""
    if not d.is_finite() or d == 0:
        return d

    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP
        if decimals is not None:
            exp_digits = abs(decimals)
            ctx.prec = max(64, len(d.as_tuple().digits) + exp_digits + 16)
            return d.quantize(Decimal(1).scaleb(-decimals))
        if sig_figs is not None:
            ctx.prec = sig_figs
            return +d
    return d


def _decimal_to_plain_str(d: Decimal) -> str:
    """Format a finite Decimal as a plain decimal string without trailing zeros."""
    with localcontext() as ctx:
        exp = d.as_tuple().exponent
        extra = abs(exp) if isinstance(exp, int) else 0
        ctx.prec = max(64, len(d.as_tuple().digits) + extra + 16)
        normalized = d.normalize()
        text = format(normalized, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _group_thousands(int_part: str) -> str:
    """Insert ``\\smallSpace`` separators every three digits from the right."""
    if len(int_part) <= 3:
        return int_part
    groups = [int_part[max(0, i - 3) : i] for i in range(len(int_part), 0, -3)]
    groups.reverse()
    return "\\smallSpace".join(groups)


def _format_magnitude(mag: Decimal) -> str:
    """Format a positive finite Decimal magnitude without its enclosing ``$...$``."""
    exp = mag.adjusted()

    if exp < _SCIENTIFIC_LOW_EXP or exp >= _SCIENTIFIC_HIGH_EXP:
        with localcontext() as ctx:
            ctx.prec = max(64, len(mag.as_tuple().digits) + 16)
            mantissa = mag.scaleb(-exp)
        mantissa_str = _decimal_to_plain_str(mantissa)
        if mantissa_str == "1":
            return f"10^{{{exp}}}"
        return f"{mantissa_str}\\cdot 10^{{{exp}}}"

    plain = _decimal_to_plain_str(mag)
    if exp == _GROUPING_EXP:
        int_part, *frac_parts = plain.split(".")
        grouped = _group_thousands(int_part)
        if frac_parts:
            return f"{grouped}.{frac_parts[0]}"
        return grouped

    return plain


def _format_real_signed(
    num,
    sig_figs: Optional[int],
    decimals: Optional[int],
) -> Tuple[str, str]:
    """Return ``(sign, unsigned_body)`` for a real value."""
    d = _to_decimal(num, sig_figs)

    if d.is_nan():
        return "", "\\text{NaN}"
    if d.is_infinite():
        return ("-" if d.is_signed() else ""), "∞"

    d = _round_decimal(d, sig_figs=sig_figs, decimals=decimals)
    if d == 0:
        return "", "0"

    sign = "-" if d.is_signed() else ""
    return sign, _format_magnitude(abs(d))


def _format_complex_body(
    num: complex,
    sig_figs: Optional[int],
    decimals: Optional[int],
) -> str:
    """Format a complex number as a LaTeX math body (without outer ``$``)."""
    re_sign, re_body = _format_real_signed(num.real, sig_figs, decimals)
    im_sign, im_body = _format_real_signed(num.imag, sig_figs, decimals)

    if im_body == "0":
        return f"{re_sign}{re_body}"

    im_term = "i" if im_body == "1" else f"{im_body}i"
    if re_body == "0":
        return f"{im_sign}{im_term}"

    op = "-" if im_sign == "-" else "+"
    return f"{re_sign}{re_body}{op}{im_term}"


def koundTeX(
    num: Union[int, float, Decimal, Fraction, complex],
    *,
    sig_figs: Optional[int] = 10,
    decimals: Optional[int] = None,
) -> str:
    """Format any number as a LaTeX math string suitable for ``fondi`` and kaxe labels.

    - Zero and ``-0.0`` return ``"$0$"``.
    - Values with ``0 < |x| < 0.01`` or ``|x| >= 100 000`` use normalized
      scientific notation (e.g. ``"$5\\cdot 10^{-3}$"``, ``"$10^{5}$"``).
    - Values with ``10 000 <= |x| < 100 000`` use ``\\smallSpace`` thousands
      separators while preserving fractional digits.
    - Non-finite values render as ``"$\\text{NaN}$"``, ``"$∞$"``, or ``"$-∞$"``.
    - IEEE-754 floating-point noise is cleaned by default via ``sig_figs=10``.

    Parameters
    ----------
    num : int | float | Decimal | Fraction | complex
        Numeric value to format.
    sig_figs : int | None, optional
        Maximum significant digits used to clean float noise when ``decimals``
        is not given. Default is ``10``. Pass ``None`` to keep all digits.
    decimals : int | None, optional
        Fixed decimal-place rounding (matching ``round(x, decimals)`` semantics).
        Overrides ``sig_figs`` when provided.

    Returns
    -------
    str
        LaTeX math string wrapped in ``$...$``, e.g. ``"$5\\cdot 10^{-3}$"``
        or ``"$314$"``.

    Examples
    --------
    >>> koundTeX(0.005)
    '$5\\cdot 10^{-3}$'
    >>> koundTeX(314)
    '$314$'
    >>> koundTeX(12345.67)
    '$12\\smallSpace345.67$'
    >>> koundTeX(732000000)
    '$7.32\\cdot 10^{8}$'
    """
    if sig_figs is not None:
        if _is_bool(sig_figs) or not isinstance(sig_figs, int):
            raise TypeError(f"sig_figs must be an int or None, got {type(sig_figs).__name__}")
        if sig_figs < 1:
            raise ValueError("sig_figs must be >= 1")

    if decimals is not None and (_is_bool(decimals) or not isinstance(decimals, int)):
        raise TypeError(f"decimals must be an int or None, got {type(decimals).__name__}")

    if not _is_bool(num) and isinstance(num, numbers.Complex) and not isinstance(num, numbers.Real):
        body = _format_complex_body(num, sig_figs, decimals)
        return f"${body}$"

    sign, body = _format_real_signed(num, sig_figs, decimals)
    return f"${sign}{body}$"
