from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

def main():
    print("Hello from mcp-demo!")

@mcp.tool()
def get_user():
    return "User name is abhinav"


if __name__ == "__main__":
    mcp.run(transport="stdio")
