# UV-based Makefile for arXiv Discord Bot
PYTHON_RUN = uv run

.PHONY: help install test lint format clean run-webhook run-scheduler

help:
	@echo "Available commands:"
	@echo "  install       Install dependencies with UV"
	@echo "  test          Run tests"
	@echo "  lint          Run linter"  
	@echo "  format        Format code"
	@echo "  clean         Clean up cache files"
	@echo "  run-webhook   Run webhook server"
	@echo "  run-scheduler Run scheduler"

install:
	uv sync

test:
	$(PYTHON_RUN) pytest tests/ -v

test-cov:
	$(PYTHON_RUN) pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

lint:
	$(PYTHON_RUN) ruff check src/ tests/

format:
	$(PYTHON_RUN) ruff format src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .ruff_cache

run-webhook:
	$(PYTHON_RUN) python src/webhook_server.py

run-scheduler:
	$(PYTHON_RUN) python src/scheduler.py

# Development shortcuts
dev-test: lint test

# Quick test for specific module
test-parser:
	$(PYTHON_RUN) pytest tests/test_query_parser/ -v

test-tokenizer:
	$(PYTHON_RUN) pytest tests/test_query_parser/test_tokenizer.py -v

test-integration:
	$(PYTHON_RUN) pytest tests/test_query_parser/test_integration.py -v

# Development shortcuts
dev-test: lint test

# Quick test for specific modules
test-parser:
	$(PYTHON_RUN) pytest tests/test_query_parser/ -v