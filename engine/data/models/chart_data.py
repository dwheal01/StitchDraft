from dataclasses import dataclass
from typing import List
from engine.data.models.node import Node
from engine.data.models.link import Link

@dataclass
class ChartData:
    """Data transfer object for chart information."""
    name: str
    nodes: List[Node]
    links: List[Link]