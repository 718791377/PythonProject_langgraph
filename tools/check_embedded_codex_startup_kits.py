#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

CHECK_NAME = "embedded_codex_startup_kits"
SCHEMA_VERSION = 1
CHECKER_PATH = "tools/check_embedded_codex_startup_kits.py"
TEST_NAME = "check_embedded_codex_startup_kits.test.py"
TEST_PATH = f"test/{TEST_NAME}"
GUARD_STEP = "check_embedded_codex_startup_kits"
PLAN_PATH = "docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.md"
PLAN_ZH_PATH = "docs_bilingual/implementation_plans/embedded_codex_startup_kits_and_project_kit_plan.zh-CN.md"

STARTUP_DOCS = [
    "thesis.md",
    "architecture.md",
    "agent-governance.md",
    "agent-role-map.md",
    "agent-permissions.md",
    "delivery-plan.md",
    "observability.md",
    "risk-register.md",
    "human-review-checklist.md",
    "decision-log.md",
    "backup-restore.md",
    "monthly-review.md",
]

LEDGER_SLUGS = [
    "decision-log-entry-template",
    "risk-register-entry-template",
    "experiment-log-entry-template",
    "learning-log-entry-template",
    "human-review-record-template",
    "monthly-review-template",
]

PROJECT_KIT_FILES = [
    "README",
    "startup-checklist",
    "folder-structure",
    "governance-gates",
    "local-main-workflow",
    "remote-publication-gate",
    "monthly-review-sample",
]

REQUIRED_PAIRS: list[tuple[str, str, str, str]] = [
    (
        "codex_cli_personal_production_durable_team_minimum_startup_documents",
        "product_lifecycle",
        "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md",
        "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.zh-CN.md",
    ),
    (
        "one_person_company_embedded_codex_startup_matrix",
        "product_lifecycle",
        "docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md",
        "docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.zh-CN.md",
    ),
]
REQUIRED_PAIRS.extend(
    (
        "shared_governance_" + slug.replace("-", "_"),
        "template",
        f"docs_bilingual/templates/shared_governance_ledgers/{slug}.md",
        f"docs_bilingual/templates/shared_governance_ledgers/{slug}.zh-CN.md",
    )
    for slug in LEDGER_SLUGS
)
REQUIRED_PAIRS.append(
    (
        "tailoring_decision_record_template",
        "template",
        "docs_bilingual/templates/tailoring_decision_record_template.md",
        "docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md",
    )
)
REQUIRED_PAIRS.extend(
    (
        "one_person_company_with_embedded_codex_" + ("readme" if slug == "README" else slug.replace("-", "_")),
        "product_lifecycle",
        f"docs_bilingual/project_kits/one_person_company_with_embedded_codex/{'README.md' if slug == 'README' else slug + '.md'}",
        f"docs_bilingual/project_kits/one_person_company_with_embedded_codex/{'README.zh-CN.md' if slug == 'README' else slug + '.zh-CN.md'}",
    )
    for slug in PROJECT_KIT_FILES
)

REQUIRED_FILES = [path for _doc_id, _doc_class, en, zh in REQUIRED_PAIRS for path in (en, zh)]

MATRIX_TOKENS = [
    "one-person-company startup document",
    "embedded Codex startup document",
    "shared ledger",
    "scope: business | codex | mixed",
    "truth_owner: founder | codex-operator | human-review",
    "evidence_source: customer | revenue | repo | runtime | agent | legal",
    "decision_right: human | delegated-draft-only",
    "linked_docs",
    "two-gate",
    "business gate",
    "Codex execution gate",
]

STARTUP_ANCHORS = [
    "minimum embedded platform-governance start set",
    "agents",
    "worktrees",
    "durable state",
    "validation gates",
    "release gates",
    "evidence",
    "rollback",
    "review",
]

LEDGER_FIELDS = ["scope", "truth_owner", "evidence_source", "decision_right", "linked_docs"]
TAILORING_FIELDS = ["mode", "why_not_heavier", "why_not_lighter", "escalation_triggers", "rollback", "local_main_evidence"]
PROJECT_KIT_TERMS = [
    "startup checklist",
    "folder structure",
    "governance gates",
    "local-main",
    "remote-publication gate",
    "monthly review",
    "business gate",
    "Codex execution gate",
]
PROCESS_GROUP_EN = ["Inputs", "Tools And Techniques", "Outputs"]
PROCESS_GROUP_ZH = ["输入", "工具与技术", "输出"]
MOJIBAKE_SENTINELS = ["\ufffd", "Ã", "Â", "â€", "锛", "涓", "乱码"]


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path, errors: list[str], checked: set[str]) -> str:
    rel = norm(path)
    checked.add(rel)
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except FileNotFoundError:
        errors.append(f"Required file is missing: {rel}")
        return ""
    except UnicodeDecodeError as exc:
        errors.append(f"File is not valid UTF-8: {rel}: {exc}")
        return ""
    if "\ufffd" in text:
        errors.append(f"{rel} contains Unicode replacement character.")
    for sentinel in MOJIBAKE_SENTINELS:
        if sentinel and sentinel in text:
            label = "replacement character" if sentinel == "\ufffd" else "mojibake sentinel"
            errors.append(f"{rel} contains {label}: {sentinel!r}.")
            break
    return text


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return {}


def parse_registry(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("- doc_id:"):
            if current:
                entries.append(current)
            current = {"doc_id": stripped.split(":", 1)[1].strip()}
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        entries.append(current)
    return entries


def require_tokens(rel: str, text: str, tokens: Iterable[str], errors: list[str], context: str) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{rel} is missing {context} token `{token}`.")


def assert_ascii(rel: str, text: str, errors: list[str]) -> None:
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        errors.append(f"{rel} English primary contains non-ASCII text at character index {exc.start}.")


def validate_frontmatter_pair(doc_id: str, doc_class: str, en_rel: str, zh_rel: str, texts: dict[str, str], errors: list[str]) -> None:
    for rel, lang in ((en_rel, "en"), (zh_rel, "zh-CN")):
        fm = parse_frontmatter(texts.get(rel, ""))
        if not fm:
            errors.append(f"{rel} is missing YAML front matter.")
            continue
        expected = {
            "doc_id": doc_id,
            "lang": lang,
            "doc_class": doc_class,
            "status": "active",
            "canonical_path": en_rel,
            "zh_cn_path": zh_rel,
        }
        for key, value in expected.items():
            if fm.get(key) != value:
                errors.append(f"{rel} front matter {key}={fm.get(key)!r}; expected {value!r}.")
        if lang == "zh-CN" and fm.get("translation_of") != en_rel:
            errors.append(f"{rel} front matter translation_of={fm.get('translation_of')!r}; expected {en_rel!r}.")


def validate_startup_order(text: str, errors: list[str]) -> None:
    found = []
    for line in text.splitlines():
        match = re.match(r"^\s*\d+\.\s+`([^`]+\.md)`", line)
        if match:
            found.append(match.group(1))
    if found != STARTUP_DOCS:
        errors.append(
            "Codex 12-document startup order mismatch; expected "
            + ", ".join(STARTUP_DOCS)
            + "; got "
            + ", ".join(found)
        )
    counts = Counter(found)
    for item in STARTUP_DOCS:
        if counts[item] != 1:
            errors.append(f"Codex 12-document startup order must contain `{item}` exactly once; got {counts[item]}.")
    require_tokens(
        "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md",
        text,
        STARTUP_ANCHORS,
        errors,
        "startup",
    )


def validate_registry(root: Path, registry_text: str, errors: list[str]) -> None:
    entries = parse_registry(registry_text)
    doc_ids = [entry.get("doc_id", "") for entry in entries]
    canonical_paths = [entry.get("canonical_path", "") for entry in entries]
    zh_paths = [entry.get("zh_cn_path", "") for entry in entries]
    for doc_id, count in Counter(doc_ids).items():
        if doc_id and count > 1:
            errors.append(f"docs_bilingual/docs_registry.yaml has duplicate doc_id `{doc_id}`.")
    for path, count in Counter([p for p in canonical_paths + zh_paths if p]).items():
        if count > 1:
            errors.append(f"docs_bilingual/docs_registry.yaml has duplicate path `{path}`.")
    by_pair = {(entry.get("canonical_path", ""), entry.get("zh_cn_path", "")): entry for entry in entries}
    for doc_id, _doc_class, en_rel, zh_rel in REQUIRED_PAIRS:
        entry = by_pair.get((en_rel, zh_rel))
        if not entry:
            errors.append(f"docs_bilingual/docs_registry.yaml is missing Stage B pair `{en_rel}` / `{zh_rel}`.")
            continue
        if entry.get("doc_id") != doc_id:
            errors.append(f"docs_bilingual/docs_registry.yaml entry for `{en_rel}` has doc_id={entry.get('doc_id')!r}; expected {doc_id!r}.")
    for entry in entries:
        canonical = entry.get("canonical_path", "")
        zh = entry.get("zh_cn_path", "")
        if canonical and not (root / canonical).exists():
            errors.append(f"docs_bilingual/docs_registry.yaml canonical_path does not exist: {canonical}")
        if zh and not (root / zh).exists():
            errors.append(f"docs_bilingual/docs_registry.yaml zh_cn_path does not exist: {zh}")
        if canonical and zh and canonical == zh:
            errors.append(f"docs_bilingual/docs_registry.yaml has identical canonical_path and zh_cn_path for `{entry.get('doc_id')}`.")


def validate_registrations(root: Path, errors: list[str], checked: set[str]) -> None:
    manifest_rel = "tools/ci/ci_test_manifest.json"
    guard_rel = "tools/run_openspec_guard.py"
    safety_rel = "tools/safety_rule_script_backing_registry.json"
    guard_test_rel = "test/run_openspec_guard_json.test.py"
    manifest_text = read_text(root / manifest_rel, errors, checked)
    try:
        manifest = json.loads(manifest_text) if manifest_text else {}
    except json.JSONDecodeError as exc:
        errors.append(f"{manifest_rel} is not valid JSON: {exc}")
        manifest = {}
    if TEST_NAME not in manifest.get("python_unittest", []):
        errors.append(f"{manifest_rel} does not register `{TEST_NAME}`.")

    guard_text = read_text(root / guard_rel, errors, checked)
    if CHECKER_PATH not in guard_text and "check_embedded_codex_startup_kits.py" not in guard_text:
        errors.append(f"{guard_rel} does not declare `{CHECKER_PATH}`.")
    if GUARD_STEP not in guard_text:
        errors.append(f"{guard_rel} does not include guard step `{GUARD_STEP}`.")
    if "--json" not in guard_text:
        errors.append(f"{guard_rel} does not include JSON guard invocation support.")

    safety_text = read_text(root / safety_rel, errors, checked)
    for token, label in ((CHECKER_PATH, "checker"), (TEST_PATH, "test"), (GUARD_STEP, "guard step"), (PLAN_PATH, "plan")):
        if token not in safety_text:
            errors.append(f"{safety_rel} does not register {label} `{token}`.")

    guard_test_text = read_text(root / guard_test_rel, errors, checked)
    if GUARD_STEP not in guard_test_text:
        errors.append(f"{guard_test_rel} does not mirror guard step `{GUARD_STEP}`.")


def evaluate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: set[str] = set()
    texts: dict[str, str] = {}

    for rel in REQUIRED_FILES:
        texts[rel] = read_text(root / rel, errors, checked)

    for doc_id, doc_class, en_rel, zh_rel in REQUIRED_PAIRS:
        validate_frontmatter_pair(doc_id, doc_class, en_rel, zh_rel, texts, errors)
        assert_ascii(en_rel, texts.get(en_rel, ""), errors)

    startup_rel = "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md"
    validate_startup_order(texts.get(startup_rel, ""), errors)

    matrix_rel = "docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md"
    matrix_text = texts.get(matrix_rel, "")
    require_tokens(matrix_rel, matrix_text, MATRIX_TOKENS, errors, "startup matrix")
    for doc in STARTUP_DOCS:
        if doc not in texts.get(startup_rel, "") and doc not in matrix_text:
            errors.append(f"Stage B startup surfaces do not mention `{doc}`.")

    for slug in LEDGER_SLUGS:
        for suffix in (".md", ".zh-CN.md"):
            rel = f"docs_bilingual/templates/shared_governance_ledgers/{slug}{suffix}"
            require_tokens(rel, texts.get(rel, ""), LEDGER_FIELDS, errors, "shared ledger field")

    tailoring_rel = "docs_bilingual/templates/tailoring_decision_record_template.md"
    require_tokens(tailoring_rel, texts.get(tailoring_rel, ""), TAILORING_FIELDS, errors, "tailoring field")
    require_tokens(
        "docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md",
        texts.get("docs_bilingual/templates/tailoring_decision_record_template.zh-CN.md", ""),
        TAILORING_FIELDS,
        errors,
        "tailoring field",
    )

    aggregate_kit = "\n".join(
        texts.get(f"docs_bilingual/project_kits/one_person_company_with_embedded_codex/{'README.md' if slug == 'README' else slug + '.md'}", "")
        for slug in PROJECT_KIT_FILES
    )
    require_tokens("docs_bilingual/project_kits/one_person_company_with_embedded_codex/", aggregate_kit, PROJECT_KIT_TERMS, errors, "project kit")

    execution_files = [
        "docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md",
        "docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md",
        "docs_bilingual/templates/tailoring_decision_record_template.md",
    ]
    execution_files.extend(f"docs_bilingual/templates/shared_governance_ledgers/{slug}.md" for slug in LEDGER_SLUGS)
    execution_files.extend(
        f"docs_bilingual/project_kits/one_person_company_with_embedded_codex/{'README.md' if slug == 'README' else slug + '.md'}"
        for slug in PROJECT_KIT_FILES
    )
    for rel in execution_files:
        require_tokens(rel, texts.get(rel, ""), PROCESS_GROUP_EN, errors, "process-group")
        zh_rel = rel[:-3] + ".zh-CN.md" if not rel.endswith("README.md") else rel.replace("README.md", "README.zh-CN.md")
        require_tokens(zh_rel, texts.get(zh_rel, ""), PROCESS_GROUP_ZH, errors, "process-group")

    registry_rel = "docs_bilingual/docs_registry.yaml"
    registry_text = read_text(root / registry_rel, errors, checked)
    validate_registry(root, registry_text, errors)
    validate_registrations(root, errors, checked)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check": CHECK_NAME,
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "checked_paths": sorted(checked),
        "counts": {
            "required_pairs": len(REQUIRED_PAIRS),
            "required_files": len(REQUIRED_FILES),
            "startup_documents": len(STARTUP_DOCS),
            "ledger_templates": len(LEDGER_SLUGS),
            "project_kit_pages": len(PROJECT_KIT_FILES),
            "checked_paths": len(checked),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate embedded Codex startup-kit docs, templates, project kit, and guard registrations.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)
    payload = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'fail'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
