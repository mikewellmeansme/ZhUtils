import matplotlib.pylab as plt
from numpy import nanmean as np_nanmean
from pandas import (
    read_excel,
    DataFrame
)
from pandera import (
    Check,
    Column,
    DataFrameSchema
)
from typing import Callable, Optional
from zhutils.superb_dataframe import SuperbDataFrame


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

ComparisonFunction = Callable[[DataFrame], tuple[float, float]]


class DailyDataFrame(SuperbDataFrame):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        daily_dataframe_schema.validate(self)

    
    def moving_avg(
            self,
            columns: list,
            window: int = 7,
            nanmean: Optional[bool] = False
        ) -> DataFrame:
        r"""
        Возвращает скользящее среднее
        window : окно
        nanmean : используем nanmean для сглаживания? (тогда потеряются данные по краям)
        """
        result = self[columns]
        if nanmean:
            result = result.rolling(window=window, center=True).apply(np_nanmean)
        else:
            result = result.rolling(window=window, center=True, min_periods=1).mean()
        
        return result


    def moving_sum(
            self, 
            columns: list,
            window: int = 7
        )-> DataFrame:
        r"""
        Возвращает скользящую сумму для выбранных колонок
        window : окно
        """
        result = self[columns]
        result = self.rolling(window=window, center=True, min_periods=1).sum()
        
        return result
    

    def plot_monthly(
            self,
            temp_ylim: list = [-25, 25],
            prec_ylim: list = [0, 70]
        ) -> tuple:
        r"""
        Plot mean teperatures for all years and mean total precipitation
        """
        plt.rcParams['font.size'] = '16'
        fig, ax = plt.subplots(nrows=1, ncols=1, dpi=300, figsize=(6, 6))
        plt.subplots_adjust(top=0.95, bottom=.1, right=.89, left=.11)
        
        ax.yaxis.set_label_coords(-.08, .5)
        ax2 = ax.twinx()
        ax.set_zorder(1)  # default zorder is 0 for ax1 and ax2
        ax.patch.set_visible(False)  # prevents ax1 from hiding ax2
        ax2.patch.set_visible(True)
        mean_prec = []
        mean_temp = []

        for i in range(1, 13):
            month_df = self[self['Month'] == i]
            mean_prec.append(month_df.groupby('Year').sum()['Precipitation'].mean())
            mean_temp.append(month_df.groupby('Year').mean()['Temperature'].mean())
        
        ax.axhline(0, c='lightgrey')
        ax.plot(mean_temp, c='firebrick', linewidth=3)
        ax2.bar(range(12), mean_prec, color='royalblue', width=1)
        ax.set_xticks(range(12))
        ax.set_xticklabels(['J', 'F', 'M', 'A', 'M ', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
        ax.set_ylabel('T, °C')

        ax2.set_ylabel('P, mm')
        ax.set_ylim(temp_ylim)
        ax2.set_ylim(prec_ylim)
        ax.set_xlabel('Month')
        return fig, ax
    

    def compare_with_daily(
            self,
            other: DataFrame,
            compare_by: ComparisonFunction,
            index: str = 'Temperature',
            moving_avg_window: Optional[int] = None,
            previous_year: Optional[bool] = False
        ):

        r"""
        Params:
            other: DataFrame с которым происходит сравнение,
            compare_by: Функция сравнения (Принимает на вход DataFrame с колонкой Year),
            index: 'Temperature', или 'Precipitation'
            moving_avg_window: Окно скользящего среднего для сглаживания климатики. По-умолчанию None -- сглаживание не применяется
            previous_year: Флаг того, сравнивается ли климатика этого года или предыдущего
        """

        other_schema.validate(other)

        if moving_avg_window:
            df = self.copy()
            rolled_df = self.moving_avg(['Temperature', 'Precipitation'], moving_avg_window)
            df['Temperature'] = rolled_df['Temperature']
            df['Precipitation'] = rolled_df['Precipitation']
        else:
            df = self

        groups = df.drop(columns=['Year']).groupby(['Month', 'Day']).groups

        comparison = []

        for key in groups:
            temp_df = df.loc[groups[key]]
            if previous_year:
                temp_df['Temperature'] = temp_df['Temperature'].shift()
                temp_df['Precipitation'] = temp_df['Precipitation'].shift()

            to_compare = temp_df.merge(other, on='Year')
            stat, p_value = compare_by(to_compare, index)

            comparison.append([*key, stat, p_value])
        
        columns = {0: 'Month', 1:'Day', 2:'Stat', 3:'P-value'}
        result = DataFrame(comparison).rename(columns=columns)
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
