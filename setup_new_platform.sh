#!/bin/bash
# Setup script for the new React + FastAPI platform

echo "=========================================="
echo "Aadhaar Intelligence Platform Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo ""
echo "✅ Prerequisites check passed"
echo ""

# Setup Backend
echo "📦 Setting up FastAPI backend..."
cd backend
echo "   Installing Python dependencies..."
pip install -r requirements.txt
cd ..

# Setup Frontend
echo ""
echo "📦 Setting up React frontend..."
cd frontend
echo "   Installing Node dependencies (this may take a few minutes)..."
npm install
cd ..

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the platform:"
echo "  1. Start the backend:  ./start_backend.sh"
echo "  2. Start the frontend: ./start_frontend.sh"
echo ""
echo "Or use: ./start_platform.sh (starts both)"
echo ""

