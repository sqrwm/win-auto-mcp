import time
import logging
from pywinauto import Application


logger = logging.getLogger(__name__)


def close_translate_pane(main_window):
    """
    Close the translation pane in the application.
    """
    try:
        # Find the translation pane window
        
        translate_pane = main_window.child_window(
            title_re="Translate page from.*",
            control_type="Pane",
            depth=20
        )
        if not translate_pane.exists(timeout=2):
            return

        close_btn = translate_pane.child_window(
            title="Close",
            control_type="Button",
            depth=20
        )
        close_btn.click_input()
        logger.info(f"Close the translation pane")
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error closing translation pane: {repr(e)}")



def close_restore_pane(main_window):
    """
    Close the restore pane in the application.
    """
    try:        
        pane = main_window.child_window(
            title="Restore pages",
            control_type="Pane",
            depth=20
        )
        if not pane.exists(timeout=2):
            return

        close_btn = pane.child_window(
            title="Close",
            control_type="Button",
            depth=20
        )
        close_btn.click_input()
        logger.info(f"Close the restore pane")
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error closing restore pane: {repr(e)}")



def click_got_it(main_window):
    """
    Click got it button in the application.
    """
    try:        
        btn = main_window.child_window(
            title="Got it",
            control_type="Button",
        )
        if not btn.exists(timeout=2):
            return

        btn.click_input()
        logger.info(f"Click got it button")
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error clicking got it button: {repr(e)}")


def close_all_alert(main_window): 
    # click_got_it(main_window) 
    close_restore_pane(main_window)
    close_translate_pane(main_window)