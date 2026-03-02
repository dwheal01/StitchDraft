"""Test PatternParser refactoring to use IMarkerProvider."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.models.pattern_parser import PatternParser
from engine.domain.models.marker_manager import MarkerManager
from engine.domain.interfaces.imarker_provider import IMarkerProvider
from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine.data.models.expanded_pattern import ExpandedPattern


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
    expanded_result = parser.expand_pattern(pattern, 10, "RS")
    
    assert isinstance(expanded_result, ExpandedPattern), "Should return ExpandedPattern"
    assert len(expanded_result.stitches) == 10, f"Should expand to 10 stitches, got {len(expanded_result.stitches)}"
    assert expanded_result.consumed == 10, f"Should consume 10 stitches, got {expanded_result.consumed}"
    assert expanded_result.produced == 10, f"Should produce 10 stitches, got {expanded_result.produced}"
    print("✓ Basic pattern expansion works")
    
    # Test with markers
    marker_manager.add_marker("RS", 5, 10)
    pattern_with_marker = "k5, sm, p5"
    expanded_result = parser.expand_pattern(pattern_with_marker, 10, "RS")
    
    assert isinstance(expanded_result, ExpandedPattern), "Should return ExpandedPattern"
    assert len(expanded_result.stitches) == 10, "Should expand to 10 stitches with marker"
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

def test_factory_creation():
    """Test that ChartSection is created correctly via factory."""
    print("\n=== Testing Factory Creation ===")
    
    # Use factory instead of direct construction
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="factory_test", start_side="RS")
    
    # Verify PatternParser is created correctly
    assert chart.pattern_parser is not None, "PatternParser should be created"
    assert isinstance(chart.pattern_parser.marker_provider, IMarkerProvider), "Should use IMarkerProvider"
    print("✓ Factory creates ChartSection with PatternParser correctly")
    
    # Test that pattern parsing still works
    chart.cast_on_start(10)
    chart.add_row("k5, p5")
    
    assert chart.get_current_num_of_stitches() == 10, "Should have 10 stitches"
    print("✓ Chart operations work after refactoring")
    
    return chart


def test_work_est():
    """Test 'work est' continues pattern by matching right-side appearance."""
    print("\n=== Testing work est (continue as established) ===")

    marker_manager = MarkerManager()
    parser = PatternParser(marker_provider=marker_manager)
    # Previous row [k,k,p,p,k]: if that row was RS, RS appearance is same; if it was WS, RS appearance is flip
    last_row = ["k", "k", "p", "p", "k"]

    # RS: previous row was WS, so RS appearance of last_row is flip → we work that on RS
    result_rs = parser.expand_pattern("work est", 5, "RS", last_row=last_row, is_round=False)
    assert result_rs.stitches == ["p", "p", "k", "k", "p"], f"RS work est: got {result_rs.stitches}"
    print("✓ work est on RS matches RS appearance")

    # WS: previous row was RS, so RS appearance is last_row; we purl to show knit, knit to show purl
    result_ws = parser.expand_pattern("work est", 5, "WS", last_row=last_row, is_round=False)
    assert result_ws.stitches == ["p", "p", "k", "k", "p"], f"WS work est: got {result_ws.stitches}"
    print("✓ work est on WS matches RS appearance")

    # Round: same as previous
    result_round = parser.expand_pattern("work est", 5, "WS", last_row=last_row, is_round=True)
    assert result_round.stitches == ["k", "k", "p", "p", "k"], f"Round work est: got {result_round.stitches}"
    print("✓ work est in round repeats previous row")

    # Explicit count: work est 3 (RS, prev row WS → prev_rs for k,k,p is p,p,k)
    result_3 = parser.expand_pattern("work est 3", 5, "RS", last_row=last_row, is_round=False)
    assert result_3.stitches == ["p", "p", "k"], f"work est 3: got {result_3.stitches}"
    print("✓ work est 3 expands to 3 stitches")

    # Chart integration: add_row with work est completes and preserves stitch count
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="work_est_chart", start_side="RS")
    chart.cast_on_start(6)
    chart.add_row("k2, p2, k2")
    chart.add_row("k2, work est, k2")
    rows = chart.row_manager.get_rows()
    assert len(rows) >= 2, f"Should have at least 2 pattern rows, got {len(rows)}"
    assert chart.get_current_num_of_stitches() == 6, "Should still have 6 stitches"
    work_est_row = rows[-1]
    assert len(work_est_row) == 6, f"Work est row should have 6 stitches, got {len(work_est_row)}"
    print("✓ add_row('k2, work est, k2') works on chart")

    print("✓ All work est tests passed")


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
        test_factory_creation()
        test_work_est()
        
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