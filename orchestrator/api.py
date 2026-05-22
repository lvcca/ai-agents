from fastapi import FastAPI
import uuid
from src.state.state import Task_Type, create_execution_task, create_task, execute_task, execution_key, get_all_tasks, get_task, remove_task, request_key
from src.logger import get_logger
from src.worker.task_worker import start_task
from src.worker.execution_worker import start_execution_task

app = FastAPI()

########
# Task / Request Setup
########

logger = get_logger('api')

@app.get("/allTasks")
async def alltasks():
    allTasks = get_all_tasks(Task_Type.TASK)
    return {"allTasks": allTasks}

@app.post("/taskDirect")
async def createDirect(payload: dict):
    LLM_DIRECT = True
    task_id = request_key(str(uuid.uuid4()))
    task = payload.get("task")

    logger.info(f'taskDirect test {task}')
    
    create_task(task_id, task, LLM_DIRECT)
    start_task(task_id, task, LLM_DIRECT)

    return {"task_id": task_id, "status": "queued"}

@app.post("/task")
async def create(payload: dict):
    task_id = request_key(str(uuid.uuid4()))
    task = payload.get("task")
    logger.info(f'task test {task}')

    create_task(task_id, task)
    start_task(task_id, task)

    return {"task_id": task_id, "status": "queued"}

@app.get("/task/{task_id}")
async def task(task_id: str):
    return get_task(task_id)

@app.post("/task/delete/{task_id}")
async def rm_task(task_id: str):
    return remove_task(task_id)

########
# Execution
########

@app.get("/allExecutions")
async def alltasks():
    allExecutions = get_all_tasks(Task_Type.EXECUTION)
    return {"allExecutions": allExecutions}

@app.post("/execute")
async def execute(payload: dict):
    execute_id = execution_key(str(uuid.uuid4()))
    _err = None
    
    try:
        task = payload.get("task")
        
        logger.info(f'execution task: {task}')

        create_execution_task(execute_id, task)
        execute_task(execute_id, task)
        start_execution_task(execute_id, task)

    except Exception as e:
        logger.error(f'something went wrong in execute {e}')
        _err = e

    response = {"execute_id": execute_id, "status": "queued"}

    if _err is not None:
        response["error"] = _err
    
    return response