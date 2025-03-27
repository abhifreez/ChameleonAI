# MCP Server Package

This package provides an MCP (Message Control Protocol) server implementation for content generation.

## Installation

The package is part of the main project and should be installed with the project dependencies.

## Usage

### Running the Server

You can run the server in two ways:

1. As a module:
```bash
python -m mcp_server
```

2. With a custom port:
```bash
python -m mcp_server --port 5001
```

### Importing in Code

```python
from mcp_server import ChameleonMCP, run_server

# Use the server class directly
server = ChameleonMCP()

# Or run the server
await run_server(port=5000)
```

## Available Tools

1. `generate_lecture`: Generates lecture content with title and topics
   - Required parameters:
     - `lecture_title`: string
     - `topics`: array of strings
   - Optional parameters:
     - `structure_model`: string (default: "gemini-2.0-flash")
     - `presentation_model`: string (default: "gemini-2.0-flash")
     - `notes_model`: string (default: "gemini-2.0-flash")

2. `generate_content`: Generates general content using a specified model
   - Required parameters:
     - `prompt`: string
   - Optional parameters:
     - `model_name`: string (default: "deepseek")
     - `system_prompt`: string 