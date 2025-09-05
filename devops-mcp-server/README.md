# MCP Server

This server provides a local interface to interact with Google Cloud services through the Gemini CLI.

## Embedded Installation

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

### Running the Server

To run the MCP server, use the `start.sh` script with the `--transport stdio` argument. This will start the server and make it available for the Gemini CLI to use.

```bash
./start.sh --transport stdio
```

The script will automatically create a Python virtual environment, install the required dependencies from `requirements.txt`, and then start the server.

### Gemini CLI Configuration

To use this MCP server with the Gemini CLI, you need to update your Gemini CLI `settings.json` configuration file. Add a new entry under the `"mcpServers"` section to point to your local server.

**Example `settings.json` configuration:**

```json
{
  ...
  "mcpServers": {
    "devops": {
      "command": "/path/to/your/devops-mcp-server/start.sh",
      "args": [
        "--transport",
        "stdio"
      ]
    }
  }
  ...
}
```

Replace `/path/to/your/devops-mcp-server/start.sh` with the absolute path to the `start.sh` script in your cloned repository.

Once configured, you can invoke the server from the Gemini CLI using the `devops` prefix, for example:

```
gemini devops:cloud_run.services.list
```

## Running with Docker

This server is designed to be run as a Docker container. Here's how you can build and run it:

### 1. Build the Docker Image

From the root directory of the project, run the following command to build the Docker image:

```bash
docker build -t devops-mcp-server .
```

### 2. Run the Docker Container

### Using Your Local Google Cloud Credentials

To allow the server to use your local Google Cloud Application Default Credentials (ADC), you need to mount your local `gcloud` configuration directory into the container. This will allow the server to create GCP projects on your behalf.
```bash
gcloud auth application-default login
```

### Run

Once the image is built, you can run it as a container. The server will be available on port 8000.

```bash
docker run -v ~/.config/gcloud:/root/.config/gcloud -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json -p 9000:9000 devops-mcp-server
```
**Security Warning:** By mounting this directory, you are giving the container access to your `gcloud` credentials. You should only do this with Docker images that you trust.

**Note for Windows users:** The path to the `gcloud` configuration directory is `%APPDATA%\gcloud`.

### Gemini CLI Configuration

To use this MCP server with the Gemini CLI, you need to update your Gemini CLI `settings.json` configuration file. Add a new entry under the `"mcpServers"` section to point to your local server.

**Example `settings.json` configuration:**

```json
{
  ...
  "mcpServers": {
    "devops": {
      "httpUrl": "https://localhost:9000/mcp/",
      "timeout": 5000
    }
  }
  ...
}
```
