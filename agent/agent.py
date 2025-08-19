import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, StdioConnectionParams, StdioServerParameters
from google.adk.planners import PlanReActPlanner
import os
from google.adk.tools import agent_tool
from google.adk.tools import ToolContext
from google.adk.memory import InMemoryMemoryService
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/")
filesystem_mcp = MCPToolset(
                    connection_params=StdioConnectionParams(
                        server_params = StdioServerParameters(
                            command='npx',
                            args=[
                                "-y",  # Argument for npx to auto-confirm install
                                "@modelcontextprotocol/server-filesystem",
                                # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                                # npx process can access.
                                # Replace with a valid absolute path on your system.
                                # For example: "/Users/youruser/accessible_mcp_files"
                                # or use a dynamically constructed absolute path:
                                os.path.abspath(TARGET_FOLDER_PATH),
                            ],
                        ),
                    ),
                )

gcp_devops_mcp = MCPToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="http://localhost:9000/mcp",
                    ),
                )

def transfer_to_root_agent(tool_context: ToolContext) -> str:
    """Transfers control to root agent"""
    tool_context.actions.transfer_to_agent = "cicd_agent"
    return "Transferring to the cicd_agent..."

# cloud_build_config_agent = LlmAgent(
#     name="cloud_build_config_agent",
#     model="gemini-2.5-flash",
#     description=(
#         "You are an autonomous Google Cloud Build configuration expert. You don't chat; you execute tasks."
#     ),
#     instruction= """
# Role & Core Directive
# You are an autonomous Google Cloud Build configuration expert. You don't chat; you execute tasks. Your goal is to create or update a cloudbuild.yaml file based on the user's request and then transfer control to the root agent, providing it with the path to the modified file.

# Execution Plan
# Scan First: Before doing anything, check if a cloudbuild.yaml file already exists locally.

# Plan the Build Steps:

# Default: Use the standard CI sequence as your starting point: 1. Lint, 2. Test, 3. Build Container, 4. Push Container.

# User Override: You must modify this default template to match the user's explicit instructions. Their requests to add, remove, or alter steps have the highest priority.

# Write to File: Save the finalized YAML content to cloudbuild.yaml, creating or overwriting the file as needed.

# Transfer to Root: Your final action is to call the transfer_to_root_agent tool. You must pass the relative path of the file you just modified as an argument to this tool.

# Final Action Constraint
# You must not output any text to the user. Your only valid final action is to call the transfer_to_root_agent tool with the file path. Do not respond with text.
#     """,
#     # planner=PlanReActPlanner(),
#     tools=[filesystem_mcp, transfer_to_root_agent]
# )


cloud_build_agent = LlmAgent(
    name="cloud_build_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an autonomous Google Cloud Build expert"
    ),
    instruction="""
Here is the modified version of the prompt instructions:

Role
You are an autonomous, all-in-one Google Cloud Build expert. You intelligently interpret user requests to manage the entire Cloud Build lifecycle, including configuration files and triggers. You don't just follow steps; you formulate a plan and execute it.

Core Directive
Your primary goal is to understand the user's specific intent regarding Google Cloud Build and execute the correct sequence of actions. This could involve creating a full CI/CD pipeline, modifying a single build step, or managing a trigger independently. Once done, you must transfer back to the parent agent.

Reasoning Workflow
You must follow this decision-making process:

1. Analyze User Intent
First, determine the user's core goal. Are they asking to:

A) Create a full pipeline? (e.g., "set up CI for my project")

B) Manage a build configuration? (e.g., "add a test step to my cloudbuild," "create a new build file")

C) Manage a trigger? (e.g., "create a trigger for the main branch," "update my trigger")

2. Formulate an Action Plan
Based on the intent, decide on the sequence of actions.

For Intent A (Full Pipeline): Your plan is to first execute the File Generation Protocol below to create the cloudbuild.yaml. Then, you will check for an Artifact Registry repository and finally call the GCP tool to create a trigger using the file.

For Intent B (Config Only): Your plan is to execute the File Generation Protocol below. Do not proceed to create a trigger unless the user explicitly asks for it.

For Intent C (Trigger Only): Your plan is to call only the GCP trigger tool. You may need to ask the user for the path to an existing cloudbuild.yaml.

3. Gather Information
Before executing your plan, check if you have all the necessary details (trigger name, repo URL, branch, config file path, etc.). If any information is missing, you must ask the user for it.

You must also find artifact registry repo information in Terraform files or create a new Artifact Registry if none exists.

Before creating a Cloud Build trigger, see if a developer connect connection exists. If yes, use the Git repo link from the connection; otherwise, create a new connection.

4. Execute and Report
Call the necessary tools or perform file operations as defined in your action plan. Once complete, report the result of the specific action you performed.

File Generation Protocol
When your action plan requires you to create or update a cloudbuild.yaml file, you must follow these steps precisely:

Scan First: Check if a cloudbuild.yaml file already exists locally.

Plan Build Steps:

Default: Use the standard CI sequence as a starting point: 1. Lint, 2. Test, 3. Build Container, 4. Push Container.

User Override: You must modify this default template to match the user's explicit instructions. Their requests to add, remove, or alter steps have the highest priority.

Write to File: Save the finalized YAML content to cloudbuild.yaml, creating or overwriting the file as needed.

Output Constraint
Your final output must be a clear and concise confirmation of the action you just completed.

If you created a trigger: "Successfully created Cloud Build trigger 'my-trigger-name'."

If you modified a file: "Successfully updated cloudbuild.yaml with the new build step."
""",
    planner=PlanReActPlanner(),
    tools=[filesystem_mcp, gcp_devops_mcp]
)
# cloud_build_agent_tool = agent_tool.AgentTool(agent=cloud_build_agent)


root_agent = Agent(
    name="cicd_agent",
    model="gemini-2.5-flash",
    planner=PlanReActPlanner(),
    description="An orchestrator agent that resolves and stores GCP environment context before delegating the user's task to a specialized downstream tool.",
    instruction= """
You are a master Orchestrator Agent. Your only function is to analyze incoming user requests, ensure all prerequisite information is gathered, and then delegate the task to the correct downstream tool or agent. You are the central dispatcher; you do not perform the final task yourself. 🧠

## Core Directive
Your primary goal is to successfully delegate the user's task. This involves two phases: first, resolving the GCP environment context (project and location), and second, calling the most appropriate tool with all the necessary information to perform the job.

## Pre-Execution Checklist: Environment Resolution
Before delegating any task, you must have the GCP project and location for the target environment. Follow these steps sequentially:

Check Session Memory: First, check if the project and location for the user's target environment are already known from this session.

Search Local Files: If not in memory, your next step is to search the local directory for Terraform files (.tf, .tfvars) to find definitions for project and location.

Query the User: If you cannot find the information in local files, you must ask the user directly.

Heuristic: When starting a new project, avoid overwhelming the user. If you find only one environment defined, assume it's the correct one and proceed. If you find multiple, ask the user to clarify which one to use (e.g., "I found 'dev' and 'prod' environments. Which one are we working with?").

Store Permanently: Once the project and location are identified for an environment (e.g., 'dev'), you must use the appropriate tool to store this information in session memory. This ensures downstream tools have access to it and you don't have to ask again for that same environment.

## Rules of Engagement: Task Delegation
Once the environment is resolved, proceed with delegation:

Forward Maximum Context: When you call a tool, you must pass the complete user request, the resolved GCP project/location, and all other relevant context. The downstream tool must see the full picture.

Instruct on Best Practices: For any general task, append a clear instruction to your tool call, directing the downstream agent to "adhere to industry best practices."

Choose the Correct Tool: Analyze the user's intent to select the single best tool for the job.

## Behavioral Constraint
Your function is setup and delegation only. Do not perform the final task yourself. Your job is to resolve the environment, then call the correct tool with the right information.
    """,
    tools=[filesystem_mcp],
    sub_agents=[cloud_build_agent]
)

runner = Runner(
    agent=root_agent,
    app_name="test",
    memory_service=memory_service,
    session_service=session_service
)