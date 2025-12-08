from typing import List, TYPE_CHECKING
from engine.data.models.node import Node

if TYPE_CHECKING:
    from engine.chart_section import ChartSection

class ChartQueries:
    """Query interface for ChartSection data."""
    
    def __init__(self, chart: 'ChartSection'):
        # Import at runtime to avoid circular import
        from engine.chart_section import ChartSection
        self._chart: ChartSection = chart
    
    def get_current_num_of_stitches(self) -> int:
        """Get the current number of stitches in the chart."""
        return self._chart.node_manager.get_last_row_produced()
    
    def get_current_row_num(self) -> int:
        """Get the current row number."""
        return self._chart.row_manager.get_row_count()
    
    def get_row_num(self, side: str) -> int:
        """Get the row number for a given side."""
        row_num = 1
        last_row_produced = self._chart.node_manager.get_last_row_produced()
        if last_row_produced > 0:
            last_row_stitches = self._chart.node_manager.get_last_row_stitches()
            if side == "RS":
                row_num += last_row_stitches[0].row
            else:
                row_num += last_row_stitches[-1].row
        return row_num
    
    def get_stitches_on_hold(self) -> List[Node]:
        """Get stitches currently on hold."""
        return self._chart.node_manager.get_stitches_on_hold()
    
    def get_markers(self, side: str) -> List[int]:
        """Get all marker positions for a given side."""
        return self._chart.marker_manager.get_markers(side)
    
    def find_last_stitch(self) -> Node:
        """Get the rightmost stitch position if last row is RS, otherwise leftmost stitch position if last row is WS."""
        last_row_side = self._chart.row_manager.get_last_row_side()
        last_row_stitches = self._chart.node_manager.get_last_row_stitches()
        if last_row_side == "RS":
            return last_row_stitches[-1]
        else:
            return last_row_stitches[0]
    
    def find_first_stitch(self) -> Node:
        """Get the leftmost stitch position if last row is WS, otherwise rightmost stitch position if last row is RS."""
        last_row_side = self._chart.row_manager.get_last_row_side()
        last_row_stitches = self._chart.node_manager.get_last_row_stitches()
        if last_row_side == "RS":
            return last_row_stitches[0]
        else:
            return last_row_stitches[-1]