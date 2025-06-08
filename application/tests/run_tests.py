#!/usr/bin/env python3
"""
Test runner script for ChatApp
Run all tests and generate coverage reports
"""

import sys
import subprocess
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner"""
    print("ChatApp Test Suite")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists('app'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
    
    success = True
    
    # Install dependencies
    if os.path.exists('requirements-test.txt'):
        print("Installing test dependencies...")
        if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-test.txt'], 
                          "Installing test dependencies"):
            print("Warning: Could not install test dependencies")
    
    # Run unit tests
    print("\nRunning unit tests...")
    if not run_command([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                      "Unit tests"):
        success = False
    
    # Run tests with coverage
    print("\nRunning tests with coverage...")
    if not run_command([sys.executable, '-m', 'pytest', 'tests/', '--cov=app', '--cov-report=term-missing'], 
                      "Tests with coverage"):
        success = False
    
    # Summary
    print("\n" + "="*60)
    if success:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
    
    print("="*60)


if __name__ == '__main__':
    main()