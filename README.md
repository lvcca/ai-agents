# AI-Agents Framework
=====================================

## Overview

AI-Agents is a lightweight, modular, and highly customizable AI agent framework built in Python. It provides a simple and intuitive API for creating intelligent agents that can interact with their environment and make decisions based on inputs.

## Installation

To install the AI-Agents framework, simply run the following command in your terminal:

```bash
git checkout git@github.com:lvcca/ai-agents.git; 
# from project root
docker compose down; 
docker compose up --build --force-recreate;
```

## Usage

```bash
curl -X POST \
  http://localhost:8000/execute \
  -H 'Content-Type: application/json' \
  -d '{"task": "Only using tools in the tool schema, execute the shell commands required to update the system package manager."}'
```

### Output

```shell
  {"task_id":"execution:032b8ee9-f142-4ce7-8fa8-1e66ce1384af","status":"queued"}
```

## Contributing

We welcome contributions from developers and users. If you'd like to contribute to the AI-Agents project, please submit a pull request with your changes.

## License

AI-Agents is released under the [MIT License](https://opensource.org/licenses/MIT).

## Issues

If you encounter any issues or have questions about using AI-Agents, please submit an issue on our GitHub repository.
