#!/bin/bash

# LegalDify Setup Script
# This script sets up both the backend and prepares the frontend for development

set -e

echo "🚀 LegalDify Setup Script"
echo "========================="
echo ""

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.11 or higher is required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version found"

# Check Swift/Xcode
echo "📍 Checking Swift installation..."
if ! command -v swift &> /dev/null; then
    echo "❌ Error: Swift/Xcode is not installed"
    echo "Please install Xcode from the Mac App Store"
    exit 1
fi
echo "✅ Swift found"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
echo "------------------------"

cd backend

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p plugins
mkdir -p chroma_db
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
# LegalDify Backend Configuration
DEBUG=False
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite:///./legal_dify.db

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=legal_documents

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM Configuration (add your API key here)
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
# LLM_API_KEY=your-api-key-here
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=100
EOL
    echo "⚠️  Please edit backend/.env and add your LLM API key"
fi

# Download embedding model
echo "🤖 Downloading embedding model (this may take a few minutes)..."
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

echo "✅ Backend setup complete!"

# Setup Frontend
echo ""
echo "🔧 Setting up Frontend..."
echo "------------------------"

cd ../client

# Build Swift package
echo "📦 Building Swift package..."
swift build

echo "✅ Frontend setup complete!"

# Final instructions
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend service:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo ""
echo "2. Open the frontend in Xcode:"
echo "   cd client"
echo "   open Package.swift"
echo "   Then press ⌘+R to build and run"
echo ""
echo "📚 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "⚠️  Don't forget to add your OpenAI API key to backend/.env!"
echo ""