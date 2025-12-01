"""Test runner that executes all Python test files."""
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_module(module_name: str) -> Tuple[bool, str]:
    """
    Run a test module and return success status and output.
    
    Args:
        module_name: Name of the test module (e.g., 'test_factory')
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    output_buffer = io.StringIO()
    error_buffer = io.StringIO()
    
    try:
        # Import the test module
        module = __import__(f'engine.{module_name}', fromlist=['run_all_tests'])
        
        # Check if it has a run_all_tests function
        if hasattr(module, 'run_all_tests'):
            # Capture output
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                success = module.run_all_tests()
            
            output = output_buffer.getvalue()
            errors = error_buffer.getvalue()
            
            if errors:
                output += f"\nErrors:\n{errors}"
            
            return success, output
        else:
            # If no run_all_tests function, execute the file as a script
            test_file_path = Path(__file__).parent / f"{module_name}.py"
            
            if not test_file_path.exists():
                return False, f"Test file not found: {test_file_path}"
            
            # Run the test file as a subprocess
            result = subprocess.run(
                [sys.executable, str(test_file_path)],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nStderr:\n{result.stderr}"
            
            # Success if exit code is 0
            success = result.returncode == 0
            
            return success, output
            
    except Exception as e:
        return False, f"Error running {module_name}: {str(e)}\n{error_buffer.getvalue()}"


def main():
    """Run all test files."""
    print("=" * 80)
    print("RUNNING ALL PYTHON TESTS")
    print("=" * 80)
    print()
    
    # List of all test files (without .py extension)
    test_modules = [
        'test_factory',
        'test_refactored_chart_section',
        'test_service_integration',
        'test_chart_service_complete',
        'test_view_models',
        'test_validation_infrastructure',
        'test_pattern_parser_refactor',
        'test_pattern_processor',
    ]
    
    results: List[Tuple[str, bool, str]] = []
    total_tests = len(test_modules)
    passed_tests = 0
    
    # Run each test
    for module_name in test_modules:
        print(f"\n{'=' * 80}")
        print(f"Running {module_name}...")
        print('=' * 80)
        
        success, output = run_test_module(module_name)
        results.append((module_name, success, output))
        
        if success:
            passed_tests += 1
            print(f"✓ {module_name} PASSED")
        else:
            print(f"✗ {module_name} FAILED")
        
        # Print output (last 50 lines to avoid overwhelming output)
        if output:
            lines = output.strip().split('\n')
            if len(lines) > 50:
                print("\n... (showing last 50 lines) ...")
                print('\n'.join(lines[-50:]))
            else:
                print(output)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print()
    
    # Print detailed results
    for module_name, success, output in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status:12} {module_name}")
    
    print("=" * 80)
    
    # Exit with appropriate code
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {total_tests - passed_tests} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
