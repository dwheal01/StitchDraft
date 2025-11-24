"""Test script for ChartSectionFactory."""
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
    print("=" * 50)
    print("Testing ChartSectionFactory")
    print("=" * 50)
    
    try:
        # Test 1: Create with config
        chart1 = test_factory_create_with_config()
        
        # Test 2: Create with defaults
        chart2 = test_factory_create_with_defaults()
        
        # Test 3: Test operations
        chart3 = test_factory_operations()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nPossible fixes:")
        print("1. Check that all imports in chart_section_factory.py are correct")
        print("2. Make sure you're running from the project root")
        print("3. Check that ChartConfig is in engine/data/models/")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()