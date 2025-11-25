from typing import TYPE_CHECKING
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest

if TYPE_CHECKING:
    from engine.chart_section import ChartSection

class StitchCountValidator:
    """Validates stitch count consistency."""
    
    def validate_stitch_count(
        self,
        chart: 'ChartSection',
        consumed: int,
        produced: int
    ) -> ValidationResult:
        """
        Validate that a stitch operation maintains consistency.
        
        Args:
            chart: The chart section
            consumed: Number of stitches consumed
            produced: Number of stitches produced
            
        Returns:
            ValidationResult indicating if the operation is valid
        """
        errors = []
        
        # Get current stitch count
        current_count = chart.get_current_num_of_stitches()
        
        # Calculate new count
        new_count = current_count - consumed + produced
        
        # Validate that we don't consume more than available
        if consumed > current_count:
            errors.append(
                f"Cannot consume {consumed} stitches when only {current_count} are available"
            )
        
        # Validate that new count is non-negative
        if new_count < 0:
            errors.append(
                f"Operation would result in negative stitch count: {new_count}"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_consistency(self, chart: 'ChartSection') -> ValidationResult:
        """
        Validate that the chart's stitch counter matches actual stitch count.
        
        Args:
            chart: The chart section
            
        Returns:
            ValidationResult indicating if counts are consistent
        """
        errors = []
        
        # Check if chart has a stitch counter
        if not hasattr(chart, 'stitch_counter'):
            return ValidationResult(is_valid=True, errors=[])
        
        actual_count = chart.get_current_num_of_stitches()
        tracked_count = chart.stitch_counter.get_current_count()
        
        if actual_count != tracked_count:
            errors.append(
                f"Stitch count mismatch: tracked={tracked_count}, actual={actual_count}"
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )