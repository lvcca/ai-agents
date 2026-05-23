import json

from src.llm import call_llm_data_narrower
from src.worker.process_task import process_task 
from src.worker.worker_util import extract_response_block
from src.logger import error_details, get_logger

logger = get_logger('tool_exec')

def tool_exec(task, initial_exec):
    try:
        print(f'initial_exec: {initial_exec}')

        narrowed = call_llm_data_narrower(f'sanitize the following output: {initial_exec}')

        print(f'narrowed: {narrowed}')

        json_response = extract_response_block(narrowed)

        print(f'extracted_json: {json_response}')
        
        task = json.loads(json_response)

        tasks = task['identified_internal_tools_required']

        if tasks is not None and len(tasks) > 0:
            print('identified_internal_tools_required not empty! Start processing tasks...');
            process_task(task)

        else:
            logger.error(f'something went wrong in tool exec, task:{task}')


    except Exception as e:
        logger.error(f'something went wrong in tool_exec: {e}, error_details: {error_details()}')