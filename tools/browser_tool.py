import os
import logging
import sys
import time
import inspect

from math import hypot
from utils.element_util import extract_element_info
from utils.logger import log_tool_call
from utils.response_format import format_tool_response, init_tool_response
from pywinauto import Application, mouse
from utils.gen_code import record_calls

        

def register_mouse_tools(mcp, browser_manager):
    """Register mouse tools to MCP server."""

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def mouse_drag_drop(caller: str, source_title: str, source_control_type: str, target_title:str, target_control_type: str, 
                              scenario: str = '', step_raw: str = '', step: str = '', need_snapshot: int = 1) -> str:
        """
        Performs a drag and drop operation from source element to target element
        
        Args:
            caller: Identifier of the calling module/function
            source_title: The name/title of the source element to drag from (typically a TreeItem in Edge)
            source_control_type: The type of control of source element
            target_title: The name/title of the target element to drop onto (typically a TreeItem in Edge)
            target_control_type: The type of control of target element
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with status and error information
            
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            source = dlg.child_window(title=source_title, control_type=source_control_type) 
            target = dlg.child_window(title=target_title, control_type=target_control_type)
            start_point = source.rectangle().mid_point()
            end_point = target.rectangle().mid_point()

            mouse.press(coords=start_point)
            time.sleep(0.5)
            x1, y1 = start_point
            x2, y2 = end_point
            total_distance = hypot(x2 - x1, y2 - y1)
            step_size = 20
            steps = max(1, int(total_distance // step_size))
            for i in range(1, steps + 1):
                xi = x1 + (x2 - x1) * i // steps
                yi = y1 + (y2 - y1) * i // steps
                mouse.move(coords=(xi, yi))
                time.sleep(0.5)
            mouse.release(coords=end_point)
            time.sleep(0.5)
            resp["status"] = "success"
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logging.error(f"Error dragging from '{source}' to '{target}': {e}")
            
        return format_tool_response(resp)
    

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def mouse_hover(caller: str, name: str, control_type: str = 'Button', scenario: str = '', 
                          step_raw: str = '', step: str = '', need_snapshot: int = 1) -> str:
        """
        Moves the mouse to hover over a specified UI element
        
        Args:
            caller: Identifier of the calling module/function
            name: The name/title of the element to hover over
            control_type: The type of control to hover over (default: Button, can be TreeItem, Text, etc.)
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with status and error information
            
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            target = dlg.child_window(title=name, control_type=control_type) 
            target_point = target.rectangle().mid_point()
            mouse.move(coords=target_point)
            time.sleep(0.5)
            snapshot = extract_element_info(browser_manager.get_main_window())   
            resp["status"] = "success"
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logging.error(f"Error hovering over element '{name}': {e}")
            
        return format_tool_response(resp)
