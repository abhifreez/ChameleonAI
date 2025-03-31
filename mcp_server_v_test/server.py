#from mcp.server.factmcp import FastMCP
from mcp.server.fastmcp import FastMCP

# Load environment variables


# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# if __name__ == "__main__":
#     # Initialize and run the server
#     mcp.run(transport='stdio')
# if __name__ == "__main__":
    
#     mcp.run(transport="studio")
    #mcp.run(config={"port": 3000}, transport="http")


if __name__ == "__main__":
    mcp.run()