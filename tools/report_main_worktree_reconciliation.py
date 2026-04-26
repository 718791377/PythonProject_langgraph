#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_BACKUP_REF = "backup/mainworktree-dirty-before-main-align-20260426-234655"
DEFAULT_TARGET_REF = "gitlab/main"


@dataclass(frozen=True)
class ChangeRecord:
    path: str
    status: str
    old_path: str | None = None


@dataclass(frozen=True)
class ClassifiedPath:
    path: str
    category: str
    local_status: str | None
    target_status: str | None
    local_old_path: str | None = None
    target_old_path: str | None = None


def run_git(root: Path, args: list[str], *, binary: bool = False) -> str | bytes:
    command = ["git", "-C", str(root), *args]
    if binary:
        return subprocess.check_output(command, stderr=subprocess.DEVNULL)
    return subprocess.check_output(command, text=True, encoding="utf-8", errors="replace")


def resolve_ref(root: Path, ref: str) -> str:
    return str(run_git(root, ["rev-parse", ref])).strip()


def object_bytes(root: Path, ref: str, path: str) -> bytes | None:
    try:
        return bytes(run_git(root, ["show", f"{ref}:{path}"], binary=True))
    except subprocess.CalledProcessError:
        return None


def parse_name_status(root: Path, left_ref: str, right_ref: str) -> dict[str, ChangeRecord]:
    records: dict[str, ChangeRecord] = {}
    output = str(run_git(root, ["diff", "--name-status", left_ref, right_ref]))
    for raw_line in output.splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            old_path = parts[1]
            new_path = parts[2]
            records[new_path] = ChangeRecord(path=new_path, status=status, old_path=old_path)
            records[old_path] = ChangeRecord(path=old_path, status="RENAMED_FROM", old_path=new_path)
            continue
        if len(parts) >= 2:
            records[parts[1]] = ChangeRecord(path=parts[1], status=status)
    return records


def top_level(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else path


def bucket_openspec_path(path: str) -> str:
    parts = path.split("/")
    if path.startswith("openspec/changes/archive/") and len(parts) >= 4:
        return "/".join(parts[:4])
    if path.startswith("openspec/changes/") and len(parts) >= 3:
        return "/".join(parts[:3])
    if path.startswith("openspec/specs/") and len(parts) >= 3:
        return "/".join(parts[:3])
    return top_level(path)


def classify_paths(root: Path, base_ref: str, local_ref: str, target_ref: str) -> list[ClassifiedPath]:
    local_changes = parse_name_status(root, base_ref, local_ref)
    target_changes = parse_name_status(root, base_ref, target_ref)

    local_paths = {path for path, record in local_changes.items() if record.status != "RENAMED_FROM"}
    target_paths = {path for path, record in target_changes.items() if record.status != "RENAMED_FROM"}

    classified: list[ClassifiedPath] = []
    for path in sorted(local_paths | target_paths):
        local_record = local_changes.get(path)
        target_record = target_changes.get(path)
        local_touched = path in local_paths
        target_touched = path in target_paths

        local_bytes = object_bytes(root, local_ref, path) if local_touched else None
        target_bytes = object_bytes(root, target_ref, path) if target_touched or local_touched else None

        if local_touched and target_touched:
            category = "both_changed_same_content" if local_bytes == target_bytes else "both_changed_different"
        elif local_touched:
            category = (
                "local_changed_already_same_as_target"
                if target_bytes is not None and local_bytes == target_bytes
                else "local_only"
            )
        else:
            category = "target_only"

        classified.append(
            ClassifiedPath(
                path=path,
                category=category,
                local_status=local_record.status if local_record else None,
                target_status=target_record.status if target_record else None,
                local_old_path=local_record.old_path if local_record else None,
                target_old_path=target_record.old_path if target_record else None,
            )
        )
    return classified


def summarize(classified: list[ClassifiedPath]) -> dict[str, object]:
    counts = Counter(item.category for item in classified)
    by_category_top_level: dict[str, dict[str, int]] = {}
    openspec_groups: dict[str, dict[str, int]] = {}
    for category in sorted(counts):
        category_items = [item for item in classified if item.category == category]
        by_category_top_level[category] = dict(Counter(top_level(item.path) for item in category_items).most_common())
        openspec_groups[category] = dict(
            Counter(bucket_openspec_path(item.path) for item in category_items if item.path.startswith("openspec/")).most_common()
        )
    return {
        "total_paths": len(classified),
        "by_category": dict(sorted(counts.items())),
        "by_category_top_level": by_category_top_level,
        "openspec_groups": openspec_groups,
    }


def render_markdown(payload: dict[str, object], *, language: str) -> str:
    title = (
        "Main Worktree Backup Reconciliation Inventory"
        if language == "en"
        else "主工作区备份分支对账清单"
    )
    intro = (
        "This report compares the local backup branch with `gitlab/main` so future work can migrate useful local-only or both-changed content without making local `main` drift from GitLab main."
        if language == "en"
        else "本报告对比本地备份分支和 `gitlab/main`，用于后续在不让本地 `main` 偏离 GitLab main 的前提下，迁移有价值的 local-only 或 both-changed 内容。"
    )
    labels = {
        "local_only": "Local only / 仅本地备份有更新",
        "target_only": "Target only / 仅 gitlab/main 有更新",
        "both_changed_different": "Both changed differently / 双方都更新且内容不同",
        "both_changed_same_content": "Both changed to same content / 双方都更新但内容相同",
        "local_changed_already_same_as_target": "Local already same as target / 本地改动已等同目标",
    }
    lines = [
        f"# {title}",
        "",
        intro,
        "",
        "## References / 引用",
        "",
        f"- `{payload['base_ref']}` - base reference used as the shared ancestor for comparison.",
        f"- `{payload['local_ref']}` - local backup branch that preserved dirty main-worktree content.",
        f"- `{payload['target_ref']}` - target mainline reference that local `main` must match.",
        "",
        "## Counts / 统计",
        "",
    ]
    summary = payload["summary"]  # type: ignore[index]
    by_category = summary["by_category"]  # type: ignore[index]
    for key in sorted(labels):
        lines.append(f"- `{key}` - {labels[key]}: {by_category.get(key, 0)}")
    lines.extend(["", "## Non-OpenSpec paths requiring review / 需要复核的非 OpenSpec 路径", ""])
    paths = payload["paths"]  # type: ignore[index]
    for category in ("both_changed_different", "local_only", "target_only", "both_changed_same_content"):
        items = [
            item
            for item in paths  # type: ignore[assignment]
            if item["category"] == category and not item["path"].startswith("openspec/")
        ]
        if not items:
            continue
        lines.extend([f"### `{category}` - {labels[category]}", ""])
        for item in items:
            lines.append(f"- `{item['path']}` - {labels[category]}.")
        lines.append("")
    lines.extend(["## OpenSpec local-only groups / OpenSpec 本地-only 分组", ""])
    openspec_groups = summary["openspec_groups"]["local_only"]  # type: ignore[index]
    for group, count in openspec_groups.items():
        lines.append(f"- `{group}` - contains {count} local-only OpenSpec path(s) to review before migration.")
    lines.extend(
        [
            "",
            "## Recommended next steps / 推荐下一步",
            "",
            "- `reconcile/active-docs-three-way-merge` - use a clean branch from `gitlab/main` to merge the both-changed active documentation files.",
            "- `reconcile/checker-three-way-merge` - use a clean branch from `gitlab/main` to merge checker and test updates.",
            "- `reconcile/local-only-doc-name-clarity` - use a clean branch from `gitlab/main` to review local-only bilingual documentation updates.",
            "- `reconcile/openspec-name-clarity-batch-*` - use small batches from `gitlab/main` to migrate confirmed OpenSpec name-clarity comments.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_payload(root: Path, base_ref: str, local_ref: str, target_ref: str) -> dict[str, object]:
    classified = classify_paths(root, base_ref, local_ref, target_ref)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "main_worktree_reconciliation_report",
        "root": str(root),
        "base_ref": base_ref,
        "base_commit": resolve_ref(root, base_ref),
        "local_ref": local_ref,
        "local_commit": resolve_ref(root, local_ref),
        "target_ref": target_ref,
        "target_commit": resolve_ref(root, target_ref),
        "summary": summarize(classified),
        "paths": [asdict(item) for item in classified],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report local backup vs gitlab/main reconciliation categories.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--base-ref", default=None, help="Shared base ref. Defaults to <backup-ref>^.")
    parser.add_argument("--backup-ref", default=DEFAULT_BACKUP_REF, help="Local backup branch/ref to compare.")
    parser.add_argument("--target-ref", default=DEFAULT_TARGET_REF, help="Target mainline ref to compare.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--markdown-output", default=None, help="Write English Markdown report to this path.")
    parser.add_argument("--markdown-zh-output", default=None, help="Write Chinese Markdown report to this path.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")
    base_ref = args.base_ref or f"{args.backup_ref}^"
    payload = build_payload(root, base_ref, args.backup_ref, args.target_ref)

    if args.markdown_output:
        output_path = (root / args.markdown_output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_markdown(payload, language="en"), encoding="utf-8")
    if args.markdown_zh_output:
        output_path = (root / args.markdown_zh_output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_markdown(payload, language="zh"), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        summary = payload["summary"]
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
