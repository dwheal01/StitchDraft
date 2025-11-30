"""Test PatternProcessor functionality."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.models.pattern_processor import PatternProcessor
from engine.pattern_parser import PatternParser
from engine.marker_manager import MarkerManager
from engine.domain.models.validators.pattern_validator import PatternValidator
from engine.data.models.pattern_context import PatternContext
from engine.data.models.expanded_pattern import ExpandedPattern
from engine.domain.factories.chart_section_factory import ChartSectionFactory


def test_pattern_processor_creation():
    """Test PatternProcessor creation."""
    print("\n=== Testing PatternProcessor Creation ===")
    
    marker_manager = MarkerManager()
    pattern_parser = PatternParser(marker_provider=marker_manager)
    processor = PatternProcessor(pattern_parser=pattern_parser)
    
    assert processor.pattern_parser is not None, "PatternParser should be set"
    assert processor.pattern_validator is not None, "PatternValidator should be created"
    print("✓ PatternProcessor created successfully")
    
    return processor


def test_expand_pattern():
    """Test pattern expansion."""
    print("\n=== Testing Pattern Expansion ===")
    
    marker_manager = MarkerManager()
    pattern_parser = PatternParser(marker_provider=marker_manager)
    processor = PatternProcessor(pattern_parser=pattern_parser)
    
    context = PatternContext(
        available_stitches=10,
        side="RS",
        markers=[],
        last_row_side="RS",
        is_round=False
    )
    
    result = processor.expand_pattern("k5, p5", context)
    
    assert isinstance(result, ExpandedPattern), "Should return ExpandedPattern"
    assert len(result.stitches) == 10, f"Should have 10 stitches, got {len(result.stitches)}"
    assert result.consumed == 10, f"Should consume 10, got {result.consumed}"
    assert result.produced == 10, f"Should produce 10, got {result.produced}"
    print("✓ Pattern expansion works correctly")
    
    return processor


def test_validate_pattern():
    """Test pattern validation."""
    print("\n=== Testing Pattern Validation ===")
    
    processor = PatternProcessor()
    
    context = PatternContext(
        available_stitches=10,
        side="RS",
        markers=[],
        last_row_side="RS",
        is_round=False
    )
    
    # Test valid pattern
    is_valid = processor.validate_pattern("k5, p5", context)
    assert is_valid == True, "Valid pattern should pass"
    print("✓ Valid pattern passes validation")
    
    # Test invalid pattern (empty)
    is_valid = processor.validate_pattern("", context)
    assert is_valid == False, "Empty pattern should fail"
    print("✓ Invalid pattern (empty) fails validation")
    
    # Test invalid pattern (unbalanced parentheses)
    is_valid = processor.validate_pattern("repeat(k5, p5", context)
    assert is_valid == False, "Unbalanced parentheses should fail"
    print("✓ Invalid pattern (unbalanced parentheses) fails validation")
    
    return processor


def test_process_markers():
    """Test marker processing."""
    print("\n=== Testing Marker Processing ===")
    
    marker_manager = MarkerManager()
    marker_manager.add_marker("RS", 5, 10)
    
    pattern_parser = PatternParser(marker_provider=marker_manager)
    processor = PatternProcessor(pattern_parser=pattern_parser)
    
    context = PatternContext(
        available_stitches=10,
        side="RS",
        markers=[5],
        last_row_side="RS",
        is_round=False
    )
    
    markers = processor.process_markers("k5, sm, p5", context)
    assert isinstance(markers, list), "Should return list of markers"
    print("✓ Marker processing works")
    
    return processor


def test_validate_and_expand():
    """Test validate and expand workflow."""
    print("\n=== Testing Validate and Expand ===")
    
    marker_manager = MarkerManager()
    pattern_parser = PatternParser(marker_provider=marker_manager)
    processor = PatternProcessor(pattern_parser=pattern_parser)
    
    context = PatternContext(
        available_stitches=10,
        side="RS",
        markers=[],
        last_row_side="RS",
        is_round=False
    )
    
    # Test valid pattern
    result = processor.validate_and_expand("k5, p5", context)
    assert isinstance(result, ExpandedPattern), "Should return ExpandedPattern"
    assert len(result.stitches) == 10, "Should expand to 10 stitches"
    print("✓ Validate and expand works for valid pattern")
    
    # Test invalid pattern
    try:
        processor.validate_and_expand("", context)
        assert False, "Should raise ValueError for invalid pattern"
    except ValueError as e:
        assert "validation failed" in str(e).lower(), "Error should mention validation"
        print("✓ Validate and expand raises error for invalid pattern")
    
    return processor


def test_chart_service_integration():
    """Test PatternProcessor integration with ChartService."""
    print("\n=== Testing ChartService Integration ===")
    
    from engine.domain.services.chart_service import ChartService
    from engine.data.repositories.chart_repository import ChartRepository
    
    # Create components
    marker_manager = MarkerManager()
    pattern_parser = PatternParser(marker_provider=marker_manager)
    pattern_processor = PatternProcessor(pattern_parser=pattern_parser)
    
    repository = ChartRepository(data_path=".")
    service = ChartService(
        chart_repository=repository,
        pattern_processor=pattern_processor
    )
    
    # Create a chart
    chart = service.create_chart(name="processor_test", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    
    # Test pattern processing
    result = service.process_pattern(chart, "k5, p5")
    
    assert isinstance(result, ExpandedPattern), "Should return ExpandedPattern"
    assert len(result.stitches) == 10, "Should expand to 10 stitches"
    print("✓ ChartService integration works")
    
    return service


def run_all_tests():
    """Run all PatternProcessor tests."""
    print("=" * 60)
    print("PATTERN PROCESSOR TEST SUITE")
    print("=" * 60)
    
    try:
        test_pattern_processor_creation()
        test_expand_pattern()
        test_validate_pattern()
        test_process_markers()
        test_validate_and_expand()
        test_chart_service_integration()
        
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