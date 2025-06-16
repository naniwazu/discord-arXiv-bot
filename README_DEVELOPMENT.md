# Development Guide

## Setup

### Prerequisites
- Python 3.10+
- UV (Ultra-fast Python package manager)

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-arxiv-bot.git
   cd discord-arxiv-bot
   ```

2. **Install UV** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up development environment**
   ```bash
   # Create virtual environment and install dependencies
   uv venv
   uv sync
   ```

4. **Set up environment variables**
   Environment variables are documented in CLAUDE.md:
   - `DISCORD_BOT_TOKEN` - Discord bot token
   - `DISCORD_PUBLIC_KEY` - Discord application public key
   - `DISCORD_APPLICATION_ID` - Discord application ID
   - `PORT` - Server port (default: 8000)

## Testing

### Run all tests
```bash
uv run pytest tests/ -v
```

### Run tests with coverage
```bash
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

### Run specific test modules
```bash
# Test only the parser
uv run pytest tests/test_query_parser/ -v

# Test only the tokenizer
uv run pytest tests/test_query_parser/test_tokenizer.py -v

# Run integration tests
uv run pytest tests/test_query_parser/test_integration.py -v
```

### Run tests for different phases
```bash
# Phase 1 features only (basic queries)
uv run pytest tests/ -v -k "not phase2 and not phase3"

# Phase 1 + Phase 2 tests (includes OR/NOT operators)
uv run pytest tests/ -v -k "not phase3"

# All phases (includes parentheses and grouping)
uv run pytest tests/ -v
```

## Code Quality

### Linting
```bash
uv run ruff check src/ tests/
```

### Auto-formatting
```bash
uv run ruff format src/ tests/
```

### Type checking (if mypy is added)
```bash
uv run mypy src/
```

## Running Locally

### Run webhook server
```bash
uv run python src/webhook_server.py
```

### Run scheduler
```bash
uv run python src/scheduler.py
```

### Test with ngrok (for Discord webhook testing)
```bash
# Install ngrok if needed
# Run webhook server
uv run python src/webhook_server.py

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
   # Run linting and tests
   uv run ruff check src/ tests/
   uv run pytest tests/ -v
   ```

3. Commit with descriptive messages
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. Push and create a pull request

## Query Parser Implementation Status

### ✅ Phase 1 (Completed)
- Basic keyword search with field prefixes (@author, #category, *all, $abstract)
- Numbers for result limits (1-1000)
- Sort options (s/r/l with d/a for direction)
- Phrase search with quotes

### ✅ Phase 2 (Completed)
- OR operator (`|`) for alternative terms: `quantum | neural`
- NOT operator (`-`) for exclusion: `quantum -classical`
- Mixed operators with proper precedence
- Advanced sorting (sa, ra, la for ascending order)

### ✅ Phase 3 (Completed)
- Parentheses grouping: `(quantum | neural) @hinton`
- Field context preservation: `@(hinton lecun)` → `au:(hinton AND lecun)`
- arXiv-style field grouping: `ti:(quantum computing)`
- Nested parentheses and complex expressions
- Error handling for unmatched/empty parentheses

## Adding New Features

### Testing Individual Phases
```bash
# Test Phase 2 features (operators)
uv run pytest tests/test_query_parser/test_phase2_features.py -v

# Test Phase 3 features (parentheses)
uv run pytest tests/test_query_parser/test_phase3_features.py -v

# Test all parser functionality
uv run pytest tests/test_query_parser/ -v
```

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
# Phase 1 example
→ Query: `ti:quantum AND au:hinton` (20 results, Relevance Descending)

# Phase 2 example  
→ Query: `(ti:quantum OR ti:neural) AND NOT ti:classical` (50 results, Submitted Ascending)

# Phase 3 example
→ Query: `(ti:quantum OR ti:neural) AND au:(hinton AND lecun)` (10 results, Relevance Descending)
```

## Performance Testing

### Test with large queries
```bash
uv run pytest tests/test_query_parser/test_edge_cases.py::TestEdgeCases::test_very_long_query -v
```

### Profile parser performance
```python
import cProfile
from src.query_parser import QueryParser

parser = QueryParser()

# Test Phase 3 complex query
complex_query = '(bert | gpt | t5) @google -@bengio (#cs.AI | #cs.LG) ti:(quantum computing)'
cProfile.run('parser.parse(complex_query)')
```