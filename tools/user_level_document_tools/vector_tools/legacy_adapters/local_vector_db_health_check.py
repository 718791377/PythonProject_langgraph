#!/usr/bin/env python3
"""Read-only health checks for the local vector database control plane.

This script validates the baseline described in
docs_bilingual/implementation_plans/local_vector_database_implementation_plan.md.
It does not write to <configured-external-source-root>.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request


PROJECT_ROOT = Path.cwd()
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "local-vector-db.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be an object: {path}")
    return data


def read_text_best_effort(path: Path, max_chars: int = 500_000) -> str:
    raw = path.read_bytes()[:max_chars]
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> tuple[bool, Any, str | None]:
    payload = None
    request_headers = dict(headers or {})
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    req = request.Request(url, method=method, headers=request_headers, data=payload)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
        return True, json.loads(raw.decode("utf-8")), None
    except (error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return False, None, str(exc)


def check_path(label: str, value: str, *, expect_dir: bool | None = None) -> dict[str, Any]:
    path = Path(value)
    exists = path.exists()
    is_dir = path.is_dir() if exists else False
    is_file = path.is_file() if exists else False
    ok = exists
    if expect_dir is True:
        ok = ok and is_dir
    if expect_dir is False:
        ok = ok and is_file
    return {
        "label": label,
        "path": str(path),
        "ok": bool(ok),
        "exists": bool(exists),
        "isDir": bool(is_dir),
        "isFile": bool(is_file),
    }


def find_model(data: Any, expected: str) -> bool:
    if not isinstance(data, dict):
        return False
    candidates: list[Any] = []
    for key in ("data", "models"):
        value = data.get(key)
        if isinstance(value, list):
            candidates.extend(value)
    for item in candidates:
        if not isinstance(item, dict):
            continue
        values = {
            str(item.get("id", "")),
            str(item.get("model", "")),
            str(item.get("name", "")),
        }
        aliases = item.get("aliases")
        if isinstance(aliases, list):
            values.update(str(alias) for alias in aliases)
        if expected in values:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--out", help="Optional JSON output path.")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = load_json(config_path)
    embedding = config["embedding"]
    stores = config["stores"]
    qmd = config["qmd"]

    base_url = str(embedding["baseURL"]).rstrip("/")
    model = str(embedding["model"])
    dimensions = int(embedding["dimensions"])
    api_key = str(embedding.get("apiKey", ""))

    checks: dict[str, Any] = {}
    path_checks = [
        check_path("openclawRoot", config["openclawRoot"], expect_dir=True),
        check_path("modelFile", config["modelFile"], expect_dir=False),
        check_path("qmd.defaultRoot", qmd["defaultRoot"], expect_dir=True),
        check_path("stores.vector.dbPath", stores["vector"]["dbPath"], expect_dir=True),
    ]
    for table in stores["vector"].get("expectedTables", []):
        path_checks.append(
            check_path(
                f"stores.vector.expectedTables.{table}",
                str(Path(stores["vector"]["dbPath"]) / table),
                expect_dir=True,
            )
        )
    for surface in config.get("openclawConfigSurfaces", []):
        path_checks.append(check_path(f"openclawConfigSurface.{surface}", surface, expect_dir=False))
    checks["paths"] = path_checks

    models_ok, models_data, models_error = http_json(f"{base_url}/models", timeout=args.timeout)
    checks["modelsEndpoint"] = {
        "ok": bool(models_ok and find_model(models_data, model)),
        "reachable": bool(models_ok),
        "expectedModel": model,
        "error": models_error,
    }

    embeddings_ok, embeddings_data, embeddings_error = http_json(
        f"{base_url}/embeddings",
        method="POST",
        headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        body={"model": model, "input": str(embedding.get("smokeText", "health check"))},
        timeout=args.timeout,
    )
    vector = None
    if embeddings_ok and isinstance(embeddings_data, dict):
        rows = embeddings_data.get("data")
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            candidate = rows[0].get("embedding")
            if isinstance(candidate, list):
                vector = candidate
    checks["embeddingsEndpoint"] = {
        "ok": bool(vector is not None and len(vector) == dimensions),
        "reachable": bool(embeddings_ok),
        "expectedDimensions": dimensions,
        "actualDimensions": len(vector) if isinstance(vector, list) else None,
        "error": embeddings_error,
    }

    surface_results: list[dict[str, Any]] = []
    for surface in config.get("openclawConfigSurfaces", []):
        surface_path = Path(surface)
        result = {"path": str(surface_path), "ok": False, "containsModel": False, "containsBaseURL": False}
        if surface_path.is_file():
            text = read_text_best_effort(surface_path)
            result["containsModel"] = model in text
            result["containsBaseURL"] = base_url in text
            result["ok"] = bool(result["containsModel"] and result["containsBaseURL"])
        surface_results.append(result)
    checks["openclawConfigSurfaces"] = surface_results

    all_ok = (
        all(item["ok"] for item in path_checks)
        and checks["modelsEndpoint"]["ok"]
        and checks["embeddingsEndpoint"]["ok"]
        and all(item["ok"] for item in surface_results)
    )
    report = {
        "ok": bool(all_ok),
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "configPath": str(config_path),
        "checks": checks,
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
