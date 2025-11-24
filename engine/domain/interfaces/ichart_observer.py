from abc import ABC, abstractmethod
from typing import List
# Will import ChartSection and Node when available

class IChartObserver(ABC):
    @abstractmethod
    def on_stitch_count_changed(self, chart, old_count: int, new_count: int) -> None:
        pass
    
    @abstractmethod
    def on_node_added(self, chart, node) -> None:
        pass
    
    @abstractmethod
    def on_link_added(self, chart, link) -> None:
        pass
    
    @abstractmethod
    def on_row_added(self, chart, row: List[str]) -> None:
        pass
    
    @abstractmethod
    def on_marker_placed(self, chart, side: str, position: int) -> None:
        pass
    
    @abstractmethod
    def on_chart_state_changed(self, chart, event) -> None:
        pass