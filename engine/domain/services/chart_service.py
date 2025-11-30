from typing import List, Optional
from engine.domain.interfaces.ichart_repository import IChartRepository
from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine.data.models.chart_config import ChartConfig
from engine.data.models.chart_data import ChartData
from engine.data.models.expanded_pattern import ExpandedPattern
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.validation_results import ValidationResult
from engine.chart_section import ChartSection
from engine.data.repositories.chart_data_serializer import ChartDataSerializer
from engine.domain.models.pattern_processor import PatternProcessor
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.interfaces.ichart_observer import IChartObserver
from engine.presentation.observers.chart_visualization_observer import ChartVisualizationObserver


class ChartService:
    """Service layer for chart operations."""
    
    def __init__(
        self,
        chart_repository: IChartRepository,
        chart_factory: Optional[ChartSectionFactory] = None,
        serializer: Optional[ChartDataSerializer] = None,
        pattern_processor: Optional[PatternProcessor] = None,
        validation_chain: Optional[ValidationHandler] = None,
    ):
        """
        Initialize ChartService.
        
        Args:
            chart_repository: Repository for chart persistence
            chart_factory: Factory for creating ChartSection instances
            serializer: Serializer for converting ChartSection to ChartData
            pattern_processor: Processor for pattern expansion and validation (auto-created if None)
            validation_chain: Validation handler chain (auto-created if None)
        """
        self.chart_repository = chart_repository
        self.chart_factory = chart_factory or ChartSectionFactory()
        self.serializer = serializer or ChartDataSerializer()
        
        # Auto-create PatternProcessor if not provided
        if pattern_processor is None:
            self.pattern_processor = self._create_pattern_processor()
        else:
            self.pattern_processor = pattern_processor
        
        # Auto-create ValidationHandler chain if not provided
        if validation_chain is None:
            self.validation_chain = self._create_validation_chain()
        else:
            self.validation_chain = validation_chain
    
    def _create_pattern_processor(self) -> PatternProcessor:
        """
        Create a PatternProcessor instance.
        
        Returns:
            PatternProcessor instance
        """
        from engine.domain.models.pattern_parser import PatternParser
        from engine.domain.models.marker_manager import MarkerManager
        
        # Create MarkerManager and PatternParser
        marker_manager = MarkerManager()
        pattern_parser = PatternParser(marker_provider=marker_manager)
        
        # Create PatternProcessor
        return PatternProcessor(pattern_parser=pattern_parser)
    
    def _create_validation_chain(self) -> ValidationHandler:
        """
        Create a ValidationHandler chain.
        
        Returns:
            First handler in the validation chain
        """
        from engine.domain.models.validation.stitch_count_validation_handler import StitchCountValidationHandler
        from engine.domain.models.validation.pattern_validation_handler import PatternValidationHandler
        from engine.domain.models.validation.order_validation_handler import OrderValidationHandler
        
        # Create handlers
        stitch_handler = StitchCountValidationHandler()
        pattern_handler = PatternValidationHandler()
        order_handler = OrderValidationHandler()
        
        # Chain them together
        stitch_handler.set_next(pattern_handler).set_next(order_handler)
        
        return stitch_handler
    
    def process_pattern(
        self,
        chart: ChartSection,
        pattern: str
    ) -> ExpandedPattern:
        """
        Process a pattern using PatternProcessor.
        
        Args:
            chart: The chart section
            pattern: Pattern string to process
            
        Returns:
            ExpandedPattern result
            
        Raises:
            ValueError: If pattern is invalid
        """
        # Create PatternContext from chart state
        from engine.data.models.pattern_context import PatternContext
        
        context = PatternContext(
            available_stitches=chart.get_current_num_of_stitches(),
            side=chart.row_manager.last_row_side,
            markers=chart.marker_manager.get_markers(chart.row_manager.last_row_side),
            last_row_side=chart.row_manager.last_row_side,
            is_round=False  # Could be determined from chart state if needed
        )
        return self.pattern_processor.validate_and_expand(pattern, context)

    def create_chart(
        self,
        name: str,
        start_side: str,
        sts: int = 22,
        rows: int = 28
    ) -> ChartSection:
        """
        Create a new chart section.
        
        Args:
            name: Name of the chart
            start_side: Starting side ('RS' or 'WS')
            sts: Stitches per 4 inches
            rows: Rows per 4 inches
            
        Returns:
            Newly created ChartSection
        """
        config = ChartConfig(
            name=name,
            start_side=start_side,
            sts=sts,
            rows=rows
        )
        return self.chart_factory.create(config)
    
    def export_chart(self, chart: ChartSection) -> ChartData:
        """
        Export a chart to ChartData.
        
        Args:
            chart: ChartSection to export
            
        Returns:
            ChartData object
        """
        return self.serializer.to_chart_data(chart)
    
    def save_chart(self, chart: ChartSection) -> None:
        """
        Save a chart to the repository.
        
        Args:
            chart: ChartSection to save
        """
        chart_data = self.export_chart(chart)
        self.chart_repository.save_chart(chart_data)
    
    def load_chart(self, name: str) -> ChartData:
        """
        Load a chart from the repository.
        
        Args:
            name: Name of the chart to load
            
        Returns:
            ChartData object
        """
        return self.chart_repository.load_chart(name)
    
    def load_all_charts(self) -> List[ChartData]:
        """
        Load all charts from the repository.
        
        Returns:
            List of ChartData objects
        """
        return self.chart_repository.load_all_charts()
    
    def save_charts(self, charts: List[ChartSection]) -> None:
        """
        Save multiple charts to the repository.
        
        Args:
            charts: List of ChartSection objects to save
        """
        chart_data_list = [self.export_chart(chart) for chart in charts]
        self.chart_repository.save_charts(chart_data_list)
    
    def join_charts(self, chart1: ChartSection, chart2: ChartSection) -> ChartSection:
        """
        Join two chart sections together.
        
        Args:
            chart1: First chart section
            chart2: Second chart section to join to the first
            
        Returns:
            The joined chart (chart1 with chart2 joined to it)
        """
        return chart1.join(chart2)
    
    def validate_chart(
        self,
        chart: ChartSection,
        request: ValidationRequest
    ) -> ValidationResult:
        """
        Validate a chart using the validation chain.
        
        Args:
            chart: The chart section to validate
            request: ValidationRequest with validation parameters
            
        Returns:
            ValidationResult indicating if validation passed
        """
        # Ensure request has the chart
        if request.chart is None:
            request.chart = chart
        
        # Use validation chain if available
        if self.validation_chain:
            return self.validation_chain.handle(request)
        else:
            # Fallback: return valid result if no chain
            return ValidationResult(is_valid=True, errors=[])
    
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
        chart: ChartSection,
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