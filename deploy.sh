#!/bin/bash
# Deployment script for Aadhaar Identity Intelligence Platform Backend

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Aadhaar Intelligence Platform - Deployment          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found!${NC}"
    echo "Creating .env from template..."
    cp env.template .env
    echo -e "${RED}IMPORTANT: Edit .env file and add your NVIDIA_API_KEY${NC}"
    echo "Run: nano .env"
    exit 1
fi

# Check if NVIDIA_API_KEY is set
if grep -q "your_nvidia_api_key_here" .env; then
    echo -e "${RED}ERROR: Please set your NVIDIA_API_KEY in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configuration found${NC}"

# Check if data directory exists
if [ ! -d "backend/data" ]; then
    echo -e "${RED}ERROR: backend/data directory not found${NC}"
    echo "Please ensure your CSV data files are in backend/data/"
    exit 1
fi

echo -e "${GREEN}✓ Data directory found${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/engine/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker installed${NC}"

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo -e "${RED}ERROR: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose installed${NC}"
echo ""

# Stop existing containers
echo "📦 Stopping existing containers..."
docker compose down 2>/dev/null || true

# Build images
echo ""
echo "🔨 Building Docker images..."
docker compose build --no-cache

# Start services
echo ""
echo "🚀 Starting services..."
docker compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check backend health
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy!${NC}"
        break
    fi
    echo "Waiting for backend... ($((RETRY_COUNT+1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}ERROR: Backend failed to start${NC}"
    echo "Check logs with: docker compose logs backend"
    exit 1
fi

# Display status
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           DEPLOYMENT SUCCESSFUL! 🎉                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Services:"
echo "  🔹 Backend API:  http://localhost:8000"
echo "  🔹 API Docs:     http://localhost:8000/docs"
echo "  🔹 Health Check: http://localhost:8000/health"
echo "  🔹 Redis:        localhost:6379"
echo ""
echo "Management Commands:"
echo "  📊 View logs:     docker compose logs -f"
echo "  🔄 Restart:       docker compose restart"
echo "  ⏹  Stop:          docker compose stop"
echo "  🗑  Remove:        docker compose down"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/api/summary"
echo ""
