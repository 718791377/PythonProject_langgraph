#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "plan_exit_execution_governance"
DOC_PREFIXES = ("docs_bilingual/", "openspec/", "docs/")
DOC_EXACT_PATHS = {"完整提交流程.md"}
DOCS_BILINGUAL_PREFIX = "docs_bilingual/"
DEFAULT_RECEIPT = ".omx/worktree-task-receipt.json"
DEFAULT_CLAIMS_SUBDIR = ".omx/session-claims"


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def normalize_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    while value.startswith("./"):
        value = value[2:]
    return value


def changed_paths_for_commit(root: Path, commit: str) -> list[str]:
    result = run_git(root, ["diff-tree", "--no-commit-id", "--name-only", "-r", commit])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git diff-tree failed for {commit}")
    return [normalize_path(line) for line in result.stdout.splitlines() if line.strip()]


def range_commits(root: Path, base_ref: str, head_ref: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    result = run_git(root, ["rev-list", "--reverse", f"{base_ref}..{head_ref}"])
    if result.returncode != 0:
        errors.append(result.stderr.strip() or result.stdout.strip() or "git rev-list failed")
        return [], errors
    return [line.strip() for line in result.stdout.splitlines() if line.strip()], errors


def commit_exists(root: Path, commit: str) -> bool:
    result = run_git(root, ["cat-file", "-e", f"{commit}^{{commit}}"])
    return result.returncode == 0


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = run_git(root, ["merge-base", "--is-ancestor", ancestor, descendant])
    return result.returncode == 0


def is_docs_path(path: str) -> bool:
    return path in DOC_EXACT_PATHS or path.startswith(DOC_PREFIXES)


def is_docs_bilingual_path(path: str) -> bool:
    return path.startswith(DOCS_BILINGUAL_PREFIX)


def read_json_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def iter_confirmation_sources(root: Path, receipt: str, claims_subdir: str) -> list[tuple[str, Path, dict[str, Any] | None, str | None]]:
    sources: list[tuple[str, Path, dict[str, Any] | None, str | None]] = []
    receipt_path = root / receipt
    payload, error = read_json_file(receipt_path)
    if payload is not None or receipt_path.exists():
        sources.append(("receipt", receipt_path, payload, error))

    claims_path = root / claims_subdir
    if claims_path.exists():
        for claim_path in sorted(claims_path.glob("*.json")):
            payload, error = read_json_file(claim_path)
            sources.append(("claim", claim_path, payload, error))
    return sources


def validate_governance_commit(root: Path, commit: str, main_ref: str) -> list[str]:
    errors: list[str] = []
    if not commit:
        return ["governance_package_commit is missing."]
    if not commit_exists(root, commit):
        return [f"governance_package_commit does not exist: {commit}"]
    try:
        paths = changed_paths_for_commit(root, commit)
    except RuntimeError as exc:
        return [str(exc)]
    if not paths:
        errors.append(f"governance_package_commit changed no paths: {commit}")
    if not all(is_docs_path(path) for path in paths):
        errors.append(f"governance_package_commit must be docs-only: {commit}")
    if not any(is_docs_bilingual_path(path) for path in paths):
        errors.append(f"governance_package_commit must touch docs_bilingual/: {commit}")
    if not is_ancestor(root, commit, main_ref):
        errors.append(f"governance_package_commit must already be merged to local {main_ref}: {commit}")
    return errors


def source_relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def evaluate_confirmation_source(
    root: Path,
    source_kind: str,
    source_path: Path,
    payload: dict[str, Any] | None,
    load_error: str | None,
    main_ref: str,
) -> dict[str, Any]:
    errors: list[str] = []
    if load_error:
        errors.append(load_error)
    if payload is None:
        return {"source_kind": source_kind, "path": source_relative(root, source_path), "valid": False, "errors": errors}

    if payload.get("requires_user_confirmation_before_implementation") is not True:
        errors.append("requires_user_confirmation_before_implementation must be true.")
    if payload.get("implementation_confirmed_by_user") is not True:
        errors.append("implementation_confirmed_by_user must be true.")
    if not payload.get("implementation_confirmation_recorded_at"):
        errors.append("implementation_confirmation_recorded_at is missing.")
    if payload.get("governance_package_merged_to_local_main") is not True:
        errors.append("governance_package_merged_to_local_main must be true.")
    commit = str(payload.get("governance_package_commit") or "").strip()
    errors.extend(validate_governance_commit(root, commit, main_ref))

    return {
        "source_kind": source_kind,
        "path": source_relative(root, source_path),
        "valid": not errors,
        "errors": errors,
        "governance_package_commit": commit,
        "implementation_confirmation_recorded_at": payload.get("implementation_confirmation_recorded_at"),
    }


def evaluate_staged_confirmations(root: Path, main_ref: str, receipt: str, claims_subdir: str) -> list[dict[str, Any]]:
    return [
        evaluate_confirmation_source(root, kind, path, payload, error, main_ref)
        for kind, path, payload, error in iter_confirmation_sources(root, receipt, claims_subdir)
    ]


def evaluate(
    root: Path,
    base_ref: str,
    head_ref: str,
    receipt: str = DEFAULT_RECEIPT,
    claims_subdir: str = DEFAULT_CLAIMS_SUBDIR,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    commits, range_errors = range_commits(root, base_ref, head_ref)
    errors.extend(range_errors)

    commit_records: list[dict[str, Any]] = []
    all_changed_paths: list[str] = []
    for commit in commits:
        try:
            paths = changed_paths_for_commit(root, commit)
        except RuntimeError as exc:
            errors.append(str(exc))
            paths = []
        all_changed_paths.extend(paths)
        commit_records.append(
            {
                "commit": commit,
                "paths": paths,
                "docs_only": bool(paths) and all(is_docs_path(path) for path in paths),
                "touches_docs_bilingual": any(is_docs_bilingual_path(path) for path in paths),
                "non_docs_paths": [path for path in paths if not is_docs_path(path)],
            }
        )

    non_doc_paths = sorted({path for path in all_changed_paths if not is_docs_path(path)})
    docs_bilingual_paths = sorted({path for path in all_changed_paths if is_docs_bilingual_path(path)})
    docs_or_openspec_paths = sorted({path for path in all_changed_paths if path.startswith(("docs/", "openspec/"))})

    staged_confirmations = evaluate_staged_confirmations(root, base_ref, receipt, claims_subdir)
    valid_staged_confirmations = [record for record in staged_confirmations if record.get("valid")]
    requires_governance_package = bool(non_doc_paths)
    legacy_same_range_governance = False

    if requires_governance_package:
        legacy_governance_errors: list[str] = []
        if not commits:
            legacy_governance_errors.append("Non-document execution cannot be evaluated because the range has no commits.")
        first_record = commit_records[0] if commit_records else None
        if first_record and not first_record["docs_only"]:
            legacy_governance_errors.append(
                "When a post-/plan task contains non-document changes, the first commit in the range must be a local governance package limited to docs_bilingual/, openspec/, or docs/."
            )
        if first_record and not first_record["touches_docs_bilingual"]:
            legacy_governance_errors.append(
                "The first local governance package commit must update docs_bilingual/ first; openspec/ and docs/ may only be derived from that decision."
            )
        if not docs_bilingual_paths:
            legacy_governance_errors.append("Non-document execution requires at least one docs_bilingual/ governance artifact in the range.")
        legacy_same_range_governance = not legacy_governance_errors

        if not legacy_same_range_governance and not valid_staged_confirmations:
            errors.extend(legacy_governance_errors)
            errors.append(
                "Non-document execution requires either a same-range docs_bilingual-first governance commit or a confirmed Stage A receipt/claim whose governance package is already merged to local main."
            )
        elif legacy_same_range_governance:
            info.append("Non-document execution uses the legacy same-range docs_bilingual-first governance package.")
        else:
            info.append("Non-document execution authorized by confirmed Stage A receipt/claim.")
    else:
        info.append("No non-document changed paths detected; post-/plan governance package rule is not required for this range.")

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "commits": len(commits),
            "changed_paths": len(set(all_changed_paths)),
            "non_doc_paths": len(non_doc_paths),
            "docs_bilingual_paths": len(docs_bilingual_paths),
            "docs_or_openspec_paths": len(docs_or_openspec_paths),
            "staged_confirmation_records": len(staged_confirmations),
            "valid_staged_confirmations": len(valid_staged_confirmations),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "requires_governance_package": requires_governance_package,
        "legacy_same_range_governance": legacy_same_range_governance,
        "staged_confirmations": staged_confirmations,
        "non_doc_paths": non_doc_paths,
        "docs_bilingual_paths": docs_bilingual_paths,
        "docs_or_openspec_paths": docs_or_openspec_paths,
        "commits": commit_records,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that post-/plan non-document execution has docs_bilingual-first governance and implementation confirmation evidence.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base-ref", default="main", help="Base ref for the checked range.")
    parser.add_argument("--head-ref", default="HEAD", help="Head ref for the checked range.")
    parser.add_argument("--receipt", default=DEFAULT_RECEIPT, help="Receipt JSON path relative to root.")
    parser.add_argument("--claims-subdir", default=DEFAULT_CLAIMS_SUBDIR, help="Claims directory relative to root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = evaluate(Path(args.root), args.base_ref, args.head_ref, args.receipt, args.claims_subdir)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("Post-/plan execution governance check passed.")
            for message in payload["info"]:
                print(f"  - {message}")
        else:
            print("Post-/plan execution governance check failed:")
            for error in payload["errors"]:
                print(f"  - {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
