@echo off
echo Starting AI FinOps Platform in development mode...

start "Backend" cmd /k "cd /d %~dp0..\backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd /d %~dp0..\frontend && npm run dev"

echo.
echo  Backend  : http://localhost:8000
echo  API Docs : http://localhost:8000/api/docs
echo  Frontend : http://localhost:3000
