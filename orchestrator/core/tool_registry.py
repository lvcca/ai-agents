class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, fn, schema=None, metadata=None):
        self._tools[name] = {
            "fn": fn,
            "schema": schema,
            "metadata": metadata or {}
        }

    def get(self, name):
        return self._tools[name]["fn"]

    def list_tools(self):
        return self._tools
