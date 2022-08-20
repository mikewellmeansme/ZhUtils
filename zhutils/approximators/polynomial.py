from numpy import poly1d, polyfit
from typing import List
from zhutils.approximators import Approximator
from zhutils.correlation import dropna


sign = lambda el: '-' if el < 0 else '+'
is_small = lambda el: abs(el) < 0.0001


class Polynomial(Approximator):
    p: poly1d

    def fit(self, x: List, y: List, **kwargs) -> None:
        x, y = dropna(x, y)
        coeffs = polyfit(x, y, **kwargs)
        self.p = poly1d(coeffs)

    def predict(self, x) -> List:
        return self.p(x)

    def get_equation(self, precision: int = 2) -> str:
        coeffs = self.coeffs
        deg = len(coeffs) - 1
        equation = ''.join(['' if is_small(coeffs[i]) else f'{sign(coeffs[i])}{abs(coeffs[i]):.{precision}f}x^{{{deg-i}}}' for i in range(deg)])
        equation += '' if is_small(coeffs[-1]) else f'{sign(coeffs[-1])}{abs(coeffs[-1]):.{precision}f}'
        equation = equation[1:] if equation.startswith('+') else equation
        equation = f'$y={equation}$'
        return equation

    @property
    def coeffs(self) -> List[float]:
        return self.p.coeffs
