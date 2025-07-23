#!/usr/bin/env python3
"""
Screenshot MCP Server for macOS
An MCP server that enables natural language screenshot capture
"""

import asyncio
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Screenshot save directory
SCREENSHOT_DIR = Path.home() / "Desktop" / "mcp-screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

class ScreenshotServer:
    def __init__(self):
        self.server = Server("screenshot-mcp")
        self._setup_tools()
        
    def _setup_tools(self):
        """Define available tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="screenshot",
                    description="Capture a screenshot of the entire desktop",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Filename to save (auto-generated if omitted)"
                            },
                            "delay": {
                                "type": "integer",
                                "description": "Delay in seconds before capture (default: 0)",
                                "default": 0
                            }
                        }
                    }
                ),
                Tool(
                    name="screenshot_window",
                    description="Capture a screenshot of a specific window (interactive selection)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Filename to save (auto-generated if omitted)"
                            }
                        }
                    }
                ),
                Tool(
                    name="screenshot_area",
                    description="Capture a screenshot of a selected area (interactive selection)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Filename to save (auto-generated if omitted)"
                            }
                        }
                    }
                ),
                Tool(
                    name="list_screenshots",
                    description="List saved screenshots",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of screenshots to list (default: 10)",
                                "default": 10
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[TextContent | ImageContent | EmbeddedResource]:
            if name == "screenshot":
                return await self._take_screenshot(arguments or {})
            elif name == "screenshot_window":
                return await self._take_window_screenshot(arguments or {})
            elif name == "screenshot_area":
                return await self._take_area_screenshot(arguments or {})
            elif name == "list_screenshots":
                return await self._list_screenshots(arguments or {})
            else:
                return [TextContent(text=f"Unknown tool: {name}")]
    
    async def _take_screenshot(self, args: Dict[str, Any]) -> List[TextContent]:
        """Capture full desktop screenshot"""
        try:
            # Generate filename
            filename = args.get("filename")
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = SCREENSHOT_DIR / filename
            delay = args.get("delay", 0)
            
            # Execute screencapture command
            cmd = ["screencapture"]
            if delay > 0:
                cmd.extend(["-T", str(delay)])
            cmd.append(str(filepath))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get file size
                file_size = filepath.stat().st_size / 1024  # KB
                return [TextContent(
                    text=f"Screenshot saved successfully\n"
                         f"File: {filepath}\n"
                         f"Size: {file_size:.1f} KB"
                )]
            else:
                return [TextContent(
                    text=f"Error: Failed to capture screenshot\n{result.stderr}"
                )]
                
        except Exception as e:
            return [TextContent(text=f"Error: {str(e)}")]
    
    async def _take_window_screenshot(self, args: Dict[str, Any]) -> List[TextContent]:
        """Capture specific window screenshot"""
        try:
            filename = args.get("filename")
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"window_{timestamp}.png"
            
            filepath = SCREENSHOT_DIR / filename
            
            # -W option for window selection mode
            cmd = ["screencapture", "-W", str(filepath)]
            
            subprocess.Popen(cmd)
            
            return [TextContent(
                text="Click on a window to capture screenshot...\n"
                     f"(Will be saved to: {filepath})"
            )]
            
            # Note: screencapture runs asynchronously, so we can't detect actual capture completion
            
        except Exception as e:
            return [TextContent(text=f"Error: {str(e)}")]
    
    async def _take_area_screenshot(self, args: Dict[str, Any]) -> List[TextContent]:
        """Capture selected area screenshot"""
        try:
            filename = args.get("filename")
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"area_{timestamp}.png"
            
            filepath = SCREENSHOT_DIR / filename
            
            # -s option for selection mode
            cmd = ["screencapture", "-s", str(filepath)]
            
            subprocess.Popen(cmd)
            
            return [TextContent(
                text="Drag to select an area to capture...\n"
                     f"(Will be saved to: {filepath})"
            )]
            
        except Exception as e:
            return [TextContent(text=f"Error: {str(e)}")]
    
    async def _list_screenshots(self, args: Dict[str, Any]) -> List[TextContent]:
        """List saved screenshots"""
        try:
            limit = args.get("limit", 10)
            
            # Get PNG files sorted by modification time
            screenshots = sorted(
                SCREENSHOT_DIR.glob("*.png"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:limit]
            
            if not screenshots:
                return [TextContent(text="No screenshots found")]
            
            # Create list
            lines = ["Recent screenshots:"]
            for i, screenshot in enumerate(screenshots, 1):
                size_kb = screenshot.stat().st_size / 1024
                mtime = datetime.fromtimestamp(screenshot.stat().st_mtime)
                lines.append(
                    f"{i}. {screenshot.name} "
                    f"({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})"
                )
            
            return [TextContent(text="\n".join(lines))]
            
        except Exception as e:
            return [TextContent(text=f"Error: {str(e)}")]
    
    async def run(self):
        """Start the server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())

def main():
    """Main function"""
    server = ScreenshotServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()