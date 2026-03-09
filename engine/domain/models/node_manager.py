from typing import Dict, List
from engine.data.models.node import Node

class NodeManager:
    """Handles creation and management of knitting nodes."""

    DEFAULT_HOLD_NAME = "last"

    def __init__(self):
        self._nodes: List[Node] = []
        self._node_counter = 0
        self._last_row_stitches: List[Node] = []
        self._last_row_unconsumed_stitches: List[Node] = []
        self._hold_slots: Dict[str, List[Node]] = {}
        self._last_row_produced = len(self._last_row_stitches)
    
    def set_last_row_unconsumed_stitches(self, unconsumed_stitches: List[Node]) -> None:
        self._last_row_unconsumed_stitches = unconsumed_stitches
    
    def get_stitches_on_hold(self, name: str = None) -> List[Node]:
        """Get stitches on hold for the given slot name (returns defensive copy). Default name is 'last'."""
        slot_name = name if name is not None else self.DEFAULT_HOLD_NAME
        return list(self._hold_slots.get(slot_name, []))
    
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
    
    def set_stitches_on_hold(self, name: str = None) -> int:
        """Put current unconsumed stitches into the named hold slot (overwrite). Default name is 'last'."""
        slot_name = name if name is not None else self.DEFAULT_HOLD_NAME
        # When last row consumed all stitches (unconsumed empty), put entire needle on hold so needle clears.
        if self._last_row_unconsumed_stitches:
            stitches_to_hold = list(self._last_row_unconsumed_stitches)
        else:
            stitches_to_hold = list(self._last_row_stitches)
        self._hold_slots[slot_name] = stitches_to_hold
        count = 0
        for stitch in stitches_to_hold:
            self._last_row_stitches.remove(stitch)
            if stitch.type != "bo":
                count += 1
        self.set_last_row_produced(self._last_row_produced - count)
        self._last_row_unconsumed_stitches = []
        return len(stitches_to_hold)

    def clear_hold(self, name: str = None) -> None:
        """Clear the named hold slot."""
        slot_name = name if name is not None else self.DEFAULT_HOLD_NAME
        self._hold_slots[slot_name] = []

    def places_stitches_on_needle(self, stitches_on_hold: List[Node], from_hold_name: str = None) -> None:
        """Place stitches on needle, update counts, and clear the named hold slot."""
        slot_name = from_hold_name if from_hold_name is not None else self.DEFAULT_HOLD_NAME
        self._last_row_stitches.extend(stitches_on_hold)
        self._hold_slots[slot_name] = []
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