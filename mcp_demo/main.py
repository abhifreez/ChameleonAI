from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

def main():
    print("Hello from mcp-demo!")

@mcp.tool()
def get_user():
    return "Heena's date of birth is 17th Aug she crips 24 hours"


if __name__ == "__main__":
    mcp.run(transport="stdio")
