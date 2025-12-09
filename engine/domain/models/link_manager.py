from typing import List
from engine.data.models.link import Link

class LinkManager:
    """Handles creation and management of links between nodes."""
    
    def __init__(self):
        self._links: List[Link] = []
    
    def add_horizontal_link(self, source_id: str, target_id: str) -> None:
        """Add horizontal link between stitches."""
        # Validate node IDs to prevent creating links with invalid IDs
        if not source_id or not target_id:
            return  # Skip invalid links
        if source_id.startswith('-') or target_id.startswith('-'):
            # Skip links with negative node IDs (should not happen)
            return
        self._links.append(Link(source=source_id, target=target_id))
    
    def add_vertical_link(self, source_id: str, target_id: str) -> None:
        """Add vertical link between rows."""
        # Validate node IDs to prevent creating links with invalid IDs
        if not source_id or not target_id:
            return  # Skip invalid links
        if source_id.startswith('-') or target_id.startswith('-'):
            # Skip links with negative node IDs (should not happen)
            return
        self._links.append(Link(source=source_id, target=target_id))
    
    def get_links(self) -> List[Link]:
        """Get all links (returns defensive copy)."""
        return list(self._links)
    
    def extend_links(self, links: List[Link]) -> None:
        """Extend the links list with new links."""
        self._links.extend(links)
    
    def replace_links(self, links: List[Link]) -> None:
        """Replace all links with a new list."""
        self._links = list(links)
    
    def remove_invalid_links(self, node_ids: set) -> int:
        """
        Remove links that reference non-existent nodes.
        
        Args:
            node_ids: Set of valid node IDs
            
        Returns:
            Number of links removed
        """
        initial_count = len(self._links)
        self._links = [
            link for link in self._links
            if link.source in node_ids and link.target in node_ids
        ]
        return initial_count - len(self._links)