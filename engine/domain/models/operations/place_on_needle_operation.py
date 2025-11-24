from typing import Dict, List
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class PlaceOnNeedleOperation(IChartOperation):
    """Operation to place stitches back on needle."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Place stitches from hold back on needle."""
        stitches_on_hold = params.get('stitches_on_hold', [])
        join_side = params.get('join_side', 'RS')
        
        chart.node_manager.places_stitches_on_needle(stitches_on_hold)
        if join_side == "RS":
            chart.row_manager.set_last_row_side("WS")
        else:
            chart.row_manager.set_last_row_side("RS")
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the place on needle operation."""
        errors = []
        stitches_on_hold = params.get('stitches_on_hold')
        join_side = params.get('join_side')
        
        if not stitches_on_hold:
            errors.append("No stitches provided to place on needle")
        
        if join_side not in ['RS', 'WS']:
            errors.append(f"Invalid join_side: {join_side}. Must be 'RS' or 'WS'")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )