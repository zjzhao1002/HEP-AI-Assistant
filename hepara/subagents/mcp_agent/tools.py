import json
import logging
from pathlib import Path
from typing import Any
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


logger = logging.getLogger(__name__)


def _read_mcp_servers(filename: str | Path) -> dict[str, Any]:
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
                )
            )
        )
    except (TypeError, ValueError) as exc:
        logger.warning("Skipping MCP server %r: %s", name, exc)
        return None


def create_mcp_toolset_list(filename: str | Path) -> list[McpToolset]:
    toolsets: list[McpToolset] = []
    for name, server in _read_mcp_servers(filename).items():
        toolset = _create_mcp_toolset(name, server)
        if toolset is not None:
            toolsets.append(toolset)
    return toolsets
