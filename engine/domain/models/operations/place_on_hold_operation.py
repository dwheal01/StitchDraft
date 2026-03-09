from typing import Dict
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class PlaceOnHoldOperation(IChartOperation):
    """Operation to place stitches on hold."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Place the unconsumed stitches on hold in the named slot."""
        name = params.get('name', chart.node_manager.DEFAULT_HOLD_NAME)
        previous_stitches_on_hold = chart.node_manager.get_stitches_on_hold(name)
        old_count = chart.node_manager.get_last_row_produced()
        
        # Count stitches being placed on hold BEFORE moving them (same source as set_stitches_on_hold)
        unconsumed = chart.node_manager.get_last_row_unconsumed_stitches()
        if unconsumed:
            stitches_to_hold = unconsumed
        else:
            stitches_to_hold = chart.node_manager.get_last_row_stitches()
        count_on_hold = sum(1 for stitch in stitches_to_hold if stitch.type != "bo")
        
        # Move stitches to named hold slot (this updates last_row_produced)
        chart.node_manager.set_stitches_on_hold(name)
        new_count = chart.node_manager.get_last_row_produced()
        
        # Record operation in stitch counter (consuming stitches from active count)
        chart.stitch_counter.record_operation("place_on_hold", count_on_hold, 0)
        
        if old_count != new_count:
            chart._notify_stitch_count_changed(old_count, new_count)
        
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