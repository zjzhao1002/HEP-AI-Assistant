import os
from pathlib import Path
from google.adk.agents import Agent
from .tools import create_mcp_toolset_list

PROJECT_ROOT = Path(__file__).resolve().parents[3]

def get_mcp_list_path() -> Path:
    configured_path = os.getenv("MCP_LIST_PATH")
    if configured_path:
        path = Path(configured_path).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path
    return PROJECT_ROOT / "mcp_list.json"

GOOGLE_MODEL = os.getenv("GOOGLE_MODEL") 
model = GOOGLE_MODEL if GOOGLE_MODEL else "gemini-2.5-flash"

mcp_tools = create_mcp_toolset_list(get_mcp_list_path())

mcp_agent = Agent(
    model=model,
    name="mcp_agent",
    description="A MCP manager to call tools from external MCP servers.",
    tools=mcp_tools, # type: ignore
) if mcp_tools else None
