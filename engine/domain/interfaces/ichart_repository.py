from abc import ABC, abstractmethod
from typing import List
from engine.data.models.chart_data import ChartData

class IChartRepository(ABC):
    @abstractmethod
    def save_chart(self, chart_data: ChartData) -> None:
        pass
    
    @abstractmethod
    def load_chart(self, name: str) -> ChartData:
        pass
    
    @abstractmethod
    def load_all_charts(self) -> List[ChartData]:
        pass
    
    @abstractmethod
    def save_charts(self, charts: List[ChartData]) -> None:
        pass