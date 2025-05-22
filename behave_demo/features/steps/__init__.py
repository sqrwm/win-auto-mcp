# features/steps/__init__.py
import os
import pathlib
import importlib.util
import traceback

def auto_import_steps():

    steps_dir = pathlib.Path(__file__).parent
    base_dir = steps_dir.parent 

    for py_file in steps_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            rel_path = py_file.relative_to(base_dir)
            module_name = ".".join(rel_path.with_suffix("").parts)

            print(f"[auto-import] Loading module: {module_name}")
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except Exception as e:
            print(f"[auto-import] Failed to import {py_file}: {e}")
            traceback.print_exc()

auto_import_steps()
