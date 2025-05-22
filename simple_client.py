"""MCP HTTP client example using MCP SDK."""

import asyncio
import sys
from typing import Any
from urllib.parse import urlparse

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


def print_items(name: str, result: Any) -> None:
    # print("RAW RESULT:", result)

    print("", f"Available {name}:", sep="\n")
    items = getattr(result, name)
    if items:
        for item in items:
            print(" *", item)
    else:
        print("No items available")


async def main(server_url='http://localhost:8000/sse'):
    try:
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                # await session.call_tool(name="list_desktop_files")
                # await session.list_tools()
                print_items("content", (await session.call_tool(name="list_desktop_files")))
                print_items("tools", (await session.list_tools()))
                
    except Exception as e:
        print(f"Error connecting to server: {e}")    #     sys.exit(1)
        sys.exit(1)    
        
    
if __name__ == "__main__":    
    asyncio.run(main())