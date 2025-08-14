# Import the app instance. This also brings in the config resource.
from app import mcp

# IMPORTANT: Import the modules containing your tools.
from artifact_registry import * 

# Sample tool
@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

if __name__ == "__main__":        
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")