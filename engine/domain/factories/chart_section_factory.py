from typing import Optional
from engine.data.models.chart_config import ChartConfig
from engine.row_manager import RowManager
from engine.node_manager import NodeManager
from engine.link_manager import LinkManager
from engine.position_calculator import PositionCalculator
from engine.marker_manager import MarkerManager
from engine.pattern_parser import PatternParser

# Note: StitchCounter and StitchCountValidator will be added later
# from engine.domain.models.stitch_counter import StitchCounter
# from engine.domain.models.stitch_count_validator import StitchCountValidator
from engine.chart_section import ChartSection


class ChartSectionFactory:
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
        # Note: PatternParser currently uses callbacks, but MarkerManager implements IMarkerProvider
        pattern_parser = self._create_pattern_parser(marker_manager)
        
        # Create validators and counters (will be implemented later)
        # stitch_counter = self._create_stitch_counter()
        # validator = self._create_validator()
        
        # Create ChartSection with dependency injection
        # For now, we'll use the existing ChartSection constructor
        # Later, we'll refactor ChartSection to accept all dependencies
        chart_section = ChartSection(
            name=config.name,
            start_side=config.start_side,
            sts=config.sts,
            rows=config.rows
        )
        
        # TODO: Once ChartSection is refactored to use DI, replace above with:
        # chart_section = ChartSection(
        #     name=config.name,
        #     start_side=config.start_side,
        #     row_manager=row_manager,
        #     node_manager=node_manager,
        #     link_manager=link_manager,
        #     position_calculator=position_calculator,
        #     marker_manager=marker_manager,
        #     pattern_parser=pattern_parser,
        #     stitch_counter=stitch_counter,
        #     validator=validator
        # )
        
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
        
        Note: Currently PatternParser uses callbacks. This will be refactored
        to use IMarkerProvider interface later.
        """
        return PatternParser(
            get_markers=marker_manager.get_markers,
            move_marker=marker_manager.move_marker,
            remove_marker=marker_manager.remove_marker
        )
    
    # TODO: Implement these when StitchCounter and validators are created
    # def _create_stitch_counter(self) -> StitchCounter:
    #     """Create a StitchCounter instance."""
    #     return StitchCounter()
    # 
    # def _create_validator(self) -> StitchCountValidator:
    #     """Create a StitchCountValidator instance."""
    #     return StitchCountValidator()