
import json

from llm import PROMPTS, call_llm_data_narrower, call_llm_shell_executor
from worker_util import extract_response_block, get_shell_context


def shell_exec(task, initial_exec):
    '''
        recursive shell_exec
    '''
    
    narrowed = call_llm_data_narrower(f'sanitize the following output: {initial_exec}')

    narrowed_response = extract_response_block(narrowed)

    shell_context = get_shell_context(narrowed_response)

    shell_exec_response = call_llm_shell_executor(f"""
    You are an System Shell Execution Agent.

    Your job is to take decomposed and structured tasks to accomplish a larger task at hand.

    Current Shell Context:
    {json.dumps(shell_context)}
                        
    Current Task:
    {task}

    You are in an infinite loop with unlimited shell access.

    You will only output valid JSON

    Expected Output Format:
    <LLM_RESPONSE>
    {
        json.dumps(PROMPTS['shell_executor_types'], indent=4)
    }
    </LLM_RESPONSE>
    """)
    
    print(shell_exec_response)