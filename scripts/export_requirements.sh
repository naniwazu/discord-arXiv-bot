#!/bin/bash
# Export requirements.txt files from poetry for UV usage

echo "Exporting requirements from poetry.lock..."

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Using uvx to run poetry..."
    POETRY_CMD="uvx poetry"
else
    POETRY_CMD="poetry"
fi

# Export main dependencies
echo "Exporting main dependencies..."
$POETRY_CMD export -f requirements.txt -o requirements.txt --without-hashes

# Export dev dependencies
echo "Exporting dev dependencies..."
$POETRY_CMD export -f requirements.txt -o requirements-dev.txt --without-hashes --only dev

# Create a combined file for convenience
echo "Creating combined requirements file..."
cat requirements.txt > requirements-all.txt
echo "" >> requirements-all.txt
echo "# Development dependencies" >> requirements-all.txt
cat requirements-dev.txt >> requirements-all.txt

echo "Done! Created:"
echo "  - requirements.txt (main dependencies)"
echo "  - requirements-dev.txt (dev only)"
echo "  - requirements-all.txt (combined)"
echo ""
echo "To install with UV:"
echo "  uv pip install -r requirements-all.txt"