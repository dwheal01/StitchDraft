from typing import List, Dict, Any, Tuple, Union
from row_manager import RowManager
from node_manager import NodeManager
from link_manager import LinkManager
from position_calculator import PositionCalculator
from pattern_parser import PatternParser
from marker_manager import MarkerManager


class ChartSection:
    """Main class that coordinates knitting chart generation."""
    
    def __init__(self, name: str, start_side: str, sts: int = 22, rows: int = 28):
        self.name = name
        self.start_side = start_side
        
        # Composition - delegate to specialized classes
        self.row_manager = RowManager(start_side)
        self.node_manager = NodeManager()
        self.link_manager = LinkManager()
        self.position_calculator = PositionCalculator()
        self.marker_manager = MarkerManager()
        self.pattern_parser = PatternParser(self.marker_manager.get_markers, self.marker_manager.move_marker, self.marker_manager.remove_marker)
        
        self.position_calculator.set_guage(sts, rows)
      
    def get_current_row_num(self) -> List[str]:
      return len(self.row_manager.rows)
    
    def get_current_num_of_stitches(self) -> int:
      return self.node_manager.last_row_produced
    
    def get_stitches_on_hold(self) -> List[Dict]:
      return self.node_manager.get_stitches_on_hold()
    
    def place_on_hold(self) -> List[Dict]:
      """Place the unconsumed stitches on hold and return the previous stitches on hold."""
      previous_stitches_on_hold = self.node_manager.get_stitches_on_hold()
      num_stitches_on_hold = self.node_manager.set_stitches_on_hold()
      # self.node_manager.set_last_row_produced(len(self.node_manager.last_row_stitches)-num_stitches_on_hold)
      return previous_stitches_on_hold
    
    def place_on_needle(self, stitches_on_hold: List[Dict], join_side: str) -> None:
      """Place the stitches on needle."""
      self.node_manager.places_stitches_on_needle(stitches_on_hold)
      if join_side == "RS":
        self.row_manager.set_last_row_side("WS")
      else:
        self.row_manager.set_last_row_side("RS")
    
    def get_row_num(self, side: str) -> int:
      row_num = 1
      if self.node_manager.last_row_produced > 0:
        if side == "RS":
          row_num += self.node_manager.last_row_stitches[0]["row"]
        else:
          row_num += self.node_manager.last_row_stitches[-1]["row"]
      return row_num
    
    def add_nodes(self, row: List[str], side: str, isRound: bool = False) -> None:
      """Add nodes for a new row."""
      anchors, unconsumed_stitches = self.position_calculator.calculate_anchors(
         row, side, self.node_manager.last_row_stitches, self.link_manager, self.node_manager.node_counter
      )
      row_num = self.get_row_num(side)
      self._create_nodes_for_row(row, unconsumed_stitches, side, row_num, anchors, isRound)
      self.row_manager.add_row(row, isRound)

    def add_round(self, pattern: Union[str, int]) -> List[str]:
      """Add a round to the pattern."""
      self.add_row(pattern, True)
      return self

    def add_row(self, pattern: Union[str, int], isRound: bool = False) -> List[str]:
        """Add a new row to the pattern."""
        if isinstance(pattern, int):
            new_row = self.row_manager.duplicate_row(pattern)
        else:
            side = "WS" if self.row_manager.is_wrong_side(isRound) else "RS"
            new_row, consumed, produced, markers = self.pattern_parser.expand_pattern(
                pattern, self.node_manager.last_row_produced if self.row_manager.rows else float('inf'), side
            )

            # self.node_manager.set_last_row_produced(produced)
            # self._validate_row_consumption(consumed, produced)
            # loop through markers and add them to the marker manager
            # calculate the side of the row
            for marker in markers:
                self.marker_manager.add_marker(side, marker, len(new_row))
            
        new_row = self.row_manager.reverse_row_if_needed(new_row, isRound)
        self.add_nodes(new_row, side, isRound)
        self.node_manager.set_last_row_produced(produced+(self.node_manager.last_row_produced-consumed))

        return self
    
    def cast_on_start(self, count: int) -> None:
        """Cast on the specified number of stitches."""
        if self.start_side == "RS":
          self.add_nodes(["k"] * count, "WS")
        else:
          self.add_nodes(["k"] * count, "RS")
        self.node_manager.set_last_row_produced(count)
    
    def find_last_stitch(self) -> Dict[str, Any]:
      """Get the rightmost stitch position if last row is RS, otherwise leftmost stitch position if last row is WS."""
      if self.row_manager.last_row_side == "RS":
        return self.node_manager.last_row_stitches[-1]
      else:
        return self.node_manager.last_row_stitches[0]
      
    def find_first_stitch(self) -> Dict[str, Any]:
      """Get the leftmost stitch position if last row is WS, otherwise rightmost stitch position if last row is RS."""
      if self.row_manager.last_row_side == "RS":
        return self.node_manager.last_row_stitches[0]
      else:
        return self.node_manager.last_row_stitches[-1]
      
    def cast_on(self, count: int) -> 'ChartSection':
        """Cast on additional stitches to extend the current chart."""
        if not self.node_manager.last_row_stitches:
            raise ValueError("No stitches to cast on to")
        
        # Get the current row's y position
        current_fy = self.node_manager.last_row_stitches[0]["fy"]
        # current_row_number = len(self.row_manager.rows)
        side = "RS" if self.row_manager.last_row_side == "RS" else "WS"
        current_row_number = self.get_row_num(side)-1
        
        last_stitch = self.find_last_stitch()
        last_fx = last_stitch["fx"]
        connecting_id = last_stitch["id"]
        spacing = self.position_calculator.DEFAULT_SPACING
        
        
        # Create new cast-on stitches positioned to the right
        for i in range(count):
            if side == "RS":
              new_fx = last_fx + (i + 1) * spacing
            else:
              new_fx = last_fx - (i + 1) * spacing
            # Create the stitch node
            node = self.node_manager.create_stitch_node("k", new_fx, current_fy, current_row_number)
            self.node_manager.last_row_stitches.append(node)
            
            # Add horizontal links between stitches
            if i == 0:  # First new stitch connects to last existing stitch
                # Create link from last existing stitch to first new stitch
                last_existing_id = self.node_manager.last_row_stitches[-2]["id"]  # -2 because we just added the new stitch
                first_new_id = self.node_manager.last_row_stitches[-1]["id"]      # -1 is the new stitch
                self.link_manager.add_horizontal_link(connecting_id, first_new_id)
            
            if i < count - 1:  # Add strand node between new stitches
                self.node_manager.create_strand_node(current_row_number)
                self._add_horizontal_links(len(self.node_manager.last_row_stitches) - 2)
        
        # Update the row in row_manager to include the new stitches
        current_row = [stitch["type"] for stitch in self.node_manager.last_row_stitches]
        self.row_manager.rows[-1] = current_row  # Update the last row
        
        self.node_manager.set_last_row_produced(self.node_manager.last_row_produced + count)
        return self
    def join(self, other: 'ChartSection') -> None:
      """Join this chart section with another chart section."""
      last_stitch_self = self.find_last_stitch()
      new_fx = last_stitch_self["fx"] + self.position_calculator.DEFAULT_SPACING
      first_stitch_other = other.find_first_stitch()
      offset = new_fx - first_stitch_other["fx"]
      for stitch in other.node_manager.nodes:
        if stitch["type"] != "strand":
          stitch["fx"] += offset
      
      for marker in other.marker_manager.markers_rs:
        self.marker_manager.markers_rs.append(marker + len(self.node_manager.last_row_stitches))
      for marker in other.marker_manager.markers_ws:
        self.marker_manager.markers_ws.append(marker + len(self.node_manager.last_row_stitches))
      # self.link_manager.links.extend(other.link_manager.links)
      self.node_manager.nodes.extend(other.node_manager.nodes)
      self.node_manager.node_counter += other.node_manager.node_counter
      self.node_manager.last_row_stitches.extend(other.node_manager.last_row_stitches)

      return self
  
    def _create_nodes_for_row(self, row: List[str], unconsumed_stitches: List[Dict], side: str, row_num: int, anchors: List[float], isRound: bool = False) -> None:
        """Create nodes for a row of stitches."""
        self.node_manager.last_row_stitches = []

        for i, stitch in enumerate(row):
            if side == "WS":
              if stitch == "k":
                stitch = "p"
              elif stitch == "p":
                stitch = "k"
            fy = self.position_calculator.BASE_Y_OFFSET + (row_num - 1) * self.position_calculator.ROW_HEIGHT
            node = self.node_manager.create_stitch_node(stitch, anchors[i], fy, row_num)
            self.node_manager.last_row_stitches.append(node)
            
            if i != len(row) - 1:
                self.node_manager.create_strand_node(row_num)
                self._add_horizontal_links(i)

        self.node_manager.last_row_stitches.extend(unconsumed_stitches)
        self.node_manager.set_last_row_unconsumed_stitches(unconsumed_stitches)
    
    def _add_horizontal_links(self, i: int) -> None:
        """Add horizontal links between stitches."""
        current_id = f"{self.node_manager.node_counter - 1}"
        strand_id = f"{self.node_manager.node_counter - 1}s"
        next_id = f"{self.node_manager.node_counter}"
        
        self.link_manager.add_horizontal_link(current_id, strand_id)
        self.link_manager.add_horizontal_link(strand_id, next_id)
    
    def _validate_row_consumption(self, consumed: int, produced: int) -> None:
        """Validate row consumption matches previous row production."""
        if self.row_manager.rows:
            prev_row_len = len(self.node_manager.last_row_stitches)
            if consumed != prev_row_len:
                raise ValueError(
                    f"Row consumes {consumed} but previous row produced {prev_row_len}"
                )
    
    def __str__(self) -> str:
        """Return formatted string representation."""
        return f"""Section {self.name} (start on {self.start_side}):
  const nodes = [
{self._format_nodes()}
  ]
  const links = [
{self._format_links()}
  ]"""
    
    def _format_nodes(self) -> str:
        return '\n'.join(f"   {node}," for node in self.node_manager.nodes)
    
    def _format_links(self) -> str:
        return '\n'.join(f"   {link}," for link in self.link_manager.links)
   
    def place_marker(self, side: str, position: int) -> None:
      """Place a marker at the specified needle position."""
      self.marker_manager.add_marker(side, position, len(self.node_manager.last_row_stitches))

    def get_markers(self, side: str) -> List[int]:
      """Get all marker positions."""
      return self.marker_manager.get_markers(side)
    
    def repeat_rows(self, row_patterns: List[str], count: int) -> None:
      """Repeat a sequence of row patterns a specified number of times."""
      for _ in range(count):
          for pattern in row_patterns:
              self.add_row(pattern)
              
    def repeat_rounds(self, row_patterns: List[str], count: int) -> None:
      """Repeat a sequence of row patterns a specified number of times."""
      for _ in range(count):
          for pattern in row_patterns:
              self.add_round(pattern)
   
    @property
    def nodes(self):
      """Get nodes from the node manager."""
      return self.node_manager.nodes

    @property
    def links(self):
      """Get links from the link manager."""
      return self.link_manager.links

    @property
    def rows(self):
      """Get rows from the row manager."""
      return self.row_manager.rows
