from typing import List, Set
from engine.data.models.validation_results import ValidationResult
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.node import Node
from engine.data.models.link import Link

class OrderValidator:
    """Validates node and link ordering and integrity."""
    
    def validate_order(
        self,
        nodes: List[Node],
        links: List[Link]
    ) -> ValidationResult:
        """
        Validate that nodes and links are properly ordered.
        
        Args:
            nodes: List of nodes
            links: List of links
            
        Returns:
            ValidationResult indicating if order is valid
        """
        errors = []
        
        # Check that nodes are ordered by row
        for i in range(len(nodes) - 1):
            if nodes[i].row > nodes[i + 1].row:
                errors.append(f"Nodes not ordered by row: node {i} has row {nodes[i].row}, node {i+1} has row {nodes[i+1].row}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_link_integrity(
        self,
        links: List[Link],
        nodes: List[Node]
    ) -> ValidationResult:
        """
        Validate that all links reference existing nodes.
        
        Args:
            links: List of links
            nodes: List of nodes
            
        Returns:
            ValidationResult indicating if links are valid
        """
        errors = []
        node_ids: Set[str] = {node.id for node in nodes}
        
        for link in links:
            if link.source not in node_ids:
                errors.append(f"Link source '{link.source}' does not exist in nodes")
            if link.target not in node_ids:
                errors.append(f"Link target '{link.target}' does not exist in nodes")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )