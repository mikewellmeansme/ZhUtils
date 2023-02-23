import numpy as np
from scipy import stats
from typing import Tuple, Iterable


def dropna_mannwhitneyu(x: Iterable, y: Iterable) -> Tuple[float, float]:
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    s, p = stats.mannwhitneyu(x, y)
    return s, p


def chi_squared_homogeneity_test(x: Iterable, y: Iterable) -> Tuple[float, float]:
    # Do different samples come from the same population?
    observations = np.array([x, y])
    row_totals = np.array([np.sum(observations, axis=1)])
    col_totals = np.array([np.sum(observations, axis=0)])
    n = np.sum(observations)
    # Calculate the expected observations
    expected = np.dot(row_totals.T, col_totals) / n
    # Calculate chi-square test statistic
    chisq, p = stats.chisquare(observations, expected)
    chisq = np.sum(chisq)
    # Degrees of freedom
    rows = observations.shape[0]
    cols = observations.shape[1]
    df = (rows - 1) * (cols - 1)
    # Convert chi-square test statistic to p-value
    p = 1 - stats.chi2.cdf(chisq, df)
    return chisq, p
