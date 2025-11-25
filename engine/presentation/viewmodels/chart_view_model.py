from dataclasses import dataclass
from typing import List
from engine.presentation.viewmodels.node_view_model import NodeViewModel
from engine.presentation.viewmodels.link_view_model import LinkViewModel

@dataclass
class ChartViewModel:
    """View model for a chart in the presentation layer."""
    name: str
    nodes: List[NodeViewModel]
    links: List[LinkViewModel]