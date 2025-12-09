import json
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.chart_section import ChartSection

from engine.data.models.chart_data import ChartData
from engine.data.models.node import Node
from engine.data.models.link import Link


class ChartDataSerializer:
    """Serializes ChartSection to ChartData with deterministic ordering."""
    
    def serialize(self, chart: 'ChartSection') -> str:
        """
        Serialize a ChartSection to JSON string.
        
        Args:
            chart: ChartSection to serialize
            
        Returns:
            JSON string representation
        """
        chart_data = self.to_chart_data(chart)
        return json.dumps({
            "name": chart_data.name,
            "nodes": [self._node_to_dict(node) for node in chart_data.nodes],
            "links": [self._link_to_dict(link) for link in chart_data.links]
        }, indent=2)
    
    def serialize_deterministic(self, chart: 'ChartSection') -> str:
        """
        Serialize a ChartSection to JSON string with deterministic ordering.
        
        Args:
            chart: ChartSection to serialize
            
        Returns:
            JSON string representation with ordered nodes and links
        """
        chart_data = self.to_chart_data(chart)
        ordered_nodes = self.order_nodes(chart_data.nodes)
        ordered_links = self.order_links(chart_data.links)
        
        return json.dumps({
            "name": chart_data.name,
            "nodes": [self._node_to_dict(node) for node in ordered_nodes],
            "links": [self._link_to_dict(link) for link in ordered_links]
        }, indent=2)
    
    def to_chart_data(self, chart: 'ChartSection') -> ChartData:
        """
        Convert ChartSection to ChartData.
        
        Args:
            chart: ChartSection to convert
            
        Returns:
            ChartData object
        """
        # Use public properties to access nodes and links (returns defensive copy)
        nodes = chart.nodes
        links = chart.links
        
        return ChartData(
            name=chart.name,
            nodes=nodes,
            links=links
        )
    
    def order_nodes(self, nodes: List[Node]) -> List[Node]:
        """
        Order nodes deterministically.
        
        Ordering: by row (ascending), then by fx (ascending), then by id.
        
        Args:
            nodes: List of nodes to order
            
        Returns:
            Ordered list of nodes
        """
        return sorted(
            nodes,
            key=lambda n: (
                n.row,
                n.fx if hasattr(n, 'fx') and n.fx is not None else float('inf'),
                n.id
            )
        )
    
    def order_links(self, links: List[Link]) -> List[Link]:
        """
        Order links deterministically.
        
        Ordering: by source id, then by target id.
        
        Args:
            links: List of links to order
            
        Returns:
            Ordered list of links
        """
        return sorted(
            links,
            key=lambda l: (l.source, l.target)
        )
    
    def _convert_nodes(self, nodes: List[Node]) -> List[Node]:
        """Convert nodes (already Node objects, return as-is)."""
        return list(nodes)
    
    def _convert_links(self, links: List[Link]) -> List[Link]:
        """Convert links (already Link objects, return as-is)."""
        return list(links)
    
    def _node_to_dict(self, node: Node) -> Dict[str, Any]:
        """Convert Node dataclass to dictionary."""
        result = {
            "id": node.id,
            "type": node.type,
            "row": node.row
        }
        # Only include fx/fy if they're not None/0 (for strand nodes)
        if node.fx != 0.0 or node.fy != 0.0:
            result["fx"] = node.fx
            result["fy"] = node.fy
        return result
    
    def _link_to_dict(self, link: Link) -> Dict[str, Any]:
        """Convert Link dataclass to dictionary."""
        return {
            "source": link.source,
            "target": link.target
        }
        
    def serialize_deterministic_from_chart_data(self, chart_data: ChartData) -> str:
        """
        Serialize ChartData to JSON string with deterministic ordering.
        
        Args:
            chart_data: ChartData to serialize
            
        Returns:
            JSON string representation
        """
        ordered_nodes = self.order_nodes(chart_data.nodes)
        ordered_links = self.order_links(chart_data.links)
        
        return json.dumps({
            "name": chart_data.name,
            "nodes": [self._node_to_dict(node) for node in ordered_nodes]
            # Links removed - not used for display
        }, indent=2)
    
    def convert_single_node(self, node_dict: Dict[str, Any]) -> Node:
        """Convert a single node dictionary to Node object."""
        return Node(
            id=str(node_dict.get("id", "")),
            type=str(node_dict.get("type", "")),
            row=int(node_dict.get("row", 0)),
            fx=float(node_dict.get("fx", 0.0)) if node_dict.get("fx") is not None else 0.0,
            fy=float(node_dict.get("fy", 0.0)) if node_dict.get("fy") is not None else 0.0
        )
    
    def convert_single_link(self, link_dict: Dict[str, Any]) -> Link:
        """Convert a single link dictionary to Link object."""
        return Link(
            source=str(link_dict.get("source", "")),
            target=str(link_dict.get("target", ""))
        )