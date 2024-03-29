from pandera import (
    Check,
    Column,
    DataFrameSchema
)
from zhutils.common import Months


daily_dataframe_schema = DataFrameSchema({
    'Year' : Column(int),
    'Month': Column(int),
    'Day': Column(int),
    'Temperature': Column(float, checks=[Check.ge(-100), Check.le(100)], nullable=True, required=False),
    'Precipitation': Column(float, checks=[Check.ge(0), Check.le(1000)], nullable=True, required=False),
})

monthly_long_dataframe_schema = DataFrameSchema({
    'Year' : Column(int),
    'Month': Column(int),
    'Days': Column(int, required=False),
    'Temperature': Column(float, checks=[Check.ge(-100), Check.le(100)], nullable=True, required=False),
    'Precipitation': Column(float, checks=[Check.ge(0), Check.le(10000)], nullable=True, required=False)
})

monthly_wide_dataframe_schema = DataFrameSchema({
    'Year' : Column(int),
    **{month.name : Column(nullable=True) for month in Months}
})

other_schema = DataFrameSchema({
    'Year' : Column(int)
})

comparison_schema = DataFrameSchema({
    'Month' : Column(int),
    'Day' : Column(int),
    'Stat Temp' : Column(float, nullable=True),
    'P-value Temp' : Column(float, nullable=True),
    'Stat Temp prev' : Column(float, nullable=True),
    'P-value Temp prev' : Column(float, nullable=True),
    'Stat Prec' : Column(float, nullable=True),
    'P-value Prec' : Column(float, nullable=True),
    'Stat Prec prev' : Column(float, nullable=True),
    'P-value Prec prev' : Column(float, nullable=True),
})
