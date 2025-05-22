import json
from datetime import datetime
from typing import Any, Dict, Optional, Union, Literal


def init_tool_response() -> Dict[str, Any]:
    return {
        "status": "error",
        # "auto_continue": True,
        "data": {},
        "error": None,
        "timestamp": datetime.now().isoformat()
    }

def format_tool_response(
    response_dict: Dict[str, Any]
) -> str:
    if 'status' not in response_dict:
        raise ValueError("Response dictionary must contain 'status' key")
    
    response = {
        "status": response_dict["status"],
        # "auto_continue": response_dict.get("auto_continue", True),
        "data": response_dict.get("data", {})
    }
    
    if "error" in response_dict and response_dict["error"]:
        response["error"] = response_dict["error"]
    
    return json.dumps(response, ensure_ascii=False)

def parse_tool_response(response_json: str) -> Dict[str, Any]:
    try:
        return json.loads(response_json)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "data": {
            },
            "error": "Failed to parse response as JSON"
        }

def is_successful(response_json: str) -> bool:
    try:
        response = parse_tool_response(response_json)
        return (response["status"] == "success")
    except Exception:
        return False

