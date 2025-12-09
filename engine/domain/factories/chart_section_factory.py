from typing import Optional
from engine.data.models.chart_config import ChartConfig
from engine.domain.models.row_manager import RowManager
from engine.domain.models.node_manager import NodeManager
from engine.domain.models.link_manager import LinkManager
from engine.domain.models.position_calculator import PositionCalculator
from engine.domain.models.marker_manager import MarkerManager
from engine.domain.models.pattern_parser import PatternParser
from engine.chart_section import ChartSection
from engine.domain.models.chart_queries import ChartQueries
from engine.domain.models.chart_generator import ChartGenerator
from engine.domain.models.operation_registry import OperationRegistry
from engine.domain.models.operations.place_on_hold_operation import PlaceOnHoldOperation
from engine.domain.models.operations.place_on_needle_operation import PlaceOnNeedleOperation
from engine.domain.models.operations.join_operation import JoinOperation
from engine.domain.models.stitch_counter import StitchCounter
from engine.domain.models.validators.stitch_count_validator import StitchCountValidator
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.models.validation.stitch_count_validation_handler import StitchCountValidationHandler
from engine.domain.models.validation.pattern_validation_handler import PatternValidationHandler
from engine.domain.models.validation.order_validation_handler import OrderValidationHandler

# Note: StitchCounter and StitchCountValidator will be added later
# from engine.domain.models.stitch_counter import StitchCounter
# from engine.domain.models.stitch_count_validator import StitchCountValidator


class ChartSectionFactory:
    def _create_stitch_counter(self) -> StitchCounter:
      """Create a StitchCounter instance."""
      return StitchCounter()

    def _create_validator(self) -> StitchCountValidator:
      """Create a StitchCountValidator instance."""
      return StitchCountValidator()

    def _create_validation_chain(self) -> ValidationHandler:
        """Create and chain validation handlers using ValidationChainBuilder."""
        from engine.domain.models.validation.validation_chain_builder import ValidationChainBuilder
        
        builder = ValidationChainBuilder()
        builder.add_stitch_count_validation() \
               .add_pattern_validation() \
               .add_order_validation() \
               .add_chart_data_validation()
        
        chain = builder.build()
        if chain is None:
            raise ValueError("Validation chain must have at least one handler")
        
        return chain
 
    """Factory for creating ChartSection instances with all dependencies."""
    
    def create(self, config: ChartConfig) -> ChartSection:
        """
        Create a ChartSection with the given configuration.
        
        Args:
            config: ChartConfig with name, start_side, sts, and rows
            
        Returns:
            A fully configured ChartSection instance
        """
        # Create all managers
        row_manager = self._create_row_manager(config.start_side)
        node_manager = self._create_node_manager()
        link_manager = self._create_link_manager()
        position_calculator = self._create_position_calculator(config.sts, config.rows)
        marker_manager = self._create_marker_manager()
        
        # Create PatternParser with MarkerManager as IMarkerProvider
        pattern_parser = self._create_pattern_parser(marker_manager)
        
        # Create new refactored components
        chart_generator = self._create_chart_generator(position_calculator)
        operation_registry = self._create_operation_registry()
        
        # Create validators and counters
        stitch_counter = self._create_stitch_counter()
        validator = self._create_validator()
        validation_chain = self._create_validation_chain()
        
        # ChartQueries can now be created before ChartSection since it doesn't need it
        chart_queries = self._create_chart_queries(node_manager, row_manager, marker_manager)
        
        # Create ChartSection with dependency injection
        chart_section = ChartSection(
            name=config.name,
            start_side=config.start_side,
            row_manager=row_manager,
            node_manager=node_manager,
            link_manager=link_manager,
            position_calculator=position_calculator,
            marker_manager=marker_manager,
            pattern_parser=pattern_parser,
            chart_generator=chart_generator,
            operation_registry=operation_registry,
            stitch_counter=stitch_counter,
            validator=validator,
            validation_chain=validation_chain,
            chart_queries=chart_queries
        )
        
        return chart_section
    
    def create_with_defaults(
        self, 
        name: str, 
        start_side: str, 
        sts: int = 22, 
        rows: int = 28
    ) -> ChartSection:
        """
        Create a ChartSection with default gauge settings.
        
        Args:
            name: Name of the chart section
            start_side: Starting side ('RS' or 'WS')
            sts: Stitches per 4 inches (default: 22)
            rows: Rows per 4 inches (default: 28)
            
        Returns:
            A fully configured ChartSection instance
        """
        config = ChartConfig(
            name=name,
            start_side=start_side,
            sts=sts,
            rows=rows
        )
        return self.create(config)
    
    def _create_row_manager(self, start_side: str) -> RowManager:
        """Create a RowManager instance."""
        return RowManager(start_side)
    
    def _create_node_manager(self) -> NodeManager:
        """Create a NodeManager instance."""
        return NodeManager()
    
    def _create_link_manager(self) -> LinkManager:
        """Create a LinkManager instance."""
        return LinkManager()
    
    def _create_position_calculator(self, sts: int, rows: int) -> PositionCalculator:
        """Create and configure a PositionCalculator instance."""
        calculator = PositionCalculator()
        calculator.set_guage(sts, rows)
        return calculator
    
    def _create_marker_manager(self) -> MarkerManager:
        """Create a MarkerManager instance."""
        return MarkerManager()
    
    def _create_pattern_parser(self, marker_manager: MarkerManager) -> PatternParser:
      """
      Create a PatternParser instance with MarkerManager as IMarkerProvider.
      
      Args:
         marker_manager: MarkerManager instance (implements IMarkerProvider)
         
      Returns:
         PatternParser instance
      """
      return PatternParser(marker_provider=marker_manager)
    
    def _create_chart_generator(self, position_calculator: PositionCalculator) -> ChartGenerator:
        """Create a ChartGenerator instance."""
        return ChartGenerator(position_calculator=position_calculator)
    
    def _create_chart_queries(
        self,
        node_manager: NodeManager,
        row_manager: RowManager,
        marker_manager: MarkerManager
    ) -> ChartQueries:
        """Create a ChartQueries instance."""
        return ChartQueries(
            node_manager=node_manager,
            row_manager=row_manager,
            marker_manager=marker_manager
        )
    
    def _create_operation_registry(self) -> OperationRegistry:
        """Create and configure an OperationRegistry with all operations."""
        from engine.domain.models.operations.cast_on_operation import CastOnOperation
        from engine.domain.models.operations.add_row_operation import AddRowOperation        
        from engine.domain.models.operations.cast_on_additional_operation import CastOnAdditionalOperation
        
        registry = OperationRegistry()
        
        # Register all operations
        registry.register('place_on_hold', PlaceOnHoldOperation())
        registry.register('place_on_needle', PlaceOnNeedleOperation())
        registry.register('join', JoinOperation())
        registry.register('cast_on', CastOnOperation())
        registry.register('add_row', AddRowOperation())
        registry.register('cast_on_additional', CastOnAdditionalOperation())
                
        return registry
