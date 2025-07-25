# Screenshot MCP Server

A Model Context Protocol (MCP) server that enables natural language screenshot capture on macOS using FastMCP.

## Features

- **Full Desktop Screenshots**: Capture the entire desktop with optional delay
- **Window Screenshots**: Interactive window selection for capturing specific applications
- **Area Screenshots**: Interactive area selection for capturing custom regions
- **Screenshot Management**: List and manage saved screenshots
- **Automatic Organization**: Screenshots saved to `~/Desktop/mcp-screenshots/`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/screenshot-mcp.git
cd screenshot-mcp
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Testing

Run the test script to verify everything is working:
```bash
python test_server.py
```

## Configuration

Add the following to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "/path/to/screenshot-mcp/venv/bin/python",
      "args": ["/path/to/screenshot-mcp/server.py"],
      "env": {}
    }
  }
}
```

Replace `/path/to/screenshot-mcp` with the actual path to your cloned repository.

## Available Tools

### `screenshot`
Captures a screenshot of the entire desktop.
- **Parameters**:
  - `filename` (optional): Custom filename for the screenshot
  - `delay` (optional): Delay in seconds before capturing (default: 0)

### `screenshot_window`
Captures a screenshot of a specific window through interactive selection.
- **Parameters**:
  - `filename` (optional): Custom filename for the screenshot

### `screenshot_area`
Captures a screenshot of a selected area through interactive selection.
- **Parameters**:
  - `filename` (optional): Custom filename for the screenshot

### `list_screenshots`
Lists recently saved screenshots with details.
- **Parameters**:
  - `limit` (optional): Maximum number of screenshots to list (default: 10)

## Usage Examples

Once configured in Claude Desktop, you can use natural language commands like:
- "Take a screenshot"
- "Capture a screenshot with 3 second delay"
- "Take a screenshot of this window"
- "Screenshot just this area"
- "Show me my recent screenshots"

## Requirements

- macOS (uses built-in `screencapture` command)
- Python 3.8+
- Claude Desktop application

## File Structure

```
screenshot-mcp/
├── server.py          # Main MCP server implementation
├── test_server.py     # Test script for verification
├── requirements.txt   # Python dependencies
├── README.md         # This file
└── .gitignore        # Git ignore rules
```

## Troubleshooting

1. **Permission Issues**: macOS may require screen recording permissions for the application running the server
2. **Path Issues**: Ensure the paths in the Claude Desktop configuration are absolute and correct
3. **Virtual Environment**: Make sure to use the Python interpreter from your virtual environment

## License

This project is open source. Feel free to modify and distribute as needed.