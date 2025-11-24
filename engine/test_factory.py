"""Test script for ChartSectionFactory and refactored components."""
import sys
import os

# Add parent directory to path so we can import from engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine.data.models.chart_config import ChartConfig


def test_factory_create_with_config():
    """Test creating a ChartSection using ChartConfig."""
    print("Testing factory.create() with ChartConfig...")
    factory = ChartSectionFactory()
    
    config = ChartConfig(
        name="test_chart",
        start_side="RS",
        sts=23,
        rows=21
    )
    
    chart = factory.create(config)
    
    assert chart.name == "test_chart"
    assert chart.start_side == "RS"
    print(f"✓ Created chart: {chart.name}")
    return chart


def test_factory_create_with_defaults():
    """Test creating a ChartSection using create_with_defaults."""
    print("\nTesting factory.create_with_defaults()...")
    factory = ChartSectionFactory()
    
    chart = factory.create_with_defaults(
        name="default_chart",
        start_side="WS"
    )
    
    assert chart.name == "default_chart"
    assert chart.start_side == "WS"
    print(f"✓ Created chart: {chart.name}")
    return chart


def test_new_components_are_created():
    """Test that new refactored components are created and wired."""
    print("\nTesting new refactored components...")
    factory = ChartSectionFactory()
    
    chart = factory.create_with_defaults(
        name="component_test",
        start_side="RS"
    )
    
    # Test ChartQueries
    assert hasattr(chart, 'chart_queries'), "ChartQueries should be attached"
    assert chart.chart_queries is not None, "ChartQueries should not be None"
    print("✓ ChartQueries created and attached")
    
    # Test ChartGenerator
    assert hasattr(chart, 'chart_generator'), "ChartGenerator should be attached"
    assert chart.chart_generator is not None, "ChartGenerator should not be None"
    print("✓ ChartGenerator created and attached")
    
    # Test OperationRegistry
    assert hasattr(chart, 'operation_registry'), "OperationRegistry should be attached"
    assert chart.operation_registry is not None, "OperationRegistry should not be None"
    print("✓ OperationRegistry created and attached")
    
    # Test that operations are registered
    assert chart.operation_registry.has_operation('place_on_hold'), "place_on_hold should be registered"
    assert chart.operation_registry.has_operation('place_on_needle'), "place_on_needle should be registered"
    assert chart.operation_registry.has_operation('join'), "join should be registered"
    print("✓ Operations registered in OperationRegistry")
    
    return chart


def test_chart_queries():
    """Test ChartQueries functionality."""
    print("\nTesting ChartQueries...")
    factory = ChartSectionFactory()
    
    chart = factory.create_with_defaults(
        name="queries_test",
        start_side="RS"
    )
    
    # Cast on some stitches
    chart.cast_on_start(10)
    
    # Test queries
    stitch_count = chart.chart_queries.get_current_num_of_stitches()
    assert stitch_count == 10, f"Expected 10 stitches, got {stitch_count}"
    print(f"✓ get_current_num_of_stitches(): {stitch_count}")
    
    row_num = chart.chart_queries.get_current_row_num()
    assert row_num == 1, f"Expected 1 row, got {row_num}"
    print(f"✓ get_current_row_num(): {row_num}")
    
    markers = chart.chart_queries.get_markers("RS")
    assert isinstance(markers, list), "Markers should be a list"
    print(f"✓ get_markers('RS'): {markers}")
    
    stitches_on_hold = chart.chart_queries.get_stitches_on_hold()
    assert isinstance(stitches_on_hold, list), "Stitches on hold should be a list"
    print(f"✓ get_stitches_on_hold(): {stitches_on_hold}")
    
    return chart


def test_operation_registry():
    """Test OperationRegistry functionality."""
    print("\nTesting OperationRegistry...")
    factory = ChartSectionFactory()
    
    chart = factory.create_with_defaults(
        name="registry_test",
        start_side="RS"
    )
    
    # Test getting operations
    place_on_hold_op = chart.operation_registry.get_operation('place_on_hold')
    assert place_on_hold_op is not None, "Should be able to get place_on_hold operation"
    print("✓ Retrieved place_on_hold operation")
    
    place_on_needle_op = chart.operation_registry.get_operation('place_on_needle')
    assert place_on_needle_op is not None, "Should be able to get place_on_needle operation"
    print("✓ Retrieved place_on_needle operation")
    
    join_op = chart.operation_registry.get_operation('join')
    assert join_op is not None, "Should be able to get join operation"
    print("✓ Retrieved join operation")
    
    # Test invalid operation
    try:
        chart.operation_registry.get_operation('invalid_op')
        assert False, "Should have raised ValueError for invalid operation"
    except ValueError:
        print("✓ Correctly raised ValueError for invalid operation")
    
    return chart


def test_factory_operations():
    """Test that factory-created charts can perform operations."""
    print("\nTesting factory-created chart operations...")
    factory = ChartSectionFactory()
    
    chart = factory.create_with_defaults(
        name="operation_test",
        start_side="RS",
        sts=23,
        rows=21
    )
    
    # Test cast_on_start
    chart.cast_on_start(10)
    assert chart.get_current_num_of_stitches() == 10
    print(f"✓ cast_on_start: {chart.get_current_num_of_stitches()} stitches")
    
    # Test add_row
    chart.add_row("repeat(k1)")
    print(f"✓ add_row: {chart.get_current_num_of_stitches()} stitches")
    
    # Test place_marker
    chart.place_marker("RS", 5)
    markers = chart.get_markers("RS")
    assert 5 in markers
    print(f"✓ place_marker: markers = {markers}")
    
    return chart


if __name__ == "__main__":
    print("=" * 60)
    print("Testing ChartSectionFactory and Refactored Components")
    print("=" * 60)
    
    try:
        # Test 1: Create with config
        chart1 = test_factory_create_with_config()
        
        # Test 2: Create with defaults
        chart2 = test_factory_create_with_defaults()
        
        # Test 3: Test new components are created
        chart3 = test_new_components_are_created()
        
        # Test 4: Test ChartQueries
        chart4 = test_chart_queries()
        
        # Test 5: Test OperationRegistry
        chart5 = test_operation_registry()
        
        # Test 6: Test operations
        chart6 = test_factory_operations()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nPossible fixes:")
        print("1. Check that all imports in chart_section_factory.py are correct")
        print("2. Make sure you're running from the project root")
        print("3. Check that all new components are in the correct directories")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()