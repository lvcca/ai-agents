import traceback
import redis
import json
from enum import Enum
from src.logger import get_logger

logger = get_logger('state')

r = redis.Redis(host="redis", port=6379, decode_responses=True)

GLOBAL_CTX = "GLOBAL_CTX"

class Task_Type(Enum):
    TASK = 1
    EXECUTION = 2
    ALL = 3

def get_global_context():
    _current_context = r.get(GLOBAL_CTX)

    if _current_context is None:
        _current_context = ""

    return _current_context

def append_global_context(prompt):
    _current_context = get_global_context()

    _current_context += '\n' + prompt
    try:
        r.set(
            GLOBAL_CTX,
            _current_context
        )

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f'something went wrong in append_global_context {e}, error_details: {error_details}')


########
# Task / Request Setup
########
def request_key(task_id: str) -> str:
    _constant = "request:"
    
    if _constant not in task_id:
        return f"{_constant}{task_id}"
    else:
        return task_id

def execution_key(task_id: str) -> str:
    _constant = "execution:"

    if _constant not in task_id:
        return f"{_constant}{task_id}"
    else:
        return task_id

def create_task(task_id, task, LLM_DIRECT = None):
    r.set(request_key(task_id), json.dumps({
        "status": "queued",
        "task": task,
        "result": None,
        "LLM_DIRECT": LLM_DIRECT
    }))

def update_task(task_id, **fields):
    data = json.loads(r.get(request_key(task_id)))
    data.update(fields)
    r.set(request_key(task_id), json.dumps(data))

def get_task(task_id):
    key = ""
    
    if request_key('') not in task_id:
        key = request_key(task_id)
    else:
        key = task_id

    data = r.get(key)
    return json.loads(data) if data else None

def remove_task(task_id):
    r.delete(request_key(task_id))

def get_all_tasks(task_type: Task_Type):
    if Task_Type(task_type) == Task_Type.ALL:
        keys = r.scan_iter('*')

    if Task_Type(task_type) == Task_Type.TASK:
        keys = r.scan_iter(request_key('*'))

    if Task_Type(task_type) == Task_Type.EXECUTION:
        keys = r.scan_iter(execution_key('*'))

    tasks = [i for i in keys]
    return tasks

########
# Execution context
########

def create_execution_task(task_id, task, LLM_DIRECT = None):
    r.set(execution_key(task_id), json.dumps({
        "status": "queued",
        "task": task,
        "result": None,
        "LLM_DIRECT": LLM_DIRECT
    }))

def execute_task(task_id, task, LLM_DIRECT = None):
    try:
        exec_id = execution_key(task_id)
        
        # get existing context
        context = json.loads(r.get(exec_id))
        context = context.get('context', task) 

        # set update context and task
        r.set(exec_id, json.dumps({
            "context": context,
            "task": task,
            "LLM_DIRECT": LLM_DIRECT
        }))

    except Exception as e:
        logger.error(f'something went wrong in execute_task {e}')


def get_execution_task(task_id):
    data = r.get(execution_key(task_id))
    return json.loads(data) if data else None

def remove_execution_task(task_id):
    r.delete(execution_key(task_id))

def update_execution_task(task_id, **fields):
    _task_id = execution_key(task_id)
    
    data = json.loads(r.get(_task_id))
    data.update(fields)

    r.set(request_key(_task_id), json.dumps(data))