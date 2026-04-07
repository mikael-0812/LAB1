import inspect
import json
import sys
import os

# Add root folder to sys.path so we can import tools from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import tools

def generate_tools_schema():
    """Dynamically generates JSON schema for all available tools in tools.py"""
    schema = []
    for name, obj in inspect.getmembers(tools, inspect.isfunction):
        # We only want to expose functions that belong to `tools` and exclude helpers like load_data
        if obj.__module__ == tools.__name__ and name != 'load_data':
            sig = inspect.signature(obj)
            params = {
                "type": "object",
                "properties": {},
                "required": []
            }
            for param_name, param in sig.parameters.items():
                params["properties"][param_name] = {"type": "string"}
                if param.default == inspect.Parameter.empty:
                    params["required"].append(param_name)
                    
            schema.append({
                "name": name,
                "description": obj.__doc__.strip() if obj.__doc__ else f"Call {name}",
                "parameters": params
            })
    return schema

def execute_dynamic_tool(tool_name: str, args_str: str) -> str:
    """Dynamically executes a tool function from tools.py."""
    if not hasattr(tools, tool_name):
        return json.dumps(
            {"ok": False, "error_type": "tool_not_found", "message": f"Tool {tool_name} is not available."},
            ensure_ascii=False
        )

    func = getattr(tools, tool_name)
    try:
        if not args_str or args_str.strip() == "" or args_str == "{}":
            result = func()
        else:
            args = json.loads(args_str)
            result = func(**args)

        if result is None:
            return json.dumps(
                {"ok": False, "error_type": "no_data", "message": "No data found."},
                ensure_ascii=False
            )

        if isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False)

        return str(result)

    except Exception as e:
        return json.dumps(
            {"ok": False, "error_type": "tool_execution_error", "message": f"Error calling tool {tool_name}: {str(e)}"},
            ensure_ascii=False
        )
# Generate the global schema array for agent injection
DYNAMIC_TOOLS_SCHEMA = generate_tools_schema()
