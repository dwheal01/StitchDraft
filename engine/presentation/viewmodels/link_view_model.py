from dataclasses import dataclass

@dataclass
class LinkViewModel:
    """View model for a link between nodes in the presentation layer."""
    source_id: str
    target_id: str