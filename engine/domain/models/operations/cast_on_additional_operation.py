from typing import Dict
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class CastOnAdditionalOperation(IChartOperation):
    """Operation to cast on additional stitches to extend the current chart."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Cast on additional stitches to extend the current chart."""
        count = params.get('count', 0)
        if count <= 0:
            raise ValueError("Count must be positive")
        
        last_row_stitches = chart.node_manager.get_last_row_stitches()
        if not last_row_stitches:
            raise ValueError("No stitches to cast on to")
        
        current_fy = last_row_stitches[0].fy
        side = "RS" if chart.row_manager.get_last_row_side() == "RS" else "WS"
        current_row_number = chart.get_row_num(side) - 1
        
        last_stitch = chart.find_last_stitch()
        last_fx = last_stitch.fx
        connecting_id = last_stitch.id
        spacing = chart.position_calculator.DEFAULT_SPACING
        
        old_count = chart.node_manager.get_last_row_produced()
        
        # Create new cast-on stitches positioned to the right
        # We need to append incrementally to maintain correct state for linking
        for i in range(count):
            if side == "RS":
                new_fx = last_fx + (i + 1) * spacing
            else:
                new_fx = last_fx - (i + 1) * spacing
            node = chart.node_manager.create_stitch_node("k", new_fx, current_fy, current_row_number)
            chart.node_manager.append_to_last_row_stitches([node])
            chart._notify_node_added(node)
            
            if i == 0:
                # Get updated last_row_stitches to find the second-to-last
                updated_stitches = chart.node_manager.get_last_row_stitches()
                if len(updated_stitches) >= 2:
                    last_existing_id = updated_stitches[-2].id
                    first_new_id = updated_stitches[-1].id
                    chart.link_manager.add_horizontal_link(connecting_id, first_new_id)
                    chart._notify_link_added({"source": connecting_id, "target": first_new_id})
            
            if i < count - 1:
                chart.node_manager.create_strand_node(current_row_number)
                updated_stitches = chart.node_manager.get_last_row_stitches()
                chart.chart_generator.add_horizontal_links(chart, len(updated_stitches) - 2)
        
        # Update the row representation
        updated_stitches = chart.node_manager.get_last_row_stitches()
        current_row = [stitch.type for stitch in updated_stitches]
        chart.row_manager.update_row(chart.row_manager.get_row_count() - 1, current_row)
        
        new_count = chart.node_manager.get_last_row_produced() + count
        chart.node_manager.set_last_row_produced(new_count)
        
        # Record operation in stitch counter
        chart.stitch_counter.record_operation("cast_on", 0, count)
        
        if old_count != new_count:
            chart._notify_stitch_count_changed(old_count, new_count)
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the cast on additional operation."""
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