from typing import List, Optional, TYPE_CHECKING
from engine.domain.interfaces.ichart_observer import IChartObserver
from engine.presentation.mappers.view_model_mapper import ViewModelMapper
from engine.data.repositories.chart_data_serializer import ChartDataSerializer
from engine.presentation.viewmodels.chart_view_model import ChartViewModel

if TYPE_CHECKING:
    from engine.chart_section import ChartSection
    from engine.data.models.node import Node
    from engine.data.models.link import Link


class ChartVisualizationObserver(IChartObserver):
    """
    Observer that updates the visualization when chart state changes.
    Converts domain models to view models for presentation layer.
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
        self._last_view_model: Optional[ChartViewModel] = None
    
    def on_stitch_count_changed(self, chart: 'ChartSection', old_count: int, new_count: int) -> None:
        """Handle stitch count change event."""
        # Update view model when stitch count changes
        self._last_view_model = self.get_chart_view_model(chart)
        # In a real implementation, this would trigger a view update
        # For now, we just prepare the view model
    
    def on_node_added(self, chart: 'ChartSection', node: 'Node') -> None:
        """Handle node added event."""
        # Update view model when node is added
        self._last_view_model = self.get_chart_view_model(chart)
        # In a real implementation, this would add the node to the visualization
    
    def on_link_added(self, chart: 'ChartSection', link: 'Link') -> None:
        """Handle link added event."""
        # Update view model when link is added
        self._last_view_model = self.get_chart_view_model(chart)
        # In a real implementation, this would add the link to the visualization
    
    def on_row_added(self, chart: 'ChartSection', row: List[str]) -> None:
        """Handle row added event."""
        # Update view model when row is added
        self._last_view_model = self.get_chart_view_model(chart)
        # In a real implementation, this would update the visualization
    
    def on_marker_placed(self, chart: 'ChartSection', side: str, position: int) -> None:
        """Handle marker placed event."""
        # Update view model when marker is placed
        self._last_view_model = self.get_chart_view_model(chart)
        # In a real implementation, this would update marker visualization
    
    def on_chart_state_changed(self, chart: 'ChartSection', event) -> None:
        """Handle generic chart state change event."""
        # Update view model on any state change
        self._last_view_model = self.get_chart_view_model(chart)
        # In a real implementation, this would refresh the visualization
    
    def get_chart_view_model(self, chart: 'ChartSection') -> ChartViewModel:
        """
        Get the view model for a chart.
        This can be called by JavaScript to get updated chart data.
        
        Args:
            chart: ChartSection to convert
            
        Returns:
            ChartViewModel for the chart
        """
        chart_data = self.serializer.to_chart_data(chart)  # Fixed: was serialize_to_chart_data
        return self.mapper.to_view_model(chart_data)
    
    def get_last_view_model(self) -> Optional[ChartViewModel]:
        """
        Get the last computed view model.
        
        Returns:
            Last ChartViewModel or None if no updates have occurred
        """
        return self._last_view_model