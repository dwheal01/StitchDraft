from dataclasses import dataclass

@dataclass
class Link:
    """Represents a link between nodes."""
    source: str  # Node ID
    target: str  # Node ID