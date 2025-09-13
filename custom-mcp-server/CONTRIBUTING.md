# Contributing to MCP Database Server

Thank you for your interest in contributing to the MCP Database Server! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/mcp-database-server.git
   cd mcp-database-server
   ```
3. **Set up the development environment**:
   ```bash
   python setup.py
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
```bash
# Install in development mode
python setup.py

# Run tests to verify setup
pytest tests/ -v
```

## 📝 Making Changes

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

### Testing
- Write tests for new features
- Ensure all existing tests pass
- Aim for good test coverage
- Run the full test suite before submitting:
  ```bash
  pytest tests/ -v
  python validate_requirements.py
  python quick_functional_test.py
  ```

### Documentation
- Update README.md if adding new features
- Update API_DOCUMENTATION.md for new MCP tools
- Add inline code comments for complex logic
- Update CHANGELOG.md with your changes

## 🔄 Submitting Changes

### Pull Request Process
1. **Update your branch** with the latest main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run all tests** and ensure they pass

3. **Commit your changes** with clear messages:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

4. **Push to your fork**:
   ```bash
   git push origin your-feature-branch
   ```

5. **Create a Pull Request** on GitHub

### Commit Message Guidelines
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Examples:
- `Add: New search functionality for products`
- `Fix: Database connection timeout issue`
- `Update: README with new installation instructions`
- `Refactor: Database manager error handling`

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to reproduce the bug
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, etc.
- **Logs**: Any relevant error messages or logs

### Feature Requests
When requesting features, please include:
- **Use case**: Why is this feature needed?
- **Description**: Detailed description of the proposed feature
- **Examples**: Examples of how it would be used
- **Alternatives**: Any alternative solutions you've considered

## 🏗️ Project Structure

```
mcp-database-server/
├── src/                    # Source code
│   ├── database/          # Database layer
│   ├── server/            # MCP server implementation
│   └── client/            # Demo client
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/               # GitHub workflows
└── scripts/               # Utility scripts
```

## 🧪 Testing Guidelines

### Test Categories
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Functional Tests**: Test end-to-end workflows
- **Performance Tests**: Test performance characteristics

### Writing Tests
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Test both success and failure cases
- Mock external dependencies
- Keep tests independent and isolated

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_database_manager.py

# Run with coverage
pytest --cov=src

# Run performance tests
pytest tests/test_performance.py
```

## 📚 Code Review Guidelines

### For Contributors
- Keep pull requests focused and small
- Provide clear descriptions of changes
- Respond promptly to review feedback
- Be open to suggestions and improvements

### For Reviewers
- Be constructive and helpful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates

## 🎯 Areas for Contribution

### High Priority
- Performance optimizations
- Additional database backends
- Enhanced error handling
- Security improvements

### Medium Priority
- Additional MCP tools
- Better logging and monitoring
- Documentation improvements
- Example integrations

### Good First Issues
- Bug fixes
- Documentation updates
- Test improvements
- Code cleanup

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check README.md and API docs first

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to the MCP Database Server! 🎉