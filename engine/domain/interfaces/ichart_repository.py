from abc import ABC, abstractmethod
from typing import List
# Import will be added when data models exist
# from engine.data.models.chart_data import ChartData

class IChartRepository(ABC):
    @abstractmethod
    def save_chart(self, chart_data) -> None:
        pass
    
    @abstractmethod
    def load_chart(self, name: str):
        pass
    
    @abstractmethod
    def load_all_charts(self) -> List:
        pass
    
    @abstractmethod
    def save_charts(self, charts: List) -> None:
        pass