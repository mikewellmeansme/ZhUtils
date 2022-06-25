from pandas import (
    ExcelFile,
    DataFrame,
    concat,
    read_csv
)
from dataclasses import dataclass


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
    