import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from hepara.subagents.mcp_agent.tools import create_mcp_toolset_list


class McpConfigurationTest(unittest.TestCase):
    def test_empty_mcp_configuration_disables_mcp(self):
        contents = [None, "", "   \n", "{}", '{"mcpServers": {}}']
        for content in contents:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "mcp_list.json"
                if content is not None:
                    config_path.write_text(content, encoding="utf-8")

                self.assertEqual(create_mcp_toolset_list(config_path), [])

    def test_invalid_mcp_configuration_warns_and_disables_mcp(self):
        contents = ["{not-json", "[]", '{"servers": {}}', '{"mcpServers": []}']
        for content in contents:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "mcp_list.json"
                config_path.write_text(content, encoding="utf-8")

                with self.assertLogs(
                    "hepara.subagents.mcp_agent.tools", level="WARNING"
                ) as logs:
                    toolsets = create_mcp_toolset_list(config_path)

                self.assertEqual(toolsets, [])
                self.assertIn(str(config_path), "\n".join(logs.output))

    def test_valid_stdio_servers_support_optional_args_and_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "mcp_list.json"
            config_path.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "command-only": {"command": "command-only"},
                            "with-args": {
                                "command": "runner",
                                "args": ["one", "two"],
                            },
                            "with-env": {
                                "command": "runner",
                                "env": {"TOKEN": "value"},
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            toolsets = create_mcp_toolset_list(config_path)

        self.assertEqual(len(toolsets), 3)
        parameters = [toolset._connection_params.server_params for toolset in toolsets]
        self.assertEqual(parameters[0].args, [])
        self.assertIsNone(parameters[0].env)
        self.assertEqual(parameters[1].args, ["one", "two"])
        self.assertEqual(parameters[2].env, {"TOKEN": "value"})

    def test_invalid_server_does_not_block_valid_servers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "mcp_list.json"
            config_path.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "valid": {"command": "runner"},
                            "missing-command": {"args": ["one"]},
                            "invalid-args": {"command": "runner", "args": "one"},
                            "invalid-env": {
                                "command": "runner",
                                "env": {"TOKEN": 1},
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            with self.assertLogs(
                "hepara.subagents.mcp_agent.tools", level="WARNING"
            ) as logs:
                toolsets = create_mcp_toolset_list(config_path)

        self.assertEqual(len(toolsets), 1)
        log_text = "\n".join(logs.output)
        self.assertIn("missing-command", log_text)
        self.assertIn("invalid-args", log_text)
        self.assertIn("invalid-env", log_text)

    def test_mcp_list_path_uses_override_and_expands_home(self):
        import hepara.subagents.mcp_agent.agent as mcp_agent_module

        with patch.dict(os.environ, {"MCP_LIST_PATH": "~/configs/mcp.json"}):
            self.assertEqual(
                mcp_agent_module.get_mcp_list_path(),
                Path("~/configs/mcp.json").expanduser(),
            )

        with patch.dict(os.environ, {"MCP_LIST_PATH": "configs/mcp.json"}):
            self.assertEqual(
                mcp_agent_module.get_mcp_list_path(),
                Path.cwd() / "configs/mcp.json",
            )

    def test_coordinator_registers_mcp_agent_only_with_valid_config(self):
        import hepara.agent as root_agent_module
        import hepara.subagents.mcp_agent.agent as mcp_agent_module

        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "missing.json"
            valid_path = Path(tmpdir) / "valid.json"
            valid_path.write_text(
                json.dumps(
                    {"mcpServers": {"example": {"command": "runner"}}}
                ),
                encoding="utf-8",
            )

            with patch.dict(
                os.environ, {"MCP_LIST_PATH": str(missing_path)}, clear=False
            ):
                importlib.reload(mcp_agent_module)
                importlib.reload(root_agent_module)
                names = [tool.name for tool in root_agent_module.hep_coordinator.tools]
                self.assertNotIn("mcp_agent", names)

            with patch.dict(
                os.environ, {"MCP_LIST_PATH": str(valid_path)}, clear=False
            ):
                importlib.reload(mcp_agent_module)
                importlib.reload(root_agent_module)
                names = [tool.name for tool in root_agent_module.hep_coordinator.tools]
                self.assertIn("mcp_agent", names)

            with patch.dict(
                os.environ, {"MCP_LIST_PATH": str(missing_path)}, clear=False
            ):
                importlib.reload(mcp_agent_module)
                importlib.reload(root_agent_module)


if __name__ == "__main__":
    unittest.main()
