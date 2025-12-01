from typing import Optional
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.models.validation.stitch_count_validation_handler import StitchCountValidationHandler
from engine.domain.models.validation.pattern_validation_handler import PatternValidationHandler
from engine.domain.models.validation.order_validation_handler import OrderValidationHandler
from engine.domain.models.validation.chart_data_validation_handler import ChartDataValidationHandler

class ValidationChainBuilder:
    """Builder for creating validation handler chains (Builder pattern)."""
    
    def __init__(self):
        self._first_handler: Optional[ValidationHandler] = None
        self._last_handler: Optional[ValidationHandler] = None
    
    def add_stitch_count_validation(self) -> 'ValidationChainBuilder':
        """Add stitch count validation to the chain."""
        handler = StitchCountValidationHandler()
        return self._add_handler(handler)
    
    def add_pattern_validation(self) -> 'ValidationChainBuilder':
        """Add pattern validation to the chain."""
        handler = PatternValidationHandler()
        return self._add_handler(handler)
    
    def add_order_validation(self) -> 'ValidationChainBuilder':
        """Add order validation to the chain."""
        handler = OrderValidationHandler()
        return self._add_handler(handler)
    
    def add_chart_data_validation(self) -> 'ValidationChainBuilder':
        """Add chart data validation to the chain."""
        handler = ChartDataValidationHandler()
        return self._add_handler(handler)
    
    def _add_handler(self, handler: ValidationHandler) -> 'ValidationChainBuilder':
        """Internal method to add a handler to the chain."""
        if self._first_handler is None:
            self._first_handler = handler
            self._last_handler = handler
        else:
            self._last_handler.set_next(handler)
            self._last_handler = handler
        
        return self
    
    def build(self) -> Optional[ValidationHandler]:
        """
        Build and return the validation chain.
        
        Returns:
            The first handler in the chain, or None if no handlers were added
        """
        return self._first_handler