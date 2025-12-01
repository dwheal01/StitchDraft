from typing import List
from engine.data.models.chart_data import ChartData
from engine.data.models.node import Node
from engine.data.models.link import Link
from engine.data.models.validation_results import ValidationResult

class ChartDataValidator:
    """Validates chart data structure and integrity."""
    
    def validate_chart_data(self, chart_data: ChartData) -> ValidationResult:
        """
        Validate a ChartData object.
        
        Args:
            chart_data: The chart data to validate
            
        Returns:
            ValidationResult indicating if data is valid
        """
        errors = []
        
        # Validate nodes
        node_errors = self._validate_nodes(chart_data.nodes)
        errors.extend(node_errors)
        
        # Validate links
        link_errors = self._validate_links(chart_data.links, chart_data.nodes)
        errors.extend(link_errors)
        
        # Validate basic structure
        if not chart_data.name or len(chart_data.name.strip()) == 0:
            errors.append("Chart name cannot be empty")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def _validate_nodes(self, nodes: List[Node]) -> List[str]:
        """Validate node structure."""
        errors = []
        node_ids = set()
        
        for node in nodes:
            # Check for duplicate IDs
            if node.id in node_ids:
                errors.append(f"Duplicate node ID: {node.id}")
            node_ids.add(node.id)
            
            # Validate required fields
            if not node.id or len(node.id.strip()) == 0:
                errors.append("Node ID cannot be empty")
            if not node.type or len(node.type.strip()) == 0:
                errors.append(f"Node {node.id} has empty type")
            if node.row < 0:
                errors.append(f"Node {node.id} has negative row number")
        
        return errors
    
    def _validate_links(self, links: List[Link], nodes: List[Node]) -> List[str]:
        """Validate link structure and integrity."""
        errors = []
        node_ids = {node.id for node in nodes}
        
        for link in links:
            # Check source exists
            if link.source not in node_ids:
                errors.append(f"Link references non-existent source node: {link.source}")
            
            # Check target exists
            if link.target not in node_ids:
                errors.append(f"Link references non-existent target node: {link.target}")
            
            # Check for self-loops (if not allowed)
            if link.source == link.target:
                errors.append(f"Link has self-loop: {link.source} -> {link.target}")
        
        return errors