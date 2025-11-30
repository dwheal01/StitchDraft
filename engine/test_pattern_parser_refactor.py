"""Test PatternParser refactoring to use IMarkerProvider."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.pattern_parser import PatternParser
from engine.marker_manager import MarkerManager
from engine.domain.interfaces.imarker_provider import IMarkerProvider
from engine.domain.factories.chart_section_factory import ChartSectionFactory


def test_marker_manager_implements_interface():
    """Test that MarkerManager implements IMarkerProvider."""
    print("\n=== Testing MarkerManager implements IMarkerProvider ===")
    
    marker_manager = MarkerManager()
    
    # Check that it's an instance of IMarkerProvider
    assert isinstance(marker_manager, IMarkerProvider), "MarkerManager should implement IMarkerProvider"
    print("✓ MarkerManager implements IMarkerProvider")
    
    # Test interface methods
    markers = marker_manager.get_markers("RS")
    assert isinstance(markers, list), "get_markers should return a list"
    print("✓ get_markers() works")
    
    # Test that methods exist and are callable
    assert callable(marker_manager.move_marker), "move_marker should be callable"
    assert callable(marker_manager.remove_marker), "remove_marker should be callable"
    print("✓ All interface methods are implemented")
    
    return marker_manager


def test_pattern_parser_uses_interface():
    """Test that PatternParser uses IMarkerProvider."""
    print("\n=== Testing PatternParser uses IMarkerProvider ===")
    
    marker_manager = MarkerManager()
    parser = PatternParser(marker_provider=marker_manager)
    
    # Verify that marker_provider is set
    assert hasattr(parser, 'marker_provider'), "PatternParser should have marker_provider"
    assert parser.marker_provider is marker_manager, "marker_provider should be the passed instance"
    assert isinstance(parser.marker_provider, IMarkerProvider), "marker_provider should implement IMarkerProvider"
    print("✓ PatternParser uses IMarkerProvider")
    
    # Test that it can call methods through the interface
    markers = parser.marker_provider.get_markers("RS")
    assert isinstance(markers, list), "Should be able to call get_markers through interface"
    print("✓ PatternParser can use marker provider methods")
    
    return parser


def test_pattern_parser_functionality():
    """Test that PatternParser still works correctly after refactoring."""
    print("\n=== Testing PatternParser Functionality ===")
    
    marker_manager = MarkerManager()
    parser = PatternParser(marker_provider=marker_manager)
    
    # Test basic pattern expansion
    pattern = "k5, p5"
    expanded, consumed, produced, markers = parser.expand_pattern(pattern, 10, "RS")
    
    assert len(expanded) == 10, f"Should expand to 10 stitches, got {len(expanded)}"
    assert consumed == 10, f"Should consume 10 stitches, got {consumed}"
    assert produced == 10, f"Should produce 10 stitches, got {produced}"
    print("✓ Basic pattern expansion works")
    
    # Test with markers
    marker_manager.add_marker("RS", 5, 10)
    pattern_with_marker = "k5, sm, p5"
    expanded, consumed, produced, markers = parser.expand_pattern(pattern_with_marker, 10, "RS")
    
    assert len(expanded) == 10, "Should expand to 10 stitches with marker"
    print("✓ Pattern expansion with markers works")
    
    return parser


def test_factory_integration():
    """Test that factory creates PatternParser correctly."""
    print("\n=== Testing Factory Integration ===")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="factory_test", start_side="RS")
    
    # Verify PatternParser is created correctly
    assert hasattr(chart, 'pattern_parser'), "Chart should have pattern_parser"
    assert chart.pattern_parser is not None, "pattern_parser should not be None"
    assert isinstance(chart.pattern_parser, PatternParser), "pattern_parser should be PatternParser"
    print("✓ Factory creates PatternParser")
    
    # Verify it uses IMarkerProvider
    assert hasattr(chart.pattern_parser, 'marker_provider'), "PatternParser should have marker_provider"
    assert isinstance(chart.pattern_parser.marker_provider, IMarkerProvider), "marker_provider should implement IMarkerProvider"
    assert chart.pattern_parser.marker_provider is chart.marker_manager, "marker_provider should be the chart's marker_manager"
    print("✓ Factory wires PatternParser with MarkerManager via IMarkerProvider")
    
    return chart


def test_backward_compatibility():
    """Test that existing code still works."""
    print("\n=== Testing Backward Compatibility ===")
    
    # Test that ChartSection can still be created with old-style constructor
    from engine.chart_section import ChartSection
    
    chart = ChartSection(name="backward_test", start_side="RS", sts=23, rows=21)
    
    # Verify PatternParser is created correctly
    assert chart.pattern_parser is not None, "PatternParser should be created"
    assert isinstance(chart.pattern_parser.marker_provider, IMarkerProvider), "Should use IMarkerProvider"
    print("✓ Backward compatibility maintained")
    
    # Test that pattern parsing still works
    chart.cast_on_start(10)
    chart.add_row("k5, p5")
    
    assert chart.get_current_num_of_stitches() == 10, "Should have 10 stitches"
    print("✓ Chart operations work after refactoring")
    
    return chart


def run_all_tests():
    """Run all PatternParser refactoring tests."""
    print("=" * 60)
    print("PATTERN PARSER REFACTORING TEST SUITE")
    print("=" * 60)
    
    try:
        test_marker_manager_implements_interface()
        test_pattern_parser_uses_interface()
        test_pattern_parser_functionality()
        test_factory_integration()
        test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)