from math import floor, log10

def fexp(f: float) -> int:
    """
    Returns the exponent of floating number
    """
    return floor(log10(abs(f))) if f != 0 else 0

def fman(f: float) -> float:
    """
    Returns the mantissa of floating number
    """
    return f / 10 ** fexp(f)
