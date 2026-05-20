from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_remote_publication_approval_policy.py"

spec = importlib.util.spec_from_file_location("check_remote_publication_approval_policy", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def write_valid_registry(root: Path) -> None:
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
    (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "rules": [
                    {
                        "id": module.REGISTRY_RULE_ID,
                        "prompt_reminders": [
                            "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md"
                        ],
                        "script_controls": ["tools/check_remote_publication_approval_policy.py"],
                        "guard_steps": [module.GUARD_STEP],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class RemotePublicationApprovalPolicyCheckerTests(unittest.TestCase):
    def test_repository_surfaces_pass(self) -> None:
        payload = module.run_check(ROOT)
        self.assertTrue(payload["ok"], payload["errors"])

    def test_missing_required_surface_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = module.run_check(Path(temp_dir))
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Missing required remote publication approval surface" in e for e in payload["errors"]))

    def test_missing_generic_continue_guard_fails(self) -> None:
        blocked = {
            "Generic continuation such as `continue`, `go on`, `proceed`, or a localized equivalent is not remote publication approval",
            "Generic `continue` / `go on` / `proceed` wording, including localized equivalents, is not enough",
            "泛化的 `continue` / `继续` 不足以授权远端发布",
            "泛化的 `continue`、`继续`、`go on` 或 `proceed` 不是远端发布批准",
            "Generic continuation language such as `continue`, `go on`, `proceed`, or a localized equivalent SHALL NOT be treated as remote publication approval",
            "Generic continuation after local integration",
            "do not treat generic continuation as approval",
            "不得把泛化的继续指令当作批准",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(s for s in snippets if s not in blocked), encoding="utf-8")
            write_valid_registry(root)
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("Generic continuation" in e or "泛化" in e for e in payload["errors"]), payload["errors"])


    def test_missing_single_approval_green_path_fails(self) -> None:
        blocked = {
            "single approval for the normal green-path remote publication flow",
            "????????????????????",
            "normal green-path remote publication sequence as one approval",
            "GitLab publication branch push/update",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(s for s in snippets if s not in blocked), encoding="utf-8")
            write_valid_registry(root)
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("green-path" in e or "?????" in e for e in payload["errors"]), payload["errors"]
        )

    def test_missing_scoped_sandbox_escalation_fails(self) -> None:
        blocked = {
            "request one scoped escalation",
            "rather than asking once per command",
            "instead of asking once per command",
            "?????????",
            "??????????",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(s for s in snippets if s not in blocked), encoding="utf-8")
            write_valid_registry(root)
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("scoped escalation" in e or "?????" in e for e in payload["errors"]), payload["errors"]
        )

    def test_missing_registry_rule_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel, snippets in module.REQUIRED_SNIPPETS.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(snippets), encoding="utf-8")
            (root / "tools").mkdir(exist_ok=True)
            (root / "tools" / "run_openspec_guard.py").write_text(module.GUARD_STEP, encoding="utf-8")
            (root / "tools" / "safety_rule_script_backing_registry.json").write_text(
                json.dumps({"schema_version": 1, "rules": []}), encoding="utf-8"
            )
            payload = module.run_check(root)
        self.assertFalse(payload["ok"])
        self.assertTrue(any(module.REGISTRY_RULE_ID in e for e in payload["errors"]), payload["errors"])


if __name__ == "__main__":
    unittest.main()
