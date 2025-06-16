#!/bin/bash
# Development environment setup script

echo "Setting up development environment for arXiv Discord Bot..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing via pip..."
    pip install poetry
fi

# Install dependencies
echo "Installing dependencies..."
poetry install --with dev

# Install pre-commit hooks if available
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Installing pre-commit hooks..."
    poetry run pre-commit install
fi

# Run initial tests
echo "Running tests to verify setup..."
poetry run pytest tests/test_query_parser/test_parser.py::TestQueryParser::test_simple_keyword -v

echo "Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  make test       - Run all tests"
echo "  make lint       - Run linter"
echo "  make format     - Format code"
echo "  make test-cov   - Run tests with coverage"
echo ""
echo "Or use poetry directly:"
echo "  poetry run pytest tests/ -v"
echo "  poetry run ruff check src/"