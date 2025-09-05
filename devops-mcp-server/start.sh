#!/bin/bash
#
# ---
#
# This script is used to start the MCP server.
#
# ---

# For better error handling
set -euo pipefail

# ---
#
# All stdout from this script is redirected to stderr.
#
# When MCP server is run in embedded mode as stdio transport,
# MCP clients (e.g. Gemini-cli) expect stdout to be JSON-RPC.
#
# ---
exec 1>&2

# ---
#
# The main function of this script that start the MCP server,
# it will not be called when sourced.
#
# ---

main() {
  # Define virtual environment directory name
  local -r venv_dir=".venv"

  # Define Python application entry point
  local -r python_app="main.py"

  # Check if the virtual environment exists
  if [[ ! -d "${venv_dir}" ]]; then
    echo "Virtual environment not found. Creating a new one..."
    python3 -m venv "${venv_dir}"
  fi

  # Activate the virtual environment
  echo "Activating virtual environment..."
  source "${venv_dir}/bin/activate"

  # Install dependencies if requirements.txt exists
  if [[ -f "requirements.txt" ]]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --quiet -r requirements.txt
  else
    echo "requirements.txt not found. Skipping dependency installation."
  fi

  # Launch the Python application
  echo "Launching Python application: ${python_app}"
  python "${python_app}" "$@"

  # Deactivate the virtual environment upon script completion
  # This line is optional and depends on whether you want the venv to remain active in the shell
  # after the app exits. For simple startup scripts, it's often omitted.
  # deactivate
}

# ---
#
# This script is designed to be sourced or executed.
# It will not start MCP server when sourced.
#
# ---

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
