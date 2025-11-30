from typing import List, Optional
from engine.domain.interfaces.ichart_repository import IChartRepository
from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine.data.models.chart_config import ChartConfig
from engine.data.models.chart_data import ChartData
from engine.data.models.expanded_pattern import ExpandedPattern
from engine.chart_section import ChartSection
from engine.data.repositories.chart_data_serializer import ChartDataSerializer
from engine.domain.models.pattern_processor import PatternProcessor
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.interfaces.ichart_observer import IChartObserver


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
            pattern_processor: Processor for pattern expansion and validation
            validation_chain: Validation handler chain
        """
        self.chart_repository = chart_repository
        self.chart_factory = chart_factory or ChartSectionFactory()
        self.serializer = serializer or ChartDataSerializer()
        self.pattern_processor = pattern_processor
        self.validation_chain = validation_chain
    
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
            ValueError: If PatternProcessor is not available or pattern is invalid
         """
         if not self.pattern_processor:
            raise ValueError("PatternProcessor not available in ChartService")
         
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
    
    # TODO: Implement these when PatternProcessor and ValidationHandler are created
    # def process_pattern(self, chart: ChartSection, pattern: str) -> None:
    #     """Process a pattern string and update the chart."""
    #     if self.pattern_processor:
    #         context = PatternContext(...)
    #         expanded = self.pattern_processor.expand_pattern(pattern, context)
    #         # Apply expanded pattern to chart
    #     else:
    #         # Fallback to direct chart.add_row
    #         chart.add_row(pattern)
    # 
    # def validate_chart(self, chart: ChartSection, request: ValidationRequest) -> ValidationResult:
    #     """Validate a chart using the validation chain."""
    #     if self.validation_chain:
    #         return self.validation_chain.handle(request)
    #     else:
    #         return ValidationResult(is_valid=True, errors=[])
    # 
    def attach_visualization_observer(self, chart: ChartSection, observer) -> None:
      """Attach a visualization observer to a chart."""
      chart.attach(observer)