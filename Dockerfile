# Mikrobot FastVersion - Production Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r mikrobot && useradd -r -g mikrobot mikrobot

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY docs/ ./docs/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY models/ ./models/
COPY config/ ./config/

# Copy configuration files
COPY CLAUDE.md .
COPY CLAUDE_QUICK_REFER.md .
COPY README.md .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models /app/temp && \
    chown -R mikrobot:mikrobot /app

# Switch to non-root user
USER mikrobot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]