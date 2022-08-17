import numpy as np
from typing import List, Tuple
from zhutils.correlation import dropna


sign = lambda el: '-' if el < 0 else '+'
is_small = lambda el: abs(el) < 0.0001


def get_poly1d(x: List, y: List, deg: int) -> np.poly1d:
    """
    :param x: List of values from x-axis
    :param y: List of values from y-axis
    :param deg: Degree of polynomial to get
    :return: Polynomial fit for x and y
    """
    x, y = dropna(x, y)
    coeffs = np.polyfit(x, y, deg)
    p = np.poly1d(coeffs)
    return p


def get_equation(coeffs: List, precision: int = 2) -> str:
    """
    :param coeffs: Polynomial coefficients, highest power first
    :param precision: Number of decimals in coefficients
    :return: Equation for the Polynomial coefficients in LaTex format
    """
    deg = len(coeffs) - 1
    equation = ''.join(['' if is_small(coeffs[i]) else f'{sign(coeffs[i])}{abs(coeffs[i]):.{precision}f}x^{{{deg-i}}}' for i in range(deg)])
    equation += '' if is_small(coeffs[-1]) else f'{sign(coeffs[-1])}{abs(coeffs[-1]):.{precision}f}'
    equation = equation[1:] if equation.startswith('+') else equation
    equation = f'$y={equation}$'
    return equation
