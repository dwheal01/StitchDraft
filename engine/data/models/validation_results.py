from dataclasses import dataclass
from typing import List

@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    
    def raise_if_invalid(self) -> None:
        """Raise an exception if validation failed."""
        if not self.is_valid:
            error_message = "; ".join(self.errors)
            raise ValueError(f"Validation failed: {error_message}")