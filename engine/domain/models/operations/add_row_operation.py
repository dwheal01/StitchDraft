from typing import Dict, Union
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class AddRowOperation(IChartOperation):
    """Operation to add a row to the chart."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Add a new row to the pattern."""
        pattern = params.get('pattern')
        is_round = params.get('is_round', False)
        
        if pattern is None:
            raise ValueError("Pattern is required for add_row operation")
        
        if isinstance(pattern, int):
            new_row = chart.row_manager.duplicate_row(pattern)
            # For duplicate_row, consumed and produced are the same (no net change)
            consumed = len(new_row)
            produced = len(new_row)
        else:
            side = "WS" if chart.row_manager.is_wrong_side(is_round) else "RS"
            expanded = chart.pattern_parser.expand_pattern(
                pattern, 
                chart.node_manager.last_row_produced, 
                chart.row_manager.last_row_side
            )
            new_row = expanded.stitches
            consumed = expanded.consumed
            produced = expanded.produced
            markers = expanded.markers
            
            for marker in markers:
                chart.marker_manager.add_marker(side, marker, len(new_row))
                chart._notify_marker_placed(side, marker)
        
        new_row = chart.row_manager.reverse_row_if_needed(new_row, is_round)
        old_count = chart.node_manager.last_row_produced
        chart.add_nodes(new_row, side, is_round)
        
        chart.node_manager.set_last_row_produced(produced + (chart.node_manager.last_row_produced - consumed))
        
        # Record operation in stitch counter
        chart.stitch_counter.record_operation("add_row", consumed, produced)
        
        if old_count != chart.node_manager.last_row_produced:
            chart._notify_stitch_count_changed(old_count, chart.node_manager.last_row_produced)
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the add row operation."""
        errors = []
        pattern = params.get('pattern')
        
        if pattern is None:
            errors.append("Pattern is required for add_row operation")
        elif isinstance(pattern, str) and len(pattern.strip()) == 0:
            errors.append("Pattern cannot be empty")
        elif isinstance(pattern, int) and pattern < 0:
            errors.append("Row index must be non-negative")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )