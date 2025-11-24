from typing import Dict
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class PlaceOnHoldOperation(IChartOperation):
    """Operation to place stitches on hold."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Place the unconsumed stitches on hold."""
        previous_stitches_on_hold = chart.node_manager.get_stitches_on_hold()
        chart.node_manager.set_stitches_on_hold()
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the place on hold operation."""
        # Basic validation - can be expanded
        errors = []
        if context.available_stitches <= 0:
            errors.append("No stitches available to place on hold")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )