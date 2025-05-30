import json
import os
import logging
import sys
import time
import inspect

from utils.element_util import extract_element_info
from utils.keyboard_util import get_shortcut_key
from utils.logger import log_tool_call
from utils.response_format import format_tool_response, init_tool_response
from utils.gen_code import record_calls
from utils.alert_util import close_translate_pane, close_all_alert

        
logger = logging.getLogger(__name__)

def register_verify_tools(mcp, browser_manager):
    """Register verify tools to MCP server."""   
    
        
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def verify_element_exists(caller: str, 
                                    element_name: str, 
                                    control_type: str, 
                                    timeout: int = 5,
                                    scenario: str = "", 
                                    step_raw: str = "",
                                    step: str = "", 
                                    need_snapshot: int = 1
                                    ) -> str:
        """
        Verify/check if an element exists/appears
        
        Args:
            element_name: Name or text of the element to search for
            control_type: Optional control type for more specific search (TreeItem, Button, etc.)
            timeout: Maximum time in seconds to wait for the element
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            search_parent = dlg
            
            # Prepare search criteria based on parameters
            search_kwargs = {}
            search_kwargs["title_re"] = f".*{element_name}.*"
            search_kwargs["control_type"] = control_type
            
            # First try a quick search
            try:
                element = search_parent.child_window(**search_kwargs)
                
                # Check if element exists with timeout
                exists = element.exists(timeout=timeout)
                
                if exists:
                    # Get additional details about the found element
                    resp["status"] = "success"
                else:
                    resp["status"] = "failed"
                    resp["error"] = f"Element '{element_name}' not found within {timeout} seconds."
                    logger.error(f"{resp['error']}: {search_kwargs}")
            except Exception as search_error:
                resp["error"] = repr(search_error)
                logger.error(f"Error searching for element '{element_name}': {search_error}")

            if need_snapshot == 1:
                logger.info(f" verify_element_exists extract_element_info start .......")
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                logger.info(f" verify_element_exists extract_element_info end")
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error in verify_element_exists for '{element_name}': {e}")
               
        return format_tool_response(resp)
    

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def verify_checkbox_state(caller: str,
                                checkbox_name: str,
                                expected_state: str,
                                control_type: str = "CheckBox",
                                timeout: int = 5,
                                scenario: str = "", 
                                step_raw: str = "",
                                step: str = "",
                                need_snapshot: int = 1
                                ) -> str:
        """
        Verifies if a checkbox is checked or unchecked.
        
        Args:
            caller: Identifier of the calling module/function
            checkbox_name: Name or title of the checkbox to verify
            expected_state: The expected state: "checked" or "unchecked"
            control_type: Control type, defaults to "CheckBox"
            timeout: Maximum time in seconds to wait for the checkbox
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with verification result and status information
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            # Prepare search criteria based on parameters
            search_kwargs = {}
            search_kwargs["title"] = checkbox_name
            search_kwargs["control_type"] = control_type

            checkbox_element = dlg.child_window(**search_kwargs)
            exists = checkbox_element.exists(timeout=timeout)
            
            if exists:
                # Get the toggle state
                is_checked = checkbox_element.get_toggle_state() == 1
                actual_state = "checked" if is_checked else "unchecked"
                
                if expected_state.lower() == actual_state:                       
                    resp["status"] = "success"
                    resp["data"]["actual_state"] = actual_state
                else:
                    resp["status"] = "failed"
                    resp["error"] = f"Checkbox state mismatch. Expected: '{expected_state}', Actual: '{actual_state}'"
                    logger.error(resp["error"])
            else:
                resp["status"] = "failed"
                resp["error"] = f"Checkbox '{checkbox_name}' not found within {timeout} seconds."
                logger.error(f"{resp['error']}: {search_kwargs}")

            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error in verify_checkbox_state for '{checkbox_name}': {e}")
               
        return format_tool_response(resp)
    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def verify_element_value(caller: str,
                               element_name: str,
                               element_value: str,
                               control_type: str, 
                               expected_value: str,
                               step_raw: str = "",
                               step: str = "",
                               scenario: str = "", 
                               timeout: int = 5,
                               need_snapshot: int = 1
                               ) -> str:
        """
        Verifies that an control contains the expected value/content.
        
        Args:
            caller: Identifier of the calling module/function
            element_name: Name or title of the element to search for
            element_value: value of the control, extract from the element value
            control_type: Optional control type for more specific search (Edit, Button, etc.)
            expected_value: The expected value to verify, only extract from the step content, do not extract from the element value
            step_raw: Raw original step text
            step: Current test step description              
            scenario: Test scenario name
            timeout: Maximum time in seconds to wait for the element

            
        Returns:
            JSON response with verification result and status information
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            
            # Prepare search criteria based on parameters
            search_kwargs = {}
            search_kwargs["title"] = f"{element_name}"
            search_kwargs["control_type"] = control_type

            edit_element = dlg.child_window(**search_kwargs)
            exists = edit_element.exists(timeout=timeout)
            
            if exists:
                actual_value = edit_element.get_value()
                if expected_value in actual_value:                       
                    resp["status"] = "success"
                else:
                    resp["status"] = "failed"
                    resp["error"] = f"Element value mismatch. Expected: '{expected_value}', Actual: '{actual_value}'"
                    logger.error(resp["error"])
            else:
                resp["status"] = "failed"
                resp["error"] = f"Edit control '{element_name}' not found within {timeout} seconds."
                logger.error(f"{resp['error']}: {search_kwargs}")
            
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}

        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error in verify_element_value for '{expected_value}': {e}")
               
        return format_tool_response(resp)


    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def verify_elements_order(caller: str,
                            control_names: list[str],
                            control_type: str,
                            control_orders: list[int] = [],
                            step_raw: str = "",
                            step: str = "",
                            scenario: str = "", 
                            timeout: int = 5,
                            need_snapshot: int = 1
                            ) -> str:
        """
        Verifies that controls appear in the specified order (vertically or horizontally).
        
        Args:
            caller: Identifier of the calling module/function
            control_names: List of control names in the expected order
            control_type: Optional control type for more specific search (TreeItem, Button, etc.)
            ontrol_orders: Optional list of integers representing custom ordering indices for controls.
                        When provided, these indices will be used to verify the order instead of positional comparison.
                        The length should match control_names if specified.
            step_raw: Raw original step text
            step: Current test step description
            scenario: Test scenario name
            timeout: Maximum time in seconds to wait for the elements
            need_snapshot: Whether to include UI snapshot in response
            
        Returns:
            JSON response with verification result and status information
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            elements_real_order = []

            def get_tree_item_index(tree_item):
                parent = tree_item.element_info.parent
                siblings = parent.children()
                for i, elem in enumerate(siblings):
                    if elem == tree_item.element_info:
                        return i + 1
                raise ValueError(f"Element not found in siblings: {tree_item.window_text()}") 

            for name in control_names:
                search_kwargs = {"title_re": f".*{name}.*", "control_type": control_type}
                element = dlg.child_window(**search_kwargs)
                if element.exists(timeout=timeout):
                    elements_real_order.append(get_tree_item_index(element))

            expected_orders = control_orders if control_orders else sorted(elements_real_order)
            is_sorted = elements_real_order == expected_orders

            if is_sorted:
                resp["status"] = "success"
            else:
                resp["status"] = "failed"
                resp["error"] = f"Elements are not in the expected order. Expected: {expected_orders}, Actual: {elements_real_order}"
                logger.error(resp["error"])                            
           
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error in verify_elements_order: {e}")
            
        return format_tool_response(resp)
