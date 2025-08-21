import datetime
import os
from zoneinfo import ZoneInfo
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, StdioConnectionParams, StdioServerParameters
from google.adk.planners import PlanReActPlanner
from google.adk.tools import agent_tool
from google.adk.tools import ToolContext
from google.adk.memory import InMemoryMemoryService
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory
from agent.prompts import PROMPTS


session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/")
# git_mcp = MCPToolset(
#                     connection_params=StdioConnectionParams(
#                         server_params = StdioServerParameters(
#                             command='npx',
#                             args=[
#                                 "-y",  # Argument for npx to auto-confirm install
#                                 "@cyanheads/git-mcp-server",
#                             ],
#                         ),
#                     ),
#                 )

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

cloud_build_agent = LlmAgent(
    name="cloud_build_agent",
    model="gemini-2.5-pro",
    description=(
        "You are an autonomous Google Cloud Build expert"
    ),
    instruction=PROMPTS["CLOUD_BUILD_PROMPT"],
    planner=PlanReActPlanner(),
    tools=[filesystem_mcp, gcp_devops_mcp, transfer_to_root_agent]
)

design_agent = LlmAgent(
    name="design_agent",
    model="gemini-2.5-pro",
    description=(
        "Designs and refines Google Cloud CI/CD pipelines through an iterative, conversational process. It gathers user requirements, proposes architectures using a standard set of GCP DevOps tools, and produces a final pipeline specification for implementation."
    ),
    instruction=PROMPTS["DESIGN_PROMPT"],
    planner=PlanReActPlanner(),
    tools=[filesystem_mcp, gcp_devops_mcp, transfer_to_root_agent],
)

root_agent = Agent(
    name="cicd_agent",
    model="gemini-2.5-pro",
    planner=PlanReActPlanner(),
    description="An orchestrator agent that resolves and stores GCP environment context before delegating the user's task to a specialized downstream tool.",
    instruction= PROMPTS["ROOT_PROMPT"],
    tools=[filesystem_mcp],
    sub_agents=[cloud_build_agent, design_agent]
)

runner = Runner(
    agent=root_agent,
    app_name="cicd-agent",
    memory_service=memory_service,
    session_service=session_service
)