#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import unittest
from pathlib import Path


def load_suite_from_file(path: Path, index: int) -> unittest.TestSuite:
    module_name = f"local_ci_test_{index}_{path.stem.replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load test file: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository Python unittest files by path.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--pattern", default="*.test.py", help="Test filename pattern.")
    parser.add_argument("--manifest", default=None, help="Optional JSON manifest listing stable CI test files.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    test_root = root / "test"
    if args.manifest:
        manifest_path = (root / args.manifest).resolve()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        test_files = [test_root / name for name in manifest.get("python_unittest", [])]
    else:
        test_files = sorted(test_root.glob(args.pattern)) if test_root.exists() else []

    missing_files = [path for path in test_files if not path.exists()]
    if missing_files:
        for path in missing_files:
            print(f"Missing Python test file: {path}", file=sys.stderr)
        return 1

    suite = unittest.TestSuite()
    for index, path in enumerate(test_files, start=1):
        suite.addTest(load_suite_from_file(path, index))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print(f"python_unittest: ok ({len(test_files)} files)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
