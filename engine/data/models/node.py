from dataclasses import dataclass

@dataclass
class Node:
    """Represents a stitch node in the chart."""
    id: str
    type: str  # 'k', 'p', 'inc', 'dec', 'strand', 'bo'
    row: int
    fx: float
    fy: float