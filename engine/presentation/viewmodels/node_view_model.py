from dataclasses import dataclass

@dataclass
class NodeViewModel:
    """View model for a stitch node in the presentation layer."""
    id: str
    type: str  # 'k', 'p', 'inc', 'dec', 'strand', 'bo'
    x: float
    y: float
    row: int