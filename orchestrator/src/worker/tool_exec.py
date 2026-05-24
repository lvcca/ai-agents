import json

from src.state.state import update_execution_task
from src.llm import call_llm_data_narrower
from src.worker.process_task import process_task 
from src.worker.worker_util import extract_response_block
from src.logger import error_details, get_logger

logger = get_logger('tool_exec')

def tool_exec(task_id, task, initial_exec):

    update_execution_task(task_id, 
        status="running - in tool_exec",
        id=task_id
    )

    try:
        print(f'initial_exec: {initial_exec}')

        narrowed = call_llm_data_narrower(f'sanitize the following output: {initial_exec}')

        print(f'narrowed: {narrowed}')

        json_response = extract_response_block(narrowed)

        print(f'extracted_json: {json_response}')
        
        task = json.loads(json_response)

        steps = task['identified_internal_tools_required']

        if steps is not None and len(steps) > 0:
            update_execution_task(task_id, status="running - processing_step")
            
            process_task(task_id, task)

        else:
            msg = f'something went wrong in tool exec, task:{task}'
            logger.error(msg)

            update_execution_task(task_id, 
                status="failed",
                result=msg
            )


    except Exception as e:
        msg = f'something went wrong in tool_exec: {e}, error_details: {error_details()}'
        logger.error(msg)
        
        update_execution_task(task_id, 
            status="failed",
            result=msg
        )