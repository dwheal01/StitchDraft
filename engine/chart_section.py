from typing import List, Dict, Union, Optional
from engine.domain.models.row_manager import RowManager
from engine.domain.models.node_manager import NodeManager
from engine.domain.models.link_manager import LinkManager
from engine.domain.models.position_calculator import PositionCalculator
from engine.domain.models.pattern_parser import PatternParser
from engine.domain.models.marker_manager import MarkerManager
from engine.domain.models.chart_queries import ChartQueries
from engine.domain.models.chart_generator import ChartGenerator
from engine.domain.models.operation_registry import OperationRegistry
from engine.domain.models.stitch_counter import StitchCounter
from engine.domain.models.validators.stitch_count_validator import StitchCountValidator
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.interfaces.ichart_observer import IChartObserver
from engine.domain.interfaces.ichart_operation import IChartOperation
from engine.data.models.chart_state_event import ChartStateEvent
from engine.data.models.node import Node
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext

class ChartSection:
    """Main class that coordinates knitting chart generation."""
    
    def __init__(
        self,
        name: str,
        start_side: str,
        operation_registry: OperationRegistry,
        row_manager: RowManager,
        # Dependencies - can be injected or created
        node_manager: NodeManager,
        link_manager: LinkManager,
        position_calculator: PositionCalculator,
        marker_manager: MarkerManager,
        pattern_parser: PatternParser,
        chart_generator: ChartGenerator,
        stitch_counter: StitchCounter,
        validator: StitchCountValidator,
        validation_chain: Optional[ValidationHandler] = None,
        chart_queries: Optional[ChartQueries] = None,  # Set after construction
    ):
        self.name = name
        self.start_side = start_side
        self.observers: List[IChartObserver] = []
        
         # All dependencies are required - no default creation
        self.row_manager = row_manager
        self.node_manager = node_manager
        self.link_manager = link_manager
        self.position_calculator = position_calculator
        self.marker_manager = marker_manager
        self.pattern_parser = pattern_parser
        self.chart_generator = chart_generator
        self.operation_registry = operation_registry
        self.stitch_counter = stitch_counter
        self.validator = validator
        self.validation_chain = validation_chain
        
        # ChartQueries now only needs managers, no circular dependency
        if chart_queries is not None:
            self.chart_queries = chart_queries
        else:
            self.chart_queries = ChartQueries(
                node_manager=self.node_manager,
                row_manager=self.row_manager,
                marker_manager=self.marker_manager
            )
            
    # Observer management
    def attach(self, observer: IChartObserver) -> None:
        """Attach an observer to receive state change notifications."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def detach(self, observer: IChartObserver) -> None:
        """Detach an observer."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, event: ChartStateEvent) -> None:
        """Notify all observers of a state change."""
        for observer in self.observers:
            observer.on_chart_state_changed(self, event)
    
    # Query methods - delegate to ChartQueries
    def get_current_row_num(self) -> int:
        """Get the current row number."""
        return self.chart_queries.get_current_row_num()
    
    def get_current_num_of_stitches(self) -> int:
        """Get the current number of stitches."""
        return self.chart_queries.get_current_num_of_stitches()
    
    def get_stitches_on_hold(self) -> List[Node]:
        """Get stitches currently on hold."""
        return self.chart_queries.get_stitches_on_hold()
    
    def get_row_num(self, side: str) -> int:
        """Get the row number for a given side."""
        return self.chart_queries.get_row_num(side)
    
    def get_markers(self, side: str) -> List[int]:
        """Get all marker positions for a given side."""
        return self.chart_queries.get_markers(side)
    
    def find_last_stitch(self) -> Node:
        """Get the rightmost stitch position if last row is RS, otherwise leftmost stitch position if last row is WS."""
        return self.chart_queries.find_last_stitch()
    
    def find_first_stitch(self) -> Node:
        """Get the leftmost stitch position if last row is WS, otherwise rightmost stitch position if last row is RS."""
        return self.chart_queries.find_first_stitch()
    
    def _validate_and_execute_operation(
        self, 
        operation_name: str, 
        params: Dict,
        consumed: Optional[int] = None,
        produced: Optional[int] = None
    ) -> 'ChartSection':
        """
        Validate and execute an operation with stitch count consistency checks.
        
        Args:
            operation_name: Name of the operation to execute
            params: Parameters for the operation
            consumed: Number of stitches consumed (for validation)
            produced: Number of stitches produced (for validation)
            
        Returns:
            ChartSection after operation execution
            
        Raises:
            ValueError: If validation fails
        """
        op = self.operation_registry.get_operation(operation_name)
        
        # Create PatternContext for validation
        last_row_side = self.row_manager.get_last_row_side()
        context = PatternContext(
            available_stitches=self.get_current_num_of_stitches(),
            side=last_row_side,
            markers=self.marker_manager.get_markers(last_row_side),
            last_row_side=last_row_side,
            is_round=params.get('is_round', False)
        )
        
        # Validate operation using operation's validate method
        validation_result = op.validate(params, context)
        if not validation_result.is_valid:
            raise ValueError(f"Operation '{operation_name}' validation failed: {', '.join(validation_result.errors)}")
        
        # Validate stitch count using validation chain if available
        if self.validation_chain is not None and (consumed is not None or produced is not None):
            request = ValidationRequest(
                chart=self,
                operation=operation_name,
                context=context,
                consumed=consumed,
                produced=produced,
                pattern=params.get('pattern')
            )
            chain_result = self.validation_chain.handle(request)
            if not chain_result.is_valid:
                raise ValueError(f"Stitch count validation failed: {', '.join(chain_result.errors)}")
        
        # Execute the operation
        result = op.execute(self, params)
        
        # Post-execution consistency check
        self._verify_stitch_count_consistency()
        
        return result
    
    def _verify_stitch_count_consistency(self) -> None:
        """
        Verify that stitch counter matches actual stitch count after operation.
        Raises ValueError if inconsistency is detected.
        """
        if self.validator is not None:
            consistency_result = self.validator.validate_consistency(self)
            if not consistency_result.is_valid:
                raise ValueError(
                    f"Stitch count inconsistency detected after operation: {', '.join(consistency_result.errors)}"
                )
    
    # Operations - delegate to OperationRegistry or implement directly
    def place_on_hold(self) -> List[Node]:
        """Place the unconsumed stitches on hold and return the previous stitches on hold."""
        previous_stitches_on_hold = self.node_manager.get_stitches_on_hold()
        
        # Calculate stitches to be placed on hold for validation
        stitches_to_hold = self.node_manager.get_last_row_unconsumed_stitches()
        count_on_hold = sum(1 for stitch in stitches_to_hold if stitch.type != "bo")
        
        self._validate_and_execute_operation(
            'place_on_hold', 
            {},
            consumed=count_on_hold,
            produced=0
        )
        return previous_stitches_on_hold
    
    def place_on_needle(self, stitches_on_hold: List[Node], join_side: str) -> None:
        """Place the stitches on needle."""
        # Calculate stitches to be placed on needle for validation
        count_on_needle = sum(1 for stitch in stitches_on_hold if stitch.type != "bo")
        
        self._validate_and_execute_operation(
            'place_on_needle',
            {'stitches_on_hold': stitches_on_hold, 'join_side': join_side},
            consumed=0,
            produced=count_on_needle
        )
    
    # Node creation - delegate to ChartGenerator
    def add_nodes(self, row: List[str], side: str, isRound: bool = False) -> None:
        """Add nodes for a new row."""
        row_num = self.get_row_num(side)
        
        # Use ChartGenerator to create nodes
        self.chart_generator.create_nodes_for_row(self, row, side, row_num)
        self.row_manager.add_row(row, isRound)
        
        # Notify observers
        self._notify_row_added(row)
        self._notify_node_added()
    
    def add_round(self, pattern: Union[str, int]) -> 'ChartSection':
        """Add a round to the pattern."""
        self.add_row(pattern, True)
        return self
    
    def add_row(self, pattern: Union[str, int], isRound: bool = False) -> 'ChartSection':
        """Add a new row to the pattern."""
        op = self.operation_registry.get_operation('add_row')
        
        # Create PatternContext for basic validation
        last_row_side = self.row_manager.get_last_row_side()
        context = PatternContext(
            available_stitches=self.get_current_num_of_stitches(),
            side=last_row_side,
            markers=self.marker_manager.get_markers(last_row_side),
            last_row_side=last_row_side,
            is_round=isRound
        )
        
        # Validate operation parameters (pattern exists, etc.)
        validation_result = op.validate({'pattern': pattern, 'is_round': isRound}, context)
        if not validation_result.is_valid:
            raise ValueError(f"Operation 'add_row' validation failed: {', '.join(validation_result.errors)}")
        
        # Execute operation (it will validate stitch counts after pattern expansion)
        result = op.execute(self, {'pattern': pattern, 'is_round': isRound})
        
        # Post-execution consistency check
        self._verify_stitch_count_consistency()
        
        return result
        
    def cast_on_start(self, count: int) -> None:
        """Cast on the specified number of stitches."""
        self._validate_and_execute_operation(
            'cast_on',
            {'count': count},
            consumed=0,
            produced=count
        )
    
    def cast_on(self, count: int) -> 'ChartSection':
        """Cast on additional stitches to extend the current chart."""
        return self._validate_and_execute_operation(
            'cast_on_additional',
            {'count': count},
            consumed=0,
            produced=count
        )
    
    def join(self, other: 'ChartSection') -> 'ChartSection':
        """Join this chart section with another chart section."""
        # Join operation doesn't change stitch counts, just merges charts
        op = self.operation_registry.get_operation('join')
        return op.execute(self, {'other_chart': other})
        
    def place_marker(self, side: str, position: int) -> None:
        """Place a marker at the specified needle position."""
        last_row_stitches = self.node_manager.get_last_row_stitches()
        self.marker_manager.add_marker(side, position, len(last_row_stitches))
        self._notify_marker_placed(side, position)
    
    def repeat_rows(self, row_patterns: List[str], count: int) -> None:
        """Repeat a sequence of row patterns a specified number of times."""
        for _ in range(count):
            for pattern in row_patterns:
                self.add_row(pattern)
    
    def repeat_rounds(self, row_patterns: List[str], count: int) -> None:
        """Repeat a sequence of row patterns a specified number of times."""
        for _ in range(count):
            for pattern in row_patterns:
                self.add_round(pattern)
    
    @property
    def nodes(self):
        """Get nodes from the node manager (returns defensive copy)."""
        return self.node_manager.get_nodes()
    
    @property
    def links(self):
        """Get links from the link manager (returns defensive copy)."""
        return self.link_manager.get_links()
    
    @property
    def rows(self):
        """Get rows from the row manager (returns defensive copy)."""
        return self.row_manager.get_rows()
    
    # Observer notification methods
    def _notify_stitch_count_changed(self, old_count: int, new_count: int) -> None:
        """Notify observers of stitch count change."""
        for observer in self.observers:
            observer.on_stitch_count_changed(self, old_count, new_count)
    
    def _notify_node_added(self, node: Optional[Node] = None) -> None:
        """Notify observers of node addition."""
        for observer in self.observers:
            if node:
                observer.on_node_added(self, node)
    
    def _notify_link_added(self, link: Dict) -> None:
        """Notify observers of link addition."""
        for observer in self.observers:
            observer.on_link_added(self, link)
    
    def _notify_row_added(self, row: List[str]) -> None:
        """Notify observers of row addition."""
        for observer in self.observers:
            observer.on_row_added(self, row)
    
    def _notify_marker_placed(self, side: str, position: int) -> None:
        """Notify observers of marker placement."""
        for observer in self.observers:
            observer.on_marker_placed(self, side, position)