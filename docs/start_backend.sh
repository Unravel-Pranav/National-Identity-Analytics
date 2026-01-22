#!/bin/bash
# Start the FastAPI backend server

echo "🚀 Starting FastAPI backend on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

