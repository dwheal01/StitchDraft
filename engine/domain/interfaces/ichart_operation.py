from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

# Forward reference to avoid circular import
if TYPE_CHECKING:
    from engine.chart_section import ChartSection

class IChartOperation(ABC):
    @abstractmethod
    def execute(self, chart: 'ChartSection', params: Dict) -> 'ChartSection':
        pass
    
    @abstractmethod
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        pass