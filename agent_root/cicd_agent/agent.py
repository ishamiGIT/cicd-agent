import datetime
import os
import logging
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, StdioConnectionParams, StdioServerParameters
from google.adk.planners import PlanReActPlanner
from google.adk.tools import agent_tool
from google.adk.tools import ToolContext
from google.adk.memory import InMemoryMemoryService
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from cicd_agent.prompts import *
from vertexai import rag
import vertexai

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
MODEL = "gemini-2.5-pro"
RAG_PATTERNS_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/5476377146882523136"
RAG_KNOWLEDGE_CORPUS_ID = "projects/haroonc-exp/locations/us-east4/ragCorpora/2017612633061982208"
TARGET_FOLDER_PATH = os.environ.get('WORKING_DIR', '/data')
vertexai.init(project="haroonc-exp", location="us-east4")
# git_mcp = MCPToolset(
#                     connection_params=StdioConnectionParams(
#                         server_params = StdioServerParameters(
#                             command='npx',
#                             args=[
#                                 "-y",  # Argument for npx to auto-confirm install
#                                 "@cyanheads/git-mcp-server",
#                             ],
#                         ),
#                         timeout = 15.0,
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
                        timeout = 15.0,
                    ),
                )

gcp_devops_mcp = MCPToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url = os.environ.get('DEVOPS_MCP_URL', 'http://host.docker.internal:9000/mcp'),
                    ),
                )

def transfer_to_root_agent(tool_context: ToolContext) -> str:
    """Transfers control to root agent"""
    tool_context.actions.transfer_to_agent = "cicd_agent"
    return "Transferring to the cicd_agent..."

def transfer_to_implementation_agent(plan: str, tool_context: ToolContext) -> str:
    """Transfers control to implementation agent"""
    tool_context.actions.transfer_to_agent = "implementation_agent"
    user_plan_key = "user:plan"
    tool_context.state[user_plan_key] = plan
    return "Transferring to the implementation_agent..."

def query_knowledge(query: str):
    """Queries the knowledge base for information on how to build and manage CI/CD pipelines.

    Args:
        query: The query to search for in the knowledge base.

    Returns:
        The response from the retrieval query.
    """
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=RAG_KNOWLEDGE_CORPUS_ID,
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    knowledge = ""

    for i, context in enumerate(response.contexts.contexts):
        knowledge += f'knowledge {i}: {context.text} \n\n'

    return knowledge

def search_common_cicd_patterns(keywords: str):
    """Searches for common CI/CD patterns and best practices.

    Args:
        keywords: The keywords to search for in the CI/CD patterns.

    Returns:
        The response from the retrieval query.
    """
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=2,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=RAG_PATTERNS_CORPUS_ID,
            )
        ],
        text=keywords,
        rag_retrieval_config=rag_retrieval_config,
    )
    patterns = ""

    for i, context in enumerate(response.contexts.contexts):
        patterns += f'Pattern {i}: {context.text} \n\n'

    return patterns


implementation_agent = LlmAgent(
    name="implementation_agent",
    model= MODEL,
    description=(
        """
        Executes concrete plans and direct commands to provision and manage GCP resources. 
        Use this agent for any task that involves doing or making, such as applying a YAML plan or handling a single command like "create an artifact registry repo".
        It does not design or create new plans.
        """
    ),
    instruction=PROMPTS[IMPLEMNETATION_PROMPT],
    planner=PlanReActPlanner(),
    tools=[filesystem_mcp, gcp_devops_mcp, transfer_to_root_agent, query_knowledge]
)

design_agent = LlmAgent(
    name="design_agent",
    model=MODEL,
    description=(
        """
        Designs and refines Google Cloud CI/CD pipelines through an iterative, conversational process.
        It gathers user requirements, proposes architectures using a standard set of GCP DevOps tools,
        and produces a final pipeline specification for implementation.
        """
    ),
    instruction=PROMPTS[DESIGN_PROMPT],
    planner=PlanReActPlanner(),
    tools=[filesystem_mcp, transfer_to_implementation_agent, transfer_to_root_agent, search_common_cicd_patterns],
)

root_agent = Agent(
    name="cicd_agent",
    model=MODEL,
    planner=PlanReActPlanner(),
    description="""
    An orchestrator agent that resolves and stores GCP environment context before delegating the user's task
    to a specialized downstream tool.
    """,
    instruction= PROMPTS[ROOT_PROMPT],
    tools=[filesystem_mcp],
    sub_agents=[implementation_agent, design_agent]
)

# root_agent = Agent(
#     name="test_cicd_agent",
#     model=MODEL,
#     planner=PlanReActPlanner(),
#     description="""
#     Answers user queries based on tools availbale.
#     """,
#     instruction= "Answers user queries based on tools availbale.",
#     tools=[filesystem_mcp, search_common_cicd_patterns, query_knowledge]
#     # sub_agents=[implementation_agent, design_agent]
# )

runner = Runner(
    agent=root_agent,
    app_name="cicd-agent",
    memory_service=memory_service,
    session_service=session_service
)