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
from utils.gen_code import record_calls, MCP_SERVER_INTERNAL_CALL
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
            is_new_launch = browser_manager.browser_launch()
            if is_new_launch:
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
    async def browser_screenshot(caller: str, path: str = "screenshots/screenshot.png", scenario: str = "", step_raw: str = "", step: str = "") -> str:
        """
        Takes a screenshot of the current browser main window and saves it as a PNG file.

        Args:
            caller: Identifier of the calling module/function
            path: File path to save the screenshot (default: screenshots/screenshot.png)
            scenario: Test scenario name (for logging)
            step_raw: Raw original step text
            step: Current test step description

        Returns:
            JSON response with status and error information
        """
        resp = init_tool_response()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            main_window = browser_manager.get_main_window()
            if main_window is None:
                raise RuntimeError("Main window not found, cannot take screenshot.")
            img = main_window.capture_as_image()
            if img is None:
                raise RuntimeError("capture_as_image() returned None. Is Pillow installed?")
            img.save(path)
            resp["data"] = {"path": path, "step_raw": step_raw}

            resp["status"] = "success"
            print(f"Screenshot saved to {path}")
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error taking browser screenshot: {e}")
            print(f"Error taking screenshot: {e}")


    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def browser_launch_with_user_data(caller: str, custom_user_data_dir: str, scenario: str = "", step: str = "", step_raw: str = "", 
                             need_snapshot: int = 1) -> str:
        """
        Launches the web browser with user specified data.
        
        Args:
            caller: Identifier of the calling module/function
            user_data_path: User data directory for the browser
            scenario: Test scenario name (for logging)
            step: Current test step description (for logging)
            step_raw: Raw original step text
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        resp = init_tool_response()        
        try:
            browser_manager.browser_launch(custom_user_data_dir=custom_user_data_dir)
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
                # depth=20
            )
            address_edit.wrapper_object().click_input()
            address_edit.wrapper_object().type_keys('^a{BACKSPACE}' + url + '{ENTER}')

            # main_window.set_focus()
            # main_window.type_keys("^l")  # Ctrl+L to focus the address bar
            # time.sleep(2)
            # main_window.type_keys(f'{url}{{ENTER}}')
            time.sleep(2)
            close_translate_pane(main_window)
            time.sleep(1)
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
    async def native_button_click(caller: str, name: str, control_type: str, automation_id: str = "", scenario: str = "", step_raw: str = "", 
                                  step: str = "", timeout: int = 5, need_snapshot: int = 1) -> str:
        """
        Clicks on a native button element in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            name: The exact title/name of the button to click
            control_type: The type of control to open
            automation_id: The exact automation_id of the button to click
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        if control_type == "TreeItem":
            return await open_folder(caller=MCP_SERVER_INTERNAL_CALL, name=name, control_type=control_type, automation_id=automation_id, 
                                     scenario=scenario, step_raw=step_raw, step=step, timeout=timeout, 
                                     need_snapshot=need_snapshot)
        
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            search_kwargs = {'title': name, 'control_type': control_type}
            if automation_id:
                search_kwargs["auto_id"] = automation_id

            element = dlg.child_window(**search_kwargs)
            exists = element.exists(timeout=timeout)
            if exists:
                btn = element.wrapper_object()
                btn.click_input()
                time.sleep(1)
                resp["status"] = "success"
            else:
                resp["status"] = "failed"
                resp["error"] = f"{control_type} control '{name}' not found within 5 seconds."
                resp["data"]['search_kwargs'] = {'title': name, 'control_type': control_type}
                logger.error(f"{resp['error']}: {resp['data']['search_kwargs']}")
                
            if need_snapshot == 1:
                time.sleep(1)
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"].update({"step_raw": step_raw, "snapshot": snapshot})
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
    async def native_right_click(caller: str, name: str, control_type: str, automation_id: str = "", scenario: str = "", step_raw: str = "", 
                                  step: str = "", timeout: int = 5, need_snapshot: int = 1) -> str:
        """
        Right clicks on a native control element in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            name: The exact title/name of the button to click
            control_type: The type of control to open
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
            search_kwargs = {'title': name, 'control_type': control_type}
            if automation_id:
                search_kwargs["auto_id"] = automation_id

            element = dlg.child_window(**search_kwargs)
            exists = element.exists(timeout=timeout)
            if exists:
                btn = element.wrapper_object()
                btn.right_click_input()
                time.sleep(1)
                resp["status"] = "success"
            else:
                resp["status"] = "failed"
                resp["error"] = f"{control_type} control '{name}' not found within 5 seconds."
                resp["data"]['search_kwargs'] = {'title': name, 'control_type': control_type}
                logger.error(f"{resp['error']}: {resp['data']['search_kwargs']}")
                
            if need_snapshot == 1:
                time.sleep(1)
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"].update({"step_raw": step_raw, "snapshot": snapshot})
        except Exception as e:
            resp["error"] = repr(e)
            import traceback
            traceback.print_exc()
            logger.error(f"Error right clicking control '{name}': {repr(e)}")

        logger.info(f"native_button_click done")    
        return format_tool_response(resp)    

    
    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def native_double_right_click(caller: str, name: str, control_type: str, automation_id: str = "", scenario: str = "", step_raw: str = "", 
                                        step: str = "", timeout: int = 5, need_snapshot: int = 1) -> str:
        """
        Performs a double-click operation on a native control element in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            name: The exact title/name of the control to right-click
            control_type: The type of control to open
            automation_id: The exact automation_id of the control to click
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with browser snapshot data and status information
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            search_kwargs = {'title': name, 'control_type': control_type}
            if automation_id:
                search_kwargs["auto_id"] = automation_id

            element = dlg.child_window(**search_kwargs)
            exists = element.exists(timeout=timeout)
            if exists:
                btn = element.wrapper_object()
                btn.double_click_input()
                time.sleep(1)
                resp["status"] = "success"
            else:
                resp["status"] = "failed"
                resp["error"] = f"{control_type} control '{name}' not found within 5 seconds."
                resp["data"]['search_kwargs'] = {'title': name, 'control_type': control_type}
                logger.error(f"{resp['error']}: {resp['data']['search_kwargs']}")
                
            if need_snapshot == 1:
                time.sleep(1)
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"].update({"step_raw": step_raw, "snapshot": snapshot})
        except Exception as e:
            resp["error"] = repr(e)
            import traceback
            traceback.print_exc()
            logger.error(f"Error double clicking control '{name}': {repr(e)}")
                    
        return format_tool_response(resp)    
    

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def send_keystrokes(caller: str, keys_sequence_raw: str, key_sequence_formatted, str, step_raw: str, step: str, scenario: str = '', need_snapshot: int = 1) -> str:
        """
        Sends keystrokes to the active browser window using pywinauto, with support for key combinations.

        Args:
            caller (str): Identifier of the calling module or context.
            key_sequence_raw (str): The original human-readable keystroke sequence (e.g., 'Ctrl+Shift+.').
            key_sequence_formatted (str): The sequence converted to pywinauto's type_keys format 
                                        (e.g., '^+.' for Ctrl+Shift+.).
            step_raw (str): The raw BDD step text from the feature file.
            step (str): The current test step description.
            scenario (str, optional): Scenario name for logging/tracking. Defaults to ''.
        Returns:
            str: JSON-formatted result with status, optional snapshot data, and any error message.
        """
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            # dlg.type_keys(get_shortcut_key(keys_sequence_raw))
            dlg.type_keys(key_sequence_formatted)
            time.sleep(2)
            if need_snapshot == 1:
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
            resp["status"] = "success"
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error sending keystrokes raw:'{keys_sequence_raw}' '{key_sequence_formatted}': {repr(e)}")
            
        return format_tool_response(resp)
    

    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def enter_text(caller: str, title: str, content:str, control_type: str, automation_id: str, scenario: str = '', step_raw: str = '', 
                         step: str = '', need_snapshot: int = 1) -> str:
        """
        Enters text into an editable field in the browser UI.
        
        Args:
            caller: Identifier of the calling module/function
            title: The exact title/name of the edit field 
            content: The text to enter into the edit field
            control_type: The type of control to open
            automation_id: The exact automation_id of the control to click
            scenario: Test scenario name
            step_raw: Raw original step text
            step: Current test step description
            
        Returns:
            JSON response with status and error information
        """
        
        resp = init_tool_response()
        try:
            dlg = browser_manager.get_main_window()
            search_kwargs = {'title': title, 'control_type': control_type}
            if automation_id:
                search_kwargs["auto_id"] = automation_id

            element = dlg.child_window(**search_kwargs)
            if element.exists() is False:
                if automation_id:
                    search_kwargs = {'auto_id': automation_id, 'control_type': control_type}
                    element = dlg.child_window(**search_kwargs)
            # edit_text = dlg.child_window(title=f'{title}', control_type=control_type)
            element.wrapper_object().click_input()
            element.wrapper_object().type_keys('^a{BACKSPACE}', with_spaces=True)
            element.wrapper_object().type_keys(content, with_spaces=True)
            # element.set_edit_text(content)
            time.sleep(1)
            resp["status"] = "success"
            
            if need_snapshot == 1:
                time.sleep(1)
                snapshot = extract_element_info(browser_manager.get_main_window()) 
                resp["data"] = {"step_raw": step_raw, "snapshot": snapshot}
        except Exception as e:
            resp["error"] = repr(e)
            logger.error(f"Error inputting text to edit field '{title}': {e}")
            
        return format_tool_response(resp)


    @mcp.tool()
    @log_tool_call
    @record_calls(browser_manager)
    async def open_folder(caller: str, name: str, control_type: str, automation_id: str = "", scenario: str = "", step_raw: str = '', 
                            step: str = '', timeout: int = 5, need_snapshot: int = 1) -> str:
        """
        Open/expand a folder/TreeItem
        
        Args:
            name: Name or title of the folder
            control_type: The type of control to open
            automation_id: The exact automation_id of the folder
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
                # for leaf node, click it
                if control_type == 'TreeItem' and element.get_expand_state() != 3 and not element.is_expanded():
                    element.expand()
                else:
                    element.click_input()
                    
                time.sleep(2)
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
                # depth=20
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
                # depth=20
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
                    # depth=20
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
    
