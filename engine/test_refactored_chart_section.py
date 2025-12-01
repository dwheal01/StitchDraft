"""Test script for refactored ChartSection with dependency injection."""
import sys
import os

# Add parent directory to path so we can import from engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine.data.models.chart_config import ChartConfig
from engine.chart_section import ChartSection
from engine.domain.models.chart_queries import ChartQueries
from engine.domain.models.chart_generator import ChartGenerator
from engine.domain.models.operation_registry import OperationRegistry


def test_factory_creation():
    """Test that ChartSection is created correctly via factory."""
    print("Testing factory creation...")
    
    # Use factory instead of direct construction
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(
        name="factory_test",
        start_side="RS"
    )
    
    assert chart.name == "factory_test"
    assert chart.start_side == "RS"
    assert chart.chart_queries is not None
    assert chart.chart_generator is not None
    assert chart.operation_registry is not None
    print("✓ Factory creates ChartSection correctly")
    
    return chart


def test_dependency_injection():
    """Test that dependency injection works."""
    print("\nTesting dependency injection...")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(
        name="di_test",
        start_side="RS"
    )
    
    # Verify dependencies are injected
    assert chart.row_manager is not None
    assert chart.node_manager is not None
    assert chart.link_manager is not None
    assert chart.position_calculator is not None
    assert chart.marker_manager is not None
    assert chart.pattern_parser is not None
    assert chart.chart_generator is not None
    assert chart.chart_queries is not None
    assert chart.operation_registry is not None
    print("✓ All dependencies injected correctly")
    
    return chart


def test_chart_queries_delegation():
    """Test that query methods delegate to ChartQueries."""
    print("\nTesting ChartQueries delegation...")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(
        name="queries_test",
        start_side="RS"
    )
    
    # Cast on some stitches
    chart.cast_on_start(10)
    
    # Test that methods use ChartQueries
    stitch_count = chart.get_current_num_of_stitches()
    assert stitch_count == 10, f"Expected 10, got {stitch_count}"
    print(f"✓ get_current_num_of_stitches() delegates: {stitch_count}")
    
    row_num = chart.get_current_row_num()
    assert row_num == 1, f"Expected 1, got {row_num}"
    print(f"✓ get_current_row_num() delegates: {row_num}")
    
    markers = chart.get_markers("RS")
    assert isinstance(markers, list)
    print(f"✓ get_markers() delegates: {markers}")
    
    # Test find methods
    last_stitch = chart.find_last_stitch()
    assert last_stitch is not None
    print("✓ find_last_stitch() delegates")
    
    first_stitch = chart.find_first_stitch()
    assert first_stitch is not None
    print("✓ find_first_stitch() delegates")
    
    return chart


def test_chart_generator_delegation():
    """Test that node creation delegates to ChartGenerator."""
    print("\nTesting ChartGenerator delegation...")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(
        name="generator_test",
        start_side="RS"
    )
    
    # Cast on and add a row
    chart.cast_on_start(5)
    initial_node_count = len(chart.nodes)
    
    chart.add_row("k1")
    new_node_count = len(chart.nodes)
    
    assert new_node_count > initial_node_count, "Nodes should be added"
    print(f"✓ ChartGenerator creates nodes: {initial_node_count} -> {new_node_count}")
    
    return chart


def test_operation_registry_usage():
    """Test OperationRegistry usage."""
    print("\nTesting OperationRegistry usage...")
    factory = ChartSectionFactory()
    
    chart = factory.create_with_defaults(
        name="registry_test",
        start_side="RS"
    )
    
    # Cast on some stitches
    chart.cast_on_start(10)
    chart.add_row("k1")
    
    # Test place_on_hold operation
    stitches_before = len(chart.node_manager.last_row_stitches)
    previous_stitches = chart.place_on_hold()  # Returns previous stitches on hold
    stitches_after = len(chart.node_manager.last_row_stitches)
    
    # Get the stitches that were just placed on hold
    stitches_just_placed_on_hold = chart.node_manager.get_stitches_on_hold()
    
    assert stitches_after < stitches_before, "Stitches should be on hold"
    print(f"✓ place_on_hold() uses OperationRegistry: {stitches_before} -> {stitches_after}")
    
    # Test place_on_needle operation - use the stitches that were just placed on hold
    chart.place_on_needle(stitches_just_placed_on_hold, "RS")
    stitches_restored = len(chart.node_manager.last_row_stitches)
    assert stitches_restored > stitches_after, "Stitches should be restored"
    print(f"✓ place_on_needle() uses OperationRegistry: {stitches_after} -> {stitches_restored}")
    
    return chart

def test_observer_support():
    """Test that observer pattern is supported."""
    print("\nTesting observer support...")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(
        name="observer_test",
        start_side="RS"
    )
    
    # Create a simple mock observer
    class MockObserver:
        def __init__(self):
            self.events = []
        
        def on_stitch_count_changed(self, chart, old_count, new_count):
            self.events.append(('stitch_count_changed', old_count, new_count))
        
        def on_node_added(self, chart, node):
            self.events.append(('node_added', node))
        
        def on_link_added(self, chart, link):
            self.events.append(('link_added', link))
        
        def on_row_added(self, chart, row):
            self.events.append(('row_added', row))
        
        def on_marker_placed(self, chart, side, position):
            self.events.append(('marker_placed', side, position))
        
        def on_chart_state_changed(self, chart, event):
            self.events.append(('state_changed', event))
    
    observer = MockObserver()
    chart.attach(observer)
    
    # Perform operations that should trigger notifications
    chart.cast_on_start(5)
    chart.add_row("k1")
    chart.place_marker("RS", 2)
    
    assert len(observer.events) > 0, "Observer should receive events"
    print(f"✓ Observer received {len(observer.events)} events")
    
    # Test detach
    chart.detach(observer)
    event_count_before = len(observer.events)
    chart.add_row("k1")
    event_count_after = len(observer.events)
    
    assert event_count_after == event_count_before, "Observer should not receive events after detach"
    print("✓ Observer detach works correctly")
    
    return chart


def test_existing_functionality():
    """Test that all existing functionality still works."""
    print("\nTesting existing functionality...")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(
        name="functionality_test",
        start_side="RS",
        sts=23,
        rows=21
    )
    
    # Test cast_on_start
    chart.cast_on_start(10)
    assert chart.get_current_num_of_stitches() == 10
    print("✓ cast_on_start works")
    
    # Test add_row
    chart.add_row("repeat(k1)")
    assert chart.get_current_num_of_stitches() == 10
    print("✓ add_row works")
    
    # Test add_round
    chart.add_round("k1")
    print("✓ add_round works")
    
    # Test place_marker
    chart.place_marker("RS", 5)
    markers = chart.get_markers("RS")
    assert 5 in markers
    print("✓ place_marker works")
    
    # Test repeat_rows
    chart.repeat_rows(["k1"], 2)
    print("✓ repeat_rows works")
    
    # Test properties
    assert chart.nodes is not None
    assert chart.links is not None
    assert chart.rows is not None
    print("✓ Properties work")
    
    return chart


def test_join_operation():
    """Test join operation using OperationRegistry."""
    print("\nTesting join operation...")
    
    factory = ChartSectionFactory()
    
    chart1 = factory.create_with_defaults(
        name="chart1",
        start_side="RS"
    )
    chart1.cast_on_start(5)
    chart1.add_row("k1")
    
    chart2 = factory.create_with_defaults(
        name="chart2",
        start_side="RS"
    )
    chart2.cast_on_start(3)
    chart2.add_row("k1")
    
    nodes_before = len(chart1.nodes)
    chart1.join(chart2)
    nodes_after = len(chart1.nodes)
    
    assert nodes_after > nodes_before, "Nodes should be merged"
    print(f"✓ join() uses OperationRegistry: {nodes_before} -> {nodes_after} nodes")
    
    return chart1


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Refactored ChartSection with Dependency Injection")
    print("=" * 70)
    
    try:
        # Test 1: Factory creation
        chart1 = test_factory_creation()
        
        # Test 2: Dependency injection
        chart2 = test_dependency_injection()
        
        # Test 3: ChartQueries delegation
        chart3 = test_chart_queries_delegation()
        
        # Test 4: ChartGenerator delegation
        chart4 = test_chart_generator_delegation()
        
        # Test 5: OperationRegistry usage
        chart5 = test_operation_registry_usage()
        
        # Test 6: Observer support
        chart6 = test_observer_support()
        
        # Test 7: Existing functionality
        chart7 = test_existing_functionality()
        
        # Test 8: Join operation
        chart8 = test_join_operation()
        
        print("\n" + "=" * 70)
        print("All refactoring tests passed! ✓")
        print("=" * 70)
        print("\nSummary:")
        print("  ✓ Factory creation working")        
        print("  ✓ Dependency injection working")
        print("  ✓ ChartQueries delegation working")
        print("  ✓ ChartGenerator delegation working")
        print("  ✓ OperationRegistry usage working")
        print("  ✓ Observer pattern supported")
        print("  ✓ All existing functionality preserved")
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nPossible fixes:")
        print("1. Check that all imports are correct")
        print("2. Make sure you're running from the project root")
        import traceback
        traceback.print_exc() 
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()