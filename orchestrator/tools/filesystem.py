# filesystem.py

import json
import os
import shutil
import fnmatch
from typing import List
import subprocess

from src.logger import error_details, get_logger 

logger = get_logger('filesystem')

WORKSPACE_ROOT = "/agent_workspace"

class PathError(Exception):
    pass


def resolve_path(user_path: str) -> str:
    # full = os.path.abspath(os.path.join(WORKSPACE_ROOT, user_path))

    # if not full.startswith(WORKSPACE_ROOT):
    #     raise PathError(f"path: {user_path} escaped workspace")

    # return full
    return user_path

# -------------------
# TOOL FUNCTIONS
# -------------------

def list_directory(path: str) -> List[str]:
    return os.listdir(resolve_path(path))


def read_file(path: str) -> str:
    with open(resolve_path(path), "r") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(resolve_path(path), "w") as f:
        f.write(content)


def append_file(path: str, content: str) -> None:
    with open(resolve_path(path), "a") as f:
        f.write(content)


def create_directory(path: str) -> None:
    os.makedirs(resolve_path(path), exist_ok=True)


def move_file(src: str, dst: str) -> None:
    shutil.move(resolve_path(src), resolve_path(dst))


def copy_file(src: str, dst: str) -> None:
    shutil.copy2(resolve_path(src), resolve_path(dst))


def delete_file(path: str) -> None:
    os.remove(resolve_path(path))

def file_exists(path: str) -> bool:
    return os.path.isfile(resolve_path(path))

def current_working_directory() -> str:
    return os.getcwd()


def execute_shell(command):

    shell_context = {
        "input": command,
        "output": None,
        "error": None,
    }

    try:
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )

        shell_context["output"] = result.stdout
        shell_context["error"] = result.stderr
    
    except subprocess.CalledProcessError as e:
        msg = f'something went wrong in execute shell {e} {error_details()}'
        logger.error(msg)
        shell_context['error'] = msg
    
    except Exception as e:
        msg = f'something went wrong in execute shell {e} {error_details()}'
        logger.error(msg)
        shell_context['error'] = msg

    logger.debug(f'shell_context: {shell_context}')

    return shell_context


def search_files(directory: str, pattern: str = "*") -> List[str]:
    resolved = resolve_path(directory)

    return [
        f for f in os.listdir(resolved)
        if os.path.isfile(os.path.join(resolved, f))
        and fnmatch.fnmatch(f, pattern)
    ]


def read_text_chunks(path: str, chunk_size: int = 1024):
    with open(resolve_path(path), "r") as f:
        while chunk := f.read(chunk_size):
            yield chunk


# -------------------
# REGISTRATION ENTRYPOINT
# -------------------

def register_tools(registry):
    registry.register("current_working_directory", current_working_directory, schema="filesystem")
    registry.register("list_directory", list_directory, schema="filesystem")
    registry.register("read_file", read_file, schema="filesystem")
    registry.register("write_file", write_file, schema="filesystem")
    registry.register("append_file", append_file, schema="filesystem")
    registry.register("create_directory", create_directory, schema="filesystem")
    registry.register("move_file", move_file, schema="filesystem")
    registry.register("copy_file", copy_file, schema="filesystem")
    registry.register("delete_file", delete_file, schema="filesystem")
    registry.register("file_exists", file_exists, schema="filesystem")
    registry.register("search_files", search_files, schema="filesystem")
    registry.register("read_text_chunks", read_text_chunks, schema="filesystem")
    registry.register("execute_shell", execute_shell, schema="filesystem")