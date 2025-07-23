#!/usr/bin/env python3
"""
Screenshot MCP Server for macOS using FastMCP
An MCP server that enables natural language screenshot capture
"""

import subprocess
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

# Screenshot save directory
SCREENSHOT_DIR = Path.home() / "Desktop" / "mcp-screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP("screenshot-mcp")

@mcp.tool()
def screenshot(filename: Optional[str] = None, delay: int = 0) -> str:
    """Capture a screenshot of the entire desktop"""
    logging.info(f"screenshot called with filename: {filename}, delay: {delay}")
    
    try:
        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = SCREENSHOT_DIR / filename
        
        # Execute screencapture command
        cmd = ["screencapture"]
        if delay > 0:
            cmd.extend(["-T", str(delay)])
        cmd.append(str(filepath))
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Get file size
            file_size = filepath.stat().st_size / 1024  # KB
            success_msg = f"Screenshot saved successfully to {filepath} ({file_size:.1f} KB)"
            logging.info(f"Screenshot successful: {success_msg}")
            return success_msg
        else:
            error_msg = f"Error: Failed to capture screenshot\n{result.stderr}"
            logging.error(f"Screenshot failed: {error_msg}")
            return error_msg
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logging.error(f"Exception in screenshot: {error_msg}", exc_info=True)
        return error_msg

@mcp.tool()
def screenshot_window(filename: Optional[str] = None) -> str:
    """Capture a screenshot of a specific window (interactive selection)"""
    logging.info(f"screenshot_window called with filename: {filename}")
    
    try:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"window_{timestamp}.png"
        
        filepath = SCREENSHOT_DIR / filename
        
        # -W option for window selection mode
        cmd = ["screencapture", "-W", str(filepath)]
        
        subprocess.Popen(cmd)
        
        msg = f"Click on a window to capture screenshot...\n(Will be saved to: {filepath})"
        logging.info(f"Window screenshot initiated: {msg}")
        return msg
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logging.error(f"Exception in screenshot_window: {error_msg}", exc_info=True)
        return error_msg

@mcp.tool()
def screenshot_area(filename: Optional[str] = None) -> str:
    """Capture a screenshot of a selected area (interactive selection)"""
    logging.info(f"screenshot_area called with filename: {filename}")
    
    try:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"area_{timestamp}.png"
        
        filepath = SCREENSHOT_DIR / filename
        
        # -s option for selection mode
        cmd = ["screencapture", "-s", str(filepath)]
        
        subprocess.Popen(cmd)
        
        msg = f"Drag to select an area to capture...\n(Will be saved to: {filepath})"
        logging.info(f"Area screenshot initiated: {msg}")
        return msg
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logging.error(f"Exception in screenshot_area: {error_msg}", exc_info=True)
        return error_msg

@mcp.tool()
def list_screenshots(limit: int = 10) -> str:
    """List saved screenshots"""
    logging.info(f"list_screenshots called with limit: {limit}")
    
    try:
        # Get PNG files sorted by modification time
        screenshots = sorted(
            SCREENSHOT_DIR.glob("*.png"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        if not screenshots:
            return "No screenshots found"
        
        # Create list
        lines = ["Recent screenshots:"]
        for i, screenshot in enumerate(screenshots, 1):
            size_kb = screenshot.stat().st_size / 1024
            mtime = datetime.fromtimestamp(screenshot.stat().st_mtime)
            lines.append(
                f"{i}. {screenshot.name} "
                f"({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})"
            )
        
        result = "\n".join(lines)
        logging.info(f"Listed {len(screenshots)} screenshots")
        return result
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logging.error(f"Exception in list_screenshots: {error_msg}", exc_info=True)
        return error_msg

def main():
    """Main function"""
    logging.info("Starting FastMCP screenshot server...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()