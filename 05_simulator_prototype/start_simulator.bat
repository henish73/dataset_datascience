@echo off
echo ==================================================
echo   Booting the 2026 AI-Labor Paradox Simulator...  
echo ==================================================

echo [1/2] Starting FastAPI Prediction Backend (Port 8000)...
start cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo [2/2] Starting Vite React Frontend (Port 5173)...
start cmd /k "cd frontend && npm run dev"

echo.
echo Dashboard should now be accessible at http://localhost:5173
echo API Swagger Docs available at http://localhost:8000/docs
echo.
