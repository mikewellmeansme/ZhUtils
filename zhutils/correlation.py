from typing import (
    Union,
    Callable,
    Iterable
)

from numpy import (
    array,
    isnan,
    logical_or,
    sqrt
)
from scipy.stats import (
    pearsonr,
    spearmanr,
    t
)


def dropna(x: Iterable, y: Iterable) -> tuple[array, array]:
    x, y = array(x), array(y)
    nas = logical_or(isnan(x), isnan(y))
    x, y = x[~nas], y[~nas]
    return x, y


def dropna_pearsonr(x: Iterable, y: Iterable) -> tuple[float, float]:
    x, y = dropna(x, y)
    r, p = pearsonr(x, y)
    return r, p


def dropna_spearmanr(x: Iterable, y: Iterable) -> tuple[float, float]:
    x, y = dropna(x, y)
    r, p = spearmanr(x, y)
    return r, p


def get_t_stat(r: float, n: int) -> float:
    return (r * sqrt(n - 2)) / (sqrt(1 - r ** 2))


def get_p_value(r: float, n: int) -> float:
    r = abs(r)
    t_stat = get_t_stat(r, n)
    return t.sf(t_stat, n-2)*2


def print_r_anp_p(r: float, p: float,
                  r_decimals: int = 2, p_decimals: int = 3, **kwargs) -> str:
    return f"{r:.{r_decimals}f}\n(p={p:.{p_decimals}f})"


def print_conf_interval_and_se(low: float, high: float, se: float,
                               r_decimals: int = 2, se_decimals: int = 3, **kwargs) -> str:
    return f"[{low:.{r_decimals}f}; {high:.{r_decimals}f}]\n(se={se:.{se_decimals}f})"
