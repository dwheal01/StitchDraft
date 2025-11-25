from typing import List
from engine.data.models.stitch_count_event import StitchCountEvent

class StitchCounter:
    """Tracks stitch count changes and maintains history."""
    
    def __init__(self, initial_count: int = 0):
        """
        Initialize the stitch counter.
        
        Args:
            initial_count: Starting stitch count (default: 0)
        """
        self.current_count = initial_count
        self.history: List[StitchCountEvent] = []
    
    def get_current_count(self) -> int:
        """Get the current stitch count."""
        return self.current_count
    
    def record_operation(
        self,
        operation: str,
        consumed: int,
        produced: int
    ) -> None:
        """
        Record a stitch operation and update the count.
        
        Args:
            operation: Name of the operation (e.g., 'cast_on', 'add_row', 'dec')
            consumed: Number of stitches consumed
            produced: Number of stitches produced
        """
        old_count = self.current_count
        self.current_count = old_count - consumed + produced
        
        event = StitchCountEvent(
            operation=operation,
            consumed=consumed,
            produced=produced,
            old_count=old_count,
            new_count=self.current_count
        )
        self.history.append(event)
    
    def validate_consistency(self, actual_count: int) -> bool:
        """
        Validate that the tracked count matches the actual count.
        
        Args:
            actual_count: The actual number of stitches in the chart
            
        Returns:
            True if counts match, False otherwise
        """
        return self.current_count == actual_count
    
    def get_history(self) -> List[StitchCountEvent]:
        """Get the history of stitch count changes."""
        return self.history.copy()
    
    def reset(self, count: int = 0) -> None:
        """Reset the counter to a specific count."""
        self.current_count = count
        self.history.clear()