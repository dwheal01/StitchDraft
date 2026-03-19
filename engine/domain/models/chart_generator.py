from typing import List, Dict, Any, TYPE_CHECKING
from engine.data.models.node import Node
from engine.data.models.link import Link
from engine.data.models.generation_context import GenerationContext

if TYPE_CHECKING:
    from engine.chart_section import ChartSection

class _NoopLinkManager:
    """Prevents vertical-link side effects when we only need anchor positions."""

    def add_vertical_link(self, *args, **kwargs) -> None:
        pass

    def add_horizontal_link(self, *args, **kwargs) -> None:
        pass

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

        # WS rows are stored in needle-order, but we want the *visual* layout to match
        # the original RS-style geometry for overall chart spacing.
        # For incomplete WS rows, we shift the worked anchors so the visual gap appears
        # on the correct side (e.g. CO 10, WS k2 => two purls on the right).
        if context.side == "WS":
            # Anchor x-geometry (for worked stitches) is computed RS-style to keep the
            # overall chart width consistent with earlier behavior.
            anchors, _ = chart.position_calculator.calculate_anchors(
                row,
                "RS",
                context.previous_stitches,
                _NoopLinkManager(),
                chart.node_manager.get_node_counter(),
            )

            # Unconsumed stitches must be the WS-correct ones so that subsequent
            # place-on-hold operations move the right stitches.
            _, unconsumed_stitches = chart.position_calculator.calculate_anchors(
                row,
                "WS",
                context.previous_stitches,
                chart.link_manager,
                chart.node_manager.get_node_counter(),
            )

            unconsumed_regular = [s for s in unconsumed_stitches if s.type != "bo"]
            # If this row is a simple k/p-only worked segment, we can deterministically
            # remap anchor + unconsumed x positions onto an even centered grid based on
            # how many live stitches remain unconsumed. This avoids visual overlap issues
            # that show up later when those stitches are moved onto hold.
            if anchors and unconsumed_regular and all(t in ("k", "p") for t in row):
                prev_live_sorted = sorted(
                    [s for s in context.previous_stitches if s.type != "bo"], key=lambda s: s.fx
                )
                un_live_sorted = sorted(unconsumed_regular, key=lambda s: s.fx)
                total_live = len(prev_live_sorted)
                un_live_count = len(un_live_sorted)

                if total_live >= 2 and len(row) == (total_live - un_live_count):
                    spacing = (prev_live_sorted[-1].fx - prev_live_sorted[0].fx) / (total_live - 1)
                    needle_positions = chart.position_calculator.centered_array(total_live, spacing)
                    # Unconsumed stitches occupy the leftmost live slots; worked occupy the rightmost.
                    left_positions = needle_positions[:un_live_count]
                    right_positions = needle_positions[un_live_count:]
                    anchors = right_positions
                    for s, x in zip(un_live_sorted, left_positions):
                        s.fx = x

            # Fallback: heuristic shift of worked anchors based on unconsumed size.
            if unconsumed_regular and anchors and len(context.previous_stitches) >= 2 and not all(t in ("k", "p") for t in row):
                prev_regular = [s for s in context.previous_stitches if s.type != "bo"]
                if len(prev_regular) >= 2:
                    spacing = (prev_regular[-1].fx - prev_regular[0].fx) / (len(prev_regular) - 1)
                else:
                    spacing = 0

                minA = min(anchors)
                maxA = max(anchors)
                centerA = sum(anchors) / len(anchors)
                # If anchors are currently on the left, shift right; if on the right, shift left.
                if maxA <= 0:
                    sign = 1
                elif minA >= 0:
                    sign = -1
                else:
                    sign = 1 if centerA < 0 else -1
                shift = sign * spacing * len(unconsumed_regular)
                anchors = [a + shift for a in anchors]
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
            # In this method we don't have unconsumed stitches returned, so we can't
            # apply the partial-WS shift. It's only used for measurement/preview,
            # where precise partial gaps are less important.
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
        
        # Calculate anchors. WS rows are stored reversed for needle order, but anchor
        # x-coordinates must preserve the original RS-style overall chart spacing.
        if side == "WS":
            anchors, _ = chart.position_calculator.calculate_anchors(
                row,
                "RS",
                previous_stitches,
                _NoopLinkManager(),
                chart.node_manager.get_node_counter(),
            )

            _, unconsumed_stitches = chart.position_calculator.calculate_anchors(
                row,
                "WS",
                previous_stitches,
                chart.link_manager,
                chart.node_manager.get_node_counter(),
            )

            unconsumed_regular = [s for s in unconsumed_stitches if s.type != "bo"]
            if anchors and unconsumed_regular and all(t in ("k", "p") for t in row):
                prev_live_sorted = sorted([s for s in previous_stitches if s.type != "bo"], key=lambda s: s.fx)
                un_live_sorted = sorted(unconsumed_regular, key=lambda s: s.fx)
                total_live = len(prev_live_sorted)
                un_live_count = len(un_live_sorted)

                if total_live >= 2 and len(row) == (total_live - un_live_count):
                    spacing = (prev_live_sorted[-1].fx - prev_live_sorted[0].fx) / (total_live - 1)
                    needle_positions = chart.position_calculator.centered_array(total_live, spacing)
                    left_positions = needle_positions[:un_live_count]
                    right_positions = needle_positions[un_live_count:]
                    anchors = right_positions
                    for s, x in zip(un_live_sorted, left_positions):
                        s.fx = x
            elif unconsumed_regular and anchors and len(previous_stitches) >= 2 and not all(t in ("k", "p") for t in row):
                prev_regular = [s for s in previous_stitches if s.type != "bo"]
                if len(prev_regular) >= 2:
                    spacing = (prev_regular[-1].fx - prev_regular[0].fx) / (len(prev_regular) - 1)
                else:
                    spacing = 0

                minA = min(anchors)
                maxA = max(anchors)
                centerA = sum(anchors) / len(anchors)
                if maxA <= 0:
                    sign = 1
                elif minA >= 0:
                    sign = -1
                else:
                    sign = 1 if centerA < 0 else -1
                shift = sign * spacing * len(unconsumed_regular)
                anchors = [a + shift for a in anchors]
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