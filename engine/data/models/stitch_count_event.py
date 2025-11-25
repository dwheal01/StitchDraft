from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StitchCountEvent:
    """Event representing a stitch count change."""
    operation: str  # e.g., 'cast_on', 'add_row', 'dec', 'inc'
    consumed: int  # Number of stitches consumed
    produced: int  # Number of stitches produced
    old_count: int  # Stitch count before operation
    new_count: int  # Stitch count after operation
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()