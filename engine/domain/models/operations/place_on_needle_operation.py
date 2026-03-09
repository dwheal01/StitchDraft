from typing import Dict, List
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class PlaceOnNeedleOperation(IChartOperation):
    """Operation to place stitches back on needle."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Place stitches from the named hold slot back on needle. Optionally insert cast_on_between new stitches between current needle and hold."""
        from_hold = params.get('from_hold', chart.node_manager.DEFAULT_HOLD_NAME)
        join_side = params.get('join_side', 'RS')
        cast_on_between = params.get('cast_on_between', 0) or 0
        stitches_on_hold = params.get('stitches_on_hold')
        if stitches_on_hold is None:
            stitches_on_hold = chart.node_manager.get_stitches_on_hold(from_hold)
        if not stitches_on_hold:
            raise ValueError(f"No stitches in hold '{from_hold}'")
        
        old_count = chart.node_manager.get_last_row_produced()
        count_from_hold = sum(1 for stitch in stitches_on_hold if stitch.type != "bo")
        first_hold_id = stitches_on_hold[0].id if stitches_on_hold else None

        if cast_on_between > 0:
            last_row_stitches = chart.node_manager.get_last_row_stitches()
            if not last_row_stitches:
                raise ValueError("No stitches on needle to cast on between")
            # Connect from the end of the current needle (where we append hold)
            last_stitch = last_row_stitches[-1]
            current_fy = last_row_stitches[0].fy
            side = join_side  # position new co in same direction as join
            current_row_number = chart.get_row_num(side) - 1
            last_fx = last_stitch.fx
            connecting_id = last_stitch.id
            spacing = chart.position_calculator.DEFAULT_SPACING
            new_nodes = []
            for i in range(cast_on_between):
                if side == "RS":
                    new_fx = last_fx + (i + 1) * spacing
                else:
                    new_fx = last_fx - (i + 1) * spacing
                node = chart.node_manager.create_stitch_node("co", new_fx, current_fy, current_row_number)
                new_nodes.append(node)
                chart.node_manager.append_to_last_row_stitches([node])
                chart._notify_node_added(node)
            if new_nodes:
                chart.link_manager.add_horizontal_link(connecting_id, new_nodes[0].id)
                chart._notify_link_added({"source": connecting_id, "target": new_nodes[0].id})
                for j in range(len(new_nodes) - 1):
                    chart.link_manager.add_horizontal_link(new_nodes[j].id, new_nodes[j + 1].id)
                    chart._notify_link_added({"source": new_nodes[j].id, "target": new_nodes[j + 1].id})
                if first_hold_id:
                    chart.link_manager.add_horizontal_link(new_nodes[-1].id, first_hold_id)
                    chart._notify_link_added({"source": new_nodes[-1].id, "target": first_hold_id})

        chart.node_manager.places_stitches_on_needle(stitches_on_hold, from_hold_name=from_hold)
        new_count = chart.node_manager.get_last_row_produced()

        if join_side == "RS":
            chart.row_manager.set_last_row_side("WS")
        else:
            chart.row_manager.set_last_row_side("RS")

        chart.stitch_counter.record_operation("place_on_needle", 0, count_from_hold + cast_on_between)

        if old_count != new_count:
            chart._notify_stitch_count_changed(old_count, new_count)

        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the place on needle operation."""
        errors = []
        join_side = params.get('join_side')
        cast_on_between = params.get('cast_on_between', 0) or 0
        # stitches_on_hold may be resolved at execute time from from_hold
        stitches_on_hold = params.get('stitches_on_hold')
        from_hold = params.get('from_hold')
        if stitches_on_hold is None and from_hold is None:
            errors.append("No stitches provided to place on needle (need stitches_on_hold or from_hold)")
        
        if join_side not in ['RS', 'WS']:
            errors.append(f"Invalid join_side: {join_side}. Must be 'RS' or 'WS'")
        
        if cast_on_between < 0 or cast_on_between > 1000:
            errors.append("cast_on_between must be between 0 and 1000")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )