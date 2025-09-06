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

-- Add summary and key_points columns for storing document summaries
ALTER TABLE documents ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS key_points JSON;

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

-- Create degrees table if it doesn't exist
CREATE TABLE IF NOT EXISTS degrees (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    abbreviation VARCHAR NOT NULL,
    description TEXT NOT NULL,
    prompt_context TEXT NOT NULL,
    department VARCHAR NOT NULL,
    duration_years FLOAT DEFAULT 0.0,
    credit_hours INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSON DEFAULT '{}'
);

-- Create indexes for degrees table
CREATE INDEX IF NOT EXISTS idx_degrees_is_active ON degrees(is_active);
CREATE INDEX IF NOT EXISTS idx_degrees_department ON degrees(department);

-- Create courses table if it doesn't exist
CREATE TABLE IF NOT EXISTS courses (
    id VARCHAR PRIMARY KEY,
    course_number VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT NOT NULL,
    prompt_context TEXT NOT NULL,
    degree_id VARCHAR,
    credits INTEGER DEFAULT 0,
    semester VARCHAR NOT NULL,
    professor VARCHAR NOT NULL,
    attributes TEXT[] DEFAULT '{}',
    prerequisites TEXT[] DEFAULT '{}',
    learning_objectives TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    metadata JSON DEFAULT '{}',
    FOREIGN KEY (degree_id) REFERENCES degrees(id) ON DELETE SET NULL
);

-- Create indexes for courses table
CREATE INDEX IF NOT EXISTS idx_courses_course_number ON courses(course_number);
CREATE INDEX IF NOT EXISTS idx_courses_degree_id ON courses(degree_id);
CREATE INDEX IF NOT EXISTS idx_courses_is_active ON courses(is_active);
CREATE INDEX IF NOT EXISTS idx_courses_semester ON courses(semester);

-- Add course_id to documents table for linking documents to courses
ALTER TABLE documents ADD COLUMN IF NOT EXISTS course_id VARCHAR;
-- Add foreign key constraint (will skip if already exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_documents_course') THEN
        ALTER TABLE documents ADD CONSTRAINT fk_documents_course 
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_documents_course_id ON documents(course_id);

-- Add week column to documents table for grouping readings by week
ALTER TABLE documents ADD COLUMN IF NOT EXISTS week INTEGER;
CREATE INDEX IF NOT EXISTS idx_documents_week ON documents(week);

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON TABLE documents TO legaldify;
GRANT ALL PRIVILEGES ON TABLE prompts TO legaldify;
GRANT ALL PRIVILEGES ON TABLE degrees TO legaldify;
GRANT ALL PRIVILEGES ON TABLE courses TO legaldify;