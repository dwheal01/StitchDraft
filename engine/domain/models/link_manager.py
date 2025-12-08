from typing import List
from engine.data.models.link import Link

class LinkManager:
    """Handles creation and management of links between nodes."""
    
    def __init__(self):
        self.links: List[Link] = []
    
    def add_horizontal_link(self, source_id: str, target_id: str) -> None:
        """Add horizontal link between stitches."""
        self.links.append(Link(source=source_id, target=target_id))
    
    def add_vertical_link(self, source_id: str, target_id: str) -> None:
        """Add vertical link between rows."""
        self.links.append(Link(source=source_id, target=target_id))
    
    def get_links(self) -> List[Link]:
        """Get all links (returns defensive copy)."""
        return list(self.links)
    
    def extend_links(self, links: List[Link]) -> None:
        """Extend the links list with new links."""
        self.links.extend(links)