from src.llm import call_llm_shell_results_analyzer
from src.worker.worker_util import PROMPTS, safe_execute
from src.logger import get_logger, error_details
from src.state.state import create_job, get_execution_task, get_task, job_key, start_job, update_execution_task, update_job
from bootstrap import registry

logger = get_logger('process_task_util')

def analyze_shell_results(job_results, job_ids, task_id):
    final_results = call_llm_shell_results_analyzer(f"""
You are an System Execution agent.

Your job is to analyze system shell results.
                    
Each job should have an object entry that meets the ShellResults data structure:
{
    PROMPTS['shell_results_types']
}
                                        
Each job_result:
{
    [str(job_result) for job_result in job_results]
}

Each job_id:
{
    [str(job_id) for job_id in job_ids]
}

Task accomplished by job:
{
    get_execution_task(f"{task_id}")
}

Explain your findings.
""")
    
    return final_results

def get_tool(step):
    _Tool = None

    if isinstance(step, dict):
        _Tool = step.get("name")

    elif isinstance(step, str):
        _Tool = step.split(".")[-1:]

    else:
        _Tool = step
    
    return _Tool


def job_str(job_ids):
    if job_ids is not None: 
        return ",".join([str (job) for job in job_ids])
    
    else:
        return ''