from typing import List
from engine.data.models.node import Node

class NodeManager:
    """Handles creation and management of knitting nodes."""
    
    def __init__(self):
        self._nodes: List[Node] = []
        self._node_counter = 0
        self._last_row_stitches: List[Node] = []
        self._last_row_unconsumed_stitches: List[Node] = []
        self._stitches_on_hold: List[Node] = []
        self._last_row_produced = len(self._last_row_stitches)
    
    def set_last_row_unconsumed_stitches(self, unconsumed_stitches: List[Node]) -> None:
        self._last_row_unconsumed_stitches = unconsumed_stitches
    
    def get_stitches_on_hold(self) -> List[Node]:
        """Get stitches on hold (returns defensive copy)."""
        return list(self._stitches_on_hold)
    
    def get_nodes(self) -> List[Node]:
        """Get all nodes (returns defensive copy)."""
        return list(self._nodes)
    
    def get_last_row_stitches(self) -> List[Node]:
        """Get last row stitches (returns defensive copy)."""
        return list(self._last_row_stitches)
    
    def get_last_row_unconsumed_stitches(self) -> List[Node]:
        """Get last row unconsumed stitches (returns defensive copy)."""
        return list(self._last_row_unconsumed_stitches)
    
    def get_last_row_produced(self) -> int:
        """Get the number of stitches produced in the last row."""
        return self._last_row_produced
    
    def get_node_counter(self) -> int:
        """Get the current node counter value."""
        return self._node_counter
    
    def set_last_row_stitches(self, stitches: List[Node]) -> None:
        """Set the last row stitches."""
        self._last_row_stitches = list(stitches)
    
    def append_to_last_row_stitches(self, stitches: List[Node]) -> None:
        """Append stitches to the last row stitches."""
        self._last_row_stitches.extend(stitches)
    
    def clear_last_row_stitches(self) -> None:
        """Clear the last row stitches."""
        self._last_row_stitches = []
    
    def extend_nodes(self, nodes: List[Node]) -> None:
        """Extend the nodes list with new nodes."""
        self._nodes.extend(nodes)
    
    def increment_node_counter(self, amount: int = 1) -> None:
        """Increment the node counter by the specified amount."""
        self._node_counter += amount
    
    def set_stitches_on_hold(self) -> int:
        self._stitches_on_hold = self._last_row_unconsumed_stitches
        count = 0
        for stitch in self._stitches_on_hold:
            self._last_row_stitches.remove(stitch)
            if stitch.type != "bo":
                count += 1
        self.set_last_row_produced(self._last_row_produced - count)
        return len(self._stitches_on_hold)
    
    def places_stitches_on_needle(self, stitches_on_hold: List[Node]) -> None:
        """Place stitches on needle and update counts."""
        self._last_row_stitches.extend(stitches_on_hold)
        # clear stitches on hold
        # loop through stitches on hold and count all non "bo" stitches
        num_stitches_on_needle = 0
        for stitch in self._last_row_stitches:
            if stitch.type != "bo":
                num_stitches_on_needle += 1
        self._last_row_produced = num_stitches_on_needle
    
    def update_last_row_produced(self, consumed: int, produced: int) -> int:
        """Update last row produced count and return old count."""
        old_count = self._last_row_produced
        self._last_row_produced = produced + (self._last_row_produced - consumed)
        return old_count
    
    def replace_nodes(self, nodes: List[Node]) -> None:
        """Replace all nodes with new list."""
        self._nodes = list(nodes)

    def set_last_row_produced(self, produced: int) -> None:
        self._last_row_produced = produced
    
    def create_stitch_node(self, stitch: str, fx: float, fy: float, row: int) -> Node:
        """Create a stitch node."""
        node = Node(
            id=f"{self._node_counter}",
            type=stitch,
            row=row,
            fx=fx,
            fy=fy
        )
        self._nodes.append(node)
        self._node_counter += 1
        return node
    
    def create_strand_node(self, row: int) -> Node:
        """Create a strand node."""
        # Ensure we don't create a strand node with negative ID
        if self._node_counter == 0:
            raise ValueError("Cannot create strand node: no stitch nodes exist yet")
        
        node = Node(
            id=f"{self._node_counter - 1}s",
            type="strand",
            row=row,
            fx=0.0,
            fy=0.0
        )
        self._nodes.append(node)
        return node