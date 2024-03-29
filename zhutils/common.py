from pandas import DataFrame
from typing import (
    Callable,
    Iterable,
    Optional,
    Tuple,
    Union
)
from enum import Enum

ComparisonFunction = Callable[[DataFrame, str], Tuple[float, float]]
OutputFunction = Callable[..., Union[str, float]]
CorrFunction = Callable[[Iterable, Iterable], Tuple[float, float]]


class Months(Enum):
    January   = 1
    February  = 2
    March     = 3
    April     = 4
    May       = 5
    June      = 6
    July      = 7
    August    = 8
    September = 9
    October   = 10
    November  = 11
    December  = 12

    def __str__(self):
        return self.name
