from typing import List, TYPE_CHECKING
from engine.domain.interfaces.ichart_observer import IChartObserver
from engine.presentation.mappers.view_model_mapper import ViewModelMapper
from engine.data.repositories.chart_data_serializer import ChartDataSerializer

if TYPE_CHECKING:
    from engine.chart_section import ChartSection
    from engine.data.models.node import Node
    from engine.data.models.link import Link


class ChartVisualizationObserver(IChartObserver):
    """
    Observer that updates the visualization when chart state changes.
    This is a placeholder for the JavaScript implementation.
    """
    
    def __init__(self, view=None, mapper: ViewModelMapper = None):
        """
        Initialize the observer.
        
        Args:
            view: The visualization view (JavaScript/HTML, not used in Python)
            mapper: Mapper to convert domain models to view models
        """
        self.view = view  # Will be None for Python, used by JavaScript
        self.mapper = mapper or ViewModelMapper()
        self.serializer = ChartDataSerializer()
    
    def on_stitch_count_changed(self, chart: 'ChartSection', old_count: int, new_count: int) -> None:
        """Handle stitch count change event."""
        # In a real implementation, this would trigger a view update
        # For now, we just log or prepare data for JavaScript
        pass
    
    def on_node_added(self, chart: 'ChartSection', node: 'Node') -> None:
        """Handle node added event."""
        # In a real implementation, this would add the node to the visualization
        pass
    
    def on_link_added(self, chart: 'ChartSection', link: 'Link') -> None:
        """Handle link added event."""
        # In a real implementation, this would add the link to the visualization
        pass
    
    def on_row_added(self, chart: 'ChartSection', row: List[str]) -> None:
        """Handle row added event."""
        # In a real implementation, this would update the visualization
        pass
    
    def on_marker_placed(self, chart: 'ChartSection', side: str, position: int) -> None:
        """Handle marker placed event."""
        # In a real implementation, this would update marker visualization
        pass
    
    def on_chart_state_changed(self, chart: 'ChartSection', event) -> None:
        """Handle generic chart state change event."""
        # In a real implementation, this would refresh the visualization
        pass
    
    def get_chart_view_model(self, chart: 'ChartSection'):
        """
        Get the view model for a chart.
        This can be called by JavaScript to get updated chart data.
        """
        chart_data = self.serializer.serialize_to_chart_data(chart)
        return self.mapper.to_view_model(chart_data)