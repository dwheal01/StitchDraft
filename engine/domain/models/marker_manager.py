from typing import List
from engine.domain.interfaces.imarker_provider import IMarkerProvider

class MarkerManager(IMarkerProvider):
    """Handles creation and management of markers."""
    
    def __init__(self):
        self.markers_rs = []
        self.markers_ws = []
    
    def add_marker(self, side: str, position: int, num_stitches: int) -> None:
        """Add a marker to the collection."""
        if side == "RS":
            self.markers_rs.append(position)
            self.markers_ws.append(num_stitches-position)
        elif side == "WS":
            self.markers_rs.append(num_stitches-position)
            self.markers_ws.append(position)
        self.markers_rs.sort()
        self.markers_ws.sort()
     
    def clear_markers(self) -> None:
       self.markers_rs = []
       self.markers_ws = []
       
    def move_marker(self, side: str, position: int, shift_amount: int, num_stitches: int) -> None:
      old_markers = self.get_markers(side)
      if shift_amount != 0:
         self.clear_markers()
         for i in range(len(old_markers)):
            if i < position:
               self.add_marker(side, old_markers[i], num_stitches)
            elif i >= position:
               self.add_marker(side, old_markers[i] + shift_amount, num_stitches)
    
    def remove_marker(self, side: str, position: int) -> None:
      if side == "RS":
          index = self.markers_rs.index(position)
          self.markers_rs.remove(self.markers_rs[index])
          self.markers_ws.remove(self.markers_ws[len(self.markers_ws)-index-1])
      elif side == "WS":
          index = self.markers_ws.index(position)
          self.markers_ws.remove(self.markers_ws[index])
          self.markers_rs.remove(self.markers_rs[len(self.markers_rs)-index-1])
          
    def get_markers(self, side: str) -> List[int]:
        """Get the markers for the collection."""
        return self.markers_rs if side == "RS" else self.markers_ws