# MCP Server

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
