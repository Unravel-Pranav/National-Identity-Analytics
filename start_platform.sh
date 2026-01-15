#!/bin/bash
# Start both backend and frontend concurrently

echo "=========================================="
echo "Starting Aadhaar Intelligence Platform"
echo "=========================================="
echo ""
echo "🔧 Backend API: http://localhost:8000"
echo "🎨 Frontend UI: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in foreground
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

