
import uuid

from src.worker.worker_util import safe_execute
from src.logger import get_logger, error_details
from src.state.state import update_execution_task
from bootstrap import registry

logger = get_logger('execution_worker')


def process_task(task_id, task):
    successful = False

    steps = task['identified_internal_tools_required']

    job_ids = []
    
    try:
        for step in steps:
            job_id = str(uuid.uuid4())
            
            if job_id not in job_ids:
                job_ids.append(job_id)

            update_execution_task(task_id, status="running - processing_step", jobs_created=job_ids)

            Tool = step["Tool"]
            Params = None

            if step["Params"] is not None:
                Params = step["Params"]

            try:
                if Tool and Tool['name'] is not None:
                    Tool = Tool['name']

                if Tool and type(Tool) is type(str()):
                    if len(Tool.split('.')) > 0:
                         Tool = Tool.split('.')[-1:]

            except Exception as e:
                logger.warning('Tool["name"] check failed -- not fatal.')
            
            print(f'executing tool: {Tool}. Found params: {Params}')
            
            found_tool = registry.get(Tool)

            if found_tool is not None:
                print(f'found tool: {found_tool.__name__}')
                result = safe_execute(found_tool, Params)
                print(f'{found_tool} result: {result}')

        successful = True

    except Exception as e:
        msg = f'something went wrong in process_task: {e}, error_details: {error_details()}'
        logger.error(msg)
        update_execution_task(task_id, status="failed", jobs_created=job_ids, result=msg)
    
    return successful