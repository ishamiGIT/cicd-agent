```
+-----------------------------------------------------------------------------+
|                        CI/CD Agent Architecture Flow                        |
+-----------------------------------------------------------------------------+

                               +----------+
                               |   User   |
                               +----------+
                                    |
                                    | Request ("I need a secure GKE pipeline...")
                                    v
                           +------------------+
                           |    Root Agent    |
                           |  (Dispatcher) 🚦 |
                           +------------------+
                                    |
                                    | Delegates to...
                                    v
.-------------------------  DESIGN PHASE  ------------------------------------.
|                                                                             |
|      +---------------------+                                                |
|      |    Design Agent     | <------------------------------------+         |
|      | (The Architect ✍️) |                                       |         |
|      +---------------------+                                      |         |
|         |           ^                                             |         |
|         |           |  Collaborative Loop (Draft -> Revise)       |         |
|         | Looks up  +-----------------------------------------> (User)      |
|         | Patterns                                                          |
|         v                                                                   |
|      +---------------------+                                                |
|      |   Pattern Library   |                                                |
|      | (Knowledge Base)    |                                                |
|      +---------------------+                                                |
|         |                                                                   |
|         | Produces...                                                       |
|         v                                                                   |
|      +---------------------+                                                |
|      |  Final YAML Plan    | (The "Blueprint")                              |
|      +---------------------+                                                |
|                                                                             |
'-----------------------------------------------------------------------------'
                                    |
                                    | Plan is handed off via Root Agent to...
                                    v
.-------------------------  IMPLEMENTATION PHASE  ----------------------------.
|                                                                             |
|      +----------------------+                                               |
|      | Implementation Agent |                                               |
|      | (Project Manager 👷) |                                               |
|      +----------------------+                                               |
|                 |                                                           |
|                 | Executes Plan using...                                    |
|                 v                                                           |
|      +----------------------+                                               |
|      |  Specialized Tools   | (Deterministic Code)                          |
|      +----------------------+                                               |
|                 |                                                           |
|                 | Makes API calls to...                                     |
|                 v                                                           |
|      +----------------------+                                               |
|      |         GCP          |                                               |
|      +----------------------+                                               |
|                 ^                                                           |
|                 |                                                           |
|                 +--------------> Reports progress back to User <------------+
|                                                                             |
'-----------------------------------------------------------------------------'
```

# CI/CD Agent for Google Cloud

 CI/CD agent designed to automate the process of building and deploying applications on Google Cloud Platform. It leverages a multi-agent architecture to provide a seamless and intelligent experience for managing CI/CD pipelines.

## Project Overview

The core of this project is a system of interconnected agents, each with a specific role in the CI/CD process. This allows for a modular and extensible architecture where each agent is an expert in its domain.

### Key Features

*   **Automated Pipeline Generation**: The agent can automatically generate `cloudbuild.yaml` files based on the project's archetype (e.g., Python, Node.js, Java).
*   **Intelligent Context Discovery**: The agent can automatically discover the GCP project, location, and application type from the local environment.
*   **Idempotent Operations**: All operations are designed to be idempotent, ensuring that they can be run multiple times without causing errors.
*   **Extensible Architecture**: The multi-agent architecture allows for the addition of new agents and capabilities over time.

## Agent Architecture

The project is composed of the following agents:

*   **Root Agent (`cicd_agent`)**: This is the main orchestrator agent that receives user requests and delegates them to the appropriate specialist agent.
*   **Design Agent (`design_agent`)**: This agent is responsible for designing and refining CI/CD pipelines. It interacts with the user to gather requirements and then generates a pipeline specification.
*   **Implementation Agent (`implementation_agent`)**: This agent is responsible for executing the deployment plans generated by the Design Agent.

## Knowledge Base

The project includes a knowledge base of best practices for building and deploying applications on Google Cloud. This includes:

*   **`how_to_build_cloudbuild_yaml.md`**: A guide on how to automatically generate a `cloudbuild.yaml` file with best practices for CI/CD.
*   **`how_to_create_cloudbuild_trigger.md`**: A guide on how to create a Cloud Build trigger, including all the necessary prerequisite checks.

## CI/CD Patterns

The project also includes a collection of common CI/CD patterns that can be used as a starting point for designing new pipelines.

*   **`scheduled_nightly_release.yaml`**: A pattern for a scheduled nightly release, where code is built and tested on every push, but a release is only created at a fixed time.
