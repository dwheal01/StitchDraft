from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.models.validators.pattern_validator import PatternValidator
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest

class PatternValidationHandler(ValidationHandler):
    """Handler for pattern validation."""
    
    def __init__(self):
        super().__init__()
        self.validator = PatternValidator()
    
    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Validate pattern if pattern and context are provided."""
        if request.pattern and request.context:
            return self.validator.validate_pattern(
                request.pattern,
                request.context
            )
        
        # If no pattern info, pass validation
        return ValidationResult(is_valid=True, errors=[])