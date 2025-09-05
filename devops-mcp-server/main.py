# Import the app instance. This also brings in the config resource.
from app import mcp

# IMPORTANT: Import the modules containing your tools.
import artifact_registry
import cloud_run
import dev_connect
import cloud_build
import iam
import cicd
import rag
import vertexai


import argparse
import os
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def initialize_services():
    """Initializes all external services like Vertex AI."""
    logging.info("Initializing Vertex AI...")
    vertexai.init(project="haroonc-exp", location="us-east4")
    logging.info("Vertex AI Initialized.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GCP DevOps MCP Server.")
    parser.add_argument("--transport", type=str, default="stdio", help="MCP Transport ('http' or 'stdio')")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="MCP Server Host")
    parser.add_argument("--port", type=int, default=9000, help="MCP Server Port")
    parser.add_argument("--path", type=str, default="/mcp", help="MCP Path")

    args = parser.parse_args()    
    initialize_services()
    logging.info(f"Starting server as {args.transport} transport")
    if args.transport == "stdio":
        mcp.run(transport=args.transport)
    elif args.transport == "http":
        mcp.run(transport=args.transport, host=args.host, port=args.port, path=args.path)
    else:
        os.error(f"Transport {args.transport } is not supported!")
    