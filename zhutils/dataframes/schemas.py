from pandera import (
    Check,
    Column,
    DataFrameSchema
)

daily_dataframe_schema = DataFrameSchema({
    'Year' : Column(int),
    'Month': Column(int),
    'Day': Column(int),
    'Temperature': Column(float, checks=[Check.ge(-100), Check.le(100)], nullable=True),
    'Precipitation': Column(float, checks=[Check.ge(0), Check.le(1000)], nullable=True),
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
