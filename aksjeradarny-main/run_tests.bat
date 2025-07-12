@echo off
echo Running AksjeRadar Test Suite
echo ==========================

echo Installing dependencies...
pip install colorama requests

echo.
echo Starting Flask application...
start cmd /k "cd %~dp0 && python run.py"

echo.
echo Waiting for application to start...
timeout /t 5 /nobreak > nul

echo.
echo Running service tests...
python test_services.py

echo.
echo Running endpoint tests...
python test_endpoints.py

echo.
echo Tests completed! Press any key to exit.
pause > nul
