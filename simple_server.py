# # -*- coding: utf-8 -*-
import os
import logging
import sys
import argparse
from mcp.server.fastmcp import FastMCP
from browser_session import BrowserSessionManager
from tools.browser_tool import register_browser_tools
from tools.gen_code_tool import register_gen_code_tools
from tools.mouse_tool import register_mouse_tools
from tools.verify_tool import register_verify_tools
from utils.logger import log_tool_call

settings = {
    "log_level": "DEBUG"
}

# 创建 MCP server
mcp = FastMCP("hello-mcp-server", log_level="INFO", settings=settings)
browser_manager = None  # 全局可访问


def main():
    global browser_manager
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["edge", "edge-beta"], default="edge")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="sse")
    args = parser.parse_args()
    
    browser_manager = BrowserSessionManager(args.browser)

    register_browser_tools(mcp, browser_manager)
    register_mouse_tools(mcp, browser_manager)
    register_gen_code_tools(mcp, browser_manager)
    register_verify_tools(mcp, browser_manager)

    mcp.run(args.transport)


if __name__ == "__main__":
    main()
   
