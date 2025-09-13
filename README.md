# NoSQL MCP Server

[![Tests](https://github.com/chandan1819/nosql-mcp-server/workflows/Tests/badge.svg)](https://github.com/chandan1819/nosql-mcp-server/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/chandan1819/nosql-mcp-server.svg)](https://github.com/chandan1819/nosql-mcp-server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/chandan1819/nosql-mcp-server.svg)](https://github.com/chandan1819/nosql-mcp-server/network)

A **Model Context Protocol (MCP) server** implementation with **NoSQL database integration** using TinyDB. This server provides full CRUD operations through MCP tools and includes a comprehensive demonstration client.

> 🚀 **Perfect for**: AI assistants, chatbots, data analysis, rapid prototyping, and educational projects

## ✨ Features

- 🔧 **Complete MCP Server** with TinyDB NoSQL database
- 📊 **Full CRUD Operations** (Create, Read, Update, Delete)
- 🔍 **Advanced Search & Filtering** with complex queries
- 🎯 **Sample Data** - Users, Tasks, and Products collections
- 🤖 **Interactive Demo Client** with progress reporting
- ⚡ **One-Command Setup** - `python setup.py`
- 🖥️ **Cross-Platform** - Windows, macOS, Linux
- 🧪 **240+ Tests** with automated CI/CD
- 📚 **Comprehensive Documentation** and guides
- 🔗 **Kiro/VS Code Integration** for chat-based queries

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/chandan1819/nosql-mcp-server.git
cd nosql-mcp-server

# 2. Navigate to the project
cd custom-mcp-server

# 3. Automated setup (creates venv, installs deps, initializes DB)
python setup.py

# 4. Start the server
python run_server.py

# 5. In another terminal, run the demo
python demo_client.py
```

**That's it!** The demo will showcase INSERT, FETCH, UPDATE, and DELETE operations.

## 🎯 Use Cases

### 🤖 AI Assistant Integration
Connect your AI assistant to a persistent database for:
- User preferences and history
- Task management and tracking  
- Product catalogs and inventory
- Custom data storage needs

### 💬 Chat-Based Database Queries
Use with Kiro or VS Code to query your database using natural language:
- *"Show me all high priority tasks"*
- *"Create a chart of user activity"*
- *"Find products under $50"*
- *"Update all pending tasks to in-progress"*

### 🔬 Rapid Prototyping
Perfect for quickly building data-driven applications:
- NoSQL flexibility for evolving schemas
- Instant setup with sample data
- RESTful-like operations through MCP
- Easy integration with existing tools

## 📊 What's Included

### 🗄️ Database Collections
- **Users** - Sample user accounts with roles
- **Tasks** - Project tasks with assignments and priorities  
- **Products** - Product catalog with pricing and categories

### 🛠️ MCP Tools
- `create_record` - Add new records with validation
- `read_records` - Fetch records with optional filtering
- `update_record` - Modify existing records
- `delete_record` - Remove records with safety checks
- `search_records` - Advanced search with complex queries

### 📱 Demo Client Features
- Interactive demonstration mode
- Quick test mode for automation
- Progress reporting and error handling
- Before/after comparisons for updates
- Comprehensive logging

## 🔧 Advanced Features

### 🔍 Complex Queries
```python
# Find high priority tasks assigned to active users
{
  "collection": "tasks",
  "filters": {
    "priority": "high",
    "assigned_to": {"$in": [1, 2, 3]},
    "status": {"$ne": "completed"}
  }
}
```

### 📈 Data Analysis
- User activity tracking
- Task completion statistics
- Product inventory management
- Custom reporting capabilities

### 🔗 Integration Options
- **Kiro IDE** - Chat-based database queries
- **VS Code** - MCP extension support
- **Custom Clients** - Build your own MCP clients
- **API Integration** - Use as a data backend

## 📚 Documentation

- **[Complete Setup Guide](custom-mcp-server/README.md)** - Detailed installation and usage
- **[API Documentation](custom-mcp-server/API_DOCUMENTATION.md)** - All MCP tools and examples
- **[Kiro Integration Guide](custom-mcp-server/KIRO_INTEGRATION_GUIDE.md)** - Chat-based database queries
- **[Demo Client Guide](custom-mcp-server/DEMO_CLIENT_README.md)** - Interactive demonstration
- **[Contributing Guide](custom-mcp-server/CONTRIBUTING.md)** - Development guidelines

## 🧪 Testing & Quality

- **240+ Comprehensive Tests** covering all functionality
- **GitHub Actions CI/CD** with automated testing
- **Cross-Platform Testing** on Python 3.8-3.12
- **Code Quality Checks** and validation scripts
- **Performance Testing** and benchmarks

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](custom-mcp-server/CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](custom-mcp-server/LICENSE) file for details.

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

## 🔗 Links

- **Repository**: https://github.com/chandan1819/nosql-mcp-server
- **Issues**: https://github.com/chandan1819/nosql-mcp-server/issues
- **Discussions**: https://github.com/chandan1819/nosql-mcp-server/discussions
- **MCP Protocol**: https://modelcontextprotocol.io/

---

**Built with ❤️ for the MCP community**