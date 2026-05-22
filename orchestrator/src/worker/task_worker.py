import threading
import json
from src.worker.worker_util import parse_json_safe
from src.state.state import update_task
from src.llm import call_llm_chat, call_llm_tasks
from src.logger import get_logger

logger = get_logger('task_worker')


def revise_plan(task, plan, call_llm, depth=5):
    """
        Recursive bounded plan refinement.
    """

    if depth == 0:
        return {
            "approved": False,
            "steps": plan,
            "revise_plan": False,
        }
    
    logger.info(f'current task: {task}')
    logger.info(f'current plan: {plan}')

    prompt = f"""
You are a planning critic. You only have {depth} number of attempts left to get this right.

TASK:
{task}

PLAN:
{json.dumps(plan, indent=2)}

Evaluate the plan.

Return ONLY JSON:

If 'revise_plan' is Truthy:
    Assume the plan is not acceptable and revise the plan before critic. 
    Always remove the revise_plan flag from the output.

If acceptable return the following data-structure:
{{
  "approved": True,
  "steps": [...]
}}

If not acceptable return the following data-structure:
{{
  "approved": False,
  "steps": [...],
  "revise_plan": True
}}
"""
    
    logger.info(f'prompt: {prompt}')

    raw = call_llm(prompt)
    
    logger.info(f'response: {raw}')

    result = parse_json_safe(raw)

    if result is None:
        return revise_plan(task, plan, call_llm, depth - 1)

    if result.get("approved") is True:
        return result

    new_plan = result.get("steps", plan)

    return revise_plan(task, new_plan, call_llm, depth - 1)

def run_agents(task_id, task, LLM_DIRECT):

    update_task(task_id, status="running")

    try:

        if LLM_DIRECT:
            final_output = call_llm_chat(f"{task}")

        else:
            plan = call_llm_tasks(f"""
                You are a planning agent.

                Your job is to decompose tasks into concise executable steps.

                RULES:
                - Return ONLY valid JSON
                - Do not explain reasoning
                - Do not include markdown
                - Use at most 5 steps
                - Steps must be concrete and actionable

                OUTPUT FORMAT:
                {{
                "steps": [
                    "step 1",
                    "step 2"
                ]
                }}

                TASK:
                {task}
                """)
            
            revised_plan = revise_plan(task, plan, call_llm_tasks)

            final_output = call_llm_tasks(f"""
                You are an execution agent.

                Your job is to complete the requested task using the provided plan.

                ORIGINAL TASK:
                {task}

                PLAN:
                {revised_plan}

                RULES:
                - Follow the steps carefully
                - Be concise
                - Do not explain your reasoning unless necessary
                - Return only the completed result

                EXECUTION:
                """)
            
            final_output = json.dumps({"output": final_output, "task": task, "plan": revised_plan}, indent=2, ensure_ascii=False)

        update_task(task_id,
            status="done",
            result=final_output
        )

    except Exception as e:
        update_task(task_id,
            status="failed",
            result=str(e)
        )


def start_task(task_id, task, LLM_DIRECT = None):
    thread = threading.Thread(target=run_agents, args=(task_id, task, LLM_DIRECT))
    thread.start()
