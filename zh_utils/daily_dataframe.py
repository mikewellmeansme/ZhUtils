from numpy import nanmean as np_nanmean
from pandas import read_excel
from pandera import (
    Check,
    Column,
    DataFrameSchema
)
from pandera.errors import SchemaError
from superb_dataframe import SuperbDataFrame


schema = DataFrameSchema({
    'Year' : Column(int),
    'Month': Column(int),
    'Day': Column(int),
    'Temperature': Column(float, checks=[Check.ge(-100), Check.le(100)]),
    'Precipitation': Column(float, checks=[Check.ge(0), Check.le(1000)]),
})


class DailyDataFrame(SuperbDataFrame):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        schema.validate(self)

    
    def moving_avg(self, columns: list, window: int = 7, nanmean: bool = False):
        r"""
        Возвращает скользящее средние для температуры
        window : окно
        nanmean : используем nanmean для сглаживания? (тогда потеряются данные по краям)
        """
        result = self[columns]
        if nanmean:
            result = result.rolling(window=window, center=True).apply(np_nanmean)
        else:
            result = result.rolling(window=window, center=True, min_periods=1).mean()
        
        return result


    def moving_sum(self,  columns: list, window: int = 7,):
        r"""
        Возвращает скользящую сумму для выбранных колонок
        window : окно
        """
        result = self[columns]
        result = self.rolling(window=window, center=True, min_periods=1).sum()
        
        return result


def daily_df_reshape(file_path: str, temp_sheet: str, prec_sheet: str) -> SuperbDataFrame:
    r"""
    Function for merging two daily tables into one SuperbDataFrame

    Params:
        file_path: Path to the xlsx file with daily climate data
        temp_sheet: Name of sheet with daily temperature data
        prec_sheet: Name of sheet with daily precipitation data
    """
    temp = read_excel(file_path, sheet_name=temp_sheet)
    prec = read_excel(file_path, sheet_name=prec_sheet)
    years = []
    months = []
    days = []
    for year in temp.drop(columns=['Month', 'Day']).columns:
        months.extend(temp['Month'])
        days.extend(temp['Day'])
        years.extend([year]*366)
    
    result = SuperbDataFrame({
        'Year': years,
        'Month': months,
        'Day': days,
        'Temperature': temp.drop(columns=['Month', 'Day']).T.values.reshape(-1),
        'Precipitation': prec.drop(columns=['Month', 'Day']).T.values.reshape(-1),
    })
    return result
