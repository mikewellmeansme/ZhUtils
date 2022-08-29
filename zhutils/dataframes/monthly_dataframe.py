
from pandas import (
    merge,
    read_excel, 
    DataFrame
)
from pandera import (
    Column,
    DataFrameSchema
)
from typing import Callable, Optional, Tuple
from zhutils.dataframes import SuperbDataFrame

month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

monthly_dataframe_schema = DataFrameSchema({
    'Year' : Column(int),
    **{month : Column(float, nullable=True) for month in month_names}
})

other_schema = DataFrameSchema({
    'Year' : Column(int)
})

ComparisonFunction = Callable[[DataFrame], Tuple[float, float]]


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
