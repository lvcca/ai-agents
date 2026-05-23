
import uuid

from src.worker.worker_util import safe_execute
from src.logger import get_logger, error_details
from src.state.state import create_job, start_job, update_execution_task, update_job
from bootstrap import registry

logger = get_logger('execution_worker')

def get_tool(step):
    _Tool = None

    if isinstance(step, dict):
        _Tool = step.get("name")

    if isinstance(step, str):
        _Tool = step.split(".")[-1:]

    else:
        _Tool = step
    
    return _Tool


def job_str(job_ids: [str]):
    return ",".join([str (job) for job in job_ids])

def process_task(task_id, task):
    successful = False

    steps = task['identified_internal_tools_required']

    job_ids = []
    
    try:
        for step in steps:
            job_id = str(uuid.uuid4())
            
            if job_id not in job_ids:
                job_ids.append(job_id)

            create_job(job_id, step)
            start_job(job_id, step)
            
            Tool = None

            Tool = step['Tool']
            Params = step['Params']

            if step["Params"] is not None:
                Params = step["Params"]

            try:
                if Tool and Tool['name'] is not None:
                    Tool = Tool['name']

                if Tool and isinstance(Tool, str):
                    if len(Tool.split('.')) > 0:
                         Tool = Tool.split('.')[-1:]

            except Exception as e:
                logger.warning('Tool["name"] check failed -- not fatal.')
            
            update_execution_task(task_id, status="running-processing_step", jobs_created=f"{job_str(job_ids)}")
            
            print(f'executing tool: {Tool}. Found params: {Params}, job_ids: job_ids')
            
            found_tool = registry.get(Tool)

            update_execution_task(task_id, status="running-found_tool", jobs_created=f"{job_str(job_ids)}")

            if found_tool is not None:
                
                print(f'found tool: {found_tool.__name__}')

                update_job(task_id, status="running-safe_execute", jobs_created=f"{job_str(job_ids)}")
                
                result = safe_execute(task_id, found_tool, Params)

                update_job(task_id, status="running-safe_execute completed", jobs_created=f"{job_str(job_ids)}", result=result)

                print(f'{found_tool} result: {result}')

        successful = True

    except Exception as e:
        msg = f'something went wrong in process_task error_details: {error_details()}'
        logger.error(msg)
        
        update_job(task_id, status="failed", jobs_created=f"{job_str(job_ids)}")
    
    return successful