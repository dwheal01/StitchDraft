from abc import ABC, abstractmethod
from typing import Optional
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest

class ValidationHandler(ABC):
    """Abstract base class for validation handlers (Chain of Responsibility pattern)."""
    
    def __init__(self):
        self._next_handler: Optional['ValidationHandler'] = None
    
    def set_next(self, handler: 'ValidationHandler') -> 'ValidationHandler':
        """
        Set the next handler in the chain.
        
        Args:
            handler: The next validation handler
            
        Returns:
            The handler (for chaining)
        """
        self._next_handler = handler
        return handler
    
    def handle(self, request: ValidationRequest) -> ValidationResult:
        """
        Handle the validation request, passing to next handler if current one passes.
        
        Args:
            request: The validation request
            
        Returns:
            ValidationResult from the first handler that fails, or success if all pass
        """
        result = self.validate(request)
        
        # If validation failed, return immediately
        if not result.is_valid:
            return result
        
        # If validation passed and there's a next handler, pass to it
        if self._next_handler is not None:
            return self._next_handler.handle(request)
        
        # All validations passed
        return result
    
    @abstractmethod
    def validate(self, request: ValidationRequest) -> ValidationResult:
        """
        Perform validation.
        
        Args:
            request: The validation request
            
        Returns:
            ValidationResult indicating if validation passed
        """
        pass