from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class ChartStateEvent:
    """Event representing a change in chart state."""
    event_type: str  # 'stitch_count_changed', 'node_added', etc.
    chart: Any  # ChartSection (forward reference)
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()