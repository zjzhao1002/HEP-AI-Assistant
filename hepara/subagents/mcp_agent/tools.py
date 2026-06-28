import os
import json
import logging
from typing import Any, Dict, List
from pathlib import Path
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.skills import load_skill_from_dir, Skill
from google.adk.tools.skill_toolset import SkillToolset
from mcp import StdioServerParameters

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MCP_PATH = os.getenv("MCP_PATH")
SKILL_PATH = os.getenv("SKILL_PATH")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")
model = GOOGLE_MODEL if GOOGLE_MODEL else "gemini-2.5-flash"

def _get_mcp_path() -> Path:
    configured_path = MCP_PATH
    if configured_path:
        path = Path(configured_path).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path
    return PROJECT_ROOT / "mcp_config.json"

def _read_mcp_servers(filename: str | Path) -> Dict[str, Any]:
    path = Path(filename)
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.info("MCP configuration %s does not exist; MCP is disabled.", path)
        return {}
    except OSError as exc:
        logger.warning("Could not read MCP configuration %s: %s", path, exc)
        return {}

    if not content.strip():
        logger.info("MCP configuration %s is empty; MCP is disabled.", path)
        return {}

    try:
        config = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in MCP configuration %s: %s", path, exc)
        return {}

    if config == {}:
        logger.info("MCP configuration %s is empty; MCP is disabled.", path)
        return {}
    if not isinstance(config, dict):
        logger.warning("MCP configuration %s must be a JSON object.", path)
        return {}

    servers = config.get("mcpServers")
    if servers is None:
        logger.warning(
            "MCP configuration %s must contain an 'mcpServers' object.", path
        )
        return {}
    if not isinstance(servers, dict):
        logger.warning("'mcpServers' in %s must be a JSON object.", path)
        return {}
    if not servers:
        logger.info("MCP configuration %s has no servers; MCP is disabled.", path)
        return {}

    return servers

def _create_mcp_toolset(name: str, server: Any) -> McpToolset | None:
    if not name.strip():
        logger.warning("Skipping MCP server with an empty name.")
        return None
    if not isinstance(server, dict):
        logger.warning("Skipping MCP server %r: configuration must be an object.", name)
        return None

    command = server.get("command")
    if not isinstance(command, str) or not command.strip():
        logger.warning("Skipping MCP server %r: 'command' must be a non-empty string.", name)
        return None

    args = server.get("args", [])
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        logger.warning("Skipping MCP server %r: 'args' must be an array of strings.", name)
        return None

    env = server.get("env")
    if env is not None and (
        not isinstance(env, dict)
        or not all(isinstance(key, str) and isinstance(value, str) for key, value in env.items())
    ):
        logger.warning("Skipping MCP server %r: 'env' must map strings to strings.", name)
        return None

    try:
        return McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=command,
                    args=args,
                    env=env,
                ),
                timeout=10
            )
        )
    except (TypeError, ValueError) as exc:
        logger.warning("Skipping MCP server %r: %s", name, exc)
        return None

def _get_skill(path: str | Path, skill_name: str) -> Skill | None:
    skill_path = Path(path) / skill_name
    try:
        skill = load_skill_from_dir(skill_path)
        return skill
    except (FileNotFoundError, ValueError) as exc:
        logger.warning("Skipping skill: %r: %s", skill_name, exc)
        return None

def _create_subagent(name: str, mcp_toolset: McpToolset, skill: Skill | None) -> Agent:
    if skill is not None:
        skill_toolset = SkillToolset(skills=[skill])
        subagent = Agent(
            model = model,
            name = name,
            description=skill.description,
            instruction=skill.instructions,
            tools = [mcp_toolset, skill_toolset]
        )
        return subagent
    else:
        subagent = Agent(
            model=model,
            name=name,
            description=f"A subagent to use {name} MCP server to response user request.",
            instruction=f"You task is to use tools from {name} MCP server to response user request.",
            tools=[mcp_toolset]
        )
        return subagent

def create_subagents() -> List[Agent] | None:
    path = _get_mcp_path()
    servers = _read_mcp_servers(path)
    if not servers:
        return None

    subagents: List[Agent] = []
    for name, server in servers.items():
        toolset = _create_mcp_toolset(name, server)
        if toolset is None:
            continue
        if SKILL_PATH:
            skill = _get_skill(SKILL_PATH, name)
            subagent = _create_subagent(name, toolset, skill)
        else:
            subagent = _create_subagent(name, toolset, None)
        subagents.append(subagent)

    return subagents

def list_mcp_servers() -> str:
    valid_subagents = create_subagents()
    if valid_subagents is None:
        return "No available MCP servers."

    server_names = ""
    for subagent in valid_subagents:
        name = subagent.name
        server_names += f"{name}\n"
    return server_names
