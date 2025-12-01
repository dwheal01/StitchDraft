from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.validation_results import ValidationResult
from engine.data.repositories.chart_data_validator import ChartDataValidator

class ChartDataValidationHandler(ValidationHandler):
    """Validation handler for chart data structure validation."""
    
    def __init__(self):
        super().__init__()
        self._validator = ChartDataValidator()
    
    def validate(self, request: ValidationRequest) -> ValidationResult:
        """
        Validate chart data structure.
        
        Args:
            request: The validation request
            
        Returns:
            ValidationResult indicating if data is valid
        """
        # Only validate if we have chart data
        if request.chart is None:
            return ValidationResult(is_valid=True, errors=[])
        
        # Convert chart to ChartData for validation
        from engine.data.models.chart_data import ChartData
        from engine.data.models.node import Node
        from engine.data.models.link import Link
        
        chart_data = ChartData(
            name=request.chart.name,
            nodes=[Node(id=n.id, type=n.type, row=n.row, fx=n.fx, fy=n.fy) for n in request.chart.nodes],
            links=[Link(source=l.source, target=l.target) for l in request.chart.links]
        )
        
        return self._validator.validate_chart_data(chart_data)