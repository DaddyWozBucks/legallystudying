# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    netcat-traditional \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Update pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir psycopg2-binary && \
    pip install --no-cache-dir redis && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/plugins /app/data/chroma_db /app/logs /app/uploads /app/ocr_output/extracted_text /app/ocr_output/logs

# Download the embedding model during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy and set permissions for entrypoint
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Use the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]