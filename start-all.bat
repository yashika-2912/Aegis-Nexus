@echo off
echo Starting Aegis Shop Backend...
cd /d "%~dp0aegis-shop\backend"
start "Shop Services" cmd /k "python run_all.py"
timeout /t 3 /nobreak >nul

echo Starting Aegis Nexus Backend...
cd /d "%~dp0Aegis-Nexus\backend"
set PYTHONPATH=%CD%
start "Nexus Backend" cmd /k "set PYTHONPATH=%CD% && python -m uvicorn app.main:app --host 0.0.0.0 --port 8010"
timeout /t 2 /nobreak >nul

echo Starting Aegis Shop Frontend (port 3000)...
cd /d "%~dp0aegis-shop\frontend"
start "Shop Frontend" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo Starting Aegis Nexus Frontend (port 3001)...
cd /d "%~dp0Aegis-Nexus\frontend"
start "Nexus Frontend" cmd /k "npm run dev"

echo.
echo All services starting:
echo   Aegis Shop:    http://localhost:3000
echo   Aegis Nexus:   http://localhost:3001
echo   Shop API:      http://localhost:8000
echo   Nexus API:     http://localhost:8010
pause
