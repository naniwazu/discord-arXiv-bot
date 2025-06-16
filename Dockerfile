FROM python:3.11-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies with UV
RUN uv pip install --system -r uv.lock

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Command to run the webhook server
CMD ["python", "src/webhook_server.py"]