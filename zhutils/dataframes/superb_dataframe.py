from numpy import NaN
from pandas import ( 
    DataFrame,
    Series
)
from scipy.stats import bootstrap
from typing import (
    Union,
    Callable,
    Iterable,
    Dict,
    Tuple
)

from zhutils.correlation import (
    dropna,
    get_p_value,
    dropna_pearsonr,
    dropna_spearmanr,
    print_r_anp_p,
    print_conf_interval_and_se
)


class SuperbDataFrame(DataFrame):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def corr_and_p_values(
            self,
            corr_function: Callable[[Iterable, Iterable], Tuple[float, float]] = dropna_pearsonr,
            r_decimals: int = 2,
            p_decimals: int = 3
        ) -> DataFrame:
        r"""
        Similar to DataFrame.corr(), but returns correlations between columns with their p-values.
        Cell format: '0.90\n(p=0.001)'.

        Params:
            corr_function: Function for correlation calculations (default Pearson).
                           Signature: corr_function(Iterable, Iterable) -> (float, float)
            r_decimals: Number of decimal places of the correlation coefficient
            p_decimals: Number of decimal places of the p-value
        """

        result = DataFrame(columns=self.columns)
        result = result.transpose().join(result, how='outer')

        for c1 in self.columns:
            for c2 in self.columns:
                r, p = corr_function(self[c1], self[c2])
                result[c1][c2] = print_r_anp_p(r, p, r_decimals, p_decimals)

        return result


    def bootstrap_corr(
            self,
            bootstrap_parameters: Dict,
            corr_function: Callable[[Iterable, Iterable], Tuple[float, float]] = dropna_spearmanr,
            output_function: Callable[..., Union[str, float]] = print_r_anp_p,
            r_decimals: int = 2,
            p_decimals: int = 3
        ) -> DataFrame:
        r"""
        Similar to DataFrame.corr(), but returns bootstrap correlations between columns.
        Cell format must be described in output_func.

        Params:
            bootstrap_parameters: Parameters for the scipy.stats.bootstrap()
            corr_function: Function for correlation calculations (default Pearson).
                           Signature: corr_function(Iterable, Iterable) -> (float, float)
            output_function: Function for describing the cell format (default '0.90\n(p=0.001)').
                         Signature: output_func(r, p, high, low, se, r_decimals, p_decimals) -> str|float
            r_decimals: Number of decimal places of the correlation coefficient
            p_decimals: Number of decimal places of the p-value
        """
        result = DataFrame(columns=self.columns)
        result = result.transpose().join(result, how='outer')

        def get_corr(x, y):
            return corr_function(x, y)[0]

        for c1 in self.columns:
            for c2 in self.columns:
                if c1 != c2:
                    res = bootstrap(data=(self[c1], self[c2]), statistic=get_corr,
                                    vectorized=False, paired=True, **bootstrap_parameters)
                    low, high = res.confidence_interval
                    se = res.standard_error
                    r = low + (high - low) / 2
                    n = len(dropna(self[c1], self[c2])[0])
                    p = get_p_value(r, n)

                    params = {
                        'r': r,
                        'p': p,
                        'low': low,
                        'high': high,
                        'se': se,
                        'r_decimals': r_decimals,
                        'p_decimals': p_decimals
                    }

                    result[c1][c2] = output_function(**params)
                else:
                    result[c1][c2] = NaN
        return result


    def pairwise_len(self) -> DataFrame:
        r"""
        Returns the DataFrame with lengths of pairwise overlay of columns

        Example:
            For DataFrame:
                A B C
              1 1   7
              2 2 5 8
              3   6 9
              4 4   10
            It will teturn:
                A B C
              A 3 1 3
              B 1 2 2
              C 3 2 4
              
        """
        dfcols = DataFrame(columns=self.columns)
        result = dfcols.transpose().join(dfcols, how='outer')
        for c1 in self.columns:
            for c2 in self.columns:
                result[c1][c2] = len(dropna(self[c1], self[c2])[0])
        return result
    

    def median_index(self) -> Series:
        r"""
        Returns the Series with indexes for the median elements per column
        """
        ranks = self.rank(pct=True)
        close_to_median = abs(ranks - 0.5)
        return close_to_median.idxmin()
