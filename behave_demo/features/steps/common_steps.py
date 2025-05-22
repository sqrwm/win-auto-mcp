
from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json

# --- auto-generated step ---
@step('I navigate to "{param}"')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_navigate", arguments={'caller': 'behave-automation', 'url': param, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I click the star icon in the address bar')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="native_button_click", arguments={'caller': 'behave-automation', 'name': 'Add this page to favorites (Ctrl+D)', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I press ENTER key')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="send_keystrokes", arguments={'caller': 'behave-automation', 'name': '{ENTER}', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I click the "{param}" button in the favorites dialog')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_button_click", arguments={'caller': 'behave-automation', 'name': param, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I launch browser')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="browser_launch", arguments={'caller': 'behave-automation', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@given('navigate to "{param}"')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_navigate", arguments={'url': param, 'caller': 'behave', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 



# --- auto-generated step ---
@step('"{param}" should appear in my favorites list')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_button_click", arguments={'name': 'Favorites', 'caller': 'behave', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'element_name': param, 'caller': 'behave', 'control_type': 'TreeItem', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 


# --- auto-generated step ---
@given('I launch Edge')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="browser_launch", arguments={'caller': 'behave-automation', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@when('I hover over the Favorites icon in the address bar')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="mouse_hover", arguments={'caller': 'behave-automation', 'name': 'Add this page to favorites (Ctrl+D)', 'control_type': 'Button', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@then('I should see "{param}" tooltip')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': param, 'control_type': 'Button', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@when('I click on the "{param}" icon')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_button_click", arguments={'caller': 'behave-automation', 'name': param, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@then('I should see the "{param}" dialog')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': param, 'control_type': 'Window', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('the dialog should auto-fill the page name "Microsoft - Official Home Page"')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': 'Favorite name', 'control_type': 'Edit', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('"Favorites bar" should be selected as the default folder')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': 'Folder', 'control_type': 'ComboBox', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I should see "More", "Done" and "Remove" buttons')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': 'More', 'control_type': 'Button', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': 'Done', 'control_type': 'Button', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': 'Remove', 'control_type': 'Button', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('the dialog should auto-fill the page name "Microsoft - "')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_exists", arguments={'caller': 'behave-automation', 'element_name': 'Favorite name', 'control_type': 'Edit', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@when('I navigate to "{param}"')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_navigate", arguments={'caller': 'behave-automation', 'url': param, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('I press "Ctrl+D" on my keyboard')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="send_keystrokes", arguments={'caller': 'behave-automation', 'name': '^d', 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('the dialog should auto-fill the page name "Microsoft"')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="verify_element_value", arguments={'caller': 'behave-automation', 'element_name': 'Favorite name', 'element_value': '', 'control_type': 'Edit', 'expected_value': 'Microsoft', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 


# --- auto-generated step ---
@step('I click "{param}" button')
def step_impl(context, param):
    result = call_tool_sync(context, context.session.call_tool(name="native_button_click", arguments={'caller': 'behave-automation', 'name': param, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 

# --- auto-generated step ---
@step('"Custom" should be toggled on')
def step_impl(context):
    result = call_tool_sync(context, context.session.call_tool(name="verify_checkbox_state", arguments={'caller': 'behave-automation', 'checkbox_name': 'Sort by, Group, Custom', 'expected_state': 'checked', 'control_type': 'CheckBox', 'timeout': 5, 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 
