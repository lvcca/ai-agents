import json

from src.llm import call_llm_shell_branch_analyzer, call_llm_shell_branch_simplifier
from src.worker.worker_util import PROMPTS
from src.logger import get_logger
from src.state.state import get_execution_task, get_job
from bootstrap import registry

logger = get_logger('process_task_util')

def simplify_opinion(next_step):
    final_result = call_llm_shell_branch_simplifier(f"""
You are a quality assurance expert. 

Input:
{ next_step }

Expected Output Format:
<LLM_RESPONSE>
    ShellBranchAnalysisSimplified
</LLM_RESPONSE>
""")
    return final_result

def get_second_opinion(analysis, job_results, job_ids, task_id):
    final_result = call_llm_shell_branch_analyzer(f"""
You are a quality assurance expert.

Your sole purpose is to evaluate the analysis of a job 

Analysis:
{ json.dumps(analysis) }

Pivot Decision Rule:
If `pivot_required=true` ALWAYS include a viable "next_step".                                        
Set `pivot_required=true` ONLY when the current execution trajectory can no longer realistically converge on successful task completion.
                                                   
A pivot is NOT required when:
- The branch is still progressing toward the task goal
- Failures are recoverable within the current execution strategy
- Additional execution within the same branch could still satisfy the task

A pivot IS recommended (pivot_recommended) when:
- original_task_goal has not been accomplished and next_step would change that.

Interpretation Rules:
- Evaluate trajectory viability from observed execution results and existing state.
- If original_task_goal not accomplished, lean towards pivot_required.

Do NOT:
- Expand beyond branch viability assessment

Each job must conform to the ShellResults structure:
{PROMPTS['shell_results_types']}

Job Results:
{[str(job_result) for job_result in job_results]}

Job IDs:
{[get_job(str(job_id)) for job_id in job_ids]}

Task Goal as original_task_goal:
{get_execution_task(task_id).get('task')}

Expected Output Format:
<LLM_RESPONSE>
    ShellBranchAnalysis
</LLM_RESPONSE>
""")
    return final_result

def analyze_shell_results(job_results, job_ids, task_id):
    final_results = call_llm_shell_branch_analyzer(f"""
You are a System Execution Branch Analysis agent.

Your sole responsibility is to evaluate whether the current execution branch remains viable for accomplishing the task goal.

IF pivot_required == falsey:
    You are NOT:
    - a planner
    - a shell command generator
    - a task executor
    - a strategy synthesizer

Do NOT propose commands, execution steps, remediation actions, or next-step plans.

Your only responsibility is branch viability analysis.

Pivot Decision Rule:
If `pivot_required=true` ALWAYS include a viable "next_step".                                        
Set `pivot_required=true` ONLY when the current execution trajectory can no longer realistically converge on successful task completion.
                                                   
A pivot is NOT required when:
- The branch is still progressing toward the task goal
- Failures are recoverable within the current execution strategy
- Additional execution within the same branch could still satisfy the task

A pivot IS required when:
- The branch has irreversibly diverged from the task goal
- Continuing execution within the current branch cannot satisfy the task
- The current execution strategy is no longer viable or helpful for resolving the current task.
- No viable continuation exists within the current branch.

Interpretation Rule:
Evaluate trajectory viability only from observed execution results.

Do NOT:
- infer or suggest future commands
- prescribe system actions
- construct next-step shell instructions
- expand beyond branch viability assessment

Each job must conform to the ShellResults structure:
{PROMPTS['shell_results_types']}

Job Results:
{[str(job_result) for job_result in job_results]}

Job IDs:
{[get_job(str(job_id)) for job_id in job_ids]}

Task Goal as original_task_goal:
{get_execution_task(task_id).get('task')}

Analysis Instructions:
1. Assess whether observed outputs remain aligned with the task goal
2. Determine whether successful completion is still reachable within this branch
3. Set `pivot_required=true` only if no viable continuation exists
4. Explain the reasoning strictly in terms of branch viability

Expected Output Format:
<LLM_RESPONSE>
    ShellBranchAnalysis
</LLM_RESPONSE>
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