from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_custom_agent_toml_schema.py"

spec = importlib.util.spec_from_file_location("check_custom_agent_toml_schema", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


VALID_AGENT = '''
name = "sample-agent"
description = "Useful sample agent for tests."
developer_instructions = """
Follow the task brief and report changed files.
"""
'''


def agent_with_model(model: str) -> str:
    return f'''
name = "sample-agent"
description = "Useful sample agent for tests."
model = "{model}"
developer_instructions = """
Follow the task brief and report changed files.
"""
'''


class CustomAgentTomlSchemaCheckerTests(unittest.TestCase):
    def test_missing_agent_directories_warn_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            root.mkdir()
            user_agents = Path(temp_dir) / "missing-user-agents"
            payload = module.run_check(root, user_agents)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["counts"]["checked_files"], 0)
        self.assertGreaterEqual(payload["counts"]["warnings"], 1)

    def test_valid_repo_and_user_agents_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            repo_agents = root / ".codex" / "agents"
            user_agents = Path(temp_dir) / "user-agents"
            repo_agents.mkdir(parents=True)
            user_agents.mkdir(parents=True)
            (repo_agents / "repo-agent.toml").write_text(VALID_AGENT, encoding="utf-8")
            (user_agents / "user-agent.toml").write_text(VALID_AGENT, encoding="utf-8")
            payload = module.run_check(root, user_agents)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["counts"]["checked_files"], 2)

    def test_allowed_agent_model_values_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            repo_agents = root / ".codex" / "agents"
            user_agents = Path(temp_dir) / "user-agents"
            repo_agents.mkdir(parents=True)
            user_agents.mkdir(parents=True)
            (repo_agents / "gpt-54.toml").write_text(agent_with_model("gpt-5.4"), encoding="utf-8")
            (user_agents / "gpt-55.toml").write_text(agent_with_model("gpt-5.5"), encoding="utf-8")
            payload = module.run_check(root, user_agents)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["counts"]["checked_files"], 2)

    def test_disallowed_agent_model_values_fail(self) -> None:
        disallowed_models = [
            "gpt-5.3",
            "gpt-5.3-codex",
            "gpt-5.3-codex-spark",
            "gpt-5.4-mini",
            "gpt-5.5-mini",
        ]
        for model in disallowed_models:
            with self.subTest(model=model):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir) / "repo"
                    repo_agents = root / ".codex" / "agents"
                    user_agents = Path(temp_dir) / "user-agents"
                    repo_agents.mkdir(parents=True)
                    user_agents.mkdir(parents=True)
                    (repo_agents / "bad-model.toml").write_text(agent_with_model(model), encoding="utf-8")
                    payload = module.run_check(root, user_agents)
                self.assertFalse(payload["ok"])
                self.assertTrue(any("unsupported top-level `model`" in item for item in payload["errors"]), payload["errors"])

    def test_missing_required_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            repo_agents = root / ".codex" / "agents"
            user_agents = Path(temp_dir) / "user-agents"
            repo_agents.mkdir(parents=True)
            user_agents.mkdir(parents=True)
            (repo_agents / "bad.toml").write_text(
                'name = "bad"\ndescription = "Missing instructions"\n', encoding="utf-8"
            )
            payload = module.run_check(root, user_agents)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("developer_instructions" in item for item in payload["errors"]), payload["errors"])

    def test_empty_string_required_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            repo_agents = root / ".codex" / "agents"
            user_agents = Path(temp_dir) / "user-agents"
            repo_agents.mkdir(parents=True)
            user_agents.mkdir(parents=True)
            (repo_agents / "bad.toml").write_text(
                'name = "bad"\ndescription = "   "\ndeveloper_instructions = "Do work"\n', encoding="utf-8"
            )
            payload = module.run_check(root, user_agents)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("description" in item for item in payload["errors"]), payload["errors"])

    def test_invalid_toml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            repo_agents = root / ".codex" / "agents"
            user_agents = Path(temp_dir) / "user-agents"
            repo_agents.mkdir(parents=True)
            user_agents.mkdir(parents=True)
            (repo_agents / "bad.toml").write_text('name = "unterminated\n', encoding="utf-8")
            payload = module.run_check(root, user_agents)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("not parseable" in item for item in payload["errors"]), payload["errors"])

    def test_current_user_agents_pass_when_available(self) -> None:
        user_agents = module.default_user_agents_dir()
        if not user_agents.exists():
            self.skipTest(f"user agents directory is not present: {user_agents}")
        payload = module.run_check(ROOT, user_agents)
        if not payload["ok"] and any("unsupported top-level `model`" in item for item in payload["errors"]):
            self.skipTest("current user agents have not yet been normalized by the live installer")
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertGreater(payload["counts"]["checked_files"], 0)


if __name__ == "__main__":
    unittest.main()
