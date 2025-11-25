from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.models.validators.stitch_count_validator import StitchCountValidator
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest

class StitchCountValidationHandler(ValidationHandler):
    """Handler for stitch count validation."""
    
    def __init__(self):
        super().__init__()
        self.validator = StitchCountValidator()
    
    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Validate stitch count if operation and counts are provided."""
        if request.operation and request.consumed is not None and request.produced is not None:
            return self.validator.validate_stitch_count(
                request.chart,
                request.consumed,
                request.produced
            )
        
        # If no stitch count info, pass validation
        return ValidationResult(is_valid=True, errors=[])