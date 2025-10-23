# Multi-stage Dockerfile for production deployment

# Stage 1: Build stage for Python dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy server requirements
COPY server/pyproject.toml server/uv.lock* ./server/

# Install dependencies
RUN cd server && uv sync --frozen

# Stage 2: Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /app/server/.venv /app/server/.venv

# Copy application code
COPY server/ ./server/

# Set environment variables
ENV PATH="/app/server/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app/server

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/')" || exit 1

# Run the application with daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]





