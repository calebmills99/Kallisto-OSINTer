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

# Use gunicorn for production
# Timeout set to 300s (5 minutes) for long-running OSINT operations
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "guardr_api:app"]
