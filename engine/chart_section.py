from typing import List, Dict, Any, Tuple, Union, Optional
from row_manager import RowManager
from node_manager import NodeManager
from link_manager import LinkManager
from position_calculator import PositionCalculator
from pattern_parser import PatternParser
from marker_manager import MarkerManager
from engine.domain.models.chart_queries import ChartQueries
from engine.domain.models.chart_generator import ChartGenerator
from engine.domain.models.operation_registry import OperationRegistry
from engine.domain.interfaces.ichart_observer import IChartObserver
from engine.data.models.chart_state_event import ChartStateEvent


class ChartSection:
    """Main class that coordinates knitting chart generation."""
    
    def __init__(
        self,
        name: str,
        start_side: str,
        # Dependencies - can be injected or created
        row_manager: Optional[RowManager] = None,
        node_manager: Optional[NodeManager] = None,
        link_manager: Optional[LinkManager] = None,
        position_calculator: Optional[PositionCalculator] = None,
        marker_manager: Optional[MarkerManager] = None,
        pattern_parser: Optional[PatternParser] = None,
        chart_generator: Optional[ChartGenerator] = None,
        chart_queries: Optional[ChartQueries] = None,
        operation_registry: Optional[OperationRegistry] = None,
        stitch_counter: Optional['StitchCounter'] = None,
        validator: Optional['StitchCountValidator'] = None,
        validation_chain: Optional['ValidationHandler'] = None,
        # Legacy parameters for backward compatibility
        sts: int = 22,
        rows: int = 28,
    ):
        self.name = name
        self.start_side = start_side
        self.observers: List[IChartObserver] = []
        
        # Dependency injection - use provided or create new
        if row_manager is not None:
            self.row_manager = row_manager
        else:
            self.row_manager = RowManager(start_side)
        
        if node_manager is not None:
            self.node_manager = node_manager
        else:
            self.node_manager = NodeManager()
        
        if link_manager is not None:
            self.link_manager = link_manager
        else:
            self.link_manager = LinkManager()
        
        if position_calculator is not None:
            self.position_calculator = position_calculator
        else:
            self.position_calculator = PositionCalculator()
            self.position_calculator.set_guage(sts, rows)
        
        if marker_manager is not None:
            self.marker_manager = marker_manager
        else:
            self.marker_manager = MarkerManager()
        
        if pattern_parser is not None:
            self.pattern_parser = pattern_parser
        else:
            self.pattern_parser = PatternParser(
                self.marker_manager.get_markers,
                self.marker_manager.move_marker,
                self.marker_manager.remove_marker
            )
        
        # New refactored components
        if chart_generator is not None:
            self.chart_generator = chart_generator
        else:
            self.chart_generator = ChartGenerator(position_calculator=self.position_calculator)
        
        # ChartQueries needs ChartSection, so create it after self is initialized
        if chart_queries is not None:
            self.chart_queries = chart_queries
        else:
            self.chart_queries = ChartQueries(self)
        
        if operation_registry is not None:
            self.operation_registry = operation_registry
        else:
            self.operation_registry = OperationRegistry()
            
        if stitch_counter is not None:
            self.stitch_counter = stitch_counter
        else:
            from engine.domain.models.stitch_counter import StitchCounter
            self.stitch_counter = StitchCounter()
        
        if validator is not None:
            self.validator = validator
        else:
            from engine.domain.models.validators.stitch_count_validator import StitchCountValidator
            self.validator = StitchCountValidator()
        
        if validation_chain is not None:
            self.validation_chain = validation_chain
        else:
            from engine.domain.models.validation.validation_handler import ValidationHandler
            self.validation_chain = None  # Optional, can be set later
    
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
    
    def get_stitches_on_hold(self) -> List[Dict]:
        """Get stitches currently on hold."""
        return self.chart_queries.get_stitches_on_hold()
    
    def get_row_num(self, side: str) -> int:
        """Get the row number for a given side."""
        return self.chart_queries.get_row_num(side)
    
    def get_markers(self, side: str) -> List[int]:
        """Get all marker positions for a given side."""
        return self.chart_queries.get_markers(side)
    
    def find_last_stitch(self) -> Dict[str, Any]:
        """Get the rightmost stitch position if last row is RS, otherwise leftmost stitch position if last row is WS."""
        return self.chart_queries.find_last_stitch()
    
    def find_first_stitch(self) -> Dict[str, Any]:
        """Get the leftmost stitch position if last row is WS, otherwise rightmost stitch position if last row is RS."""
        return self.chart_queries.find_first_stitch()
    
    # Operations - delegate to OperationRegistry or implement directly
    def place_on_hold(self) -> List[Dict]:
        """Place the unconsumed stitches on hold and return the previous stitches on hold."""
        if self.operation_registry.has_operation('place_on_hold'):
            op = self.operation_registry.get_operation('place_on_hold')
            previous_stitches_on_hold = self.node_manager.get_stitches_on_hold()
            op.execute(self, {})
            return previous_stitches_on_hold
        else:
            # Fallback to direct implementation
            previous_stitches_on_hold = self.node_manager.get_stitches_on_hold()
            self.node_manager.set_stitches_on_hold()
            return previous_stitches_on_hold
    
    def place_on_needle(self, stitches_on_hold: List[Dict], join_side: str) -> None:
        """Place the stitches on needle."""
        if self.operation_registry.has_operation('place_on_needle'):
            op = self.operation_registry.get_operation('place_on_needle')
            op.execute(self, {'stitches_on_hold': stitches_on_hold, 'join_side': join_side})
        else:
            # Fallback to direct implementation
            self.node_manager.places_stitches_on_needle(stitches_on_hold)
            if join_side == "RS":
                self.row_manager.set_last_row_side("WS")
            else:
                self.row_manager.set_last_row_side("RS")
    
    # Node creation - delegate to ChartGenerator
    def add_nodes(self, row: List[str], side: str, isRound: bool = False) -> None:
        """Add nodes for a new row."""
        print("side: ", side)
        row_num = self.get_row_num(side)
        print("row_num: ", row_num)
        
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
        if isinstance(pattern, int):
            new_row = self.row_manager.duplicate_row(pattern)
        else:
            side = "WS" if self.row_manager.is_wrong_side(isRound) else "RS"
            print("last row produced: ", self.node_manager.last_row_produced)
            new_row, consumed, produced, markers = self.pattern_parser.expand_pattern(
                pattern, self.node_manager.last_row_produced if self.row_manager.rows else float('inf'), side
            )
            
            for marker in markers:
                self.marker_manager.add_marker(side, marker, len(new_row))
                self._notify_marker_placed(side, marker)
        
        new_row = self.row_manager.reverse_row_if_needed(new_row, isRound)
        old_count = self.node_manager.last_row_produced
        self.add_nodes(new_row, side, isRound)
        print("produced: ", produced)
        print("consumed: ", consumed)
        print("number of last row produced: ", self.node_manager.last_row_produced)
        
        self.node_manager.set_last_row_produced(produced + (self.node_manager.last_row_produced - consumed))
        if old_count != self.node_manager.last_row_produced:
            self._notify_stitch_count_changed(old_count, self.node_manager.last_row_produced)
        
        print(len(self.node_manager.last_row_stitches))
        return self
    
    def cast_on_start(self, count: int) -> None:
        """Cast on the specified number of stitches."""
        old_count = self.node_manager.last_row_produced
        if self.start_side == "RS":
            self.add_nodes(["k"] * count, "WS")
        else:
            self.add_nodes(["k"] * count, "RS")
        self.node_manager.set_last_row_produced(count)
        if old_count != count:
            self._notify_stitch_count_changed(old_count, count)
    
    def cast_on(self, count: int) -> 'ChartSection':
        """Cast on additional stitches to extend the current chart."""
        if not self.node_manager.last_row_stitches:
            raise ValueError("No stitches to cast on to")
        
        current_fy = self.node_manager.last_row_stitches[0]["fy"]
        side = "RS" if self.row_manager.last_row_side == "RS" else "WS"
        current_row_number = self.get_row_num(side) - 1
        
        last_stitch = self.find_last_stitch()
        last_fx = last_stitch["fx"]
        print("last_fx: ", last_fx)
        connecting_id = last_stitch["id"]
        spacing = self.position_calculator.DEFAULT_SPACING
        
        old_count = self.node_manager.last_row_produced
        
        # Create new cast-on stitches positioned to the right
        for i in range(count):
            if side == "RS":
                new_fx = last_fx + (i + 1) * spacing
            else:
                new_fx = last_fx - (i + 1) * spacing
            print("new_fx: ", new_fx)
            node = self.node_manager.create_stitch_node("k", new_fx, current_fy, current_row_number)
            self.node_manager.last_row_stitches.append(node)
            self._notify_node_added(node)
            
            if i == 0:
                last_existing_id = self.node_manager.last_row_stitches[-2]["id"]
                first_new_id = self.node_manager.last_row_stitches[-1]["id"]
                self.link_manager.add_horizontal_link(connecting_id, first_new_id)
                self._notify_link_added({"source": connecting_id, "target": first_new_id})
            
            if i < count - 1:
                self.node_manager.create_strand_node(current_row_number)
                self.chart_generator.add_horizontal_links(self, len(self.node_manager.last_row_stitches) - 2)
        
        current_row = [stitch["type"] for stitch in self.node_manager.last_row_stitches]
        self.row_manager.rows[-1] = current_row
        
        self.node_manager.set_last_row_produced(self.node_manager.last_row_produced + count)
        if old_count != self.node_manager.last_row_produced:
            self._notify_stitch_count_changed(old_count, self.node_manager.last_row_produced)
        return self
    
    def join(self, other: 'ChartSection') -> 'ChartSection':
        """Join this chart section with another chart section."""
        if self.operation_registry.has_operation('join'):
            op = self.operation_registry.get_operation('join')
            return op.execute(self, {'other_chart': other})
        else:
            # Fallback to direct implementation
            last_stitch_self = self.find_last_stitch()
            new_fx = last_stitch_self["fx"] + self.position_calculator.DEFAULT_SPACING
            first_stitch_other = other.find_first_stitch()
            offset = new_fx - first_stitch_other["fx"]
            for stitch in other.node_manager.nodes:
                if stitch["type"] != "strand":
                    stitch["fx"] += offset
            
            for marker in other.marker_manager.markers_rs:
                self.marker_manager.markers_rs.append(marker + len(self.node_manager.last_row_stitches))
            for marker in other.marker_manager.markers_ws:
                self.marker_manager.markers_ws.append(marker + len(self.node_manager.last_row_stitches))
            
            self.node_manager.nodes.extend(other.node_manager.nodes)
            self.node_manager.node_counter += other.node_manager.node_counter
            self.node_manager.last_row_stitches.extend(other.node_manager.last_row_stitches)
            
            return self
    
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
    
    def _notify_node_added(self, node: Optional[Dict] = None) -> None:
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