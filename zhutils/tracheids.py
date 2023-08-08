from pandas import (
    ExcelFile,
    DataFrame,
    concat,
    read_csv
)
from dataclasses import dataclass
from typing import Union
from zhutils.normalization import get_normalized_df


@dataclass
class Tracheids:
    name: str
    file_path: str
    trees: list

    def __post_init__(self):
        if self.file_path.endswith('.xlsx'):
            self.data = self._load_from_xlsx_()
        elif self.file_path.endswith('.csv'):
            self.data = self._load_from_csv_()

    def _load_from_xlsx_(self) -> DataFrame:

        xlsx_file = ExcelFile(self.file_path)
        
        dataframes = []

        for tree in self.trees:
            df = xlsx_file.parse(tree)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.dropna(axis=0)
            df.insert(0, 'Tree', tree)
            dataframes.append(df.rename(columns={'Год': 'Year', 'ШГК': 'TRW'}).reset_index(drop=True))

        result = concat(dataframes).reset_index(drop=True)
        result = result.astype({'Year': 'int32', '№': 'int32'})

        return result
    
    def _load_from_csv_(self) -> DataFrame:
        result = read_csv(self.file_path)
        return result

    def to_csv(self, output_path) -> None:
        self.data.to_csv(f'{output_path}{self.name}.csv', index=False)
    
    def normalize(self, to: Union[int, str] = 'mean') -> DataFrame:
        """
        Params:
            to: The number of cells to which the tracheidograms should be normalized
        """
        if isinstance(to, int):
            result = (
                self
                    .data
                    .groupby(['Tree', 'Year'])
                    .apply(get_normalized_df, to)
            )
        elif isinstance(to, str):
            # TODO: min \ max \ median \ other support?
            year_to_norm = (
                self
                    .data[['Tree', 'Year', '№']]
                    .groupby(['Tree', 'Year'])
                    .max()
                    .reset_index()
                    .groupby('Year')
                    .mean()
                    .applymap(lambda x: int(round(x)))
                    .to_dict()
                    ['№']
            )
            
            def get_conditional_normalized_df(df):
                year = df.head(1)['Year'].values[0]
                return get_normalized_df(df, year_to_norm[year])
            
            result = (
                self
                    .data
                    .groupby(['Tree', 'Year'])
                    .apply(get_conditional_normalized_df)
            )
        else:
            raise TypeError(f'Wrong type for argument {type(to)}. Expected int or str!')

        return result.reset_index().drop(columns=['level_2'])
