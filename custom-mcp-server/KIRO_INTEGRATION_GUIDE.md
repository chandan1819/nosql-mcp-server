# Using Custom MCP Server with Kiro/VS Code

## Setup Instructions

### 1. Configure MCP Server in Kiro

Add the following configuration to your `.kiro/settings/mcp.json` file:

```json
{
  "mcpServers": {
    "custom-database-server": {
      "command": "python",
      "args": [
        "custom-mcp-server/run_server.py"
      ],
      "env": {
        "MCP_LOG_LEVEL": "INFO",
        "PYTHONPATH": "custom-mcp-server/src"
      },
      "disabled": false,
      "autoApprove": [
        "read_records",
        "search_records",
        "create_record",
        "update_record",
        "delete_record"
      ]
    }
  }
}
```

### 2. Initialize the Database

Before using the server, make sure the database is initialized:

```bash
cd custom-mcp-server
python setup.py
```

### 3. Restart Kiro

After adding the configuration, restart Kiro to load the new MCP server.

## Using the Database in Chat

Once configured, you can use natural language in Kiro chat to interact with your database:

### Example Chat Queries

#### 📊 **Getting Database Information**

**"Show me all users in the database"**
- This will use the `read_records` tool to fetch all users

**"How many tasks are there?"**
- This will query the tasks collection and show the count

**"What products do we have in stock?"**
- This will filter products where `in_stock` is true

#### 🔍 **Searching and Filtering**

**"Find all tasks assigned to user ID 1"**
- Uses filtering to show tasks for a specific user

**"Show me high priority tasks"**
- Filters tasks by priority level

**"List products under $50"**
- Filters products by price range

#### 📈 **Data Analysis Requests**

**"Create a summary of task statuses"**
- Kiro will fetch tasks and create a summary breakdown

**"Show me user activity - who has the most tasks?"**
- Analyzes task assignments across users

**"What's the average product price?"**
- Calculates statistics from product data

#### 📊 **Chart and Visualization Requests**

**"Create a chart showing task distribution by status"**
- Kiro will fetch task data and create a visual chart

**"Show me a bar chart of products by category"**
- Visualizes product distribution

**"Create a pie chart of user roles"**
- Shows user role distribution visually

### Available MCP Tools

Your custom server provides these tools that Kiro can use:

1. **`read_records`** - Fetch records from any collection
   - Collections: `users`, `tasks`, `products`
   - Supports filtering

2. **`search_records`** - Advanced search with complex filters
   - Supports multiple criteria
   - Logical operators (AND, OR)

3. **`create_record`** - Add new records
   - Auto-generates IDs
   - Validates data

4. **`update_record`** - Modify existing records
   - Filter-based updates
   - Partial updates supported

5. **`delete_record`** - Remove records
   - Safety checks included
   - Filter-based deletion

### Sample Database Content

Your database contains:

**Users Collection:**
- Admin users and regular users
- Fields: id, name, email, role, created_at

**Tasks Collection:**
- Various tasks with assignments
- Fields: id, title, description, assigned_to, status, priority, created_at, due_date

**Products Collection:**
- Sample products with pricing
- Fields: id, name, description, price, category, in_stock, created_at

## Troubleshooting

### Server Not Connecting
1. Check that Python is in your PATH
2. Verify the server path in the configuration
3. Check Kiro's MCP server logs
4. Ensure the database is initialized

### Tools Not Available
1. Restart Kiro after configuration changes
2. Check the MCP server status in Kiro's MCP panel
3. Verify the `autoApprove` list includes the tools you want to use

### Database Errors
1. Run `python custom-mcp-server/setup.py` to reinitialize
2. Check that the `data/` directory exists
3. Verify database file permissions

## Advanced Usage

### Custom Queries
You can ask Kiro to perform complex operations:

**"Find all overdue tasks and update their priority to high"**
- Combines read and update operations

**"Create a new user and assign them the pending tasks"**
- Combines create and update operations

**"Generate a report of completed tasks by user"**
- Complex data analysis and formatting

### Data Visualization
Kiro can create various chart types with your data:

- **Bar Charts**: Task counts by status, products by category
- **Pie Charts**: User role distribution, task priority breakdown  
- **Line Charts**: Task completion over time (if you add timestamps)
- **Tables**: Formatted data displays with sorting and filtering

### Integration with Other Tools
Your MCP server can work alongside other MCP servers in Kiro, allowing you to:

- Combine database data with external APIs
- Use AI tools to analyze your database content
- Generate documentation from your database schema
- Create automated reports and dashboards

## Next Steps

1. **Add More Data**: Populate your database with real data for your use case
2. **Extend Schema**: Add more fields or collections as needed
3. **Custom Tools**: Add specialized MCP tools for your specific workflows
4. **Automation**: Create Kiro hooks to automatically update data
5. **Reporting**: Build custom reporting tools using the MCP interface

Happy querying! 🚀