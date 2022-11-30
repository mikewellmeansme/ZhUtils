import pandas as pd

from typing import Optional, List, Union
from zhutils.common import ComparisonFunction, Months
from zhutils.dataframes.errors import FileExtentionError
from zhutils.dataframes.superb_dataframe import SuperbDataFrame
from zhutils.dataframes.schemas import (
    other_schema,
    monthly_long_dataframe_schema,
    monthly_wide_dataframe_schema
)


class MonthlyDataFrame(SuperbDataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        monthly_long_dataframe_schema.validate(self)
    
    @classmethod
    def from_wide(
            cls,
            paths: List[Union[str, pd.DataFrame]],
            clim_indexes: List[str],
            sheet_names: Optional[List[Union[int, str]]]=None
        ):
        """
        Creates a MonthlyDataFrame from multiple wide tables (csv, xls, xlsx, pd.DataFrame)

        Params:
            paths: Paths to the wide table files or wide DataFrames
            clim_indexes: Names of climate index contained in each file
            sheet_names: Only for xls / xlsx files. Names of sheets with wide tables
        """

        sheet_names = [0] * len(paths) or sheet_names
        if not (len(paths) == len(clim_indexes) == len(sheet_names)):
            raise ValueError(
                "Lengths of paths, clim_indexes and sheet_names lists must be the same!"
            )

        long_dfs = []

        for path, clim_index, sheet_name in zip(paths, clim_indexes, sheet_names): 
            if isinstance(path, pd.DataFrame):
                wide_df = path
            else:
                if path.endswith('.csv'):
                    wide_df = pd.read_csv(path)
                elif path.endswith('.xls') or path.endswith('.xlsx'):
                    wide_df = pd.read_excel(path, sheet_name)
                else:
                    raise FileExtentionError(
                        f"""Wrong file extention for wide monthly dataframe! 
                        Expected CSV, XLS or XLSX, 
                        got {path}"""
                    )
            
            monthly_wide_dataframe_schema.validate(wide_df)

            long_df = wide_df.melt(id_vars='Year', value_name=clim_index, var_name='Month')
            long_df['Month'] = long_df['Month'].apply(lambda month: Months[month].value)
            long_df = long_df.set_index(['Year', 'Month'])

            long_dfs.append(long_df)
        
        result = pd.concat(long_dfs, axis=1, join='outer').sort_index().reset_index()
        
        return MonthlyDataFrame(result)
    
    def compare_with(
            other: pd.DataFrame,
            using: ComparisonFunction,
            index: str = 'Temperature',
            previous_year: Optional[bool] = False
        ) -> pd.DataFrame:
        other_schema.validate(other)
        pass

    def to_wide(self, clim_index: str = 'Temperature') -> pd.DataFrame:
        return self.pivot(
            index='Year',
            columns='Month',
            values=clim_index
        ).reset_index().rename(columns={month.value: month.name for month in Months})
