from typing import List, Dict, Any
from engine.data.models.chart_data import ChartData
from engine.data.models.node import Node
from engine.data.models.link import Link
from engine.presentation.viewmodels.chart_view_model import ChartViewModel
from engine.presentation.viewmodels.node_view_model import NodeViewModel
from engine.presentation.viewmodels.link_view_model import LinkViewModel


class ViewModelMapper:
    """Maps domain/data models to presentation view models."""
    
    def to_view_model(self, chart_data: ChartData) -> ChartViewModel:
        """Convert ChartData to ChartViewModel.

        RS and WS charts use the same x layout so that the visual output matches
        (e.g. WS-start "incorrect" chart looks like the RS-start "correct" chart).
        """
        node_view_models = [self.to_node_view_model(node) for node in chart_data.nodes]
        link_view_models = [self.to_link_view_model(link) for link in chart_data.links]
        
        return ChartViewModel(
            name=chart_data.name,
            nodes=node_view_models,
            links=link_view_models
        )
    
    def to_node_view_model(self, node: Node) -> NodeViewModel:
        """Convert Node to NodeViewModel."""
        stitch_type = node.type
        if stitch_type in ("work est", "work_est", "cont as est"):
            stitch_type = "k"  # fallback when work est was not expanded
        return NodeViewModel(
            id=node.id,
            type=stitch_type,
            x=node.fx,
            y=node.fy,
            row=node.row
        )
    
    def to_link_view_model(self, link: Link) -> LinkViewModel:
        """Convert Link to LinkViewModel."""
        return LinkViewModel(
            source_id=link.source,
            target_id=link.target
        )
    
    def view_model_to_dict(self, view_model: ChartViewModel) -> Dict[str, Any]:
        """
        Convert ChartViewModel to dictionary for JSON serialization.
        
        Args:
            view_model: ChartViewModel to convert
            
        Returns:
            Dictionary representation suitable for JSON
        """
        return {
            "name": view_model.name,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type,
                    "x": node.x,
                    "y": node.y,
                    "row": node.row
                }
                for node in view_model.nodes
            ],
            "links": [
                {
                    "source": link.source_id,
                    "target": link.target_id
                }
                for link in view_model.links
            ]
            # Links removed - not used for display
        }