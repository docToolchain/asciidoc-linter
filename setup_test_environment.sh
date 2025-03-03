#!/bin/bash
# setup_test_environment.sh - Setup script for test environment

echo "Setting up test environment..."

# Upgrade pip
python -m pip install --upgrade pip

# Install project with test dependencies
pip install -e ".[test]"

# Install pyyaml
pip install pyyaml

echo "Test environment setup complete. You can now run: python run_tests_html.py OR python -m pytest"
