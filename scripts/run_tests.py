#!/usr/bin/env python3
"""
Test runner script that executes all tests and returns status.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_single_test(test_file_path):
    """Run a single test file and return results."""
    test_name = os.path.basename(test_file_path)
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, test_file_path
        ], capture_output=True, text=True, timeout=30)
        
        return {
            'name': test_name,
            'passed': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'duration': 0  # Could add timing if needed
        }
    except subprocess.TimeoutExpired:
        return {
            'name': test_name,
            'passed': False,
            'output': '',
            'error': 'Test timed out after 30 seconds',
            'duration': 30
        }
    except Exception as e:
        return {
            'name': test_name,
            'passed': False,
            'output': '',
            'error': str(e),
            'duration': 0
        }

def run_all_tests():
    """Run all tests in the tests directory."""
    tests_dir = Path(__file__).parent.parent / 'tests'
    
    # Find all test files
    test_files = []
    for file_path in tests_dir.glob('test_*.py'):
        test_files.append(file_path)
    
    if not test_files:
        return {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'success_rate': 0.0,
            'timestamp': datetime.now().isoformat(),
            'results': [],
            'overall_status': 'no_tests'
        }
    
    # Run each test
    results = []
    for test_file in test_files:
        print(f"Running {test_file.name}...")
        result = run_single_test(test_file)
        results.append(result)
        
        # Print immediate feedback
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"  {status}")
        if not result['passed'] and result['error']:
            print(f"    Error: {result['error']}")
    
    # Calculate summary
    passed = sum(1 for r in results if r['passed'])
    failed = len(results) - passed
    success_rate = (passed / len(results)) * 100 if results else 0
    
    overall_status = 'passed' if failed == 0 else 'failed'
    
    return {
        'total_tests': len(results),
        'passed': passed,
        'failed': failed,
        'success_rate': success_rate,
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'overall_status': overall_status
    }

def main():
    """Main function to run tests and display results."""
    print("=" * 50)
    print("Running all tests...")
    print("=" * 50)
    
    test_results = run_all_tests()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Success rate: {test_results['success_rate']:.1f}%")
    print(f"Timestamp: {test_results['timestamp']}")
    
    if test_results['overall_status'] == 'passed':
        print("\n✅ ALL TESTS PASSED!")
        return 0
    elif test_results['overall_status'] == 'failed':
        print("\n❌ SOME TESTS FAILED!")
        return 1
    else:
        print("\n⚠️  NO TESTS FOUND!")
        return 1

if __name__ == "__main__":
    sys.exit(main())