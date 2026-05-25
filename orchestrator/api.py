from fastapi import FastAPI
import uuid

from src.worker.worker_util import post_execute
from src.state.state import Task_Type, create_execution_task, create_task, execution_key, get_job, get_tasks, get_task, remove_execution_task, remove_task, request_key
from src.logger import get_logger
from src.worker.task_worker import start_task
from src.worker.execution_worker import start_execution_task
from bootstrap import registry

app = FastAPI()

########
# Task / Request Setup
########

logger = get_logger('api')

def Registery(*args, **kwargs):
    return registry(*args, **kwargs)

@app.get("/allTasks")
async def alltasks():
    allTasks = get_tasks(Task_Type.TASK)
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
    allExecutions = get_tasks(Task_Type.EXECUTION)
    return {"allExecutions": allExecutions}

@app.post("/execution/delete/{exec_id}")
async def rm_task(exec_id: str):
    _exec_id = execution_key(exec_id)
    return remove_execution_task(_exec_id)

@app.post("/execute")
async def execute(payload: dict):
    return post_execute(payload, create_execution_task, start_execution_task)

########
# all jobs
########

@app.get("/job/allJobs")
async def alltasks():
    allJobs = get_tasks(Task_Type.JOB)
    return {"allJobs": allJobs}

@app.post("/job/delete/{job_id}")
async def rm_task(job_id: str):
    _job_id = execution_key(job_id)
    return remove_execution_task(_job_id)

@app.get("/job/{task_id}")
async def task(task_id: str):
    return get_job(task_id)