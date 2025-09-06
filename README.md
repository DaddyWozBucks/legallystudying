# LegalDify - AI-Powered Document Intelligence Platform

> A sophisticated, modular document intelligence platform that enables semantic search and AI-powered analysis of documents through a local RAG (Retrieval-Augmented Generation) pipeline.

A sophisticated, modular document intelligence platform that enables semantic search and AI-powered analysis of documents through a local RAG (Retrieval-Augmented Generation) pipeline.

## Architecture Overview

LegalDify follows Clean Architecture principles with a clear separation of concerns:

### Backend (Python/FastAPI)
- **Domain Layer**: Core business entities and use cases
- **Application Layer**: API endpoints, DTOs, and services
- **Infrastructure Layer**: Database implementations, external integrations
- **Plugin System**: Extensible document parsing architecture

### Frontend (Swift/SwiftUI)
- **MVVM Architecture**: Clear separation of views and business logic
- **Coordinator Pattern**: Centralized navigation management
- **Native macOS Integration**: Deep platform integration

## Features

- **Document Processing**: Support for PDF, DOCX, and extensible formats
- **Semantic Search**: AI-powered document search using vector embeddings
- **RAG Pipeline**: Question-answering with source attribution
- **Plugin Architecture**: Easy extension with new document parsers
- **Native macOS Experience**: SwiftUI-based interface with platform integration

## 🚀 Quick Start with Docker

The easiest way to run LegalDify is using Docker, which includes all required services.

### Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- 8GB RAM minimum (16GB recommended)
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))

### One-Command Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/legal_dify.git
cd legal_dify
```

2. Copy the environment file and add your API key:
```bash
cp .env.docker .env
# Edit .env and add your OpenRouter API key
```

3. Start all services:
```bash
./start-docker.sh
```

That's it! The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin** (optional): http://localhost:5050

### What's Included in Docker

The Docker setup automatically provisions:
- ✅ **PostgreSQL** - Primary database
- ✅ **ChromaDB** - Vector database for semantic search
- ✅ **Redis** - Caching and task queue
- ✅ **Backend API** - FastAPI service with all dependencies
- ✅ **Nginx** - Reverse proxy (ports 80/443)
- ✅ **pgAdmin** - Database management UI (optional)

## Manual Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

5. Start the backend service:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Build the Swift package:
```bash
swift build
```

3. Open in Xcode:
```bash
open Package.swift
```

4. Build and run from Xcode (⌘+R)

## Docker Management

### Common Docker Commands

```bash
# Start all services
./start-docker.sh

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart a specific service
docker-compose restart backend

# View service status
docker-compose ps

# Remove all data and start fresh
docker-compose down -v
docker-compose up -d

# Access backend shell
docker-compose exec backend bash

# Run with development profile (includes pgAdmin)
docker-compose --profile dev up -d
```

### Troubleshooting Docker

If you encounter issues:

1. **Services won't start**: Check Docker Desktop is running
2. **Port conflicts**: Ensure ports 8000, 5432, 6379, 8001 are free
3. **Out of memory**: Increase Docker Desktop memory allocation
4. **Permission issues**: Run `chmod +x start-docker.sh`

## Usage

### Starting the Application

1. First, ensure the backend service is running:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

2. Launch the macOS client from Xcode or the built application

### Importing Documents

1. Click the "+" button or use File → Import Document (⌘+O)
2. Select PDF or DOCX files to import
3. Documents are automatically processed and indexed

### Searching Documents

1. Use the search bar or press ⌘+F
2. Enter natural language queries
3. View AI-generated answers with source attribution

## Plugin Development

Create custom document parsers by implementing the `IDataSourcePlugin` interface:

```python
from infrastructure.plugins.base_plugin import IDataSourcePlugin

class CustomPlugin(IDataSourcePlugin):
    @staticmethod
    def get_name() -> str:
        return "custom_parser"
    
    @staticmethod
    def get_supported_identifiers() -> List[str]:
        return [".custom"]
    
    async def process(self, source_path: str) -> List[Dict[str, Any]]:
        # Implementation here
        pass
```

Place the plugin file in `backend/plugins/` and it will be automatically loaded.

## API Documentation

Once the backend is running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

### Backend Configuration

Edit `backend/app/config.py` or use environment variables:

- `DATABASE_URL`: SQLite database location
- `CHROMA_PERSIST_DIRECTORY`: Vector database storage
- `CHUNK_SIZE`: Text chunk size for embeddings
- `MAX_FILE_SIZE_MB`: Maximum upload file size

### Client Configuration

Access Settings in the macOS app to configure:
- Backend URL
- Processing preferences
- UI preferences

## Project Structure

```
legal_dify/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── dto/          # Data transfer objects
│   │   ├── services/     # Business services
│   │   └── config.py     # Configuration
│   ├── domain/
│   │   ├── entities/     # Core business entities
│   │   ├── use_cases/    # Business logic
│   │   └── repositories/ # Repository interfaces
│   ├── infrastructure/
│   │   ├── database/     # Database implementations
│   │   ├── plugins/      # Plugin system
│   │   └── parsers/      # Document parsers
│   └── plugins/          # Custom plugins directory
├── client/
│   └── LegalDify/
│       ├── Application/   # App entry point
│       ├── Domain/        # Business models
│       ├── Infrastructure/# Services and networking
│       └── Presentation/  # Views and ViewModels
└── docs/                  # Documentation

```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd client
swift test
```

## Performance Considerations

- **Embedding Model**: The default model balances speed and accuracy
- **Chunk Size**: Adjust based on document types and query patterns
- **Vector Database**: ChromaDB provides good performance for up to 1M vectors
- **Concurrent Processing**: Documents are processed asynchronously

## Troubleshooting

### Backend won't start
- Check Python version: `python3 --version` (requires 3.11+)
- Verify all dependencies: `pip install -r requirements.txt`
- Check port availability: `lsof -i :8000`

### Client can't connect
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check firewall settings
- Ensure localhost is accessible

### Document processing fails
- Check file permissions
- Verify plugin is loaded: Check `/api/v1/plugins` endpoint
- Review logs in backend console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes following the architecture guidelines
4. Add tests for new functionality
5. Submit a pull request

## License

[License details to be added]

## Support

For issues and questions:
- GitHub Issues: [repository issues page]
- Documentation: See `/docs` directory# legallystudying
