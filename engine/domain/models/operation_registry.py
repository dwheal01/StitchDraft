from typing import Dict
from engine.domain.interfaces.ichart_operation import IChartOperation

class OperationRegistry:
    """Registry for chart operations."""
    
    def __init__(self):
        self._operations: Dict[str, IChartOperation] = {}
    
    def register(self, name: str, operation: IChartOperation) -> None:
        """Register an operation with a name."""
        self._operations[name] = operation
    
    def get_operation(self, name: str) -> IChartOperation:
        """Get an operation by name."""
        if name not in self._operations:
            raise ValueError(f"Operation '{name}' not found in registry")
        return self._operations[name]
    
    def has_operation(self, name: str) -> bool:
        """Check if an operation is registered."""
        return name in self._operations