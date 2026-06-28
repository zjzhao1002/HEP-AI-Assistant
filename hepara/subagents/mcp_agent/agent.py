import os
from pathlib import Path
from typing import List
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools import FunctionTool
from .tools import create_subagents, list_mcp_servers
from .prompt import MCP_AGENT_PROMPT

MCP_PATH = os.getenv("MCP_PATH")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")
model = GOOGLE_MODEL if GOOGLE_MODEL else "gemini-2.5-flash"

def create_agent_tools() -> List[AgentTool] | None:
    agent_tools: List[AgentTool] = []
    subagents = create_subagents()
    if subagents:
        for subagent in subagents:
            agent_tools.append(AgentTool(subagent))
        return agent_tools
    else:
        return None

list_mcp_servers_tool = FunctionTool(func=list_mcp_servers)
all_tools = [list_mcp_servers_tool]
agent_tools = create_agent_tools()
if agent_tools:
    all_tools += agent_tools

mcp_agent = Agent(
    model=model,
    name="mcp_agent",
    description="A MCP manager to call tools from external MCP servers.",
    tools=all_tools, # type: ignore
    instruction=MCP_AGENT_PROMPT
) if agent_tools else None
