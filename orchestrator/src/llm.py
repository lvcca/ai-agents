import requests
from os import getenv
from src.logger import get_logger, error_details

logger = get_logger('llm')

OLLAMA_URL = getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# prompts
CODING_TASKS_PROMPTS_FILE = "prompts/coding_tasks_prompts.md"
EXECUTION_PROMPTS_FILE = "prompts/execution_prompts.md"
CHAT_PROMPTS_FILE = "prompts/chat_prompts.md"
TOOL_NARROWER_PROMPTS_FILE = "prompts/tool_narrower.md"
SHELL_EXECUTOR_PROMPTS_FILE = "prompts/shell_executor_prompts.md"
SHELL_RESULTS_ANALYZER_PROMPTS_FILE ="prompts/shell_results_analyzer_prompts.md"
KARPATHY_GUIDELINES_PROMPTS_FILE = "prompts/karpathy_guidelines_prompts.md"

# types
TOOL_API_TYPE_FILE = "prompts/types/ApiToolChain.ts"
SHELL_EXECUTOR_TYPE_FILE = "prompts/types/ShellExecutor.ts"
SHELL_RESULTS_TYPE_FILE = "prompts/types/ShellResults.ts"

# consts
LLAMA_3_1 = "llama3.1"
QWEN3_CODER = "qwen3-coder:30b"
GRANITE_4 = "granite4.1:3b"

def load_context(prompts_md):
    PROMPTS_CONTENT = ""
    
    try:
        CONTEXT_BEGIN = "\n\n-----BEGIN CONTEXT-----\n\n"
        CONTEXT_END = "\n\n-----END CONTEXT-----\n\n"

        PROMPTS_CONTENT += CONTEXT_BEGIN
        
        with open(prompts_md, 'r', encoding='utf-8') as file:
            PROMPTS_CONTENT += file.read()

        PROMPTS_CONTENT += CONTEXT_END

    except Exception as e:
        logger.error(f'something went wrong in load_context {e}, error details: {error_details()}')
    
    return PROMPTS_CONTENT

PROMPTS = {
    "tasks": load_context(CODING_TASKS_PROMPTS_FILE),
    "execution": load_context(EXECUTION_PROMPTS_FILE),
    "chat": load_context(CHAT_PROMPTS_FILE),
    "tool_narrower": load_context(TOOL_NARROWER_PROMPTS_FILE),
    # aux
    "tool_types": load_context(TOOL_API_TYPE_FILE),
    "karpathy_guidelines" : load_context(KARPATHY_GUIDELINES_PROMPTS_FILE),
    # shell executor stuffs
    "shell_executor" : load_context(SHELL_EXECUTOR_PROMPTS_FILE),
    "shell_executor_types" : load_context(SHELL_EXECUTOR_TYPE_FILE),
    # shell results
    "shell_results_analyzer" : load_context(SHELL_RESULTS_ANALYZER_PROMPTS_FILE),
    "shell_results_types" : load_context(SHELL_RESULTS_TYPE_FILE),
}

def call_llm(prompt, model=QWEN3_CODER):
    try:
        logger.info(f'model: {model}, calling llm: {prompt}')

        karpathy_guidelines = PROMPTS['karpathy_guidelines'] + '\n'
        
        # https://docs.ollama.com/api/generate
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model,
            "prompt": karpathy_guidelines + prompt,
            "stream": False
        })

        res = response.json()["response"]

        logger.info(f'llm response: {res} {type(res)}')

        return res
        
    except Exception as e:
        logger.error(f'something went wrong in call_llm: {e}')
        return {"Error": e}
    
    except requests.RequestException as e:
        logger.error(f'something went wrong in call_llm: {str(e)}')
        return {"Error": f"Failed to call LLM with prompt '{prompt}': {str(e)}"}

def call_llm_tasks(prompt):
    with_context = PROMPTS['tasks'] + str(prompt)
    return call_llm(with_context)

def call_llm_toolcall(prompt):
    with_context = PROMPTS['execution'] + str(prompt)
    return call_llm(with_context)

def call_llm_chat(prompt):
    with_context = PROMPTS['chat'] + str(prompt)
    return call_llm(with_context)

def call_llm_data_narrower(prompt):
    with_context = PROMPTS['tool_narrower'] + PROMPTS['tool_types'] + str(prompt)
    return call_llm(with_context)

def call_llm_shell_executor(prompt):
    with_context = PROMPTS['shell_executor'] + str(prompt)
    return call_llm(with_context)

def call_llm_shell_results_analyzer(prompt):
    with_context = PROMPTS['shell_results_analyzer'] + str(prompt)
    return call_llm(with_context)