@echo off
echo Starting Custom MCP Server...
echo.
echo Press Ctrl+C to stop the server
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup.py first to create the environment.
    pause
    exit /b 1
)

REM Activate virtual environment and start server
venv\Scripts\python.exe run_server.py

echo.
echo Server stopped.
pause