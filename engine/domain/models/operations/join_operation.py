from typing import Dict
from dataclasses import replace
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.chart_section import ChartSection
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class JoinOperation(IChartOperation):
    """Operation to join two chart sections."""
    
    def execute(self, chart: ChartSection, params: Dict) -> ChartSection:
        """Join this chart section with another chart section."""
        other = params.get('other_chart')
        if not other:
            raise ValueError("No other chart provided for join operation")
        
        # Use actual geometry: place right chart to the right (x) and align bottom rows (y).
        # Join means last row of left + last row of right form one continuous row; tops need not align.
        spacing = chart.position_calculator.DEFAULT_SPACING
        self_last_row = [n for n in chart.node_manager.get_last_row_stitches() if n.type != "strand"]
        other_last_row_stitches = [n for n in other.node_manager.get_last_row_stitches() if n.type != "strand"]
        if not self_last_row or not other_last_row_stitches:
            raise ValueError("Cannot join: one or both charts have no stitch nodes in the last row")
        rightmost_fx = max(n.fx for n in self_last_row)
        leftmost_other_fx = min(n.fx for n in other_last_row_stitches)
        new_fx = rightmost_fx + spacing
        x_offset = new_fx - leftmost_other_fx
        # Align bottoms: same y for both last rows so a following add_row works across all stitches
        self_last_row_y = self_last_row[0].fy
        other_last_row_y = other_last_row_stitches[0].fy
        y_offset = self_last_row_y - other_last_row_y
        
        # Get the current node counter from the main chart
        # This will be the starting point for remapping the other chart's node IDs
        base_node_counter = chart.node_manager.get_node_counter()
        
        # Create a mapping from old IDs to new IDs
        id_mapping = {}
        
        # Offset all nodes in other chart and remap their IDs
        # Following the reference implementation: iterate through nodes and apply offset
        # IMPORTANT: Get last_row_stitches BEFORE getting nodes, since they share references
        other_last_row = other.node_manager.get_last_row_stitches()
        # Get nodes using the public API (defensive copy is fine since we create new Node objects)
        other_nodes = other.node_manager.get_nodes()
        
        # Create a mapping from old node ID to new Node object
        # This ensures we can update last_row_stitches correctly with the same Node objects
        old_id_to_new_node = {}
        offset_nodes = []
        new_node_counter = base_node_counter
        
        # Process ALL nodes and apply offset to non-strand nodes (like reference implementation)
        # First pass: process stitch nodes to build id_mapping
        for stitch in other_nodes:
            if stitch.type != "strand":
                old_id = stitch.id
                # Regular stitch node: remap ID and apply offset to fx
                new_id = f"{new_node_counter}"
                id_mapping[old_id] = new_id
                new_node_counter += 1
                # Apply x offset (right of left chart) and y offset (align bottom rows)
                new_fx = stitch.fx + x_offset
                new_fy = stitch.fy + y_offset
                new_node = replace(stitch, id=new_id, fx=new_fx, fy=new_fy)
                old_id_to_new_node[old_id] = new_node
                offset_nodes.append(new_node)
        
        # Second pass: process strand nodes (they come after their associated stitch nodes)
        for stitch in other_nodes:
            if stitch.type == "strand":
                old_id = stitch.id
                # Strand nodes: extract the base number from old ID (e.g., "5s" -> "5")
                if old_id.endswith("s"):
                    old_base = old_id[:-1]
                    # Map to the new stitch ID that corresponds to this base
                    if old_base in id_mapping:
                        # The stitch node was already remapped, use its new ID
                        new_strand_id = f"{id_mapping[old_base]}s"
                        id_mapping[old_id] = new_strand_id
                        # Strand nodes: offset fy so they stay with their row (align bottoms)
                        new_node = replace(stitch, id=new_strand_id, fy=stitch.fy + y_offset)
                        old_id_to_new_node[old_id] = new_node
                        offset_nodes.append(new_node)
                    else:
                        # This strand's stitch hasn't been processed - this shouldn't happen
                        # but if it does, skip remapping and keep original ID, still offset fy
                        offset_nodes.append(replace(stitch, fy=stitch.fy + y_offset))
                        old_id_to_new_node[old_id] = offset_nodes[-1]
                        # Don't add to id_mapping to avoid invalid mappings
                else:
                    # Strand without "s" suffix - shouldn't happen; still offset fy
                    offset_nodes.append(replace(stitch, fy=stitch.fy + y_offset))
                    old_id_to_new_node[old_id] = offset_nodes[-1]
        
        final_offset_nodes = offset_nodes
        
        # Replace nodes in other chart using mutator method
        other.node_manager.replace_nodes(final_offset_nodes)
        
        # Also offset and remap last_row_stitches using the node ID mapping
        # This ensures we use the same new Node objects that are in the nodes list
        offset_last_row = []
        for stitch in other_last_row:
            # Look up the new node object by old ID (which has offset already applied)
            new_node = old_id_to_new_node.get(stitch.id, stitch)
            offset_last_row.append(new_node)
        
        other.node_manager.set_last_row_stitches(offset_last_row)
        
        # Remap links to use new node IDs
        # Build a set of all valid node IDs from the final offset nodes
        valid_node_ids = {node.id for node in final_offset_nodes}
        other_links = other.link_manager.get_links()
        remapped_links = []
        for link in other_links:
            # Get new IDs from mapping, or keep original if not in mapping
            new_source = id_mapping.get(link.source, link.source)
            new_target = id_mapping.get(link.target, link.target)
            # Only include links where both source and target reference valid nodes
            # (nodes that exist in the final offset_nodes list)
            if new_source in valid_node_ids and new_target in valid_node_ids:
                remapped_links.append(replace(link, source=new_source, target=new_target))
            # Skip links that reference invalid nodes (they shouldn't exist, but handle gracefully)
        other.link_manager.replace_links(remapped_links)
        
        # Merge markers using accessor methods
        chart_last_row_count = len(chart.node_manager.get_last_row_stitches())
        other_markers_rs = other.marker_manager.get_markers_rs()
        other_markers_ws = other.marker_manager.get_markers_ws()
        
        for marker in other_markers_rs:
            chart.marker_manager.add_marker_to_rs(marker + chart_last_row_count)
        for marker in other_markers_ws:
            chart.marker_manager.add_marker_to_ws(marker + chart_last_row_count)
        
        # Merge nodes using mutator methods
        chart.node_manager.extend_nodes(final_offset_nodes)
        chart.node_manager.increment_node_counter(other.node_manager.get_node_counter())
        chart.node_manager.append_to_last_row_stitches(offset_last_row)
        
        # After appending, update stitch count so the joined last row reflects
        # stitches from both charts. This ensures get_current_num_of_stitches()
        # and subsequent operations (e.g. add_row) see the full joined row.
        old_count = chart.node_manager.get_last_row_produced()
        # Recompute based on the actual last-row stitches (exclude bound‑off stitches).
        combined_last_row = chart.node_manager.get_last_row_stitches()
        new_count = sum(1 for stitch in combined_last_row if stitch.type != "bo")
        chart.node_manager.set_last_row_produced(new_count)
        # Keep the stitch counter in sync so validation stays consistent.
        produced_delta = max(0, new_count - old_count)
        if produced_delta:
            chart.stitch_counter.record_operation("join", 0, produced_delta)
            chart._notify_stitch_count_changed(old_count, new_count)
        
        # Merge links from other chart
        chart.link_manager.extend_links(remapped_links)
        
        return chart
    
    def validate(self, params: Dict, context: PatternContext) -> ValidationResult:
        """Validate the join operation."""
        errors = []
        other = params.get('other_chart')
        
        if not other:
            errors.append("No other chart provided for join operation")
        elif not hasattr(other, 'node_manager'):
            errors.append("Invalid chart provided - missing node_manager")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )