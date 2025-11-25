from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.models.validators.order_validator import OrderValidator
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest

class OrderValidationHandler(ValidationHandler):
    """Handler for order and link integrity validation."""
    
    def __init__(self):
        super().__init__()
        self.validator = OrderValidator()
    
    def validate(self, request: ValidationRequest) -> ValidationResult:
        """Validate order and link integrity if nodes and links are provided."""
        if request.nodes is not None and request.links is not None:
            # Validate link integrity first
            link_result = self.validator.validate_link_integrity(
                request.links,
                request.nodes
            )
            if not link_result.is_valid:
                return link_result
            
            # Then validate order
            return self.validator.validate_order(request.nodes, request.links)
        
        # If no nodes/links info, pass validation
        return ValidationResult(is_valid=True, errors=[])