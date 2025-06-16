FROM python:3.11-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project configuration
COPY pyproject.toml README.md ./

# Install dependencies with UV (resolves from pyproject.toml)
RUN uv pip install --system .

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Command to run the webhook server
CMD ["python", "-m", "src.webhook_server"]