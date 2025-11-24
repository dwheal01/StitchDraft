from abc import ABC, abstractmethod
from typing import Dict
from engine.data.models.validation_result import ValidationResult
from engine.data.models.pattern_context import PatternContext
# Forward reference to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.chart_section import ChartSection

class IChartOperation(ABC):
    @abstractmethod
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        pass
    
    @abstractmethod
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        pass