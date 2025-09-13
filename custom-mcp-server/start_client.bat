@echo off
echo Starting MCP Client Demonstration...
echo.
echo This will demonstrate all CRUD operations
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run setup.py first to create the environment.
    pause
    exit /b 1
)

REM Activate virtual environment and start client
venv\Scripts\python.exe demo_client.py

echo.
echo Demonstration completed.
pause