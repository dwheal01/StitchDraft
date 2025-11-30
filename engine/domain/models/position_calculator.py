from typing import List, Dict

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
    
    def calculate_anchors(self, row: List[str], side: str, previous_stitches: List[Dict], link_manager=None, node_counter: int = 0) -> List[float]:
      """Calculate anchor positions for a row."""
      if not previous_stitches:
         return self.centered_array(len(row)), []
      return self._calculate_from_previous_row(row, side, previous_stitches, link_manager, node_counter)
      
    def _calculate_from_previous_row(self, row: List[str], side: str, previous_stitches: List[Dict], link_manager, node_counter: int) -> List[float]:
      """Calculate positions based on previous row."""
      anchors = []
      prev_i = 0
      print("row: ", row)
    #   print("previous_stitches: ", previous_stitches)
      print("side: ", side)
      for i, stitch in enumerate(row):
        #  print("stitch: ", row[len(row)-1-i])
         

         if self._is_regular_stitch(stitch):
               if side == "RS":
                    while previous_stitches[prev_i]["type"] == "bo":
                        prev_i += 1
                    anchors.append(previous_stitches[prev_i]["fx"])
                    link_manager.add_vertical_link(previous_stitches[prev_i]["id"], f"{node_counter + i}")

               else:
                    while previous_stitches[len(previous_stitches)-1-prev_i]["type"] == "bo":
                        prev_i += 1
                    anchors.append(previous_stitches[len(previous_stitches)-1-prev_i]["fx"])
                    link_manager.add_vertical_link(previous_stitches[len(previous_stitches)-1-prev_i]["id"], f"{node_counter + i}")
               # Add vertical link from previous row to current row
               prev_i += 1
         else:
                anchors.append(self._calculate_increase_decrease_anchor(i, prev_i, previous_stitches, side))
                self._add_increase_decrease_links(stitch, len(previous_stitches)-1-prev_i, i, previous_stitches, link_manager, node_counter)
                if stitch == "dec":
                    prev_i += 2
    #   print("i: ", i)
    #   print("number of previous stitches: ", len(previous_stitches))
    #   unconsumed stitches
      if side == "RS":
        unconsumed_stitches = previous_stitches[prev_i:]
      else:
        unconsumed_stitches = previous_stitches[:len(previous_stitches)-prev_i]
    #   unconsumed_stitches = previous_stitches[:len(previous_stitches)-prev_i]
      print("length of previous stitches: ", len(previous_stitches))
      print("prev_i: ", prev_i)
      print("previous stitches: ", previous_stitches)
      print("anchors: ", anchors)
      return self._center_anchors(anchors, row), unconsumed_stitches

    def _add_increase_decrease_links(self, stitch: str, prev_i: int, current_i: int, previous_stitches: List[Dict], link_manager, node_counter: int) -> None:
      """Add links for increase/decrease stitches."""
      if stitch == "inc":
         # Link from previous strand to increase
         prev_strand_id = f"{int(previous_stitches[prev_i]['id'])-1}s"
         link_manager.add_vertical_link(prev_strand_id, f"{node_counter + current_i}")
      elif stitch == "dec":
         # Link from two previous stitches to decrease
         link_manager.add_vertical_link(previous_stitches[prev_i]["id"], f"{node_counter + current_i}")
         link_manager.add_vertical_link(previous_stitches[prev_i+1]["id"], f"{node_counter + current_i}")
         
    def _is_regular_stitch(self, stitch: str) -> bool:
        """Check if stitch is a regular knit or purl."""
        return stitch in ["k", "p", "bo"]
    
    def _calculate_increase_decrease_anchor(self, i: int, prev_i: int, previous_stitches: List[Dict], side: str) -> float:
        """Calculate anchor position for increase/decrease stitches."""
        if i == 0:
            return previous_stitches[0]["fx"] - 50
        elif i == len(previous_stitches):
            return previous_stitches[-1]["fx"] + 50
        else:
            if side == "RS":
                return (previous_stitches[prev_i-1]["fx"] + previous_stitches[prev_i]["fx"]) / 2
            else:
                return (previous_stitches[len(previous_stitches)-prev_i-1]["fx"] + previous_stitches[len(previous_stitches)-prev_i]["fx"]) / 2
    
    def _center_anchors(self, anchors: List[float], row: List[str]) -> List[float]:
        """Center the anchors around zero."""
        if not anchors:
            return anchors
        
        center_of_anchors = sum(anchors) / len(anchors)
        print("center of anchors: ", center_of_anchors)
        return [center_of_anchors + x for x in self.centered_array(len(row))]