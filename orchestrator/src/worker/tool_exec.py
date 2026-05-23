import json
import traceback

from src.llm import call_llm_data_narrower
from src.worker.process_task import process_task 
from src.worker.worker_util import extract_response_block
from src.logger import get_logger

logger = get_logger('tool_exec')

def tool_exec(task, initial_exec, call_llm, depth=5):
    print(f'initial_exec: {initial_exec}')

    narrowed = call_llm_data_narrower(f'sanitize the following output: {initial_exec}')

    print(f'narrowed: {narrowed}')

    test = extract_response_block(narrowed)

    print(f'extracted_json: {test}')

    try:
        task = json.loads(test)

        tasks = task['identified_internal_tools_required']

        if tasks is not None and len(tasks) > 0:
            print('identified_internal_tools_required not empty! Start processing tasks...');
            process_task(task)
    
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f'something went wrong in tool_exec: {e}, error_details: {error_details}')