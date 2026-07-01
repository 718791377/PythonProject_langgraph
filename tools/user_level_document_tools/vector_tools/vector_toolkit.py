#!/usr/bin/env python3
"""Generic local vector/retrieval helper framework."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib import error, request

WORD_RE = re.compile(r"[A-Za-z0-9_.:/#\-\u4e00-\u9fff]+")

def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return json.loads(raw.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="replace"))

def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, 1):
            text = line.strip()
            if not text:
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(value, dict):
                errors.append(f"line {line_number}: record is not an object")
                continue
            value.setdefault("_lineNumber", line_number)
            rows.append(value)
    return rows, errors

def as_text(value: Any) -> str:
    return str(value or "").strip()

def check_http_embedding(config: dict[str, Any], timeout: float) -> dict[str, Any]:
    embedding = config.get("embedding", {})
    if not isinstance(embedding, dict):
        return {"ok": False, "error": "embedding config is not an object"}
    base_url = as_text(embedding.get("baseURL")).rstrip("/")
    model = as_text(embedding.get("model"))
    if not base_url or not model:
        return {"ok": False, "error": "embedding baseURL/model not configured"}
    headers = {"Content-Type": "application/json"}
    api_key = as_text(embedding.get("apiKey"))
    if api_key and not api_key.startswith("<"):
        headers["Authorization"] = f"Bearer {api_key}"
    req = request.Request(
        f"{base_url}/embeddings",
        method="POST",
        headers=headers,
        data=json.dumps({"model": model, "input": "vector toolkit smoke test"}).encode("utf-8"),
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, error.URLError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    rows = data.get("data") if isinstance(data, dict) else None
    ok = isinstance(rows, list) and bool(rows) and isinstance(rows[0], dict) and isinstance(rows[0].get("embedding"), list)
    return {"ok": bool(ok), "vectorLength": len(rows[0]["embedding"]) if ok else 0}

def command_show_config(args: argparse.Namespace) -> int:
    config = load_json(Path(args.config))
    print(json.dumps({"ok": isinstance(config, dict), "config": config}, indent=2, ensure_ascii=False))
    return 0 if isinstance(config, dict) else 1

def command_validate_manifest(args: argparse.Namespace) -> int:
    rows, errors = load_jsonl(Path(args.manifest))
    for row in rows:
        missing = [field for field in args.require_field if field not in row or row.get(field) in (None, "")]
        if missing:
            errors.append(f"line {row.get('_lineNumber')}: missing required fields: {', '.join(missing)}")
    payload = {"ok": not errors, "manifest": str(Path(args.manifest)), "recordCount": len(rows), "errors": errors[:50]}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["ok"] else 1

def command_health(args: argparse.Namespace) -> int:
    config = load_json(Path(args.config))
    if not isinstance(config, dict):
        print(json.dumps({"ok": False, "error": "config root is not an object"}, indent=2))
        return 1
    checks: list[dict[str, Any]] = []
    stores = config.get("stores", {}) if isinstance(config.get("stores"), dict) else {}
    for group_name, group in stores.items():
        if isinstance(group, dict):
            for key in ("dbPath", "path"):
                if group.get(key):
                    path = Path(str(group[key]))
                    checks.append({"name": f"{group_name}.{key}", "path": str(path), "exists": path.exists()})
    if args.check_embedding:
        checks.append({"name": "embedding.endpoint", **check_http_embedding(config, args.timeout)})
    ok = all(check.get("exists", check.get("ok", True)) for check in checks)
    print(json.dumps({"ok": bool(ok), "checks": checks}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

def command_query_jsonl(args: argparse.Namespace) -> int:
    rows, errors = load_jsonl(Path(args.manifest))
    terms = [term.lower() for term in WORD_RE.findall(args.query)]
    results: list[dict[str, Any]] = []
    for row in rows:
        haystack = json.dumps(row, ensure_ascii=False).lower()
        score = sum(1 for term in terms if term and term in haystack)
        if score:
            results.append({"score": score, "record": row})
    results.sort(key=lambda item: item["score"], reverse=True)
    payload = {"ok": not errors, "query": args.query, "errors": errors[:20], "resultCount": len(results), "results": results[: args.limit]}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["ok"] else 1

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("show-config"); show.add_argument("--config", required=True); show.set_defaults(func=command_show_config)
    validate = sub.add_parser("validate-manifest"); validate.add_argument("--manifest", required=True); validate.add_argument("--require-field", action="append", default=[]); validate.set_defaults(func=command_validate_manifest)
    health = sub.add_parser("health"); health.add_argument("--config", required=True); health.add_argument("--check-embedding", action="store_true"); health.add_argument("--timeout", type=float, default=5.0); health.set_defaults(func=command_health)
    query = sub.add_parser("query-jsonl"); query.add_argument("--manifest", required=True); query.add_argument("--query", required=True); query.add_argument("--limit", type=int, default=5); query.set_defaults(func=command_query_jsonl)
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))

if __name__ == "__main__":
    raise SystemExit(main())
