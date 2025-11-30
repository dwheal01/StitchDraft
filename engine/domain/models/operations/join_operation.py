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
        offset_nodes = []
        for stitch in other.node_manager.nodes:
            if stitch.type != "strand":
                # Create new node with offset fx
                offset_nodes.append(replace(stitch, fx=stitch.fx + offset))
            else:
                # Keep strand nodes as-is
                offset_nodes.append(stitch)
        
        # Replace nodes in other chart
        other.node_manager.nodes = offset_nodes
        
        # Also offset last_row_stitches
        offset_last_row = []
        for stitch in other.node_manager.last_row_stitches:
            if stitch.type != "strand":
                offset_last_row.append(replace(stitch, fx=stitch.fx + offset))
            else:
                offset_last_row.append(stitch)
        other.node_manager.last_row_stitches = offset_last_row
        
        # Merge markers
        for marker in other.marker_manager.markers_rs:
            chart.marker_manager.markers_rs.append(marker + len(chart.node_manager.last_row_stitches))
        for marker in other.marker_manager.markers_ws:
            chart.marker_manager.markers_ws.append(marker + len(chart.node_manager.last_row_stitches))
        
        # Merge nodes
        chart.node_manager.nodes.extend(other.node_manager.nodes)
        chart.node_manager.node_counter += other.node_manager.node_counter
        chart.node_manager.last_row_stitches.extend(other.node_manager.last_row_stitches)
        
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