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
        _name = name
        if isinstance(_name, list):
            _name = _name[0]

        return self._tools[_name]["fn"]

    def list_tools(self):
        return self._tools
