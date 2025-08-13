from functools import wraps

mcp_capabilities_registry = []

def mcp_capability(name: str, description: str, parameters: list):
    def decorator(func):
        mcp_capabilities_registry.append({
            "name": name,
            "description": description,
            "parameters": parameters,
        })
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
