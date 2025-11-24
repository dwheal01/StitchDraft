from typing import List, Dict, Any, TYPE_CHECKING
from engine.data.models.node import Node
from engine.data.models.link import Link
from engine.data.models.generation_context import GenerationContext

if TYPE_CHECKING:
    from engine.chart_section import ChartSection

class ChartGenerator:
    """Generates nodes and links for chart sections."""
    
    def __init__(self, position_calculator=None):
        """Initialize with optional position calculator."""
        self._position_calculator = position_calculator
    
    def generate_nodes(
        self, 
        chart: 'ChartSection', 
        row: List[str], 
        context: GenerationContext
    ) -> List[Node]:
        """Generate nodes for a row of stitches."""
        # Import at runtime to avoid circular import
        from engine.chart_section import ChartSection
        nodes = []
        anchors, unconsumed_stitches = chart.position_calculator.calculate_anchors(
            row, 
            context.side, 
            context.previous_stitches, 
            chart.link_manager, 
            chart.node_manager.node_counter
        )
        
        for i, stitch in enumerate(row):
            # Flip stitch type for wrong side
            if context.side == "WS":
                if stitch == "k":
                    stitch = "p"
                elif stitch == "p":
                    stitch = "k"
            
            fy = chart.position_calculator.BASE_Y_OFFSET + (context.row_num - 1) * chart.position_calculator.ROW_HEIGHT
            node = chart.node_manager.create_stitch_node(stitch, anchors[i], fy, context.row_num)
            nodes.append(node)
            
            # Add strand node between stitches (except last)
            if i != len(row) - 1:
                chart.node_manager.create_strand_node(context.row_num)
        
        return nodes
    
    def generate_links(
        self, 
        chart: 'ChartSection', 
        previous_row: List[Node], 
        current_row: List[Node]
    ) -> List[Link]:
        """Generate links between previous and current rows."""
        links = []
        # This would generate vertical links between rows
        # Implementation depends on your linking strategy
        return links
    
    def calculate_positions(
        self, 
        chart: 'ChartSection', 
        row: List[str], 
        previous_stitches: List[Node]
    ) -> List[float]:
        """Calculate positions for stitches in a row."""
        anchors, _ = chart.position_calculator.calculate_anchors(
            row,
            chart.row_manager.last_row_side,
            previous_stitches,
            chart.link_manager,
            chart.node_manager.node_counter
        )
        return anchors
    
    def create_nodes_for_row(
        self, 
        chart: 'ChartSection', 
        row: List[str], 
        side: str, 
        row_num: int
    ) -> None:
        """Create nodes for a row and update chart state."""
        # Import at runtime to avoid circular import
        from engine.chart_section import ChartSection
        
        # Get previous stitches
        previous_stitches = chart.node_manager.last_row_stitches
        
        # Calculate anchors
        anchors, unconsumed_stitches = chart.position_calculator.calculate_anchors(
            row, 
            side, 
            previous_stitches, 
            chart.link_manager, 
            chart.node_manager.node_counter
        )
        
        # Create context
        context = GenerationContext(
            row=row,
            side=side,
            row_num=row_num,
            previous_stitches=previous_stitches
        )
        
        # Generate nodes
        chart.node_manager.last_row_stitches = []
        for i, stitch in enumerate(row):
            # Flip stitch type for wrong side
            actual_stitch = stitch
            if side == "WS":
                if stitch == "k":
                    actual_stitch = "p"
                elif stitch == "p":
                    actual_stitch = "k"
            
            fy = chart.position_calculator.BASE_Y_OFFSET + (row_num - 1) * chart.position_calculator.ROW_HEIGHT
            node = chart.node_manager.create_stitch_node(actual_stitch, anchors[i], fy, row_num)
            chart.node_manager.last_row_stitches.append(node)
            
            # Add horizontal links between stitches
            if i != len(row) - 1:
                chart.node_manager.create_strand_node(row_num)
                self.add_horizontal_links(chart, i)
        
        # Add unconsumed stitches
        chart.node_manager.last_row_stitches.extend(unconsumed_stitches)
        chart.node_manager.set_last_row_unconsumed_stitches(unconsumed_stitches)
    
    def add_horizontal_links(self, chart: 'ChartSection', index: int) -> None:
        """Add horizontal links between stitches."""
        current_id = f"{chart.node_manager.node_counter - 1}"
        strand_id = f"{chart.node_manager.node_counter - 1}s"
        next_id = f"{chart.node_manager.node_counter}"
        
        chart.link_manager.add_horizontal_link(current_id, strand_id)
        chart.link_manager.add_horizontal_link(strand_id, next_id)