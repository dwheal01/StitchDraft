from typing import List
from engine.data.models.node import Node

class PositionCalculator:
    """Handles calculation of stitch positions."""
    
    def __init__(self):
        self.DEFAULT_SPACING = 0
        self.ROW_HEIGHT = 0
        self.BASE_Y_OFFSET = 0
    
    def set_guage(self, sts: int, rows: int) -> None:
      self.DEFAULT_SPACING = 96 / (sts/4)
      self.ROW_HEIGHT = 96 / (rows/4)
      self.BASE_Y_OFFSET = 0
      
    def centered_array(self, n: int, spacing: int = None) -> List[float]:
        """Create centered array of positions."""
        if spacing is None:
            spacing = self.DEFAULT_SPACING
        if n <= 0:
            return []
        offset = (n - 1) / 2 * spacing
        return [i * spacing - offset for i in range(n)]
    
    def calculate_anchors(self, row: List[str], side: str, previous_stitches: List[Node], link_manager=None, node_counter: int = 0) -> tuple[List[float], List[Node]]:
      """Calculate anchor positions for a row."""
      if not previous_stitches:
         return self.centered_array(len(row)), []
      return self._calculate_from_previous_row(row, side, previous_stitches, link_manager, node_counter)
      
    def _calculate_from_previous_row(self, row: List[str], side: str, previous_stitches: List[Node], link_manager, node_counter: int) -> tuple[List[float], List[Node]]:
      """Calculate positions based on previous row."""
      anchors = []
      prev_i = 0
      for i, stitch in enumerate(row):
         

         if self._is_regular_stitch(stitch):
               if side == "RS":
                    while previous_stitches[prev_i].type == "bo":
                        prev_i += 1
                    anchors.append(previous_stitches[prev_i].fx)
                    link_manager.add_vertical_link(previous_stitches[prev_i].id, f"{node_counter + i}")

               else:
                    while previous_stitches[len(previous_stitches)-1-prev_i].type == "bo":
                        prev_i += 1
                    anchors.append(previous_stitches[len(previous_stitches)-1-prev_i].fx)
                    link_manager.add_vertical_link(previous_stitches[len(previous_stitches)-1-prev_i].id, f"{node_counter + i}")
               # Add vertical link from previous row to current row
               prev_i += 1
         else:
                anchors.append(self._calculate_increase_decrease_anchor(i, prev_i, previous_stitches, side))
                self._add_increase_decrease_links(stitch, len(previous_stitches)-1-prev_i, i, previous_stitches, link_manager, node_counter)
                if stitch == "dec":
                    prev_i += 2
                    
      if side == "RS":
        unconsumed_stitches = previous_stitches[prev_i:]
      else:
        unconsumed_stitches = previous_stitches[:len(previous_stitches)-prev_i]
      # For both RS and WS, return evenly spaced, centered anchors. WS-specific
      # drawing conventions are handled in the presentation layer so the engine
      # geometry remains symmetric and knitting-focused.
      return self._center_anchors(anchors, row), unconsumed_stitches

    def _add_increase_decrease_links(self, stitch: str, prev_i: int, current_i: int, previous_stitches: List[Node], link_manager, node_counter: int) -> None:
      """Add links for increase/decrease stitches."""
      if stitch == "inc":
         # Link from the strand that follows the reference stitch (if it exists)
         if prev_i < len(previous_stitches) - 1:
             prev_strand_id = f"{previous_stitches[prev_i].id}s"
             link_manager.add_vertical_link(prev_strand_id, f"{node_counter + current_i}")
      elif stitch == "dec":
         # Link from two previous stitches to decrease
         link_manager.add_vertical_link(previous_stitches[prev_i].id, f"{node_counter + current_i}")
         link_manager.add_vertical_link(previous_stitches[prev_i+1].id, f"{node_counter + current_i}")
         
    def _is_regular_stitch(self, stitch: str) -> bool:
        """Check if stitch is a regular knit or purl."""
        return stitch in ["k", "p", "bo"]
    
    def _calculate_increase_decrease_anchor(self, i: int, prev_i: int, previous_stitches: List[Node], side: str) -> float:
        """Calculate anchor position for increase/decrease stitches (and co: cast-on beyond end of row)."""
        # Derive a reasonable spacing from the previous row if possible
        if len(previous_stitches) >= 2:
            spacing = (previous_stitches[-1].fx - previous_stitches[0].fx) / (len(previous_stitches) - 1)
        else:
            spacing = self.DEFAULT_SPACING if self.DEFAULT_SPACING > 0 else 50

        # Edge cases: increases/decreases at the very beginning or beyond the end
        if i == 0:
            # At the beginning of the logical row. Respect knitting direction:
            # RS: extend to the left of the leftmost previous stitch
            # WS: extend to the right of the rightmost previous stitch
            if side == "RS":
                return previous_stitches[0].fx - spacing
            else:
                return previous_stitches[-1].fx + spacing
        elif prev_i >= len(previous_stitches):
            # Stitches beyond the *consumed* previous stitches (e.g. true cast-on at end):
            # extend from the working edge using the same spacing as the previous row to
            # avoid visual shift. This uses prev_i instead of i so that increases that
            # still have unused previous stitches (like a mirrored inc near the far edge)
            # are NOT misclassified as cast-on.
            steps_from_edge = prev_i - len(previous_stitches) + 1
            if side == "RS":
                # RS: extend to the right of the rightmost previous stitch
                return previous_stitches[-1].fx + spacing * steps_from_edge
            else:
                # WS: extend to the left of the leftmost previous stitch
                return previous_stitches[0].fx - spacing * steps_from_edge
        else:
            # Interior increases/decreases: place exactly between the last-used and next-unused
            # stitches, based on the knitting direction.
            if side == "RS":
                # On RS, prev_i counts consumed stitches from the left.
                return (previous_stitches[prev_i-1].fx + previous_stitches[prev_i].fx) / 2
            else:
                # On WS, prev_i counts consumed stitches from the right.
                # Consumed indices from right are: N-1, N-2, ..., N-prev_i.
                # Last used from the right: N - prev_i
                # Next unused from the right: N - prev_i - 1
                last_used_idx = len(previous_stitches) - prev_i
                next_unused_idx = len(previous_stitches) - prev_i - 1
                return (previous_stitches[last_used_idx].fx + previous_stitches[next_unused_idx].fx) / 2
    
    def _center_anchors(self, anchors: List[float], row: List[str]) -> List[float]:
        """Center the anchors around zero."""
        if not anchors:
            return anchors
        
        # Maintain the previous behavior of evenly spacing stitches for the row
        # while centering around the average anchor position. This keeps the
        # chart visually tidy and consistent in width, even though it slightly
        # abstracts away from the exact physical spacing.
        center_of_anchors = sum(anchors) / len(anchors)
        return [center_of_anchors + x for x in self.centered_array(len(row))]