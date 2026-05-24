
import uuid

from src.worker.process_task_util import analyze_shell_results, job_str
from src.worker.worker_util import safe_execute
from src.logger import get_logger, error_details
from src.state.state import create_job, job_key, start_job, update_execution_task, update_job
from bootstrap import registry

logger = get_logger('execution_worker')

def process_task(task_id, task):
    successful = False
    final_results = None

    job_ids = []
    job_results = []
    
    try:
        steps = task['identified_internal_tools_required']

        for step in steps:
            job_id = job_key(str(uuid.uuid4()))
            
            if job_id not in job_ids:
                job_ids.append(job_id)

            create_job(job_id, step)
            start_job(job_id, step)
            
            Tool = None

            Tool = step['Tool']
            Params = step['Params']

            if step["Params"] is not None:
                Params = step["Params"]

            try:
                if Tool and isinstance(Tool, list):
                    if len(Tool) > 0:
                        print('tool list greater than 0')
                        Tool = Tool[0]
                    else:
                        print('tool list less than 0')

                elif Tool and not isinstance(Tool, str) and Tool['name'] is not None:
                    Tool = Tool['name']

                elif Tool and isinstance(Tool, str):
                    if len(Tool.split('\.')) > 0:
                         Tool = Tool.split('\.')[-1:]

            except Exception as e:
                logger.warning(f'Tool["name"] check failed -- not fatal. error: {e}, error_details: {error_details()}, Tool: {Tool}.')
            
            update_execution_task(
                task_id, 
                status="running-processing_step", 
                jobs_group=f"{job_str(job_ids)}"
            )
            
            print(f'executing tool: {Tool}. Found params: {Params}, job_ids: {job_str(job_ids)}')
            
            found_tool = registry.get(Tool)

            update_execution_task(
                task_id, 
                status="running-found_tool", 
                jobs_group=f"{job_str(job_ids)}"
            )

            if found_tool is not None:
                
                print(f'found tool: {found_tool.__name__}')

                update_job(
                    job_id, 
                    status="running-safe_execute",
                    jobs_group=f"{job_str(job_ids)}",
                    task_id=f"{task_id}"
                )
                
                result = safe_execute(job_id, found_tool, Params)

                job_results.append(result)

                sample = analyze_shell_results(job_results, job_ids, task_id)
                
                logger.info(f'sample: {sample}')

                update_job(
                    job_id, 
                    status="running-safe_execute completed", 
                    jobs_group=f"{job_str(job_ids)}", 
                    job_results=f"{job_str(job_results)}", 
                    task_id=f"{task_id}"
                )

                print(f'found tool: {found_tool}, result: {result}')
            
            else:
                job_results.append('could not find tool')

        final_results = analyze_shell_results(job_results, job_ids, task_id)

        logger.info(f'final_results: {final_results}')

        successful = True

    except Exception as e:
        msg = f'something went wrong in process_task error_details: {error_details()}'
        logger.error(msg)

        update_job(task_id, status="failed", jobs_group=f"{job_str(job_ids)}", error=f"{error_details()}")
    
    finally:
        if successful:
            logger.info('successful')
            update_execution_task(
                task_id, 
                status="done",
            )
        else:
            logger.info('not successful')
            update_execution_task(
                task_id, 
                status="failed",
            )

    return final_results