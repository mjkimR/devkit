"""Reproduce same-checkout baseline/new selection against one pytest collection."""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = "29e7dd36845455d92d42e858e3372e3dd812a22e"
CASES = {
    "gate": "packages/devkit/src/devkit/gate/engine/runner.py",
    "workflow": "packages/devkit/src/devkit/workflow/workspace.py",
    "worktree": "packages/devkit/src/devkit/worktree/lifecycle.py",
    "rules": "packages/devkit/src/devkit/rules/engine/evaluator.py",
    "distribution": "packages/devkit-dist/src/devkit/distribution/installation/engines.py",
    "compact": "packages/devkit/src/devkit/compact/execute.py",
    "scope": "packages/devkit-spec/src/devkit_spec/scope/flow.py",
    "documents": "packages/devkit-spec/src/devkit_spec/documents/index.py",
    "proposals": "packages/devkit-spec/src/devkit_spec/proposals/scaffold.py",
}


def load(name: str, text: str) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "scripts/affected_tests.py")
    sys.modules[name] = module
    exec(compile(text, module.__file__, "exec"), module.__dict__)
    return module


def main() -> None:
    start = time.perf_counter()
    collection = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    collection_seconds = time.perf_counter() - start
    nodeids = [line for line in collection.stdout.splitlines() if line.startswith("packages/") and "::" in line]
    assert nodeids
    counts: dict[str, int] = {}
    for node in nodeids:
        path = node.split("::", 1)[0]
        counts[path] = counts.get(path, 0) + 1
    baseline = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{BASE}:scripts/affected_tests.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    modules = {
        "baseline": load("baseline", baseline),
        "new": load("candidate", (ROOT / "scripts/affected_tests.py").read_text()),
    }
    result = {
        "base": BASE,
        "collection_count": len(nodeids),
        "collection_seconds": collection_seconds,
        "collected_counts_by_file": counts,
        "cases": {},
    }
    for case, source in CASES.items():
        assert (ROOT / source).is_file(), source
        row = {"source": source}
        for label, module in modules.items():
            times = []
            for _ in range(3):
                start = time.perf_counter()
                selection = module.select(ROOT, [source])
                times.append(time.perf_counter() - start)
            assert selection.mode == "partial", selection
            files = sorted(
                path for path in counts if any(path == p or path.startswith(p + "/") for p in selection.paths)
            )
            row[label] = {
                "paths": list(selection.paths),
                "collected_files": files,
                "count": sum(counts[p] for p in files),
                "seconds": times,
                "median_seconds": statistics.median(times),
            }
        result["cases"][case] = row
        print(case, row["baseline"]["count"], row["new"]["count"], flush=True)
    Path(__file__).with_name("development-selection.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
