from typing import Dict, Union
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class AddRowOperation(IChartOperation):
    """Operation to add a row to the chart."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Add a new row to the pattern."""
        chart._last_warnings = []
        pattern = params.get('pattern')
        is_round = params.get('is_round', False)
        
        if pattern is None:
            raise ValueError("Pattern is required for add_row operation")
        
        # Normalize list to single pattern (e.g. add_round(["repeat(k2, inc)"]) from main.py)
        if isinstance(pattern, list):
            pattern = pattern[0] if len(pattern) == 1 else ",".join(str(p) for p in pattern)
        
        if isinstance(pattern, int):
            new_row = chart.row_manager.duplicate_row(pattern)
            # For duplicate_row, consumed and produced are the same (no net change)
            consumed = len(new_row)
            produced = len(new_row)
        else:
            side = "WS" if chart.row_manager.is_wrong_side(is_round) else "RS"
            last_row_side = chart.row_manager.get_last_row_side() if chart.row_manager.get_row_count() > 0 else side
            # Validate pattern syntax before expansion so invalid tokens produce clear errors
            from engine.domain.models.validators.pattern_validator import PatternValidator
            pattern_context = PatternContext(
                available_stitches=chart.get_current_num_of_stitches(),
                side=side,
                markers=chart.marker_manager.get_markers(last_row_side),
                last_row_side=last_row_side,
                is_round=is_round,
            )
            validation_result = PatternValidator().validate_pattern(pattern, pattern_context)
            if not validation_result.is_valid:
                raise ValueError("; ".join(validation_result.errors))
            last_row = None
            if chart.row_manager.get_row_count() > 0:
                last_row = chart.row_manager.get_row(chart.row_manager.get_row_count() - 1)
                # Rows are stored in needle order. For work-est semantics we need the row
                # in the direction it was worked:
                # - If previous row was WS and we are on RS now, reverse it.
                # - If previous row was RS and we are on WS now, also reverse it.
                if side != last_row_side:
                    last_row = last_row[::-1]
            expanded = chart.pattern_parser.expand_pattern(
                pattern,
                chart.node_manager.get_last_row_produced(),
                side,
                last_row=last_row,
                is_round=is_round,
            )
            chart._last_warnings = list(getattr(expanded, "warnings", []) or [])
            new_row = expanded.stitches
            # In knitting, an increase needs a stitch before it; a decrease does not.
            if new_row and new_row[0] == "inc":
                raise ValueError(
                    "An increase cannot be the first stitch of a row; it requires a stitch before it."
                )
            consumed = expanded.consumed
            produced = expanded.produced
            markers = expanded.markers
            
            for marker in markers:
                chart.marker_manager.add_marker(side, marker, len(new_row))
                chart._notify_marker_placed(side, marker)
        
        # Validate stitch count after pattern expansion (only stitch counts, not pattern syntax)
        # Pattern syntax is validated by the pattern parser during expansion
        if chart.validation_chain is not None:
            from engine.data.models.validation_request import ValidationRequest

            last_row_side = chart.row_manager.get_last_row_side()
            context = PatternContext(
                available_stitches=chart.get_current_num_of_stitches(),
                side=last_row_side,
                markers=chart.marker_manager.get_markers(last_row_side),
                last_row_side=last_row_side,
                is_round=is_round
            )
            
            # Only validate stitch counts, not pattern syntax
            # Pass None for pattern to skip pattern validation
            request = ValidationRequest(
                chart=chart,
                operation="add_row",
                context=context,
                consumed=consumed,
                produced=produced,
                pattern=None  # Skip pattern syntax validation - already done by parser
            )
            validation_result = chart.validation_chain.handle(request)
            if not validation_result.is_valid:
                raise ValueError(f"Stitch count validation failed: {', '.join(validation_result.errors)}")
        
        new_row = chart.row_manager.reverse_row_if_needed(new_row, is_round)
        old_count = chart.node_manager.get_last_row_produced()
        chart.add_nodes(new_row, side, is_round)
        
        # Use update method for controlled state update
        chart.node_manager.update_last_row_produced(consumed, produced)
        new_count = chart.node_manager.get_last_row_produced()
        
        # Record operation in stitch counter
        chart.stitch_counter.record_operation("add_row", consumed, produced)
        
        if old_count != new_count:
            chart._notify_stitch_count_changed(old_count, new_count)
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the add row operation."""
        errors = []
        pattern = params.get('pattern')
        
        if pattern is None:
            errors.append("Pattern is required for add_row operation")
        elif isinstance(pattern, str) and len(pattern.strip()) == 0:
            # Allow empty patterns - they may be used for special operations like place_on_hold
            # The pattern parser will handle empty patterns appropriately
            pass
        elif isinstance(pattern, int) and pattern < 0:
            errors.append("Row index must be non-negative")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )