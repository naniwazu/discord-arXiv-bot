FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry: don't create virtual env, install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Command to run the webhook server
CMD ["python", "src/webhook_server.py"]