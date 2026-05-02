@echo off
echo ============================================================
echo  AI GenPerf ^& FinOps Intelligence Framework — Setup
echo ============================================================

echo.
echo [1/3] Setting up Python backend environment...
cd /d "%~dp0..\backend"
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo      Backend dependencies installed.

echo.
echo [2/3] Setting up Node.js frontend...
cd /d "%~dp0..\frontend"
call npm install --silent
echo      Frontend dependencies installed.

echo.
echo [3/3] Creating .env file...
cd /d "%~dp0.."
if not exist .env (
    copy .env.example .env >nul
    echo      .env created from template.
) else (
    echo      .env already exists, skipping.
)

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  Start backend:   cd backend ^&^& .venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo  Start frontend:  cd frontend ^&^& npm run dev
echo  Docker:          docker-compose up --build
echo ============================================================
