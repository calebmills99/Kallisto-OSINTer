# Dockerfile for Kallisto-OSINTer Flask API
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1001 kallisto && \
    chown -R kallisto:kallisto /app

USER kallisto

# Expose Flask port
EXPOSE 5000

# Use gunicorn for production with async API
# Single worker to share in-memory job storage (use Redis for multi-worker in production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "--threads", "4", "guardr_api_async:app"]
