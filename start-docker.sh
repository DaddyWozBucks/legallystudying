#!/bin/bash

# LegalDify Docker Startup Script
# This script starts all required services in Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       LegalDify Docker Launcher          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed and running${NC}"

# Check if .env file exists, if not create from .env.docker
if [ ! -f .env ]; then
    if [ -f .env.docker ]; then
        echo -e "${YELLOW}📝 Creating .env file from .env.docker...${NC}"
        cp .env.docker .env
        echo -e "${GREEN}✅ .env file created${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your OpenRouter API key if not already set${NC}"
    else
        echo -e "${RED}❌ No .env or .env.docker file found!${NC}"
        echo "Creating a default .env file..."
        cat > .env << 'EOF'
# LegalDify Environment Configuration
LLM_PROVIDER=openrouter
LLM_MODEL=anthropic/claude-3-haiku
LLM_API_KEY=your-openrouter-api-key-here
EOF
        echo -e "${YELLOW}⚠️  Please edit .env and add your OpenRouter API key${NC}"
        read -p "Press Enter after adding your API key to continue..."
    fi
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is set
if [ "$LLM_API_KEY" = "your-openrouter-api-key-here" ] || [ -z "$LLM_API_KEY" ]; then
    echo -e "${RED}❌ OpenRouter API key not set!${NC}"
    echo "Please edit .env file and add your OpenRouter API key"
    echo "Get your API key from: https://openrouter.ai/keys"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p data plugins nginx/ssl backend/plugins

# Create nginx config if it doesn't exist
if [ ! -f nginx/nginx.conf ]; then
    echo -e "${YELLOW}📝 Creating nginx configuration...${NC}"
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name localhost;
        
        client_max_body_size 100M;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
EOF
fi

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest Docker images...${NC}"
docker-compose pull

# Build the backend image
echo -e "${YELLOW}🔨 Building backend Docker image...${NC}"
docker-compose build backend

# Start all services
echo -e "${GREEN}🚀 Starting all services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"

# Function to check service health
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps $service | grep -q "healthy"; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service failed to become healthy${NC}"
    return 1
}

# Check each service
check_service "postgres"
check_service "redis"
check_service "chromadb"
check_service "backend"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       LegalDify is ready!                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🌐 Access points:${NC}"
echo -e "  • API:       http://localhost:8000"
echo -e "  • API Docs:  http://localhost:8000/docs"
echo -e "  • pgAdmin:   http://localhost:5050 (run with --profile dev)"
echo ""
echo -e "${YELLOW}📝 Useful commands:${NC}"
echo -e "  • View logs:        docker-compose logs -f backend"
echo -e "  • Stop services:    docker-compose down"
echo -e "  • Restart backend:  docker-compose restart backend"
echo -e "  • View status:      docker-compose ps"
echo ""
echo -e "${GREEN}✨ Happy document processing!${NC}"