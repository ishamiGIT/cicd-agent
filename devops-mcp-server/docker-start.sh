#!/bin/bash
set -e

# Define the image name as a variable for easy updates
IMAGE_NAME="devops-mcp-server"

# Build the Docker image from the Dockerfile in the current directory (.).
# Docker's cache makes this very fast if no files have changed.
echo "INFO: Building Docker image '$IMAGE_NAME'..."
docker build -t "$IMAGE_NAME" .

# Run the container. The 'exec' command replaces the shell process with the
# docker process, which is better for signal handling.
echo "INFO: Starting MCP server from container..."
exec docker run \
  --rm \
  -i \
  -v "$HOME/.config/gcloud:/root/.config/gcloud" \
  -e "GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json" \
  "$IMAGE_NAME"
 