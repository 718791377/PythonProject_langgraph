#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "local_mirrored_ci_gate"

LOCAL_GATE_PATH = Path("tools/ci/local_gate.ps1")
LOCAL_GATE_IMPL_PATH = Path("tools/ci/local_gate.py")
LOCAL_MR_REVIEW_PATH = Path("tools/ci/local_mr_review.ps1")
PYTHON_TEST_RUNNER_PATH = Path("tools/ci/run_python_tests.py")
NODE_TEST_RUNNER_PATH = Path("tools/ci/run_node_mjs_tests.mjs")
POWERSHELL_TEST_RUNNER_PATH = Path("tools/ci/run_powershell_ps1_tests.ps1")
CI_TEST_MANIFEST_PATH = Path("tools/ci/ci_test_manifest.json")
RUN_OPENSPEC_GUARD_PATH = Path("tools/run_openspec_guard.py")
PRECOMMIT_UPDATE_ARCHIVE_PATH = Path("tools/check_precommit_update_archive.py")
SAFETY_RULE_REGISTRY_PATH = Path("tools/safety_rule_script_backing_registry.json")
GITLAB_CI_PATH = Path(".gitlab-ci.yml")
GITHUB_CI_PATH = Path(".github/workflows/openspec-guard.yml")

MANIFEST_SECTIONS = ("python_unittest", "node_mjs", "powershell_ps1")
REQUIRED_MANIFEST_TESTS = (
    "check_local_mirrored_ci_gate.test.py",
    "parallel_plan_checker_ci_integration.test.py",
)
REQUIRED_GUARD_STEPS = (
    "check_precommit_update_archive",
    "check_safety_rule_script_backing",
    "check_local_mirrored_ci_gate",
)
REQUIRED_SAFETY_RULE_IDS = (
    "precommit-update-archive-gate",
    "local-mirrored-ci-mr-gate",
    "complete-local-flow-to-remote-gate",
)
REQUIRED_PRECOMMIT_MARKERS = {
    "new_tests_registered": "check_new_tests_registered",
    "new_checkers_registered": "check_new_checkers_registered",
    "ci_manifest_policy": "new_tests_must_be_registered_in_ci_manifest",
    "checker_registration_policy": "new_checkers_must_be_registered_before_commit",
}
LOCAL_GATE_STEP_ORDER = (
    "openspec_guard",
    "python_unittest",
    "node_mjs_tests",
    "powershell_ps1_tests",
    "git_diff_check",
)

LOCAL_GATE_MARKERS = {
    "check_name": "local_ci_gate",
    "openspec_guard": "run_openspec_guard.py",
    "openspec_guard_forward_slash": "tools/run_openspec_guard.py",
    "git_diff_check": "git_diff_check",
    "refresh_managed_files": "--refresh-managed-files",
    "require_clean_git": "--require-clean-git",
    "shared_with_remote_ci": "shared_with_remote_ci",
    "python_unittest": "python_unittest",
    "node_mjs_tests": "node_mjs_tests",
    "powershell_ps1_tests": "powershell_ps1_tests",
    "openspec_guard_report": "openspec-guard-report.json",
    "local_gate_report": "local-gate-report.json",
    "step_timeout": "StepTimeoutSeconds",
    "timeout_result": "timed_out",
    "ci_test_manifest": "ci_test_manifest.json",
}

LOCAL_MR_REVIEW_MARKERS = {
    "check_name": "local_mr_review",
    "dirty_worktree_check": "git status --porcelain",
    "allow_dirty_escape_hatch": "AllowDirty",
    "changed_files": "git diff --name-status",
    "commit_log": "git log --oneline",
    "diff_stat": "git diff --stat",
    "merge_simulation": "merge-tree",
}

CI_SHARED_SCRIPT_MARKERS = {
    GITLAB_CI_PATH: "tools/ci/local_gate.ps1",
    GITHUB_CI_PATH: "tools/ci/local_gate.ps1",
}

CI_REQUIRED_SHARED_GATE_FLAGS = {
    GITLAB_CI_PATH: ("-RefreshManagedFiles", "-RequireCleanGit"),
    GITHUB_CI_PATH: ("-RefreshManagedFiles", "-RequireCleanGit"),
}

CI_FORBIDDEN_INLINE_MARKERS = {
    "tools/run_openspec_guard.py": "CI must call tools/ci/local_gate.ps1 instead of run_openspec_guard.py directly.",
    "tools\\run_openspec_guard.py": "CI must call tools/ci/local_gate.ps1 instead of run_openspec_guard.py directly.",
    "tools/ci/run_python_tests.py": "CI must call tools/ci/local_gate.ps1 instead of running Python tests directly.",
    "tools\\ci\\run_python_tests.py": "CI must call tools/ci/local_gate.ps1 instead of running Python tests directly.",
    "tools/ci/run_node_mjs_tests.mjs": "CI must call tools/ci/local_gate.ps1 instead of running Node.js tests directly.",
    "tools\\ci\\run_node_mjs_tests.mjs": "CI must call tools/ci/local_gate.ps1 instead of running Node.js tests directly.",
    "tools/ci/run_powershell_ps1_tests.ps1": "CI must call tools/ci/local_gate.ps1 instead of running PowerShell tests directly.",
    "tools\\ci\\run_powershell_ps1_tests.ps1": "CI must call tools/ci/local_gate.ps1 instead of running PowerShell tests directly.",
    "git diff --check": "CI must call tools/ci/local_gate.ps1 instead of duplicating git diff --check inline.",
    "openspec validate --all": "CI must call tools/ci/local_gate.ps1 instead of duplicating openspec validate inline.",
}


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def require_file(root: Path, relative: Path, errors: list[str]) -> str:
    path = root / relative
    text = read_text(path)
    if text is None:
        errors.append(f"Missing or unreadable file: {relative.as_posix()}")
        return ""
    return text


def marker_present_any(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def markers_in_order(text: str, markers: tuple[str, ...]) -> dict[str, Any]:
    positions: dict[str, int] = {}
    cursor = -1
    in_order = True
    for marker in markers:
        position = text.find(marker)
        positions[marker] = position
        if position < 0 or position < cursor:
            in_order = False
        cursor = max(cursor, position)
    return {"in_order": in_order, "positions": positions}


def local_gate_step_append_order(text: str, steps: tuple[str, ...]) -> dict[str, Any]:
    positions: dict[str, int] = {}
    cursor = -1
    in_order = True
    for step in steps:
        pattern = re.compile(
            r"steps\.append\(\s*(?:run_step|skipped_step)\(\s*['\"]"
            + re.escape(step)
            + r"['\"]",
            re.DOTALL,
        )
        match = pattern.search(text)
        position = match.start() if match else -1
        positions[step] = position
        if position < 0 or position < cursor:
            in_order = False
        cursor = max(cursor, position)
    return {"in_order": in_order, "positions": positions}


def validate_manifest(root: Path, manifest: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    evidence: dict[str, Any] = {"sections": {}, "required_tests": {}}
    for section in MANIFEST_SECTIONS:
        values = manifest.get(section, [])
        section_evidence = {
            "is_list": isinstance(values, list),
            "entries": values if isinstance(values, list) else [],
            "duplicates": [],
            "missing_files": [],
            "invalid_entries": [],
        }
        if not isinstance(values, list):
            errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} field {section} must be a list.")
            evidence["sections"][section] = section_evidence
            continue
        seen: set[str] = set()
        for value in values:
            if not isinstance(value, str) or not value.strip():
                section_evidence["invalid_entries"].append(value)
                errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} field {section} contains invalid entry: {value!r}")
                continue
            if value in seen:
                section_evidence["duplicates"].append(value)
                errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} field {section} contains duplicate entry: {value}")
            seen.add(value)
            relative = Path(value)
            if relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 1:
                section_evidence["invalid_entries"].append(value)
                errors.append(
                    f"{CI_TEST_MANIFEST_PATH.as_posix()} field {section} entries must be test filenames: {value}"
                )
                continue
            test_path = root / "test" / value
            if not test_path.exists():
                section_evidence["missing_files"].append(value)
                errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} lists missing {section} test file: test/{value}")
        evidence["sections"][section] = section_evidence

    python_tests = manifest.get("python_unittest", [])
    if not isinstance(python_tests, list):
        python_tests = []
    for test_name in REQUIRED_MANIFEST_TESTS:
        present = test_name in python_tests
        evidence["required_tests"][test_name] = present
        if not present:
            errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} must include required Python test: {test_name}")
    return evidence


def validate_guard_and_registration_surfaces(root: Path, errors: list[str]) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    guard_text = require_file(root, RUN_OPENSPEC_GUARD_PATH, errors)
    guard_steps: dict[str, bool] = {}
    for step in REQUIRED_GUARD_STEPS:
        present = step in guard_text
        guard_steps[step] = present
        if not present:
            errors.append(f"{RUN_OPENSPEC_GUARD_PATH.as_posix()} must reference guard step: {step}")
    evidence["guard_steps"] = guard_steps

    precommit_text = require_file(root, PRECOMMIT_UPDATE_ARCHIVE_PATH, errors)
    precommit_markers: dict[str, bool] = {}
    for name, marker in REQUIRED_PRECOMMIT_MARKERS.items():
        present = marker in precommit_text
        precommit_markers[name] = present
        if not present:
            errors.append(f"{PRECOMMIT_UPDATE_ARCHIVE_PATH.as_posix()} is missing registration marker: {name}")
    evidence["precommit_registration_enforcement"] = precommit_markers

    registry_text = require_file(root, SAFETY_RULE_REGISTRY_PATH, errors)
    try:
        registry = json.loads(registry_text) if registry_text else {}
    except json.JSONDecodeError as exc:
        registry = {}
        errors.append(f"{SAFETY_RULE_REGISTRY_PATH.as_posix()} is not valid JSON: {exc}")
    rules = registry.get("rules", []) if isinstance(registry, dict) else []
    rules_by_id = {rule.get("id"): rule for rule in rules if isinstance(rule, dict)}
    rule_evidence: dict[str, Any] = {}
    for rule_id in REQUIRED_SAFETY_RULE_IDS:
        rule = rules_by_id.get(rule_id)
        record = {
            "present": rule is not None,
            "implemented": bool(rule and rule.get("status") == "implemented"),
            "script_controls": rule.get("script_controls", []) if isinstance(rule, dict) else [],
            "guard_steps": rule.get("guard_steps", []) if isinstance(rule, dict) else [],
        }
        rule_evidence[rule_id] = record
        if rule is None:
            errors.append(f"{SAFETY_RULE_REGISTRY_PATH.as_posix()} must include rule id: {rule_id}")
            continue
        if rule.get("status") != "implemented":
            errors.append(f"{SAFETY_RULE_REGISTRY_PATH.as_posix()} rule {rule_id} must be implemented.")
        if not isinstance(rule.get("script_controls"), list) or not rule.get("script_controls"):
            errors.append(f"{SAFETY_RULE_REGISTRY_PATH.as_posix()} rule {rule_id} must list script_controls.")
        if not isinstance(rule.get("guard_steps"), list) or not rule.get("guard_steps"):
            errors.append(f"{SAFETY_RULE_REGISTRY_PATH.as_posix()} rule {rule_id} must list guard_steps.")
    evidence["safety_rules"] = rule_evidence
    return evidence


def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    evidence: dict[str, Any] = {}

    local_gate_text = require_file(root, LOCAL_GATE_PATH, errors)
    local_gate_impl_text = require_file(root, LOCAL_GATE_IMPL_PATH, errors)
    local_gate_combined_text = local_gate_text + "\n" + local_gate_impl_text
    local_mr_review_text = require_file(root, LOCAL_MR_REVIEW_PATH, errors)
    require_file(root, PYTHON_TEST_RUNNER_PATH, errors)
    require_file(root, NODE_TEST_RUNNER_PATH, errors)
    require_file(root, POWERSHELL_TEST_RUNNER_PATH, errors)
    manifest_text = require_file(root, CI_TEST_MANIFEST_PATH, errors)
    try:
        manifest = json.loads(manifest_text) if manifest_text else {}
    except json.JSONDecodeError as exc:
        manifest = {}
        errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} is not valid JSON: {exc}")
    if manifest and manifest.get("schema_version") != 1:
        errors.append(f"{CI_TEST_MANIFEST_PATH.as_posix()} must declare schema_version 1.")
    evidence["ci_test_manifest"] = validate_manifest(root, manifest, errors)
    evidence.update(validate_guard_and_registration_surfaces(root, errors))

    gate_evidence: dict[str, bool] = {}
    for name, marker in LOCAL_GATE_MARKERS.items():
        present = marker in local_gate_combined_text
        gate_evidence[name] = present
    if not (
        gate_evidence.get("openspec_guard")
        or gate_evidence.get("openspec_guard_forward_slash")
    ):
        errors.append(f"{LOCAL_GATE_PATH.as_posix()} and {LOCAL_GATE_IMPL_PATH.as_posix()} must invoke tools/run_openspec_guard.py.")
    for name, present in gate_evidence.items():
        if name in {"openspec_guard", "openspec_guard_forward_slash"}:
            continue
        if not present:
            errors.append(f"{LOCAL_GATE_PATH.as_posix()} and {LOCAL_GATE_IMPL_PATH.as_posix()} are missing required marker: {name}")
    evidence["local_gate"] = gate_evidence
    local_gate_sequence = local_gate_step_append_order(local_gate_impl_text, LOCAL_GATE_STEP_ORDER)
    evidence["local_gate_step_order"] = local_gate_sequence
    if not local_gate_sequence["in_order"]:
        errors.append(
            f"{LOCAL_GATE_IMPL_PATH.as_posix()} must run the canonical shared gate sequence: "
            + ", ".join(LOCAL_GATE_STEP_ORDER)
        )

    mr_evidence: dict[str, bool] = {}
    for name, marker in LOCAL_MR_REVIEW_MARKERS.items():
        present = marker in local_mr_review_text
        mr_evidence[name] = present
        if not present:
            errors.append(f"{LOCAL_MR_REVIEW_PATH.as_posix()} is missing required marker: {name}")
    evidence["local_mr_review"] = mr_evidence

    ci_evidence: dict[str, Any] = {}
    for relative, shared_marker in CI_SHARED_SCRIPT_MARKERS.items():
        ci_text = require_file(root, relative, errors)
        path_key = relative.as_posix()
        path_evidence: dict[str, Any] = {
            "calls_shared_local_gate": shared_marker in ci_text,
            "required_shared_gate_flags": {},
            "forbidden_inline_markers": {},
        }
        if not path_evidence["calls_shared_local_gate"]:
            errors.append(f"{path_key} must call {shared_marker}.")
        for flag in CI_REQUIRED_SHARED_GATE_FLAGS.get(relative, ()):
            present = flag in ci_text
            path_evidence["required_shared_gate_flags"][flag] = present
            if not present:
                errors.append(f"{path_key} shared local gate invocation must include {flag}.")
        for marker, message in CI_FORBIDDEN_INLINE_MARKERS.items():
            present = marker in ci_text
            path_evidence["forbidden_inline_markers"][marker] = present
            if present:
                errors.append(f"{path_key}: {message}")
        ci_evidence[path_key] = path_evidence
    evidence["remote_ci"] = ci_evidence

    if not errors:
        info.append("Local-first mirrored CI/MR gate is script-backed and remote CI calls the shared local gate.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "files": {
            "local_gate": LOCAL_GATE_PATH.as_posix(),
            "local_gate_impl": LOCAL_GATE_IMPL_PATH.as_posix(),
            "local_mr_review": LOCAL_MR_REVIEW_PATH.as_posix(),
            "python_test_runner": PYTHON_TEST_RUNNER_PATH.as_posix(),
            "node_test_runner": NODE_TEST_RUNNER_PATH.as_posix(),
            "powershell_test_runner": POWERSHELL_TEST_RUNNER_PATH.as_posix(),
            "ci_test_manifest": CI_TEST_MANIFEST_PATH.as_posix(),
            "gitlab_ci": GITLAB_CI_PATH.as_posix(),
            "github_ci": GITHUB_CI_PATH.as_posix(),
        },
        "evidence": evidence,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify local-first mirrored CI/MR gate wiring.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
