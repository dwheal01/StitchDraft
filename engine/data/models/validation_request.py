from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.chart_section import ChartSection
    from engine.data.models.node import Node
    from engine.data.models.link import Link
    from engine.data.models.pattern_context import PatternContext

@dataclass
class ValidationRequest:
    """Request object for validation operations."""
    chart: 'ChartSection'
    pattern: Optional[str] = None
    nodes: Optional[List['Node']] = None
    links: Optional[List['Link']] = None
    operation: Optional[str] = None
    context: Optional['PatternContext'] = None
    consumed: Optional[int] = None
    produced: Optional[int] = None