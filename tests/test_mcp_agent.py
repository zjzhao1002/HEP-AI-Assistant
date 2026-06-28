import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import hepara.subagents.mcp_agent.tools as mcp_tools_module


class McpConfigurationTest(unittest.TestCase):
    def _write_config(self, tmpdir: str, content: str | None) -> Path:
        config_path = Path(tmpdir) / "mcp_config.json"
        if content is not None:
            config_path.write_text(content, encoding="utf-8")
        return config_path

    def _reload_tools_with_path(self, config_path: Path):
        with patch.dict(os.environ, {"MCP_PATH": str(config_path)}, clear=False):
            return importlib.reload(mcp_tools_module)

    def test_empty_mcp_configuration_disables_mcp(self):
        contents = [None, "", "   \n", "{}", '{"mcpServers": {}}']
        for content in contents:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmpdir:
                config_path = self._write_config(tmpdir, content)
                tools_module = self._reload_tools_with_path(config_path)

                self.assertIsNone(tools_module.create_subagents())
                self.assertEqual(
                    tools_module.list_mcp_servers(), "No available MCP servers."
                )

    def test_invalid_mcp_configuration_warns_and_disables_mcp(self):
        contents = ["{not-json", "[]", '{"servers": {}}', '{"mcpServers": []}']
        for content in contents:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmpdir:
                config_path = self._write_config(tmpdir, content)
                tools_module = self._reload_tools_with_path(config_path)

                with self.assertLogs(
                    "hepara.subagents.mcp_agent.tools", level="WARNING"
                ) as logs:
                    subagents = tools_module.create_subagents()

                self.assertIsNone(subagents)
                self.assertIn(str(config_path), "\n".join(logs.output))

    def test_valid_stdio_servers_support_optional_args_and_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self._write_config(
                tmpdir,
                json.dumps(
                    {
                        "mcpServers": {
                            "command_only": {"command": "command-only"},
                            "with_args": {
                                "command": "runner",
                                "args": ["one", "two"],
                            },
                            "with_env": {
                                "command": "runner",
                                "env": {"TOKEN": "value"},
                            },
                        }
                    }
                ),
            )
            tools_module = self._reload_tools_with_path(config_path)

            subagents = tools_module.create_subagents()

        self.assertIsNotNone(subagents)
        self.assertEqual(len(subagents), 3)
        parameters = [
            subagent.tools[0]._connection_params.server_params
            for subagent in subagents
        ]
        self.assertEqual(parameters[0].args, [])
        self.assertIsNone(parameters[0].env)
        self.assertEqual(parameters[1].args, ["one", "two"])
        self.assertEqual(parameters[2].env, {"TOKEN": "value"})

    def test_invalid_server_does_not_block_valid_servers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self._write_config(
                tmpdir,
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
            )
            tools_module = self._reload_tools_with_path(config_path)

            with self.assertLogs(
                "hepara.subagents.mcp_agent.tools", level="WARNING"
            ) as logs:
                subagents = tools_module.create_subagents()

        self.assertIsNotNone(subagents)
        self.assertEqual(len(subagents), 1)
        self.assertEqual(subagents[0].name, "valid")
        log_text = "\n".join(logs.output)
        self.assertIn("missing-command", log_text)
        self.assertIn("invalid-args", log_text)
        self.assertIn("invalid-env", log_text)

    def test_list_mcp_servers_only_reports_valid_servers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = self._write_config(
                tmpdir,
                json.dumps(
                    {
                        "mcpServers": {
                            "valid": {"command": "runner"},
                            "missing-command": {"args": ["one"]},
                            "invalid-env": {
                                "command": "runner",
                                "env": {"TOKEN": 1},
                            },
                        }
                    }
                ),
            )
            tools_module = self._reload_tools_with_path(config_path)

            with self.assertLogs(
                "hepara.subagents.mcp_agent.tools", level="WARNING"
            ):
                servers = tools_module.list_mcp_servers()

        self.assertEqual(servers, "valid\n")

    def test_mcp_path_uses_override_and_expands_home(self):
        with patch.dict(os.environ, {"MCP_PATH": "~/configs/mcp.json"}):
            tools_module = importlib.reload(mcp_tools_module)
            self.assertEqual(
                tools_module._get_mcp_path(),
                Path("~/configs/mcp.json").expanduser(),
            )

        with patch.dict(os.environ, {"MCP_PATH": "configs/mcp.json"}):
            tools_module = importlib.reload(mcp_tools_module)
            self.assertEqual(
                tools_module._get_mcp_path(),
                Path.cwd() / "configs/mcp.json",
            )

    def test_coordinator_registers_mcp_agent_only_with_valid_config(self):
        import hepara.agent as root_agent_module
        import hepara.subagents.mcp_agent.agent as mcp_agent_module

        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "missing.json"
            valid_path = self._write_config(
                tmpdir,
                json.dumps({"mcpServers": {"example": {"command": "runner"}}}),
            )

            with patch.dict(os.environ, {"MCP_PATH": str(missing_path)}, clear=False):
                importlib.reload(mcp_tools_module)
                importlib.reload(mcp_agent_module)
                importlib.reload(root_agent_module)
                names = [tool.name for tool in root_agent_module.hep_coordinator.tools]
                self.assertNotIn("mcp_agent", names)

            with patch.dict(os.environ, {"MCP_PATH": str(valid_path)}, clear=False):
                importlib.reload(mcp_tools_module)
                importlib.reload(mcp_agent_module)
                importlib.reload(root_agent_module)
                names = [tool.name for tool in root_agent_module.hep_coordinator.tools]
                self.assertIn("mcp_agent", names)

            with patch.dict(os.environ, {"MCP_PATH": str(missing_path)}, clear=False):
                importlib.reload(mcp_tools_module)
                importlib.reload(mcp_agent_module)
                importlib.reload(root_agent_module)

    def test_list_mcp_servers_tool_uses_configured_path_without_model_argument(self):
        import hepara.subagents.mcp_agent.agent as mcp_agent_module

        declaration = mcp_agent_module.list_mcp_servers_tool._get_declaration()

        self.assertIsNone(declaration.parameters_json_schema)


if __name__ == "__main__":
    unittest.main()
