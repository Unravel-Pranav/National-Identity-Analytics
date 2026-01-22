@echo off
REM Start both backend and frontend for Windows

echo ==========================================
echo Starting Aadhaar Intelligence Platform
echo ==========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start backend in new window
start "Backend API" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "Frontend UI" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers started in separate windows!
echo.
pause

