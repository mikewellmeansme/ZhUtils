from typing import List
from pandas import DataFrame


def get_normalized_list(x: List, norm: int) -> List:
    l_raw = []
    n = len(x)
    for el in x:
        l_raw.extend([el] * norm)
    l_norm = []
    for i in range(norm):
        l_norm.append(1 / n * sum([l_raw[j] for j in range(n * i, n * (i + 1))]))
    return l_norm


def get_normalized_df(df: DataFrame, norm: int) -> DataFrame:
    loc_df = df.reset_index(drop=True)
    columns = [column for column in loc_df.columns if 'D' in column or 'CWT' in column]
    result = {
        'TRW': [loc_df['TRW'][0]]*norm,
        '№': range(1, norm+1)
    }
    for column in columns:
        result[column] = get_normalized_list(loc_df[column], norm)

    return DataFrame(result)
