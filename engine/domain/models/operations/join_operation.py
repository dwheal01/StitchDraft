from typing import Dict
from dataclasses import replace
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class JoinOperation(IChartOperation):
    """Operation to join two chart sections."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Join this chart section with another chart section."""
        other = params.get('other_chart')
        if not other:
            raise ValueError("No other chart provided for join operation")
        
        last_stitch_self = chart.find_last_stitch()
        new_fx = last_stitch_self.fx + chart.position_calculator.DEFAULT_SPACING
        first_stitch_other = other.find_first_stitch()
        offset = new_fx - first_stitch_other.fx
        
        # Offset all nodes in other chart (create new Node objects since dataclass is immutable)
        other_nodes = other.node_manager.get_nodes()
        offset_nodes = []
        for stitch in other_nodes:
            if stitch.type != "strand":
                # Create new node with offset fx
                offset_nodes.append(replace(stitch, fx=stitch.fx + offset))
            else:
                # Keep strand nodes as-is
                offset_nodes.append(stitch)
        
        # Replace nodes in other chart using mutator method
        other.node_manager.replace_nodes(offset_nodes)
        
        # Also offset last_row_stitches
        other_last_row = other.node_manager.get_last_row_stitches()
        offset_last_row = []
        for stitch in other_last_row:
            if stitch.type != "strand":
                offset_last_row.append(replace(stitch, fx=stitch.fx + offset))
            else:
                offset_last_row.append(stitch)
        other.node_manager.set_last_row_stitches(offset_last_row)
        
        # Merge markers using accessor methods
        chart_last_row_count = len(chart.node_manager.get_last_row_stitches())
        other_markers_rs = other.marker_manager.get_markers_rs()
        other_markers_ws = other.marker_manager.get_markers_ws()
        
        for marker in other_markers_rs:
            chart.marker_manager.add_marker_to_rs(marker + chart_last_row_count)
        for marker in other_markers_ws:
            chart.marker_manager.add_marker_to_ws(marker + chart_last_row_count)
        
        # Merge nodes using mutator methods
        chart.node_manager.extend_nodes(offset_nodes)
        chart.node_manager.increment_node_counter(other.node_manager.get_node_counter())
        chart.node_manager.append_to_last_row_stitches(offset_last_row)
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the join operation."""
        errors = []
        other = params.get('other_chart')
        
        if not other:
            errors.append("No other chart provided for join operation")
        elif not hasattr(other, 'node_manager'):
            errors.append("Invalid chart provided - missing node_manager")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )