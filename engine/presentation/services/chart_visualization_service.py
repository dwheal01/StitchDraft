from typing import Optional, TYPE_CHECKING
from engine.domain.services.chart_service import ChartService
from engine.presentation.observers.chart_visualization_observer import ChartVisualizationObserver
from engine.presentation.mappers.view_model_mapper import ViewModelMapper
from engine.presentation.viewmodels.chart_view_model import ChartViewModel

if TYPE_CHECKING:
    from engine.chart_section import ChartSection


class ChartVisualizationService:
    """Service for chart visualization and presentation layer concerns."""
    
    def __init__(self, chart_service: ChartService):
        """
        Initialize ChartVisualizationService.
        
        Args:
            chart_service: ChartService for accessing chart operations
        """
        self.chart_service = chart_service
    
    def create_visualization_observer(
        self,
        view=None
    ) -> ChartVisualizationObserver:
        """
        Create a ChartVisualizationObserver instance.
        
        Args:
            view: Optional view object (for JavaScript integration)
            
        Returns:
            ChartVisualizationObserver instance
        """
        return ChartVisualizationObserver(view=view)
    
    def attach_visualization_observer(
        self,
        chart: 'ChartSection',
        observer: Optional[ChartVisualizationObserver] = None
    ) -> None:
        """
        Attach a visualization observer to a chart.
        If observer is not provided, creates a new one.
        
        Args:
            chart: ChartSection to attach observer to
            observer: Optional ChartVisualizationObserver (creates new one if None)
        """
        if observer is None:
            observer = self.create_visualization_observer()
        chart.attach(observer)
    
    def get_chart_view_model(self, chart: 'ChartSection') -> ChartViewModel:
        """
        Get the view model for a chart.
        
        Args:
            chart: ChartSection to convert
            
        Returns:
            ChartViewModel for the chart
        """
        chart_data = self.chart_service.export_chart(chart)
        mapper = ViewModelMapper()
        return mapper.to_view_model(chart_data)
