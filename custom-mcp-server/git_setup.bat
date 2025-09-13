@echo off
echo Setting up Git repository for NoSQL MCP Server...
echo.

REM Initialize git repository
echo Initializing Git repository...
git init

REM Add all files
echo Adding all files to Git...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: NoSQL MCP Server v1.0.0

- Complete MCP server implementation with TinyDB integration
- Full CRUD operations (Create, Read, Update, Delete)
- Advanced search and filtering capabilities
- Sample data initialization with users, tasks, and products
- Comprehensive demonstration client with interactive features
- Automated setup and installation scripts
- Cross-platform startup scripts
- Complete documentation suite
- Extensive test suite with 240+ tests
- Package distribution system
- Kiro/VS Code integration guide"

REM Set main branch
echo Setting main branch...
git branch -M main

REM Add remote origin
echo Adding remote origin...
git remote add origin https://github.com/chandan1819/nosql-mcp-server.git

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

echo.
echo ✅ Successfully pushed to GitHub!
echo Repository URL: https://github.com/chandan1819/nosql-mcp-server
echo.
pause