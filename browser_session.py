# tools/browser_manager.py

import os
import psutil
import time
import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from datetime import datetime
from pywinauto import Application, Desktop
from pywinauto.controls.uiawrapper import UIAWrapper


logger = logging.getLogger(__name__)

BROWSER_CONFIGS = {
    "edge": {
        "exe": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "window_title_re": ".*Microsoft.*Edge"
    },
    "edge-beta": {
        "exe": r"C:\Program Files (x86)\Microsoft\Edge Beta\Application\msedge.exe",
        "window_title_re": ".*Microsoft.*Edge Beta"
    },
    "edge-canary": {
        "exe": os.path.join(os.environ['LOCALAPPDATA'], r"Microsoft\Edge SxS\Application\msedge.exe"),
        "window_title_re": ".*Microsoft.*Edge Canary"
    },
    "chrome": {
        "exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "window_title_re": ".*Chrome.*"
    }
}

LAUNCH_ARGS = ['--no-first-run',
               '--remote-debugging-port=9222',
               '--new-window about:blank',
               '--disable-features=msImplicitSignin'
            #    r'--user-data-dir="C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\test_data\test_000"',
            #    '--start-maximized',
               ]
            


class BrowserSessionManager:
    def __init__(self, browser: str):
        if browser not in BROWSER_CONFIGS:
            raise ValueError(f"Unsupported browser: {browser}")
        
        self._app = None  # Application instance
        self.browser = browser
        self.config = BROWSER_CONFIGS[browser]

        self.gen_code_id = None
        self.gen_code_cache = []
        self.proposed_changes = None  # Store proposed code changes
        self.header_code = ''
        self.steps_dir = None  # Directory for step files
        self.step_file_target = None  # Target step file for code generation

        self.user_data_dir = None  # Directory for user data, if needed
   

    def start_and_get_new_browser_window(exe_path="msedge.exe", title_re=".*Edge.*", timeout=15):
        backend = "uia"
        desktop = Desktop(backend=backend)
        before_handles = {w.handle for w in desktop.windows() if "Edge" in (w.window_text() or "")}

        Application(backend=backend).start(exe_path)

        start_time = time.time()
        while time.time() - start_time < timeout:
            after_windows = desktop.windows()
            new_windows = [w for w in after_windows if w.handle not in before_handles and w.window_text() and "Edge" in w.window_text()]
            if new_windows:
                new_win: UIAWrapper = new_windows[0]
                new_win.wait("exists enabled visible", timeout=5)
                return new_win
            time.sleep(0.5)
        
        raise TimeoutError("No new browser window appeared after starting.")

    
    def copy_user_data_to_temp(self, custom_user_data_dir):
        user_data_dir = Path(custom_user_data_dir).resolve()

        if not user_data_dir.exists():
            raise FileNotFoundError(f"custom_user_data_dir does not exist: {user_data_dir}")

        temp_root = Path(tempfile.gettempdir()).resolve()

        dest_dir_name = "win_auto_mcp_user_data_" + user_data_dir.name + "_" + str(uuid.uuid1())
        dest_dir = temp_root / dest_dir_name
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        logger.info(f"[BrowserManager] Copying user data from \n{user_data_dir} \nto \n{dest_dir}")
        shutil.copytree(user_data_dir, dest_dir)
        return dest_dir

   
    def _new_launch(self, url: str, args: list[str], custom_user_data_dir: str = None):
        if custom_user_data_dir:
            self.user_data_dir = self.copy_user_data_to_temp(Path(custom_user_data_dir).resolve())
            
        exe_path = self.config["exe"]
        cmd = f'{exe_path}'
        if args:
            cmd += " " + " ".join(args)
        if url:
            cmd += f" {url}"
        if self.user_data_dir:
            cmd += f' --user-data-dir="{self.user_data_dir}"'

        logger.info(f"[BrowserManager] Launching new {self.browser}: {cmd}")
        Application(backend="uia").start(cmd)
        for i in range(5):
            time.sleep(1)
            try:
                self._app = Application(backend="uia").connect(title_re=self.config["window_title_re"])
                main_window = self._app.window(title_re=self.config["window_title_re"], control_type="Window")
                main_window.wait("exists", timeout=1)
                logger.info(f"[BrowserManager] Launching new {self.browser}: exists done")
                main_window.wait("visible", timeout=1)
                logger.info(f"[BrowserManager] Launching new {self.browser}: visible done")
                main_window.wait("enabled", timeout=1)
                logger.info(f"[BrowserManager] Launching new {self.browser}: done")
                break
            except Exception as e:
                logger.error(f"[BrowserManager] Launching new {self.browser} error: {repr(e)}")
                pass
            

    def browser_launch(self, url: str = "", args: list[str] = LAUNCH_ARGS, kill_existing: int = 0, custom_user_data_dir: str = None):
        if kill_existing == 1 or custom_user_data_dir:
            self.clear_gen_code_cache()
            self.browser_close()
            self.kill_browser_process_by_path()
        is_new_launch = False
        try:
            self._app = Application(backend="uia").connect(title_re=self.config["window_title_re"])
            if self._app:
                self._app = Application(backend="uia").connect(title_re=self.config["window_title_re"])
            else:
                self._new_launch(url, args, custom_user_data_dir)
                is_new_launch = True
        except Exception as e:
            self._new_launch(url, args, custom_user_data_dir)
            is_new_launch = True

        return is_new_launch
            
        
    def browser_close(self):
        if self._app:
            self._app.kill()
            self._app = None
        else:
            logger.warning("No browser session to close.")

    def kill_browser_process_by_path(self):
        exe_path = os.path.normcase(os.path.normpath(self.config["exe"]))
        killed = False

        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                proc_exe = proc.info["exe"]
                if proc_exe and os.path.normcase(os.path.normpath(proc_exe)) == exe_path:
                    print(f"Killing process: {proc_exe}")
                    proc.kill()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed:
            time.sleep(2) 


    def get_main_window(self):
        time_s = time.time()
        no_app = False
        if not self._app:
            no_app = True
            self.browser_launch()        
        
        main_window = self._app.window(title_re=self.config["window_title_re"], control_type="Window")
        # time.sleep(1)
        logger.info(f"get_main_window cost: NO_APP={no_app}, cost={int(time.time() - time_s)}, main_window={main_window}")
        logger.info(f"get_main_window cost: NO_APP={no_app}, cost={int(time.time() - time_s)}")
        return main_window
    
    def push_data_to_gen_code(self, caller, tool_name, step, scenario, param=None):
        if self.gen_code_id:
            data = {
                "gen_code_id": self.gen_code_id,
                "tool_name": tool_name,
                "step": step,
                "scenario": scenario,
                "param": param,
                "caller": caller,
            }
            self.gen_code_cache.append(data)
        else:
            pass

    def clear_gen_code_cache(self):
        self.gen_code_cache.clear()
        self.gen_code_id = None
        self.proposed_changes = None
        self.header_code = ''
        self.steps_dir = None
        self.step_file_target = None
