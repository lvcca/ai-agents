import json
import re
import uuid
import requests

from src.state.state import execution_key, update_job
from src.logger import get_logger
from src.llm import PROMPTS, error_details

logger = get_logger('worker_util')

def parse_json_safe(text):
    try:
        logger.info(f'parse_json_safe text: {text}')
        return json.loads(text)
    except Exception:   
        return None
    
tool_types = PROMPTS['tool_types']

def extract_response_block(text: str) -> str | None:
    pattern = r"<LLM_RESPONSE>([\s\S]*?)</LLM_RESPONSE>"
    
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return f'{match.group(1).strip()}'  
    
    return None


def safe_execute(key, fn, Params):
    try:
        res = normalize_and_call(key, fn, Params)
        return res
    except Exception as e:
        logger.error(f'something went wrong in safe_execute: {e}, fn: {fn.__name__}, Params: {Params}')


def get_params(Params):
    xargs = []

    if isinstance(Params, list):
        param_len = len(Params)
        for i in range(param_len):
            xargs.append(Params[i]['value'])
    
    return xargs


def normalize_and_call(key, fn, Params):

    update_job(key, status='in normalize call')

    try:
        if isinstance(Params, dict):
            update_job(key, status="found params as dict")
            print('is dict')
            
            if (Params.items()) > 0:
                return fn(**Params)
            else:
                return fn()
        
        elif isinstance(Params, list):
            update_job(key, status="found params as list")
            print('is list')
            
            if len(Params) > 0:
                return fn(*get_params(Params))
            else:
                return fn()
            
        elif isinstance(Params, str):
            update_job(key, status="found params as str")
            print('is str')
            
            if len(Params) > 0:
                return fn(Params)
            else:
                return fn()
            
        else:
            update_job(key, status="found params as default")
            print('is default')
            
            return fn()
    
    except Exception as e:
        msg = f'something went wrong in normalize_and_call: {e}, fn: {fn}, Params: {Params}, error_details: {error_details()}'
        logger.error(msg)
        update_job(key, status="failed", error=msg)
        
        return fn()
    
def get_shell_context(narrowed_response):
    default_shell_context = {
        "input": None,
        "output": None,
        "error": None,
    }

    for key in default_shell_context.keys():
        try:
            value = narrowed_response.get("SessionStreams", {}).get(key)
            if value is not None:
                default_shell_context[key] = value
                
        except Exception as e:
            logger.error(f"get_shell_context error for key={key}: {e}")

    return default_shell_context


def execute_task (task):
    '''
        Example usage
        payload = {"task": {"name": "example_task", "description": "This is an example task"}}
        execute_task_directly(payload)
    '''

    logger.info(f'task type: {type(task)}')
    logger.info(f'task: {task}')

    payload = {"task": task}
    payload = json.dumps(payload)

    logger.info(f'execute_task with payload: {payload}')
    
    url = "http://localhost:8000/execute"
    
    try:
        
        response = requests.post(url, json=payload)

        logger.info(f'execute_task with payload: {json.dumps(response.json())}')
        
        if response.status_code == 200:
            return {"task_id": response.json()["task_id"], "status": "queued"}            
        
    
    except Exception as e:
        logger.error(f'something went wrong in execute_directly: {e}')


def post_execute(payload, create_execution_task, start_execution_task):
    execute_id = execution_key(str(uuid.uuid4()))
    _err = None
    
    try:
        task = payload.get("task")
        
        logger.info(f'execution task: {task}')

        create_execution_task(execute_id, task)
        start_execution_task(execute_id, task)

    except Exception as e:
        logger.error(f'something went wrong in execute {e}')
        _err = e

    response = {"task_id": execute_id, "status": "queued"}

    if _err is not None:
        response["error"] = _err
    
    return response