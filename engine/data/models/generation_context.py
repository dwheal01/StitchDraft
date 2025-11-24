from dataclasses import dataclass
from typing import List
from engine.data.models.node import Node

@dataclass
class GenerationContext:
    """Context for generating nodes and links in a chart."""
    row: List[str]
    side: str  # 'RS' or 'WS'
    row_num: int
    previous_stitches: List[Node]
    is_round: bool = False