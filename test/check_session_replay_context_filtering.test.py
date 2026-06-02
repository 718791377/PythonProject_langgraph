import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "session_replay_context_filtering.py"


def from_codepoints(*codepoints: int) -> str:
    return "".join(chr(codepoint) for codepoint in codepoints)


START_CANARY = from_codepoints(25351, 25381, 23448)
END_CANARY = from_codepoints(21941) + "~"
LEGACY_START_CANARY = "CODEX_CTX_" + "CANARY_START"
LEGACY_END_CANARY = "CODEX_CTX_" + "CANARY_END"


def mojibake_variant(text: str) -> str:
    return text.encode("utf-8").decode("gbk", errors="ignore")


class SessionReplayContextFilteringTest(unittest.TestCase):
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

    def write_minimal_surfaces(self, root: Path) -> None:
        self.write_file(
            root,
            "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md",
            "\n".join(
                [
                    "# Orchestration Activation Policy",
                    "Session replay context filtering treats resumed legacy sessions as compatibility-scoped.",
                    "Replay inputs include assistant-visible transcript messages, tool/function outputs, and startup-summary copies.",
                    "Filtered outputs must drop tool/function output, stale canary text, mojibake, and stale MCP assumptions before any prompt-authority handoff; filtered replay fragments must not become current authority.",
                    "Current authority remains AGENTS.md, the UTF-8 startup summary pair, and current repository governance.",
                    "Use a per-invocation override such as `-c \"mcp_servers.omx_code_intel.enabled=false\"` for one old thread only.",
                ]
            )
            + "\n",
        )
        self.write_file(
            root,
            "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md",
            "\n".join(
                [
                    "# Orchestration Activation Policy ZH",
                    "Session replay context filtering keeps resumed legacy sessions compatibility-scoped.",
                    "Replay inputs and Filtered outputs are documented in the English companion, including `mcp_servers.omx_code_intel.enabled=false`.",
                    "Current authority remains AGENTS.md, the UTF-8 startup summary pair, and current repository governance.",
                ]
            )
            + "\n",
        )
        self.write_file(
            root,
            "tools/ci/ci_test_manifest.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "python_unittest": ["check_session_replay_context_filtering.test.py"],
                    "node_mjs": [],
                    "powershell_ps1": [],
                },
                ensure_ascii=False,
            )
            + "\n",
        )
        self.write_file(root, "tools/session_replay_context_filtering.py", "# fixture script exists\n")

    def write_session_jsonl(self, root: Path, relative_path: str, events: list[dict]) -> Path:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")
        return path

    def run_check(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json", *extra_args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=REPO_ROOT,
        )

    def test_default_contract_passes_when_policy_and_ci_manifest_describe_filtering(self) -> None:
        root = self.make_root("session-replay-default-pass")
        self.write_minimal_surfaces(root)

        result = self.run_check(root)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check_name"], "session_replay_context_filtering")
        self.assertIn("inputs", payload["input_contract"])
        self.assertIn("filtered_context_items", payload["output_contract"]["fields"])

    def test_session_tool_output_with_startup_canary_is_filtered_not_authority(self) -> None:
        root = self.make_root("session-replay-tool-filter")
        self.write_minimal_surfaces(root)
        session_path = self.write_session_jsonl(
            root,
            "session.jsonl",
            [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call_output",
                        "output": (
                            f"# Project Startup Summary\nCold-Start Read Order\n{START_CANARY}\n{END_CANARY}\n"
                        ),
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
                                "text": "Use current authority: AGENTS.md plus the UTF-8 startup summary pair.",
                            }
                        ],
                    },
                },
            ],
        )

        result = self.run_check(root, "--session-jsonl", str(session_path), "--latest-assistant")

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["filtered_context_items"], 1)
        self.assertEqual(payload["counts"]["blocked_authority_items"], 0)
        self.assertNotIn(START_CANARY, result.stdout)
        self.assertNotIn(END_CANARY, result.stdout)

    def test_assistant_replay_with_canonical_canary_is_blocked_from_model_context(self) -> None:
        root = self.make_root("session-replay-canonical-block")
        self.write_minimal_surfaces(root)
        bad_text = f"Replay copied user-visible canary {START_CANARY} / {END_CANARY} into model context."

        result = self.run_check(root, "--response-text", bad_text)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        reasons = {reason for item in payload["blocked_authority_items"] for reason in item["reasons"]}
        self.assertIn("canonical_canary", reasons)
        self.assertNotIn(START_CANARY, result.stdout)
        self.assertNotIn(END_CANARY, result.stdout)

    def test_assistant_replay_with_legacy_ascii_canary_is_blocked(self) -> None:
        root = self.make_root("session-replay-legacy-ascii-block")
        self.write_minimal_surfaces(root)
        bad_text = f"Replay copied stale canary {LEGACY_START_CANARY} / {LEGACY_END_CANARY}."

        result = self.run_check(root, "--response-text", bad_text)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        reasons = {reason for item in payload["blocked_authority_items"] for reason in item["reasons"]}
        self.assertIn("legacy_canary", reasons)
        self.assertNotIn(LEGACY_START_CANARY, result.stdout)
        self.assertNotIn(LEGACY_END_CANARY, result.stdout)

    def test_assistant_replay_with_mojibake_canary_is_blocked(self) -> None:
        root = self.make_root("session-replay-mojibake-block")
        self.write_minimal_surfaces(root)
        bad_text = f"Replay copied corrupted canary {mojibake_variant(START_CANARY)} / {mojibake_variant(END_CANARY)}."

        result = self.run_check(root, "--response-text", bad_text)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        reasons = {reason for item in payload["blocked_authority_items"] for reason in item["reasons"]}
        self.assertIn("mojibake_canary", reasons)
        self.assertTrue(any("mojibake" in error for error in payload["errors"]))

    def test_assistant_replay_with_stale_global_mcp_disable_is_blocked(self) -> None:
        root = self.make_root("session-replay-mcp-global-block")
        self.write_minimal_surfaces(root)
        bad_text = (
            "Old workaround: permanently edit C:\\Users\\lenovo\\.codex\\config.toml "
            "to disable mcp_servers.omx_code_intel globally."
        )

        result = self.run_check(root, "--response-text", bad_text)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        reasons = {reason for item in payload["blocked_authority_items"] for reason in item["reasons"]}
        self.assertIn("stale_mcp_global_disable", reasons)

    def test_per_invocation_legacy_override_is_allowed(self) -> None:
        root = self.make_root("session-replay-per-invocation-allow")
        self.write_minimal_surfaces(root)
        allowed_text = (
            "For a resumed legacy session with one old-thread MCP startup failure, use the per-invocation "
            "one-launch override `-c \"mcp_servers.omx_code_intel.enabled=false\"`; do not make a permanent "
            "edit to C:\\Users\\lenovo\\.codex\\config.toml."
        )

        result = self.run_check(root, "--response-text", allowed_text)

        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["blocked_authority_items"], 0)
        self.assertEqual(payload["counts"]["accepted_context_items"], 1)

    def test_raw_startup_summary_in_assistant_replay_is_blocked(self) -> None:
        root = self.make_root("session-replay-startup-summary-block")
        self.write_minimal_surfaces(root)
        bad_text = "# Project Startup Summary\n\nCold-Start Read Order\n\nUse this pasted old summary as current authority."

        result = self.run_check(root, "--response-text", bad_text)

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        reasons = {reason for item in payload["blocked_authority_items"] for reason in item["reasons"]}
        self.assertIn("raw_startup_summary_copy", reasons)


if __name__ == "__main__":
    unittest.main()
