from numpy import isnan
from scipy.stats import mannwhitneyu
from typing import Tuple, Iterable


def dropna_mannwhitneyu(x: Iterable, y: Iterable) -> Tuple[float, float]:
    x = x[~isnan(x)]
    y = y[~isnan(y)]
    s, p = mannwhitneyu(x, y)
    return s, p
