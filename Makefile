# Detect if UV is available and preferred
ifdef USE_UV
  PYTHON_RUN = uv run
  INSTALL_CMD = uv pip install -r requirements-all.txt
else ifdef USE_UVX
  PYTHON_RUN = uvx
  INSTALL_CMD = uvx poetry install --with dev
else
  PYTHON_RUN = poetry run
  INSTALL_CMD = poetry install --with dev
endif

.PHONY: help install test lint format clean run-webhook run-scheduler

help:
	@echo "Available commands:"
	@echo "  install       Install dependencies"
	@echo "  install-uv    Install with UV (fast)"
	@echo "  test          Run tests"
	@echo "  lint          Run linter"
	@echo "  format        Format code"
	@echo "  clean         Clean up cache files"
	@echo "  run-webhook   Run webhook server"
	@echo "  run-scheduler Run scheduler"
	@echo ""
	@echo "Environment variables:"
	@echo "  USE_UV=1      Use UV for all commands"
	@echo "  USE_UVX=1     Use UVX for all commands"

install:
	$(INSTALL_CMD)

install-uv:
	@echo "Setting up UV environment..."
	uv venv
	./scripts/export_requirements.sh
	uv pip install -r requirements-all.txt

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

# UV-specific commands
uv-test:
	USE_UV=1 make test

uv-run:
	USE_UV=1 make run-webhook