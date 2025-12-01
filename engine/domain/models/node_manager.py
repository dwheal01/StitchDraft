from typing import List
from engine.data.models.node import Node

class NodeManager:
    """Handles creation and management of knitting nodes."""
    
    def __init__(self):
        self.nodes: List[Node] = []
        self.node_counter = 0
        self.last_row_stitches: List[Node] = []
        self.last_row_unconsumed_stitches: List[Node] = []
        self.stitches_on_hold: List[Node] = []
        self.last_row_produced = len(self.last_row_stitches)
    
    def set_last_row_unconsumed_stitches(self, unconsumed_stitches: List[Node]) -> None:
        self.last_row_unconsumed_stitches = unconsumed_stitches
    
    def get_stitches_on_hold(self) -> List[Node]:
        return self.stitches_on_hold
    
    def set_stitches_on_hold(self) -> int:
        self.stitches_on_hold = self.last_row_unconsumed_stitches
        count = 0
        for stitch in self.stitches_on_hold:
            self.last_row_stitches.remove(stitch)
            if stitch.type != "bo":
                count += 1
        self.set_last_row_produced(self.last_row_produced - count)
        return len(self.stitches_on_hold)
    
    def places_stitches_on_needle(self, stitches_on_hold: List[Node]) -> None:
        self.last_row_stitches.extend(stitches_on_hold)
        # clear stitches on hold
        # loop through stitches on hold and count all non "bo" stitches
        num_stitches_on_needle = 0
        for stitch in self.last_row_stitches:
            if stitch.type != "bo":
                num_stitches_on_needle += 1
        self.last_row_produced = num_stitches_on_needle

    def set_last_row_produced(self, produced: int) -> None:
        self.last_row_produced = produced
    
    def create_stitch_node(self, stitch: str, fx: float, fy: float, row: int) -> Node:
        """Create a stitch node."""
        node = Node(
            id=f"{self.node_counter}",
            type=stitch,
            row=row,
            fx=fx,
            fy=fy
        )
        self.nodes.append(node)
        self.node_counter += 1
        return node
    
    def create_strand_node(self, row: int) -> Node:
        """Create a strand node."""
        node = Node(
            id=f"{self.node_counter - 1}s",
            type="strand",
            row=row,
            fx=0.0,
            fy=0.0
        )
        self.nodes.append(node)
        return node