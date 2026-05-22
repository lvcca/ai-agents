import threading
import json
from worker_util import extract_response_block, safe_execute, tool_types
from schemas.FileSystemSchema import FileSystemSchema
from state import update_execution_task
from llm import call_llm_data_narrower, call_llm_toolcall
from src.logger import get_logger
from bootstrap import registry
import traceback

logger = get_logger('execution_worker')

def process_task(task):
    successful = False

    steps = task['identified_internal_tools_required']
    
    try:
        for step in steps:
            Tool = step["Tool"]
            Params = None

            if step["Params"] is not None:
                Params = step["Params"]

            try:
                if Tool and Tool['name'] is not None:
                    Tool = Tool['name']

            except Exception as e:
                logger.warn('Tool["name"] check failed-- not fatal.')
            
            print(f'emulating execution of tool: {Tool}. Found params: {Params}')
            
            found_tool = registry.get(Tool)

            if found_tool is not None:
                print(f'found tool: {found_tool.__name__}')
                result = safe_execute(found_tool, Params)
                print(f'{found_tool} result: {result}')

        
        successful = True

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f'something went wrong in process_task: {e}, error_details: {error_details}')
    
    return successful

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


def run_agents(task_id, task, LLM_DIRECT):

    update_execution_task(task_id, status="running")

    try:

        if LLM_DIRECT:
            final_output = call_llm_toolcall(f"{task}")

        else:
            initial_exec = call_llm_toolcall(f"""
                You are an System Execution agent.

                Your job is to take decomposed tasks written into concise executable steps and execute them using internal APIs identified in the FileSystemApiSchema.
                                    
                FileSystemApiSchema:
                {
                    json.dumps(FileSystemSchema, indent=4)
                }

                Tool Request Format:
                {
                    json.dumps(tool_types, indent=4)
                }

                TASK:
                {task}

                RULES:
                - Use ONLY valid JSON as output 
                - Always explain reasoning
                - Do NOT include markdown
                - There are at most 5 steps
                - Steps are concrete and actionable
                - Any text not in Javascript notation WILL be prepended with a comment

                ONLY ACCEPTABLE OUTPUT FORMAT:
                Tool_Output
                """)
            
            logger.info(f'initial_exec: {initial_exec}')
            
            tool_exec(task, initial_exec, call_llm_toolcall)

            final_output = initial_exec
            
            final_output = json.dumps({"output": initial_exec, "task": task}, indent=2, ensure_ascii=False)

        update_execution_task(task_id,
            status="done",
            result=final_output
        )

    except Exception as e:
        update_execution_task(task_id,
            status="failed",
            result=str(e)
        )


def start_execution_task(task_id, task, LLM_DIRECT = None):
    thread = threading.Thread(target=run_agents, args=(task_id, task, LLM_DIRECT))
    thread.start()
