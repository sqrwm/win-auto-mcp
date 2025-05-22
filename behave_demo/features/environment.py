import json
import time
import threading
import asyncio
import janus
import queue
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


session_ready = threading.Event()

# def before_all(context):
#     context._task_queue = asyncio.Queue()
#     context._result_queue = asyncio.Queue()

#     def run_loop():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)

#         async def mcp_worker():
#             try:
#                 async with sse_client("http://localhost:8000/sse") as streams:
#                     async with ClientSession(*streams) as session:
#                         await session.initialize()
#                         context.session = session
#                         session_ready.set()

#                         while True:
#                             task = await context._task_queue.get()
#                             if task is None:
#                                 break
#                             start = time.time()
#                             time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
#                             print(f"{time_str} _task_queue.get done")
    
#                             coro = task
#                             result = await coro
#                             start = time.time()
#                             time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
#                             print(f"{time_str} await coro end")
    
#                             await context._result_queue.put(result)
#                             start = time.time()
#                             time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
#                             print(f"{time_str} _result_queue.put end")

#             except Exception as e:
#                 print(f"MCP 初始化失败: {e}")
#                 session_ready.set()

#         loop.run_until_complete(mcp_worker())

#     thread = threading.Thread(target=run_loop, daemon=True)
#     thread.start()

#     session_ready.wait()


def before_all(context):
    context._task_queue = janus.Queue()
    context._result_queue = janus.Queue()

    session_ready = threading.Event()

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def mcp_worker():
            try:
                async with sse_client("http://localhost:8000/sse") as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()
                        context.session = session
                        session_ready.set()

                        while True:
                            task = await context._task_queue.async_q.get()
                            if task is None:
                                break

                            start = time.time()
                            coro = task
                            result = await coro
                            await context._result_queue.async_q.put(result)

            except Exception as e:
                session_ready.set()

        loop.run_until_complete(mcp_worker())

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()

    session_ready.wait()



# def after_all(context):
#     if hasattr(context, "_task_queue"):
#         asyncio.run(context._task_queue.put(None))



def after_all(context):
    if hasattr(context, "_task_queue"):
        context._task_queue.sync_q.put_nowait(None)


# def call_tool_sync(context, coro, timeout=40):
#     start = time.time()
#     time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
#     print(f"\n\n{time_str} call_tool_sync start: coro={coro}")
    
#     context._task_queue.put_nowait(coro)
#     start = time.time()
#     time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
#     print(f"{time_str} _task_queue.put_nowait done")
#     while True:
#         try:
#             result = context._result_queue.get_nowait()
#             time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
#             print(f"{time_str} call_tool_sync _result_queue.get_nowait: cost={int(time.time()-start)}, result={result}\n\n")
#             return result
#         except asyncio.QueueEmpty:
#             if time.time() - start > timeout:
#                 raise TimeoutError("MCP tool invocation timed out.")
#             time.sleep(0.1)


def call_tool_sync(context, coro, timeout=40):
    start = time.time()
    context._task_queue.sync_q.put(coro)
    while True:
        try:
            result = context._result_queue.sync_q.get_nowait()
            return result
        except queue.Empty:
            if time.time() - start > timeout:
                raise TimeoutError("MCP tool invocation timed out.")
            time.sleep(0.1)


def get_tool_json(result):
    try:
        if isinstance(result, str):
            return result
        items = getattr(result, "content", None)
        if items:
            for item in items:
                if getattr(item, "text", None):
                    text = getattr(item, "text", None)
                    return json.loads(text)
    except Exception as e:
        print(f"Error getting tool JSON: {e}")
        
    return None


def before_scenario(context, scenario):
    context.scenario = scenario
    result = call_tool_sync(context, context.session.call_tool(name="browser_launch", arguments={"caller": "behave-automation", 'need_snapshot': 0}))
    result_json = get_tool_json(result)
    assert result_json.get("status") == "success", f"Expected status to be 'success', got '{result_json.get('status')}', error: '{result_json.get('error')}'" 


def after_scenario(context, scenario):
    context.scenario = scenario
    result = call_tool_sync(context, context.session.call_tool(name="browser_close", arguments={"caller": "behave-automation", 'need_snapshot': 0}))
    pass

    