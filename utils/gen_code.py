import copy
import json
import re
import os
import sys
import inspect
import logging
import functools
import pprint
import textwrap
from pathlib import Path


logger = logging.getLogger(__name__)


PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURE_DIR = os.path.join(PARENT_DIR, 'behave_demo/features')
STEPS_DIR_DEFAULT = os.path.join(PARENT_DIR, 'behave_demo/features/steps')
TARGET_STEP_FILE_DEFAULT = os.path.join(STEPS_DIR_DEFAULT, "common_steps.py")

MCP_SERVER_INTERNAL_CALL = "mcp-server-internal-transfer-call"

HEADER_AUTO_GEN = """
from behave import *
import logging
from features.environment import call_tool_sync, get_tool_json
"""


TOOL_PARAMS_REPLACE_MAP = {
    "native_button_click": {"name": "param"},
    "keyboard_input": {"name": "param"},
    "native_navigate": {"url": "param"},
    "verify_element_exists": {"element_name": "param"},
}


def need_parameterize(step_info: dict, parameterized_size: int) -> bool:
    tool_name = step_info.get("tool_name")
    print(f"\nneed_parameterize: {tool_name}, parameterized_size: {parameterized_size}\n")
    if step_info.get("is_multi_call", False):
        return False
    if tool_name in TOOL_PARAMS_REPLACE_MAP and parameterized_size == len(TOOL_PARAMS_REPLACE_MAP.get(tool_name)):
        return True
    return False

def normalize_step_text(step_text_raw: str, step_info: dict) -> tuple:
    parameterized_pattern = r'\"(.+?)\"'
    matches = list(re.finditer(parameterized_pattern, step_text_raw))
    match_size = len(matches)
    normalized_text = step_text_raw
    params = {}

    if not need_parameterize(step_info, match_size):
        return normalized_text, params
    
    idx = 0
    for match in matches:
        k = f"param{idx + 1}" if match_size > 1 else "param"
        params[k] = match.group(1)
        idx += 1

    if params:
        def replace_param(match, index=[0]):
            param_name = f"{{param{index[0] + 1}}}" if len(params) > 1 else "{param}"
            index[0] += 1
            return f'"{param_name}"'
        normalized_text = re.sub(parameterized_pattern, replace_param, step_text_raw)
    return normalized_text, params


def generate_args_data_multi_param(step_info: dict):
    tool_name = step_info.get("tool_name")
    tool_params = step_info.get("tool_params", {})
    parameterized_args = step_info.get("parameterized_args", {})
    real_parameterized = False

    if not need_parameterize(step_info, len(parameterized_args)):
        args_str = pprint.pformat(tool_params, indent=0)
        args_lines = args_str.splitlines()
        args_str_final = args_lines[0]
        if len(args_lines) > 1:
            args_str_final += "\n"
            args_str_final += textwrap.indent("\n".join(args_lines[1:]), ' ' * 12)
        return args_str_final, real_parameterized
    
    map_info = TOOL_PARAMS_REPLACE_MAP.get(tool_name, {})
    tool_params_copy = copy.deepcopy(tool_params)
    for k, parameterized_k in map_info.items():
        if k in tool_params_copy and parameterized_k in parameterized_args and tool_params_copy[k] == parameterized_args.get(parameterized_k):
            tool_params_copy[k] = parameterized_k
            real_parameterized = True

    params_str = '{\n' + ',\n'.join(
            f"{' ' * 12}'{k}': {map_info.get(k) if k in map_info and map_info.get(k) in parameterized_args and v in parameterized_args else repr(v)}"
            for k, v in tool_params_copy.items()
        ) + f"\n{' ' * 8}}}"
    
    print(f"generate_args_data_multi_param: {tool_name}, tool_params_copy: {tool_params_copy}")
    print(f"generate_args_data_multi_param: {tool_name}, params_str: {params_str}\n")
    return params_str, real_parameterized


def generate_step_definition(step_info) -> str:
    parameterized_args = step_info.get('parameterized_args', {})
    has_params = len(parameterized_args) > 0
    
    args_str, real_parameterized = generate_args_data_multi_param(step_info)
    step_type = step_info.get("step_type").lower()
    step_info['step_text'] = step_info.get("step_text_parameterized") if real_parameterized else step_info.get("step_text_raw")
    
    code_text = ""
    if step_info.get("call_idx", 0) <= 1:
        if not has_params or not real_parameterized:
            param_def = ""
        else:
            param_def = ", " + ", ".join(parameterized_args.keys())
        code_text = f"""
# --- auto-generated step ---
@{step_type}('{step_info['step_text']}')
def step_impl(context{param_def}):"""
        
    code_text += f"""
    result = call_tool_sync(context, context.session.call_tool(
        name="{step_info.get('tool_name')}", 
        arguments={args_str}
    ))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{{result_json.get('status')}}', error: '{{result_json.get('error')}}'" """
    return code_text


def extract_steps_from_cache(gen_code_id, gen_code_cache):
    dedupe_set = set()
    steps = []
    last_step = None
    call_idx = 1
    for item in gen_code_cache:
        if item.get("gen_code_id") != gen_code_id:
            continue
        
        step_lower = item.get("step").lower()
        parts = ['step', item.get("step")]
        if step_lower.startswith("given ") or step_lower.startswith("when ") or step_lower.startswith("then "):
            parts = item.get("step").split(maxsplit=1)
        elif step_lower.startswith("and ") or step_lower.startswith("but "):
            parts = item.get("step").split(maxsplit=1)
            parts[0] = 'step'
            
        is_multi_call = False
        if last_step and last_step.get("step").lower() == item.get("step").lower():
            call_idx += 1
            is_multi_call = True
        else:
            call_idx = 1

        keyword, text_raw = parts
        normalized_text, parameterized_args = normalize_step_text(text_raw, item)

        if (keyword.lower(), text_raw.lower(), call_idx) not in dedupe_set:
            dedupe_set.add((keyword.lower(), text_raw.lower(), call_idx))
            item["step_type"] = keyword.lower()
            item["step_text_parameterized"] = normalized_text
            item["step_text_raw"] = text_raw
            item["parameterized_args"] = parameterized_args 
            # item["has_parameterized_args"] = len(parameterized_args ) > 0
            item["is_multi_call"] = is_multi_call
            if is_multi_call: 
                item["call_idx"] = call_idx + 1
                if call_idx == 2:
                    last_step["is_multi_call"] = True
                    last_step["call_idx"] = 1
                    
            steps.append(item)
        last_step = item
    print(f"\nExtracted steps: {steps}\n")
    return steps


def gen_code_preview(browser_manager) -> dict:
    new_steps_code = []
    existing_code = ""
    
    step_file = browser_manager.steps_dir
    existing_code = read_step_files(Path(step_file))
    target_existing_code = read_step_files(Path(browser_manager.step_file_target))

    if not target_existing_code:
            browser_manager.header_code = HEADER_AUTO_GEN

    steps = extract_steps_from_cache(browser_manager.gen_code_id, browser_manager.gen_code_cache)
    logger.info(f"Processing {len(steps)} extracted steps")

    existing_patterns = re.findall(r'@(given|when|then|step)\(["\'](.+?)["\']\)', existing_code)
    existing_patterns = [(decorator.lower(), pattern.lower()) for decorator, pattern in existing_patterns]

    print(f"\nexisting_patterns: {existing_patterns}\n")
    new_add_patterns = ()
    for item in steps:
        step_code = generate_step_definition(item)
        step_text = item.get('step_text', '')
        step_type = item.get('step_type', '')
        print(f"\nexisting_patterns check: {(step_type, step_text.lower())}\n")
        if (step_type, step_text.lower()) in existing_patterns:
            continue
        if (step_type, step_text.lower()) in new_add_patterns and item.get("call_idx", 0) <= 1:
            continue
            # step_code = generate_step_definition(item)
        if step_code:
            new_steps_code.append(step_code)
            new_add_patterns += ((step_type, step_text.lower()),)

    browser_manager.proposed_changes = new_steps_code
    browser_manager.new_steps_count = len(new_steps_code)
    
    print(f"New steps code: {new_steps_code}")
    if not new_steps_code:
        return {'diff_preview': "No new code changes to apply - all steps already exist", 'new_steps_code': []}

    diff_preview = "+++ New Code to Add +++\n"
    diff_preview += "".join(new_steps_code)
    
    return {'diff_preview': diff_preview, 'new_steps_code': new_steps_code}

def gen_code_preview_test(gen_code_id, gen_code_cache) -> str:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from browser_session import BrowserSessionManager
    browser_manager = BrowserSessionManager('edge-beta')
    browser_manager.gen_code_id = gen_code_id
    browser_manager.gen_code_cache = gen_code_cache
    browser_manager.steps_dir = STEPS_DIR_DEFAULT
    browser_manager.step_file_target = TARGET_STEP_FILE_DEFAULT
    return gen_code_preview(browser_manager)


def ensure_step_path_exists(step_file: str) -> bool:
    step_path = Path(step_file)
    try:
        parent_dir = step_path.parent
        if not parent_dir.exists():
            logger.info(f"Creating directory structure: {parent_dir}")
            parent_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory structure for {step_path}: {str(e)}")
        return False


def read_step_files(step_path, max_depth=5, current_depth=0):
    existing_code = ""
    
    if current_depth > max_depth:
        logger.warning(f"Maximum recursion depth reached at {step_path}")
        return existing_code
    
    if not step_path.exists():
        logger.warning(f"Step path does not exist: {step_path}")
        return existing_code
        
    if step_path.is_dir():
        for py_file in step_path.glob("*.py"):
            try:
                logger.info(f"Reading step file: {py_file}")
                with open(py_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    if file_content:
                        existing_code += file_content + "\n\n"
            except Exception as e:
                logger.error(f"Error reading file {py_file}: {str(e)}")
        
        for subdir in step_path.iterdir():
            if subdir.is_dir():
                subdir_content = read_step_files(subdir, max_depth, current_depth + 1)
                if subdir_content:
                    existing_code += subdir_content + "\n\n"
    
    elif step_path.is_file() and step_path.suffix == '.py':
        try:
            with open(step_path, 'r', encoding='utf-8') as f:
                existing_code = f.read()
        except Exception as e:
            logger.error(f"Error reading file {step_path}: {str(e)}")
            
    return existing_code


def log_params(func, *args, **kwargs):
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    tool_params = dict()
   
    args_no_name = []
    for i, arg in enumerate(args):
        if i < len(param_names):
            tool_params[param_names[i]] = arg
        else:
            args_no_name.append(repr(arg))
    # tool_params["args_no_name"] = ", ".join(args_no_name) if args_no_name else None
 
    for k, v in kwargs.items():
        tool_params[k] = v
    
    tool_params['need_snapshot'] = 0
    return tool_params


def parse_steps_dir_from_step_path(step_file: str):
    step_path = Path(step_file).resolve()

    current = step_path
    while current.name != "steps":
        current = current.parent
        if current == current.parent:
            current = None
            break

    steps_dir = current
    if not current:
        if step_file.endswith('.py'):
            steps_dir = step_path.parent
        else:
            steps_dir = step_path
      
    os.makedirs(steps_dir, exist_ok=True)
    return str(steps_dir)


def gen_step_file_from_feature_path(feature_file: str):
    is_feature_file = True if feature_file.endswith('.feature') else False
    feature_path = Path(feature_file).resolve()

    current = feature_path
    while current.name != "features":
        current = current.parent
        if current == current.parent:
            current = None
            break
    
   
    features_dir = current
    if not current:
        if is_feature_file:
            features_dir = feature_path.parent
        else:
            features_dir = feature_path
    steps_dir = features_dir / "steps"

    rel_path = feature_path.relative_to(features_dir)
    step_file_dir = steps_dir / rel_path.parent
    step_file_name = "common_step.py"
    if is_feature_file:
        step_file_name = rel_path.stem + ".py"
    elif rel_path.stem:
        step_file_name = rel_path.stem + "\common_step.py"
    step_file_path = step_file_dir / step_file_name
    os.makedirs(step_file_dir, exist_ok=True)
  
    return str(steps_dir), str(step_file_path)

    # os.makedirs(step_file_dir, exist_ok=True)

    # if not step_file_path.exists():
    #     with open(step_file_path, "w", encoding="utf-8") as f:
    #         f.write(f"# Auto-generated step file for {rel_path.name}\n")
    #     print(f"Created: {step_file_path}")
    # else:
    #     print(f"Already exists: {step_file_path}")
 
 
def record_calls(browser_manager):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                json_result = json.loads(result)
                if json_result.get("status") != "success":
                    # logger.warning(f"result failed, no record call: tool_name={func.__name__}, result={json_result}")
                    return result
                call_info = {}
                tool_params = log_params(func, *args, **kwargs)
                if tool_params.get('caller') == MCP_SERVER_INTERNAL_CALL:
                    return result
                if browser_manager.gen_code_id and (tool_params.get('step_raw', '') or tool_params.get('step', '')):
                    tool_params['caller'] = 'behave-automation'
                    call_info['scenario'] = tool_params.pop('scenario', '')
                    # call_info['step'] = tool_params.pop('step', '')
                    step_raw = tool_params.pop('step_raw', '').strip()
                    step_ai = tool_params.pop('step', '').strip()
                    call_info['step'] = step_raw if step_raw else step_ai
                    call_info['gen_code_id'] = browser_manager.gen_code_id
                    call_info['tool_name'] = func.__name__
                    call_info['tool_params'] = tool_params
                    browser_manager.gen_code_cache.append(call_info)
                    logger.info(f"record_calls: call_info={call_info}")
 
                return result
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error record_calls: {repr(e)}")
                raise e
               
        return wrapper
    return decorator


if __name__ == "__main__":
    steps = [
            {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'borwser_launch', 'step': 'Given 22 navigate to "https://www.bing.com"', 'scenario': 'verify browser tool', 
              'tool_params': {'url': 'https://www.bing.com', 'caller': 'behave', 'need_snapshot': 0, 'need_snapsho2t': 0, 'need_snapshot3': 0}},
            {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_navigate', 'step': 'Given 22 navigate to "https://www.bing.com"', 'scenario': 'verify browser tool', 
              'tool_params': {'url': 'https://www.bing.com', 'caller': 'behave'}},
            #   {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_navigate', 'step': 'Given 22 navigate to "https://www.bing.comm"', 'scenario': 'verify browser tool', 
            #   'tool_params': {'url': 'https://www.bing.com', 'caller': 'behave'}},
            #   {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_navigate', 'step': 'Given 22 navigate to "https://www.bing.co"', 'scenario': 'verify browser tool', 
            #   'tool_params': {'url': 'https://www.bing.co', 'caller': 'behave'}},
            #   {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_navigate', 'step': 'Given 22 Navigate to "https://www.bing.co"', 'scenario': 'verify browser tool', 
            #   'tool_params': {'url': 'https://www.bing.co', 'caller': 'behave'}},
            #  {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_button_click', 'step': 'And 33 "Microsoft - .*" should appear in my favorites list', 'scenario': 'verify browser tool', 
            #   'tool_params': { 'name': 'Favorites', 'control_type': 'Button', 'caller': 'behave'}}, 
            #  {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'verify_element_exists', 'step': 'And 33 "Microsoft - .*" should appear in my favorites list', 'scenario': 'verify browser tool', 
            #   'tool_params': {'element_name': 'Microsoft - .*', 'caller': 'behave', 'control_type': 'TreeItem'}},
            #   {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_navigate', 'step': 'Given 22 navigate to "https://www.bing.co"', 'scenario': 'verify browser tool', 
            #   'tool_params': {'url': 'https://www.bing.co', 'caller': 'behave'}},
            #  {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'native_button_click', 'step': 'And 33 "Microsoft - .*" should appear in my favorites list', 'scenario': 'verify browser tool', 
            #   'tool_params': { 'name': 'Favorites', 'caller': 'behave'}}, 
            #  {'gen_code_id': '889ecfa9-9d8c-4c13-8b9f-42688133fef1', 'tool_name': 'verify_element_exists', 'step': 'And 33 "Microsoft - .*" should appear in my favorites list', 'scenario': 'verify browser tool', 
            #   'tool_params': {'element_name': 'Microsoft - .*', 'caller': 'behave', 'control_type': 'TreeItem'}}
                ]
    # rr = gen_code_preview_test('889ecfa9-9d8c-4c13-8b9f-42688133fef1', steps)
    
    # with open(TARGET_STEP_FILE_DEFAULT, 'a', encoding='utf-8') as f:
    #     for item in rr.get('new_steps_code'):
    #         f.write(item + "\n")
    # print(read_step_files(Path(r'c:\Users\toyu\code\auto-mcp-demo\behave_demo\features\steps')))

    gen_step_file_from_feature_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\features\favorites\sync_favorites.feature')
    gen_step_file_from_feature_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\features\favorites')
    gen_step_file_from_feature_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\features')
    gen_step_file_from_feature_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\sync_favorites.feature')
    
    # parse_steps_dir_from_step_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\steps')
    # parse_steps_dir_from_step_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\steps\demo-test')
    # parse_steps_dir_from_step_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\steps\demo-test\test_steps.py')
    # parse_steps_dir_from_step_path(r'C:\Users\toyu\code\edgeinternal.quality-toolkit\auto-mcp-demo\behave_demo\test_steps')
