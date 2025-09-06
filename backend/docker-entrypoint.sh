#!/bin/bash
set -e

echo "Starting LegalDify Backend Service..."

# Create necessary directories if they don't exist
mkdir -p /app/data/chroma_db /app/plugins /app/logs /app/uploads

# Wait for PostgreSQL to be ready
if [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    export PGPASSWORD=$POSTGRES_PASSWORD
    until pg_isready -h postgres -p 5432 -U legaldify; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "PostgreSQL is ready!"
    
    # Run database initialization/migration script
    echo "Running database initialization script..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U legaldify -d legaldify -f /app/init_db.sql || echo "Database initialization completed or already initialized"
    
    # Run database migrations if alembic is configured
    if [ -f "alembic.ini" ]; then
        echo "Running database migrations..."
        alembic upgrade head || echo "No migrations to run"
    fi
fi

# ChromaDB doesn't need to be fully ready for the backend to start
# It will connect when needed
echo "ChromaDB service is starting in the background..."
sleep 5

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
until nc -z redis 6379; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "Redis is ready!"

# Download embedding model if not cached
echo "Checking embedding model..."
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL:-sentence-transformers/all-MiniLM-L6-v2}')" || true

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --reload \
    --reload-dir /app/app \
    --reload-dir /app/domain \
    --reload-dir /app/infrastructure \
    --log-level ${LOG_LEVEL:-info}