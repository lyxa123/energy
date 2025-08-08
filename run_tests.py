#!/usr/bin/env python3
"""
Test runner for Energy City Simulator

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Run with verbose output
    python run_tests.py tests/test_entities.py  # Run specific test file
"""

import sys
import subprocess
import os

def main():
    """Run pytest with the tests directory"""
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Default to running all tests in the tests directory
    args = sys.argv[1:] if len(sys.argv) > 1 else ['tests/', '-v']
    
    # Run pytest
    cmd = [sys.executable, '-m', 'pytest'] + args
    return subprocess.call(cmd)

if __name__ == '__main__':
    sys.exit(main())
