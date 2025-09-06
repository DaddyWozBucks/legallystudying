-- LegalDify Database Initialization Script
-- This script creates the initial database schema for PostgreSQL

-- Create documents table if it doesn't exist
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    path VARCHAR NOT NULL,
    content_hash VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    size_bytes INTEGER NOT NULL,
    processing_status VARCHAR DEFAULT 'pending',
    parser_plugin_id VARCHAR,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSON DEFAULT '{}',
    raw_text TEXT  -- Store extracted text for quick access
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);

-- Add raw_text column if it doesn't exist (for existing databases)
ALTER TABLE documents ADD COLUMN IF NOT EXISTS raw_text TEXT;

-- Create prompts table if it doesn't exist
CREATE TABLE IF NOT EXISTS prompts (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT NOT NULL,
    template TEXT NOT NULL,
    category VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSON DEFAULT '{}'
);

-- Create indexes for prompts table
CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompts(name);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_is_active ON prompts(is_active);

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON TABLE documents TO legaldify;
GRANT ALL PRIVILEGES ON TABLE prompts TO legaldify;