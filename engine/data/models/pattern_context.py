from dataclasses import dataclass
from typing import List

@dataclass
class PatternContext:
    """Context information for pattern processing."""
    available_stitches: int
    side: str  # 'RS' or 'WS'
    markers: List[int]  # List of marker positions
    last_row_side: str
    is_round: bool = False