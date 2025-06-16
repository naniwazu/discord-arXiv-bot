# Development Guide

## Setup

### Prerequisites
- Python 3.10+
- Poetry (Python package manager)

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-arxiv-bot.git
   cd discord-arxiv-bot
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install --with dev
   ```

   Or use the setup script:
   ```bash
   ./scripts/setup_dev.sh
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord credentials
   ```

## Testing

### Run all tests
```bash
make test
```

### Run tests with coverage
```bash
make test-cov
```

### Run specific test modules
```bash
# Test only the parser
make test-parser

# Test only the tokenizer
poetry run pytest tests/test_query_parser/test_tokenizer.py -v

# Run integration tests
make test-integration
```

### Run tests for different phases
```bash
# Phase 1 features only (current implementation)
poetry run pytest tests/ -v -k "not phase2 and not phase3"

# Include Phase 2 tests (when implemented)
poetry run pytest tests/ -v -k "not phase3"
```

## Code Quality

### Linting
```bash
make lint
```

### Auto-formatting
```bash
make format
```

### Type checking (if mypy is added)
```bash
poetry run mypy src/
```

## Running Locally

### Run webhook server
```bash
make run-webhook
# or
poetry run python src/webhook_server.py
```

### Run scheduler
```bash
make run-scheduler
# or
poetry run python src/scheduler.py
```

### Test with ngrok (for Discord webhook testing)
```bash
# Install ngrok if needed
# Run webhook server
make run-webhook

# In another terminal
ngrok http 8000

# Use the ngrok URL in Discord application settings
```

## Project Structure

```
.
├── src/
│   ├── query_parser/         # New query parser module
│   │   ├── parser.py        # Main parser
│   │   ├── tokenizer.py     # Tokenization
│   │   ├── transformer.py   # Query transformation
│   │   ├── validator.py     # Validation
│   │   ├── constants.py     # Constants
│   │   └── types.py         # Type definitions
│   ├── webhook_server.py    # Discord webhook handler
│   ├── scheduler.py         # Auto-search scheduler
│   └── tools.py            # Legacy parser (backward compatibility)
├── tests/
│   └── test_query_parser/   # Parser tests
│       ├── test_parser.py
│       ├── test_tokenizer.py
│       ├── test_transformer.py
│       ├── test_validator.py
│       ├── test_phase2_features.py
│       ├── test_phase3_features.py
│       ├── test_edge_cases.py
│       ├── test_arxiv_compatibility.py
│       └── test_integration.py
└── docs/
    ├── query-syntax-specification-v2.md
    └── refactoring-plan.md
```

## Contributing

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure tests pass
   ```bash
   make dev-test  # Runs lint and test
   ```

3. Commit with descriptive messages
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. Push and create a pull request

## Adding New Features

### Phase 2 Implementation (Operators)
1. Update `transformer.py` to handle OR/NOT operators
2. Remove `@pytest.mark.skip` from Phase 2 tests
3. Run Phase 2 tests: `poetry run pytest tests/test_query_parser/test_phase2_features.py`

### Phase 3 Implementation (Parentheses)
1. Enhance tokenizer for parentheses handling
2. Implement recursive parsing in transformer
3. Remove `@pytest.mark.skip` from Phase 3 tests
4. Run Phase 3 tests: `poetry run pytest tests/test_query_parser/test_phase3_features.py`

## Debugging

### Enable debug mode in parser
```python
parser = QueryParser(debug=True)
result = parser.parse("quantum @hinton")
print(result.debug_info)
```

### View query transformation
The webhook server shows transformed queries in Discord:
```
→ Query: `ti:quantum AND au:hinton` (20 results, Relevance Descending)
```

## Performance Testing

### Test with large queries
```bash
poetry run pytest tests/test_query_parser/test_edge_cases.py::TestEdgeCases::test_very_long_query -v
```

### Profile parser performance
```python
import cProfile
from src.query_parser import QueryParser

parser = QueryParser()
cProfile.run('parser.parse("complex query here")')
```