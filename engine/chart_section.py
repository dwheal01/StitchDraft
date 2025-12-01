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
from engine.data.models.chart_state_event import ChartStateEvent
from engine.data.models.node import Node

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
        
        # ChartQueries needs ChartSection, so create it after self is initialized
        if chart_queries is not None:
            self.chart_queries = chart_queries
        else:
            self.chart_queries = ChartQueries(self)
            
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
    
    # Operations - delegate to OperationRegistry or implement directly
    def place_on_hold(self) -> List[Node]:
        """Place the unconsumed stitches on hold and return the previous stitches on hold."""
        op = self.operation_registry.get_operation('place_on_hold')
        previous_stitches_on_hold = self.node_manager.get_stitches_on_hold()
        op.execute(self, {})
        return previous_stitches_on_hold
    
    def place_on_needle(self, stitches_on_hold: List[Node], join_side: str) -> None:
        """Place the stitches on needle."""
        op = self.operation_registry.get_operation('place_on_needle')
        op.execute(self, {'stitches_on_hold': stitches_on_hold, 'join_side': join_side})
    
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
        return op.execute(self, {'pattern': pattern, 'is_round': isRound})
        
    def cast_on_start(self, count: int) -> None:
        """Cast on the specified number of stitches."""
        op = self.operation_registry.get_operation('cast_on')
        op.execute(self, {'count': count})
    
    def cast_on(self, count: int) -> 'ChartSection':
        """Cast on additional stitches to extend the current chart."""
        op = self.operation_registry.get_operation('cast_on_additional')
        return op.execute(self, {'count': count})
    
    def join(self, other: 'ChartSection') -> 'ChartSection':
        """Join this chart section with another chart section."""
        op = self.operation_registry.get_operation('join')
        return op.execute(self, {'other_chart': other})
        
    def place_marker(self, side: str, position: int) -> None:
        """Place a marker at the specified needle position."""
        self.marker_manager.add_marker(side, position, len(self.node_manager.last_row_stitches))
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
        """Get nodes from the node manager."""
        return self.node_manager.nodes
    
    @property
    def links(self):
        """Get links from the link manager."""
        return self.link_manager.links
    
    @property
    def rows(self):
        """Get rows from the row manager."""
        return self.row_manager.rows
    
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