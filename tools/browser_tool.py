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

def register_browser_tools(mcp, browser_manager):
    """Register browser tools to MCP server."""   
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def browser_launch(caller: str, scenario: str = "", step: str = "", step_raw: str = "", 
                             need_snapshot: int = 1) -> str:
        """
        Launches the web browser.
        
        Args:
            caller: Identifier of the calling module/function
            scenario: Test scenario name (for logging)
            step: Current test step description (for logging)
            step_raw: Raw original step text
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        resp = init_tool_response()        
        try:
            browser_manager.browser_launch()
            close_all_alert(browser_manager.get_main_window())
            resp["status"] = "success"
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error launching browser: {e}")
      
        return format_tool_response(resp)    
    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def browser_close(caller: str, scenario: str = "", step_raw: str = "", step: str = "") -> str:
        """
        Closes the web browser instance that was previously launched.
        
        Args:
            caller: Identifier of the calling module/function
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with status information about the browser closure
        """
        resp = init_tool_response()
        try:
            browser_manager.browser_close()
            resp["data"] = {"step_raw": step_raw}
            resp["status"] = "success"
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error closing browser: {e}")
                    
        return format_tool_response(resp)    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def native_navigate(caller: str, url: str = "", scenario: str = "", step_raw: str = "",
                              step: str = "", need_snapshot: int = 1) -> str:
        """
        Navigates the browser to a specified URL.
        
        Args:
            caller: Identifier of the calling module/function
            url: The website URL to navigate to (e.g., "https://www.example.com")
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        
        resp = init_tool_response()
        try:
            main_window = browser_manager.get_main_window() 
            address_edit = main_window.child_window(
                auto_id="view_1022",
                control_type="Edit",
                found_index=0,
                depth=20
            )
            address_edit.wrapper_object().click_input()
            address_edit.wrapper_object().type_keys('^a{BACKSPACE}' + url + '{ENTER}')

            # main_window.set_focus()
            # main_window.type_keys("^l")  # Ctrl+L to focus the address bar
            # time.sleep(2)
            # main_window.type_keys(f'{url}{{ENTER}}')
            time.sleep(2)
            resp["status"] = "success"
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            
            resp["error"] = repr(e)
            logger.error(f"Error navigating to {url}: {e}")
                    
        return format_tool_response(resp)    
    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def native_button_click(caller: str, name: str = "", automation_id: str = "", scenario: str = "", step_raw: str = "", 
                                  step: str = "", need_snapshot: int = 1) -> str:
        """
        Clicks on a native button element in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            name: The exact title/name of the button to click
            automation_id: The exact automation_id of the button to click
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        resp = init_tool_response()
        logger.info(f"native_button_click start")
        try:
            dlg = browser_manager.get_main_window()
            btn_spec = dlg.child_window(
                title=name,
                control_type="Button",
                # depth=20
            )
            exist = btn_spec.exists(timeout=5)
            logger.info(f"native_button_click click_input: exists={exist}") 
            btn = btn_spec.wrapper_object()

            btn.click_input()
            logger.info(f"native_button_click click_input done") 
            time.sleep(1)
            
            resp["status"] = "success"
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            import traceback
            traceback.print_exc()
            logger.error(f"Error clicking button '{name}': {repr(e)}")

        logger.info(f"native_button_click done")    
        return format_tool_response(resp)    
    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def native_button_right_click(caller: str, name: str = "", automation_id: str = "", scenario: str = "", step_raw: str = "", 
                                        step: str = "", need_snapshot: int = 1) -> str:
        """
        Performs a right-click operation on a native button element in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            name: The exact title/name of the button to right-click
            automation_id: The exact automation_id of the button to click
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            btn = dlg.child_window(
                title=name,
                control_type="Button",
                depth=20
            )
            btn.right_click_input()
            time.sleep(2)
            resp["status"] = "success"
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error right-clicking button '{name}': {e}")
                    
        return format_tool_response(resp)    
    

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def send_keystrokes(caller: str, name: str, scenario: str = '', step_raw: str = '', step: str = '', need_snapshot: int = 1) -> str:
        """
        Sends keyboard keystrokes to the active window, supporting special keys and key combinations.
        
        Args:
            caller: Identifier of the calling module/function
            name: The keystroke sequence to send
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description

        Returns:
            JSON response with status and error information
        """        
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            dlg.type_keys(get_shortcut_key(name))
            time.sleep(2)
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
            resp["status"] = "success"
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error sending keystrokes '{name}': {e}")
            
        return format_tool_response(resp)
    

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def enter_text(caller: str, title: str, content:str, scenario: str = '', step_raw: str = '', 
                         step: str = '', need_snapshot: int = 1) -> str:
        """
        Enters text into an editable field in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            title: Title or label of the edit field to locate
            content: The text to enter into the edit field
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with status and error information
        """
        
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            edit_text = dlg.child_window(title_re=f'.*{title}', control_type="Edit")
            edit_text.wrapper_object().click_input()
            edit_text.wrapper_object().type_keys('^a{BACKSPACE}' + content)
            # edit_text.set_edit_text(content)
            time.sleep(1)
            resp["status"] = "success"
            
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error inputting text to edit field '{title}': {e}")
            
        return format_tool_response(resp)


    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def open_folder(caller: str, name: str, automation_id: str = "", control_type: str = 'TreeItem', scenario: str = "", step_raw: str = '', 
                            step: str = '', timeout: int = 5, need_snapshot: int = 1) -> str:
        """
        Open/expand a folder/TreeItem
        
        Args:
            name: Name or title of the folder
            automation_id: The exact automation_id of the folder
            control_type: The type of control to open (default: TreeItem)
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
        """
        resp = init_tool_response()
        try:
            search_kwargs = {'title': name, 'control_type': control_type}
            if automation_id:
                search_kwargs["auto_id"] = automation_id

            dlg = browser_manager.get_main_window()
            element = dlg.child_window(**search_kwargs)
            exists = element.exists(timeout=timeout)
            if exists:
                element = element.wrapper_object()
                if not element.is_expanded():
                    element.expand()
                    time.sleep(1)
                resp["status"] = "success"
            else:
                resp["status"] = "failed"
                resp["error"] = f"{control_type} control '{name}' not found within {timeout} seconds."
                resp["data"]['search_kwargs'] = search_kwargs
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"].update({"step_raw": step_raw, "snapshot": snapshot})
        except Exception as e:
            resp["error"] = repr(e)
            import traceback
            traceback.print_exc()
            logger.error(f"Error clicking button '{name}': {repr(e)}")

        return format_tool_response(resp)    
    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def open_combobox(caller: str, dropdown_name: str, scenario: str = "", step_raw: str = '', 
                            step: str = '', need_snapshot: int = 1) -> str:
        """
        Open a combobox or dropdown list
        
        Args:
            dropdown_name: Name or identifier of the dropdown/combobox
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            dropdown = dlg.child_window(
                title=f"{dropdown_name}",
                control_type="ComboBox",
                depth=20
            )
            dropdown.click_input()
            time.sleep(2)  # Wait for the dropdown list to expand
            resp["status"] = "success"
            
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:             
            resp["error"] = repr(e)
            logger.error(f"Error inputting text to edit field '{dropdown_name}': {e}")
            
        return format_tool_response(resp)
    
    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def select_item(caller: str, option: str, control_type: str = '', scenario: str = "", step_raw: str = '', step: str = '', need_snapshot: int = 1) -> str:
        """
        Select an option from a dropdown list or menuitem
        
        Args:
            option: Text of the option to select
            control_type: control type
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
           
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            if not control_type:
                control_type = "MenuItem"
            option_item = dlg.child_window(
                title=f"{option}",
                control_type=control_type,
                depth=20
            )
            option_item.click_input()
            time.sleep(2)  
            snapshot = extract_element_info(browser_manager.get_main_window())   
            resp["data"] = {'control_type': control_type, "snapshot": snapshot}
            resp["status"] = "success"
        except Exception as e1:
            logger.error(f"Error finding item: option={option}, control_type={control_type}. error={repr(e1)}")
            try:
                option_item = dlg.child_window(
                    title=option,
                    depth=20
                )
                option_item.click_input()
                time.sleep(2)  
                snapshot = extract_element_info(browser_manager.get_main_window())   
                resp["data"] = {'control_type': control_type, "snapshot": snapshot}
                resp["status"] = "success"
            except Exception as select_error:
                resp["error"] = repr(select_error)
                logger.error(f"Error select_error without control type: option={option}: error={repr(select_error)}")
                
        return format_tool_response(resp)
    
        
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
            scenario: Test scenario name (for logging)
            step_raw: Raw original step text
            step: Current test step description
        """
        exact_match = False  # Changed to False to support regex matching
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            
            # Determine the search scope
            search_parent = dlg
            
            # Prepare search criteria based on parameters
            search_kwargs = {}
            if exact_match:
                search_kwargs["title"] = element_name
            else:
                search_kwargs["title_re"] = f".*{element_name}.*"
            
            if control_type:
                search_kwargs["control_type"] = control_type
            
            # First try a quick search
            try:
                element = search_parent.child_window(**search_kwargs, depth=20)
                
                # Check if element exists with timeout
                exists = element.exists(timeout=timeout)
                
                if exists:
                    # Get additional details about the found element
                    resp["status"] = "success"
                else:
                    search_parent.print_control_identifiers()
                    resp["status"] = "failed"
                    resp["error"] = f"Element '{element_name}' not found within {timeout} seconds."
                    logger.error(f"{resp['error']}: {search_kwargs}")
            except Exception as search_error:
                resp["error"] = repr(search_error)
                logger.error(f"Error searching for element '{element_name}': {search_error}")

            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
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
            search_kwargs["title_re"] = f"{checkbox_name}"
            search_kwargs["control_type"] = control_type

            checkbox_element = dlg.child_window(**search_kwargs, depth=20)
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
                               timeout: int = 5,
                               scenario: str = "", 
                               step_raw: str = "",
                               step: str = "",
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
            timeout: Maximum time in seconds to wait for the element
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
            search_kwargs["title_re"] = f"{element_name}"
            search_kwargs["control_type"] = control_type

            edit_element = dlg.child_window(**search_kwargs, depth=20)
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
