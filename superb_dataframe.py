from numpy import NaN
from pandas import DataFrame
from scipy.stats import bootstrap

from correlation import (
    dropna,
    get_p_value,
    CORRELATION_FUNCTIONS,
    print_r_anp_p,
    print_conf_interval_and_se
)


BOOTSTRAP_OUTPUT_MODES = {
    'r_and_p_values': print_r_anp_p,
    'conf_interval_and_se': print_conf_interval_and_se
}


class SuperbDataFrame(DataFrame):

    def corr_and_p_value(self, method: str = 'pearson',
                         r_decimals: int = 2, p_decimals: int = 3) -> DataFrame:

        result = DataFrame(columns=self.columns)
        result = result.transpose().join(result, how='outer')

        get_corr = CORRELATION_FUNCTIONS.get(method)

        if not get_corr:
            raise ValueError(
                f"Method must be either 'pearson' or 'spearman'! '{method}' was supplied"
            )

        for c1 in self.columns:
            for c2 in self.columns:
                r, p = get_corr(self[c1], self[c2])
                result[c1][c2] = print_r_anp_p(r, p, r_decimals, p_decimals)

        return result

    def bootstrap_corr(self, bootstrap_parameters: dict,
                       method: str = 'spearman', output_mode: str = 'r_and_p_values',
                       r_decimals: int = 2, p_decimals: int = 3,) -> DataFrame:
        result = DataFrame(columns=self.columns)
        result = result.transpose().join(result, how='outer')

        corr_func = CORRELATION_FUNCTIONS.get(method)
        output_func = BOOTSTRAP_OUTPUT_MODES.get(output_mode)

        if not corr_func:
            raise ValueError(
                f"Method must be either 'pearson' or 'spearman'! '{method}' was supplied!"
            )

        if not output_func:
            raise ValueError(
                f"Bootstrap Mode must be either 'r_and_p_values' or 'conf_interval_and_se'!"
                f"'{output_mode}' was supplied!"
            )

        def get_corr(x, y):
            return corr_func(x, y)[0]

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

                    params = (r, p) if output_mode == 'r_and_p_values' else (low, high, se)

                    result[c1][c2] = output_func(*params, r_decimals, p_decimals)
                else:
                    result[c1][c2] = NaN
        return result
