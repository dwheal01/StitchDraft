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

        # For WS rows the expanded row was already reversed by reverse_row_if_needed
        # (e.g. k1, inc, repeat(k1) -> k*9, inc, k). Treat it like RS for position calculation.
        if context.side == "WS":
            anchors, unconsumed_stitches = chart.position_calculator.calculate_anchors(
                row,
                "RS",
                context.previous_stitches,
                chart.link_manager,
                chart.node_manager.get_node_counter()
            )
        else:
            anchors, unconsumed_stitches = chart.position_calculator.calculate_anchors(
                row, 
                context.side, 
                context.previous_stitches, 
                chart.link_manager, 
                chart.node_manager.get_node_counter()
            )
        
        for i, stitch in enumerate(row):
            # Flip stitch type for wrong side so the chart shows RS appearance:
            # on the WS, a worked knit shows as a purl on the RS and vice versa.
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
        side = chart.row_manager.get_last_row_side()
        if side == "WS":
            anchors, _ = chart.position_calculator.calculate_anchors(
                row,
                "RS",
                previous_stitches,
                chart.link_manager,
                chart.node_manager.get_node_counter()
            )
            return anchors
        anchors, _ = chart.position_calculator.calculate_anchors(
            row,
            side,
            previous_stitches,
            chart.link_manager,
            chart.node_manager.get_node_counter()
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
        previous_stitches = chart.node_manager.get_last_row_stitches()
        
        # Calculate anchors. For WS the row was already reversed by reverse_row_if_needed.
        if side == "WS":
            anchors, unconsumed_stitches = chart.position_calculator.calculate_anchors(
                row, 
                "RS", 
                previous_stitches, 
                chart.link_manager, 
                chart.node_manager.get_node_counter()
            )
        else:
            anchors, unconsumed_stitches = chart.position_calculator.calculate_anchors(
                row, 
                side, 
                previous_stitches, 
                chart.link_manager, 
                chart.node_manager.get_node_counter()
            )
        
        # Create context
        context = GenerationContext(
            row=row,
            side=side,
            row_num=row_num,
            previous_stitches=previous_stitches
        )
        
        # Generate nodes
        chart.node_manager.clear_last_row_stitches()
        new_nodes = []
        strand_nodes = []  # Track strand nodes to link later
        for i, stitch in enumerate(row):
            actual_stitch = stitch
            if side == "WS":
                if stitch == "k":
                    actual_stitch = "p"
                elif stitch == "p":
                    actual_stitch = "k"
            
            fy = chart.position_calculator.BASE_Y_OFFSET + (row_num - 1) * chart.position_calculator.ROW_HEIGHT
            node = chart.node_manager.create_stitch_node(actual_stitch, anchors[i], fy, row_num)
            new_nodes.append(node)
            
            # Create strand node between stitches (except last)
            if i != len(row) - 1:
                strand_node = chart.node_manager.create_strand_node(row_num)
                strand_nodes.append((node, strand_node))
        
        # Create horizontal links after all nodes are created
        for i, (current_node, strand_node) in enumerate(strand_nodes):
            current_node_id = current_node.id
            strand_node_id = strand_node.id
            # The next stitch node is the one after current_node in new_nodes
            if i + 1 >= len(new_nodes):
                # Should not happen, but defensive check
                continue
            next_node = new_nodes[i + 1]
            next_node_id = next_node.id
            
            # Validate node IDs before creating links
            if not current_node_id or not strand_node_id or not next_node_id:
                continue
            if current_node_id.startswith('-') or next_node_id.startswith('-'):
                # Skip links with negative node IDs (should not happen)
                continue
            
            chart.link_manager.add_horizontal_link(current_node_id, strand_node_id)
            chart.link_manager.add_horizontal_link(strand_node_id, next_node_id)
        
        # Set new nodes and add unconsumed stitches
        chart.node_manager.set_last_row_stitches(new_nodes)
        chart.node_manager.append_to_last_row_stitches(unconsumed_stitches)
        chart.node_manager.set_last_row_unconsumed_stitches(unconsumed_stitches)
    
    def add_horizontal_links(self, chart: 'ChartSection', index: int) -> None:
        """Add horizontal links between stitches.
        
        Args:
            chart: The chart section
            index: Index of the current stitch node in the last row (0-based)
        """
        last_row_stitches = chart.node_manager.get_last_row_stitches()
        if index < 0 or index >= len(last_row_stitches) - 1:
            # Can't create link if we don't have both current and next nodes
            return
        
        current_node = last_row_stitches[index]
        next_node = last_row_stitches[index + 1]
        current_node_id = current_node.id
        next_node_id = next_node.id
        strand_node_id = f"{current_node_id}s"
        
        # Verify strand node exists
        all_nodes = chart.node_manager.get_nodes()
        strand_exists = any(node.id == strand_node_id for node in all_nodes)
        if not strand_exists:
            # Strand node should have been created, but if it doesn't exist, skip
            return
        
        chart.link_manager.add_horizontal_link(current_node_id, strand_node_id)
        chart.link_manager.add_horizontal_link(strand_node_id, next_node_id)