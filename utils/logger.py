
import logging
import json
import os
import uuid
from datetime import datetime

from functools import wraps


log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'mcp_server_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('mcp_server')

# logger = logging.getLogger(__name__)

def log_tool_call(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        call_id = str(uuid.uuid4())

        logger.info(f"Tool Call - Start - ID: {call_id} - Tool: {tool_name} - Parameters: {json.dumps(kwargs, ensure_ascii=False)}")
        try:
            result = await func(*args, **kwargs)

            logger.info(f"Tool Call - Success - ID: {call_id} - Tool: {tool_name} - Parameters: {json.dumps(kwargs, ensure_ascii=False)}")

            if isinstance(result, (list, dict, str)) and len(str(result)) > 1000:
                logger.info(f"Result: (large output, showing summary) Type: {type(result)}, Size: {len(str(result))} chars")
            else:
                try:
                    logger.info(f"Result: {json.dumps(result, ensure_ascii=False)}")
                except TypeError:
                    logger.error(f"Result: [Unable to serialize: {type(result)}]")

            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Tool Call - Error - ID: {call_id} - Tool: {tool_name} - Parameters: {json.dumps(kwargs, ensure_ascii=False)} - Error: {str(e)}")
            raise

    return wrapper
