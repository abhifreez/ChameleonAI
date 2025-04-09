import asyncio
import argparse
from .server import run_server

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the MCP server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on (default: 5000)')
    args = parser.parse_args()

    # Run the server
    await run_server(port=args.port)

if __name__ == "__main__":
    asyncio.run(main()) 