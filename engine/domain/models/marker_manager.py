from typing import List
from engine.domain.interfaces.imarker_provider import IMarkerProvider

class MarkerManager(IMarkerProvider):
    """Handles creation and management of markers."""
    
    def __init__(self):
        self._markers_rs = []
        self._markers_ws = []
    
    def add_marker(self, side: str, position: int, num_stitches: int) -> None:
        """Add a marker to the collection."""
        if side == "RS":
            self._markers_rs.append(position)
            self._markers_ws.append(num_stitches-position)
        elif side == "WS":
            self._markers_rs.append(num_stitches-position)
            self._markers_ws.append(position)
        self._markers_rs.sort()
        self._markers_ws.sort()
     
    def clear_markers(self) -> None:
       self._markers_rs = []
       self._markers_ws = []
       
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
          index = self._markers_rs.index(position)
          self._markers_rs.remove(self._markers_rs[index])
          self._markers_ws.remove(self._markers_ws[len(self._markers_ws)-index-1])
      elif side == "WS":
          index = self._markers_ws.index(position)
          self._markers_ws.remove(self._markers_ws[index])
          self._markers_rs.remove(self._markers_rs[len(self._markers_rs)-index-1])
          
    def get_markers(self, side: str) -> List[int]:
        """Get the markers for the collection (returns defensive copy)."""
        markers = self._markers_rs if side == "RS" else self._markers_ws
        return list(markers)
    
    def get_markers_rs(self) -> List[int]:
        """Get RS markers (returns defensive copy)."""
        return list(self._markers_rs)
    
    def get_markers_ws(self) -> List[int]:
        """Get WS markers (returns defensive copy)."""
        return list(self._markers_ws)
    
    def add_marker_to_rs(self, position: int) -> None:
        """Add a marker to RS markers list."""
        self._markers_rs.append(position)
        self._markers_rs.sort()
    
    def add_marker_to_ws(self, position: int) -> None:
        """Add a marker to WS markers list."""
        self._markers_ws.append(position)
        self._markers_ws.sort()