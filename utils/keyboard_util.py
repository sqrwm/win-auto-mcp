import re


BROWSER_SHORTCUT_KEYS = {
    # Tab management
    "CTRL+T": "^t",  # New Tab
    "CTRL+W": "^w",  # Close Tab
    "CTRL+SHIFT+T": "^+t",  # Reopen Closed Tab
    "CTRL+TAB": "^{TAB}",  # Switch to Next Tab
    "CTRL+SHIFT+TAB": "^+{TAB}",  # Switch to Previous Tab

    # Page actions
    "F5": "{F5}",  # Refresh Page
    "CTRL+F5": "^{F5}",  # Force Refresh (Bypass Cache)
    "ESC": "{ESC}",  # Stop Loading Page
    "CTRL+F": "^f",  # Find on Page
    "CTRL+P": "^p",  # Print Page

    # Address bar operations
    "CTRL+L": "^l",  # Focus Address Bar
    "CTRL+D": "^d",  # Bookmark Current Page
    "CTRL+SHIFT+D": "^+d",  # Bookmark All Tabs

    # History / Downloads
    "CTRL+H": "^h",  # Open Browsing History
    "CTRL+J": "^j",  # Open Downloads
    "CTRL+SHIFT+O": "^+o",  # Open Bookmarks Manager

    # Window management
    "CTRL+N": "^n",  # New Window
    "CTRL+SHIFT+N": "^+n",  # New Incognito Window
    "CTRL+SHIFT+W": "^+w",  # Close Current Window

    # Zoom controls
    "CTRL++": "^{ADD}",  # Zoom In
    "CTRL+-": "^{SUBTRACT}",  # Zoom Out
    "CTRL+0": "^0",  # Reset Zoom

    # Developer Tools
    "CTRL+SHIFT+I": "^+i",  # Open Developer Tools

    # Common keys
    "ARROWLEFT": "{LEFT}",  # Left Arrow
    "ARROWRIGHT": "{RIGHT}",  # Right Arrow
    "ARROWUP": "{UP}",  # Up Arrow
    "ARROWDOWN": "{DOWN}",  # Down Arrow
    "ENTER": "{ENTER}",  # Enter Key
    "ESCAPE": "{ESC}",  # Escape Key
    "BACKSPACE": "{BACKSPACE}",  # Backspace Key
    "DELETE": "{DELETE}",  # Delete Key
    "TAB": "{TAB}",  # Tab Key
    "SPACE": "{SPACE}",  # Spacebar Key

    # Search and address bar
    "CTRL+K": "^k",  # Focus Search Box
    "CTRL+E": "^e",  # Focus Address Bar (Alternate)

    # Scrolling
    "PAGEUP": "{PGUP}",  # Page Up
    "PAGEDOWN": "{PGDN}",  # Page Down
}


def normalize_key(key: str) -> str:
    key = re.sub(r'\s*\+\s*', '+', key.strip())  
    return key.upper()

shortcut_keys = {
    normalize_key(k): v
    for k, v in BROWSER_SHORTCUT_KEYS.items()
}

def get_shortcut_key(key: str) -> str:
    normalized = normalize_key(key)
    final_key = shortcut_keys.get(normalized, key)
    print(f"Normalized key: {normalized}")
    print(f"Final key: {final_key}")
    return final_key


if __name__ == "__main__":
    from pywinauto.keyboard import send_keys
    from pywinauto import Application
    app = Application(backend="uia").connect(title_re=".*Edge Beta.*",)
    dlg = app.window(
        title_re=".*Edge Beta.*",
        control_type="Window"
    )
    user_input = " Ctrl + Shift +   T "
    dlg.type_keys(get_shortcut_key(user_input))
   


