# CI/CD Agent and DevOps MCP Server

This project contains two services: a CI/CD Agent and a DevOps MCP Server. The CI/CD Agent is responsible for running CI/CD pipelines, and the DevOps MCP Server is a control plane for managing DevOps tasks.

## Prerequisites

To run this project, you will need to have the following tools installed:

*   Docker
*   Docker Compose

## Building and Running the Application

You can use Docker Compose to build and run the application.

### Build the images

To build the Docker images for both services, run the following command from the root of the project:

```bash
docker-compose build
```

### Start the Application

To start both services, run the following command from the root of the project:

```bash
docker-compose up -d
```

This command will also build the images if they don't exist.

### Stop the Application

To stop both services, run the following command from the root of the project:

```bash
docker-compose down
```

## Services

### CI/CD Agent

*   **Image:** `cicd-agent:latest`
*   **Port:** `8080`
*   **Description:** This service is responsible for running CI/CD pipelines. It is a Python application that uses Uvicorn to serve a web application on port 8080.

### DevOps MCP Server

*   **Image:** `devops-mcp:latest`
*   **Port:** `9000`
*   **Description:** This service is a control plane for managing DevOps tasks. It is a Python application that listens on port 9000.
