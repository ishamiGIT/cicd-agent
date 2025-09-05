# MCP Server

This server provides a local interface to interact with Google Cloud services through the Gemini CLI.

## Prerequisites

*   **Google Cloud SDK:** Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and authenticate with your Google account.
*   **Set up Application Default Credentials (ADC):**
    ```bash
    gcloud auth application-default login
    ```

## Running the Server

There are two ways to run the MCP server:

### 1. Using stdio

This method is recommended for local development and testing.

**Running the Server:**

To run the MCP server, use the `start.sh` script with the `--transport stdio` argument.

```bash
./start.sh --transport stdio
```

**Gemini CLI Configuration:**

Update your Gemini CLI `settings.json` to include the following:

```json
{
  "mcpServers": {
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

Replace `/path/to/your/devops-mcp-server/start.sh` with the absolute path to the `start.sh` script.

### 2. Using streamable HTTP and Docker

This method is recommended for a more robust setup.

**Build the Docker container:**

```bash
docker build -t devops-mcp-server . 
```

**Run the Docker container:**
```bash
docker run -v ~/.config/gcloud:/root/.config/gcloud -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json -p 9000:9000 devops-mcp-server
```

**Gemini CLI Configuration:**

Note that the server needs to be running in this case for Gemini CLI to connect to it.

Update your Gemini CLI `settings.json` to include the following:

```json
{
  "mcpServers": {
    "devops": {
      "httpUrl": "http://localhost:9000/mcp"
    }
  }
}
```