from typing import List, Protocol


class Approximator(Protocol):

    def fit(self, x: List, y: List, **kwargs) -> None:
        ...

    def predict(self, x) -> List:
        ...


    def get_equation(self, precision: int) -> str:
        ...

    @property
    def coeffs(self) -> List[float]:
        ...
