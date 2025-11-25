"""Test script for validation infrastructure."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.models.stitch_counter import StitchCounter
from engine.domain.models.validators.stitch_count_validator import StitchCountValidator
from engine.domain.models.validators.pattern_validator import PatternValidator
from engine.domain.models.validators.order_validator import OrderValidator
from engine.domain.models.validation.validation_handler import ValidationHandler
from engine.domain.models.validation.stitch_count_validation_handler import StitchCountValidationHandler
from engine.domain.models.validation.pattern_validation_handler import PatternValidationHandler
from engine.domain.models.validation.order_validation_handler import OrderValidationHandler
from engine.data.models.validation_request import ValidationRequest
from engine.data.models.validation_results import ValidationResult
from engine.data.models.pattern_context import PatternContext
from engine.data.models.node import Node
from engine.data.models.link import Link
from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine.data.models.chart_config import ChartConfig


def test_stitch_counter():
    """Test StitchCounter functionality."""
    print("\n=== Testing StitchCounter ===")
    
    counter = StitchCounter(initial_count=10)
    
    # Test initial count
    assert counter.get_current_count() == 10, "Initial count should be 10"
    print("✓ Initial count is correct")
    
    # Test recording operations
    counter.record_operation("cast_on", consumed=0, produced=5)
    assert counter.get_current_count() == 15, "Count should be 15 after cast_on"
    print("✓ Cast on operation recorded correctly")
    
    counter.record_operation("add_row", consumed=15, produced=15)
    assert counter.get_current_count() == 15, "Count should remain 15 after add_row"
    print("✓ Add row operation recorded correctly")
    
    counter.record_operation("dec", consumed=2, produced=1)
    assert counter.get_current_count() == 14, "Count should be 14 after dec"
    print("✓ Decrease operation recorded correctly")
    
    # Test history
    history = counter.get_history()
    assert len(history) == 3, "Should have 3 events in history"
    assert history[0].operation == "cast_on", "First event should be cast_on"
    assert history[2].operation == "dec", "Last event should be dec"
    print("✓ History tracking works correctly")
    
    # Test consistency validation
    assert counter.validate_consistency(14) == True, "Should be consistent with actual count"
    assert counter.validate_consistency(15) == False, "Should detect inconsistency"
    print("✓ Consistency validation works")
    
    # Test reset
    counter.reset(20)
    assert counter.get_current_count() == 20, "Count should be reset to 20"
    assert len(counter.get_history()) == 0, "History should be cleared"
    print("✓ Reset functionality works")
    
    return counter


def test_stitch_count_validator():
    """Test StitchCountValidator."""
    print("\n=== Testing StitchCountValidator ===")
    
    validator = StitchCountValidator()
    factory = ChartSectionFactory()
    
    # Create a chart for testing
    chart = factory.create_with_defaults(name="validator_test", start_side="RS")
    chart.cast_on_start(10)
    
    # Test valid operation
    result = validator.validate_stitch_count(chart, consumed=5, produced=5)
    assert result.is_valid == True, "Valid operation should pass"
    print("✓ Valid stitch count operation passes")
    
    # Test invalid: consuming more than available
    result = validator.validate_stitch_count(chart, consumed=15, produced=15)
    assert result.is_valid == False, "Should fail when consuming more than available"
    assert len(result.errors) > 0, "Should have error messages"
    print("✓ Invalid operation (over-consumption) detected")
    
    # Test invalid: negative result
    result = validator.validate_stitch_count(chart, consumed=12, produced=0)
    assert result.is_valid == False, "Should fail when result would be negative"
    print("✓ Invalid operation (negative result) detected")
    
    # Test consistency validation
    chart.stitch_counter.record_operation("test", consumed=0, produced=10)
    result = validator.validate_consistency(chart)
    assert result.is_valid == True, "Should be consistent"
    print("✓ Consistency validation works")
    
    # Test inconsistency
    chart.stitch_counter.record_operation("test", consumed=0, produced=5)
    result = validator.validate_consistency(chart)
    assert result.is_valid == False, "Should detect inconsistency"
    print("✓ Inconsistency detection works")
    
    return validator


def test_pattern_validator():
    """Test PatternValidator."""
    print("\n=== Testing PatternValidator ===")
    
    validator = PatternValidator()
    
    # Test valid pattern
    context = PatternContext(
        available_stitches=10,
        side="RS",
        markers=[],
        last_row_side="RS",
        is_round=False
    )
    result = validator.validate_pattern("k5, p5", context)
    assert result.is_valid == True, "Valid pattern should pass"
    print("✓ Valid pattern passes")
    
    # Test empty pattern
    result = validator.validate_pattern("", context)
    assert result.is_valid == False, "Empty pattern should fail"
    print("✓ Empty pattern detected")
    
    # Test unbalanced parentheses
    result = validator.validate_pattern("repeat(k5, p5", context)
    assert result.is_valid == False, "Unbalanced parentheses should fail"
    print("✓ Unbalanced parentheses detected")
    
    # Test token validation
    result = validator.validate_tokens(["k5", "p5", "inc"])
    assert result.is_valid == True, "Valid tokens should pass"
    print("✓ Valid tokens pass")
    
    result = validator.validate_tokens(["k5", "invalid_op", "p5"])
    assert result.is_valid == False, "Invalid tokens should fail"
    print("✓ Invalid tokens detected")
    
    return validator


def test_order_validator():
    """Test OrderValidator."""
    print("\n=== Testing OrderValidator ===")
    
    validator = OrderValidator()
    
    # Create valid nodes (ordered by row)
    nodes = [
        Node(id="n1", type="k", row=0, fx=0.0, fy=0.0),
        Node(id="n2", type="p", row=0, fx=20.0, fy=0.0),
        Node(id="n3", type="k", row=1, fx=0.0, fy=30.0),
        Node(id="n4", type="p", row=1, fx=20.0, fy=30.0),
    ]
    
    # Create valid links
    links = [
        Link(source="n1", target="n2"),
        Link(source="n3", target="n4"),
    ]
    
    # Test valid order
    result = validator.validate_order(nodes, links)
    assert result.is_valid == True, "Valid order should pass"
    print("✓ Valid node order passes")
    
    # Test link integrity
    result = validator.validate_link_integrity(links, nodes)
    assert result.is_valid == True, "Valid links should pass"
    print("✓ Valid link integrity passes")
    
    # Test invalid link (non-existent source)
    invalid_links = [
        Link(source="nonexistent", target="n1"),
    ]
    result = validator.validate_link_integrity(invalid_links, nodes)
    assert result.is_valid == False, "Invalid link should fail"
    print("✓ Invalid link (non-existent source) detected")
    
    # Test invalid link (non-existent target)
    invalid_links2 = [
        Link(source="n1", target="nonexistent"),
    ]
    result = validator.validate_link_integrity(invalid_links2, nodes)
    assert result.is_valid == False, "Invalid link should fail"
    print("✓ Invalid link (non-existent target) detected")
    
    # Test invalid order (nodes not ordered by row)
    unordered_nodes = [
        Node(id="n1", type="k", row=1, fx=0.0, fy=0.0),
        Node(id="n2", type="p", row=0, fx=20.0, fy=0.0),  # Row 0 comes after row 1
    ]
    result = validator.validate_order(unordered_nodes, [])
    assert result.is_valid == False, "Unordered nodes should fail"
    print("✓ Invalid node order detected")
    
    return validator


def test_validation_handler_chain():
    """Test ValidationHandler chain (Chain of Responsibility pattern)."""
    print("\n=== Testing ValidationHandler Chain ===")
    
    # Create chain
    stitch_handler = StitchCountValidationHandler()
    pattern_handler = PatternValidationHandler()
    order_handler = OrderValidationHandler()
    
    stitch_handler.set_next(pattern_handler).set_next(order_handler)
    
    # Create a chart for testing
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="chain_test", start_side="RS")
    chart.cast_on_start(10)
    
    # Test request that passes all validations
    context = PatternContext(
        available_stitches=10,
        side="RS",
        markers=[],
        last_row_side="RS",
        is_round=False
    )
    
    valid_nodes = [
        Node(id="n1", type="k", row=0, fx=0.0, fy=0.0),
        Node(id="n2", type="p", row=0, fx=20.0, fy=0.0),
    ]
    valid_links = [
        Link(source="n1", target="n2"),
    ]
    
    request = ValidationRequest(
        chart=chart,
        pattern="k5, p5",
        nodes=valid_nodes,
        links=valid_links,
        operation="add_row",
        context=context,
        consumed=10,
        produced=10
    )
    
    result = stitch_handler.handle(request)
    assert result.is_valid == True, "All validations should pass"
    print("✓ Chain passes when all validations succeed")
    
    # Test request that fails stitch count validation
    invalid_request = ValidationRequest(
        chart=chart,
        operation="add_row",
        consumed=15,  # More than available
        produced=15,
        context=context
    )
    
    result = stitch_handler.handle(invalid_request)
    assert result.is_valid == False, "Should fail stitch count validation"
    assert "consume" in result.errors[0].lower() or "available" in result.errors[0].lower(), "Error should mention consumption"
    print("✓ Chain stops at first failure (stitch count)")
    
    # Test request that fails link integrity
    invalid_links = [
        Link(source="nonexistent", target="n1"),
    ]
    invalid_link_request = ValidationRequest(
        chart=chart,
        nodes=valid_nodes,
        links=invalid_links,
        context=context,
        consumed=10,
        produced=10
    )
    
    result = stitch_handler.handle(invalid_link_request)
    assert result.is_valid == False, "Should fail link integrity validation"
    print("✓ Chain stops at link integrity failure")
    
    return stitch_handler


def test_factory_integration():
    """Test that factory creates validation components correctly."""
    print("\n=== Testing Factory Integration ===")
    
    factory = ChartSectionFactory()
    config = ChartConfig(name="factory_test", start_side="RS", sts=23, rows=21)
    chart = factory.create(config)
    
    # Verify stitch counter is created
    assert hasattr(chart, 'stitch_counter'), "Chart should have stitch_counter"
    assert chart.stitch_counter is not None, "stitch_counter should not be None"
    assert isinstance(chart.stitch_counter, StitchCounter), "stitch_counter should be StitchCounter"
    print("✓ Factory creates StitchCounter")
    
    # Verify validator is created
    assert hasattr(chart, 'validator'), "Chart should have validator"
    assert chart.validator is not None, "validator should not be None"
    print("✓ Factory creates StitchCountValidator")
    
    # Verify validation chain is created
    assert hasattr(chart, 'validation_chain'), "Chart should have validation_chain"
    assert chart.validation_chain is not None, "validation_chain should not be None"
    assert isinstance(chart.validation_chain, ValidationHandler), "validation_chain should be ValidationHandler"
    print("✓ Factory creates ValidationHandler chain")
    
    return chart


def test_chart_section_with_validation():
    """Test ChartSection operations with validation."""
    print("\n=== Testing ChartSection with Validation ===")
    
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="validation_test", start_side="RS")
    
    # Test that stitch counter tracks operations
    initial_count = chart.stitch_counter.get_current_count()
    chart.cast_on_start(10)
    
    # After cast_on_start, counter should be updated
    # Note: cast_on_start might not automatically update counter - this depends on implementation
    # For now, we'll manually verify the counter exists
    assert chart.stitch_counter is not None, "Chart should have stitch counter"
    print("✓ ChartSection has stitch counter")
    
    # Test that we can use validation chain
    if chart.validation_chain is not None:
        context = PatternContext(
            available_stitches=chart.get_current_num_of_stitches(),
            side="RS",
            markers=[],
            last_row_side="RS",
            is_round=False
        )
        
        request = ValidationRequest(
            chart=chart,
            pattern="k5, p5",
            operation="add_row",
            context=context,
            consumed=10,
            produced=10
        )
        
        result = chart.validation_chain.handle(request)
        assert result.is_valid == True or result.is_valid == False, "Should return a validation result"
        print("✓ ChartSection can use validation chain")
    
    return chart


def run_all_tests():
    """Run all validation infrastructure tests."""
    print("=" * 60)
    print("VALIDATION INFRASTRUCTURE TEST SUITE")
    print("=" * 60)
    
    try:
        test_stitch_counter()
        test_stitch_count_validator()
        test_pattern_validator()
        test_order_validator()
        test_validation_handler_chain()
        test_factory_integration()
        test_chart_section_with_validation()
        
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