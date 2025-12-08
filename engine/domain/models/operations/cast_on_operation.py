from typing import Dict
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class CastOnOperation(IChartOperation):
    """Operation to cast on stitches at the start of a chart."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Cast on the specified number of stitches."""
        count = params.get('count', 0)
        if count <= 0:
            raise ValueError("Count must be positive")
        
        old_count = chart.node_manager.get_last_row_produced()
        if chart.start_side == "RS":
            chart.add_nodes(["k"] * count, "WS")
        else:
            chart.add_nodes(["k"] * count, "RS")
        chart.node_manager.set_last_row_produced(count)
        
        # Record operation in stitch counter
        chart.stitch_counter.record_operation("cast_on_start", 0, count)
        
        if old_count != count:
            chart._notify_stitch_count_changed(old_count, count)
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the cast on operation."""
        errors = []
        count = params.get('count', 0)
        
        if count <= 0:
            errors.append("Cast on count must be positive")
        if count > 1000:  # Reasonable upper limit
            errors.append("Cast on count exceeds maximum (1000)")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )