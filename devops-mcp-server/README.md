# MCP Server

This server provides a local interface to interact with Google Cloud services through the Gemini CLI.

## Installation

### Prerequisites

*   **Python 3.10 or higher:** Ensure you have a compatible Python version installed.
*   **Google Cloud SDK:** Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and authenticate with your Google account.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/GoogleCloudPlatform/gemini-cli.git
    cd gemini-cli/mcp/devops-mcp-server
    ```

2.  **Log in to your Google Cloud account:**
    ```bash
    gcloud auth login
    ```

3.  **Set up Application Default Credentials (ADC):**
    ```bash
    gcloud auth application-default login
    ```

## Running the Server

To run the MCP server, use the `start.sh` script with the `--transport stdio` argument. This will start the server and make it available for the Gemini CLI to use.

```bash
./start.sh --transport stdio
```

The script will automatically create a Python virtual environment, install the required dependencies from `requirements.txt`, and then start the server.

## Gemini CLI Configuration

To use this MCP server with the Gemini CLI, you need to update your Gemini CLI `settings.json` configuration file. Add a new entry under the `"mcp"` section to point to your local server.

**Example `settings.json` configuration:**

```json
{
  "mcp": {
    "devops": {
      "command": "/path/to/your/devops-mcp-server/start.sh",
      "args": [
        "--transport",
        "stdio"
      ]
    }
  }
}
```

Replace `/path/to/your/devops-mcp-server/start.sh` with the absolute path to the `start.sh` script in your cloned repository.

Once configured, you can invoke the server from the Gemini CLI using the `devops` prefix, for example:

```
gemini devops:cloud_run.services.list
```