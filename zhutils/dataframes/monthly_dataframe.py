
from typing import Optional
from zhutils.common import ComparisonFunction, Months
from zhutils.dataframes.superb_dataframe import SuperbDataFrame
from zhutils.dataframes.schemas import other_schema, monthly_dataframe_schema


class MonthlyDataFrame(SuperbDataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        monthly_dataframe_schema.validate(self)
    
    def compare_with(
            other: DataFrame,
            using: ComparisonFunction,
            index: str = 'Temperature',
            previous_year: Optional[bool] = False
        ) -> DataFrame:
        pass

    def to_wide(self, clim_index: str = 'Temperature') -> DataFrame:
        return self.pivot(
            index='Year',
            columns='Month',
            values=clim_index
        ).reset_index().rename(columns={month.value: month.name for month in Months})
