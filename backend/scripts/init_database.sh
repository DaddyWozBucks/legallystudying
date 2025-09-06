#!/bin/bash

# LegalDify Database Initialization Script
# This script initializes the PostgreSQL database for LegalDify

set -e

# Load environment variables
source ../.env 2>/dev/null || true

# Database connection parameters
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-legaldify}"
DB_USER="${DB_USER:-legaldify}"
DB_PASSWORD="${DB_PASSWORD:-legaldify123}"

echo "Initializing LegalDify database..."

# Check if running in Docker or local
if [ -f /.dockerenv ]; then
    # Running in Docker
    PSQL_CMD="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
else
    # Running locally - use docker-compose
    PSQL_CMD="docker-compose exec -T postgres psql -U $DB_USER -d $DB_NAME"
fi

# Run the initialization SQL
if [ -f ../init_db.sql ]; then
    echo "Running database initialization script..."
    $PSQL_CMD < ../init_db.sql
    echo "Database initialization complete!"
else
    echo "Error: init_db.sql not found!"
    exit 1
fi

# Verify the schema
echo "Verifying database schema..."
$PSQL_CMD -c "\d documents" || echo "Warning: Could not verify documents table"

echo "Database setup complete!"