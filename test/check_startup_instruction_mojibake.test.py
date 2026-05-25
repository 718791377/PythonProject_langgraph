import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_startup_instruction_mojibake.py"

START_CANARY = "".join(chr(codepoint) for codepoint in (25351, 25381, 23448))
END_CANARY = chr(21941) + "~"

AUTHORITY_SURFACES = (
    "AGENTS.md",
    "docs_bilingual/project_startup_summary.md",
    "docs_bilingual/project_startup_summary.zh-CN.md",
    "docs_bilingual/governance/openspec_official_workflow_policy.md",
    "docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md",
    "docs_bilingual/governance/langgraph_user_level_runtime_policy.md",
    "docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md",
    "docs_bilingual/governance/user_level_launcher_payload_policy.md",
    "docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md",
    "docs_bilingual/governance/codex_user_level_mcp_scope_policy.md",
    "docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md",
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md",
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md",
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md",
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md",
)


def mojibake_variant(text: str) -> str:
    return text.encode("utf-8").decode("gbk", errors="ignore")


class StartupInstructionMojibakeCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_clean_surfaces(self, root: Path) -> None:
        for relative_path in AUTHORITY_SURFACES:
            if relative_path.endswith("project_startup_summary.md") or relative_path.endswith(
                "project_startup_summary.zh-CN.md"
            ):
                content = (
                    "# Startup\n\n"
                    f"Context-retention canary: start `{START_CANARY}` and end `{END_CANARY}`.\n"
                    "Recovery action: reread AGENTS.md before continuing.\n"
                )
            elif relative_path == "AGENTS.md":
                content = "# Project Instructions\n\nRead startup summaries as UTF-8.\n"
            else:
                content = "# Governance\n\nThis authority surface must remain UTF-8 clean.\n"
            self.write_file(root, relative_path, content)

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_check_args(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json", *extra_args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def write_session_jsonl(self, root: Path, relative_path: str, events: list[dict]) -> Path:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")
        return path

    def test_passes_clean_startup_instruction_surfaces(self) -> None:
        root = self.make_root("startup-mojibake-pass")
        self.write_clean_surfaces(root)

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)

    def test_fails_when_agents_contains_legacy_encoding_variant(self) -> None:
        root = self.make_root("startup-mojibake-agents")
        self.write_clean_surfaces(root)
        self.write_file(root, "AGENTS.md", f"Runtime rendered corrupted text: {mojibake_variant('乱码')}\n")

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("AGENTS.md contains mojibake" in error for error in payload["errors"]))

    def test_fails_when_governance_surface_contains_question_mark_runs(self) -> None:
        root = self.make_root("startup-mojibake-question-runs")
        self.write_clean_surfaces(root)
        self.write_file(
            root,
            "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md",
            "Fan-out and write-heavy parallel execution ???? leader-owned fan-in.\n",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("orchestration_activation_policy.zh-CN.md" in error for error in payload["errors"]))

    def test_fails_when_startup_summary_contains_replacement_character(self) -> None:
        root = self.make_root("startup-mojibake-replacement-char")
        self.write_clean_surfaces(root)
        self.write_file(
            root,
            "docs_bilingual/project_startup_summary.zh-CN.md",
            f"# Startup\n\nContext-retention canary: `{START_CANARY}` / `{END_CANARY}`.\nBad text: \ufffd\n",
        )

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("project_startup_summary.zh-CN.md" in error for error in payload["errors"]))

    def test_response_text_mode_fails_when_canary_is_mojibake(self) -> None:
        root = self.make_root("startup-mojibake-response")
        self.write_clean_surfaces(root)

        result = self.run_check_args(
            root,
            "--response-text",
            f"{mojibake_variant(START_CANARY)} visible response {mojibake_variant(END_CANARY)}",
        )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["response_diagnostics"][0]["status"], "mojibake_canary")
        self.assertNotIn(mojibake_variant(START_CANARY), result.stdout)
        self.assertNotIn(mojibake_variant(END_CANARY), result.stdout)

    def test_session_mode_filters_tool_output_and_checks_latest_assistant_response_mojibake(self) -> None:
        root = self.make_root("startup-mojibake-session")
        self.write_clean_surfaces(root)
        session_path = self.write_session_jsonl(
            root,
            "session.jsonl",
            [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call_output",
                        "output": f"tool output copied clean startup summary {START_CANARY} / {END_CANARY}",
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "output_text",
                                "text": f"{mojibake_variant(START_CANARY)} final visible answer {mojibake_variant(END_CANARY)}",
                            }
                        ],
                    },
                },
            ],
        )

        result = self.run_check_args(root, "--session-jsonl", str(session_path), "--latest-assistant")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["response_diagnostics"][0]["status"], "mojibake_canary")

    def test_session_turn_id_tracks_task_range_without_response_item_turn_ids(self) -> None:
        root = self.make_root("startup-mojibake-turn-id")
        self.write_clean_surfaces(root)
        session_path = self.write_session_jsonl(
            root,
            "session.jsonl",
            [
                {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-a"}},
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": f"{START_CANARY} first turn {END_CANARY}"}],
                    },
                },
                {"type": "event_msg", "payload": {"type": "task_complete", "turn_id": "turn-a"}},
                {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "turn-b"}},
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "output_text",
                                "text": f"{mojibake_variant(START_CANARY)} second turn {mojibake_variant(END_CANARY)}",
                            }
                        ],
                    },
                },
            ],
        )

        result = self.run_check_args(root, "--session-jsonl", str(session_path), "--turn-id", "turn-a", "--latest-assistant")

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["response_diagnostics"][0]["status"], "canonical_present")


if __name__ == "__main__":
    unittest.main()
