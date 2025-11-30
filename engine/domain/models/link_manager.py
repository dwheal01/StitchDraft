class LinkManager:
    """Handles creation and management of links between nodes."""
    
    def __init__(self):
        self.links = []
    
    def add_horizontal_link(self, source_id: str, target_id: str) -> None:
        """Add horizontal link between stitches."""
        self.links.append({"source": source_id, "target": target_id})
    
    def add_vertical_link(self, source_id: str, target_id: str) -> None:
        """Add vertical link between rows."""
        self.links.append({"source": source_id, "target": target_id})