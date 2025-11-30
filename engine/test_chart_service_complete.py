"""Test complete ChartService integration with all features."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.services.chart_service import ChartService
from engine.data.repositories.chart_repository import ChartRepository
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext
from engine.data.models.expanded_pattern import ExpandedPattern
from engine.domain.models.pattern_processor import PatternProcessor
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.presentation.observers.chart_visualization_observer import ChartVisualizationObserver


def test_auto_create_pattern_processor():
    """Test that ChartService auto-creates PatternProcessor."""
    print("\n=== Testing Auto-Creation of PatternProcessor ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    # Verify PatternProcessor was created
    assert service.pattern_processor is not None, "PatternProcessor should be auto-created"
    assert isinstance(service.pattern_processor, PatternProcessor), "Should be PatternProcessor instance"
    print("✓ PatternProcessor auto-created successfully")
    
    # Test that it works
    chart = service.create_chart(name="processor_test", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    
    result = service.process_pattern(chart, "k5, p5")
    assert isinstance(result, ExpandedPattern), "Should return ExpandedPattern"
    assert len(result.stitches) == 10, "Should expand to 10 stitches"
    print("✓ Auto-created PatternProcessor works correctly")
    
    return service


def test_auto_create_validation_chain():
    """Test that ChartService auto-creates ValidationHandler chain."""
    print("\n=== Testing Auto-Creation of ValidationHandler Chain ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    # Verify ValidationHandler chain was created
    assert service.validation_chain is not None, "ValidationHandler chain should be auto-created"
    assert isinstance(service.validation_chain, ValidationHandler), "Should be ValidationHandler instance"
    print("✓ ValidationHandler chain auto-created successfully")
    
    # Test that it works
    chart = service.create_chart(name="validation_test", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    
    request = ValidationRequest(
        chart=chart,
        operation="add_row",
        consumed=10,
        produced=10
    )
    
    result = service.validate_chart(chart, request)
    assert isinstance(result, ValidationResult), "Should return ValidationResult"
    assert result.is_valid == True, "Valid operation should pass"
    print("✓ Auto-created ValidationHandler chain works correctly")
    
    return service


def test_validate_chart():
    """Test validate_chart() method."""
    print("\n=== Testing validate_chart() Method ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    chart = service.create_chart(name="validate_test", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    
    # Test valid operation
    valid_request = ValidationRequest(
        chart=chart,
        operation="add_row",
        consumed=10,
        produced=10
    )
    
    result = service.validate_chart(chart, valid_request)
    assert result.is_valid == True, "Valid operation should pass"
    print("✓ Valid chart operation passes validation")
    
    # Test invalid operation (consuming more than available)
    invalid_request = ValidationRequest(
        chart=chart,
        operation="add_row",
        consumed=15,  # More than available
        produced=15
    )
    
    result = service.validate_chart(chart, invalid_request)
    assert result.is_valid == False, "Invalid operation should fail"
    assert len(result.errors) > 0, "Should have error messages"
    print("✓ Invalid chart operation fails validation correctly")
    
    return service


def test_create_visualization_observer():
    """Test create_visualization_observer() method."""
    print("\n=== Testing create_visualization_observer() Method ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    # Create observer
    observer = service.create_visualization_observer()
    
    assert observer is not None, "Observer should be created"
    assert isinstance(observer, ChartVisualizationObserver), "Should be ChartVisualizationObserver instance"
    print("✓ ChartVisualizationObserver created successfully")
    
    # Test that it has the mapper
    assert observer.mapper is not None, "Observer should have ViewModelMapper"
    print("✓ Observer has ViewModelMapper")
    
    return service, observer


def test_attach_visualization_observer():
    """Test attach_visualization_observer() method."""
    print("\n=== Testing attach_visualization_observer() Method ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    chart = service.create_chart(name="observer_test", start_side="RS", sts=23, rows=21)
    
    # Test attaching with auto-creation
    service.attach_visualization_observer(chart)
    
    assert len(chart.observers) == 1, "Chart should have one observer"
    assert isinstance(chart.observers[0], ChartVisualizationObserver), "Observer should be ChartVisualizationObserver"
    print("✓ Observer attached with auto-creation")
    
    # Test attaching with provided observer
    chart2 = service.create_chart(name="observer_test2", start_side="RS", sts=23, rows=21)
    observer = service.create_visualization_observer()
    service.attach_visualization_observer(chart2, observer)
    
    assert len(chart2.observers) == 1, "Chart should have one observer"
    assert chart2.observers[0] is observer, "Should be the provided observer"
    print("✓ Observer attached with provided instance")
    
    return service


def test_process_pattern_integration():
    """Test process_pattern() with auto-created PatternProcessor."""
    print("\n=== Testing process_pattern() Integration ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    chart = service.create_chart(name="pattern_test", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    
    # Process a pattern
    result = service.process_pattern(chart, "k5, p5")
    
    assert isinstance(result, ExpandedPattern), "Should return ExpandedPattern"
    assert result.consumed == 10, "Should consume 10 stitches"
    assert result.produced == 10, "Should produce 10 stitches"
    assert len(result.stitches) == 10, "Should have 10 stitches"
    print("✓ process_pattern() works with auto-created PatternProcessor")
    
    return service


def test_full_workflow():
    """Test a complete workflow using all ChartService features."""
    print("\n=== Testing Full Workflow ===")
    
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    # Create chart
    chart = service.create_chart(name="workflow_test", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    
    # Attach observer
    service.attach_visualization_observer(chart)
    assert len(chart.observers) == 1, "Observer should be attached"
    print("✓ Chart created with observer")
    
    # Process pattern
    expanded = service.process_pattern(chart, "k5, p5")
    assert expanded.consumed == 10, "Pattern should be processed"
    print("✓ Pattern processed")
    
    # Validate chart
    request = ValidationRequest(
        chart=chart,
        operation="add_row",
        consumed=10,
        produced=10
    )
    result = service.validate_chart(chart, request)
    assert result.is_valid == True, "Chart should be valid"
    print("✓ Chart validated")
    
    # Export and save
    service.save_chart(chart)
    print("✓ Chart saved")
    
    return service


def run_all_tests():
    """Run all ChartService integration tests."""
    print("=" * 60)
    print("CHART SERVICE COMPLETE INTEGRATION TEST SUITE")
    print("=" * 60)
    
    try:
        test_auto_create_pattern_processor()
        test_auto_create_validation_chain()
        test_validate_chart()
        test_create_visualization_observer()
        test_attach_visualization_observer()
        test_process_pattern_integration()
        test_full_workflow()
        
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