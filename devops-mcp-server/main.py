# Import the app instance. This also brings in the config resource.
from app import mcp

# IMPORTANT: Import the modules containing your tools.
from artifact_registry import * 
from cloud_run import *
from dev_connect import *
from cloud_build import *
from iam import *

# Sample tool
@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b

if __name__ == "__main__":        
    mcp.run(transport="http", host="0.0.0.0", port=9000, path="/mcp")