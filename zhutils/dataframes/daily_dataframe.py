import matplotlib.pylab as plt
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter
from numpy import nanmean as np_nanmean
from pandas import (
    merge,
    read_excel, 
    DataFrame
)
from pandera import (
    Check,
    Column,
    DataFrameSchema
)
from typing import Callable, Optional
from zhutils.dataframes import SuperbDataFrame


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
            prec_ylim: list = [0, 70],
            title: str = '',
            temperature_label: str = 'T, °C',
            precipitation_label: str = 'P, mm'
        ) -> tuple:
        r"""
        Plot mean teperatures for all years and mean total precipitation
        """
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
        ax.set_ylabel(temperature_label)

        ax2.set_ylabel(precipitation_label)
        ax.set_ylim(temp_ylim)
        ax2.set_ylim(prec_ylim)
        ax.set_xlabel('Month')

        ax.set_title(title)
        
        return fig, ax
    

    def compare_with_daily(
            self,
            other: DataFrame,
            using: ComparisonFunction,
            index: str = 'Temperature',
            moving_avg_window: Optional[int] = None,
            previous_year: Optional[bool] = False
        ):

        r"""
        Params:
            other: DataFrame с которым происходит сравнение,
            using: Функция сравнения (Принимает на вход DataFrame с колонкой Year),
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
            stat, p_value = using(to_compare, index)

            comparison.append([*key, stat, p_value])
        
        columns = {0: 'Month', 1:'Day', 2:'Stat', 3:'P-value'}
        result = DataFrame(comparison).rename(columns=columns)
        return result
    

    def get_full_daily_comparison(
            self,
            other: DataFrame,
            using: ComparisonFunction,
            moving_avg_window: Optional[int] = None,
        ) -> DataFrame:
        r"""
        Возвращает DataFrame с полным сравнением климатики с other по функции using

        Params:
            other: DataFrame с которым происходит сравнение,
            using: Функция сравнения (Принимает на вход DataFrame с колонкой Year),
            moving_avg_window: Окно скользящего среднего для сглаживания климатики. По-умолчанию None -- сглаживание не применяется
        """

        temp = self.compare_with_daily(other, using, moving_avg_window=moving_avg_window)
        temp_prev = self.compare_with_daily(other, using, moving_avg_window=moving_avg_window, previous_year=True)
        prec = self.compare_with_daily(other, using, moving_avg_window=moving_avg_window, index='Precipitation')
        prec_prev = self.compare_with_daily(other, using, moving_avg_window=moving_avg_window, previous_year=True, index='Precipitation')

        temp_interim = merge(temp, temp_prev, on=['Month', 'Day'], suffixes=(' Temp', ' Temp prev'))
        prec_interim = merge(prec, prec_prev, on=['Month', 'Day'], suffixes=(' Prec', ' Prec prev'))

        result = merge(temp_interim, prec_interim, on=['Month', 'Day'])

        return result


    def plot_full_daily_comparison(
            self,
            other: DataFrame,
            using: ComparisonFunction,
            title: str,
            moving_avg_window: Optional[int] = None,
            xlim: list = [-180, 280]
        ) -> tuple:

        r"""
        Строит график подневного сравнения климатики с other по функции using

        Params:
            other: DataFrame с которым происходит сравнение,
            using: Функция сравнения (Принимает на вход DataFrame с колонкой Year),
            title: Заголовок графика
            moving_avg_window: Окно скользящего среднего для сглаживания климатики. По-умолчанию None -- сглаживание не применяется
            xlim: Пределы по оси x графика
        """

        comparison = self.get_full_daily_comparison(other, using, moving_avg_window)

        fig, ax = plt.subplots(nrows=1, ncols=1, dpi=200, figsize=(15, 3))

        ax.xaxis.set_major_locator(MonthLocator())
        ax.xaxis.set_minor_locator(MonthLocator(bymonthday=15))
        ax.xaxis.set_major_formatter(NullFormatter())
        ax.xaxis.set_minor_formatter(DateFormatter('%b'))

        x = range(1, len(comparison) + 1)
        prev_x = range(-len(comparison) + 1, 1)
        
        ax.plot(x, comparison['Stat Temp'], color='red')
        ax.plot(x, comparison['Stat Prec'], color='blue')
        ax.plot(prev_x, comparison['Stat Temp prev'], color='red', label='Temperature')
        ax.plot(prev_x, comparison['Stat Prec prev'], color='blue', label='Precipitation')

        ax.legend()
        ax.set_xlim(xlim)
        ax.set_title(title)

        return fig, ax


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
