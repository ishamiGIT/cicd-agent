#!/bin/bash
#
# ---
#
# Start the CICD MCP server in a python virtual environment
#
# ---

# For better error handling
set -euo pipefail

# Define virtual environment directory name
VENV_DIR=".venv"

# Define Python application entry point
#local -r 
SERVER_APP="main.py"

# Change to the directory where the script is located
MCP_SERVER_ROOT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
#echo "Changing to directory: ${MCP_SERVER_ROOT_DIR}" >&2
cd "${MCP_SERVER_ROOT_DIR}"

# Check if the virtual environment exists
if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Virtual environment not found. Creating a new one..." >&2
  python3 -m venv "${VENV_DIR}"
fi

# Activate the virtual environment
echo "Activating virtual environment..." >&2
source "${VENV_DIR}/bin/activate" >&2

# Install dependencies if requirements.txt exists
if [[ -f "requirements.txt" ]]; then
  echo "Installing dependencies from requirements.txt..." >&2
  if ! pip install --quiet -r requirements.txt >&2; then
    echo "Failed to install dependencies. Exiting." >&2
    exit 1
  fi
else
  echo "requirements.txt not found. Skipping dependency installation." >&2
  exit 1
fi

# Launch the Python application
echo "Launching CICD MCP Server: ${SERVER_APP}" >&2
python "${SERVER_APP}" "$@"

# Deactivate the virtual environment upon script completion
# This line is optional and depends on whether you want the venv to remain active in the shell
# after the app exits. For simple startup scripts, it's often omitted.
deactivate
