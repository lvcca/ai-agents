import threading
import json
from src.worker.tool_exec import tool_exec
from src.state.state import update_execution_task
from src.llm import call_llm_toolcall, PROMPTS
from src.logger import get_logger

logger = get_logger('execution_worker')

def run_agents(task_id, task, LLM_DIRECT):

    update_execution_task(task_id, status="running")

    try:

        if LLM_DIRECT:
            final_output = call_llm_toolcall(f"{task}")

        else:
            initial_exec = call_llm_toolcall(f"""
                You are an System Execution agent.

                Your job is to take decomposed tasks written into concise executable steps and execute them using internal APIs identified in the FileSystemApiSchema.
                                    
                Tool Request Format AND FileSystemApiSchema:
                {
                    json.dumps(PROMPTS['tool_types'], indent=4)
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
            
            tool_exec(task, initial_exec)

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
