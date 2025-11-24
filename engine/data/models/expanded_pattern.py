from dataclasses import dataclass
from typing import List

@dataclass
class ExpandedPattern:
    """Result of expanding a pattern string."""
    stitches: List[str]
    consumed: int
    produced: int
    markers: List[int]