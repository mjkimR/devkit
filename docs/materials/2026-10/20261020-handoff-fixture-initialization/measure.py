"""Compare the original twelve handoff consumers on one checkout and interpreter.

Run with the workspace Python. Results contain case identities, elapsed samples and
per-worker preparation counts; temporary pytest logs and source copies are removed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = "packages/devkit-spec/tests/test_integration.py"
BASELINE = "475e8137e6f43656091203a207b48cabede864ba"
PLUGIN = """import json
import os
from pathlib import Path
import time
import pytest

COUNTS = {"sync": 0, "preparation_commit": 0}
TIMES = {}
CASES = []

def pytest_collection_modifyitems(config, items):
    keep = [item for item in items if "accepted_handoff_base" in item.fixturenames
            and item.originalname != "test_handoff_initialization_keeps_template_isolated"]
    config.hook.pytest_deselected(items=[item for item in items if item not in keep])
    items[:] = keep
    CASES.extend(sorted(item.nodeid.rsplit("::", 1)[-1] for item in keep))
    for module in {item.module for item in keep}:
        cli, git = module._cli, module.git
        def counted_cli(*args, _original=cli, **kwargs):
            if args[1:] == ("sync",):
                COUNTS["sync"] += 1
            return _original(*args, **kwargs)
        def counted_git(*args, _original=git, **kwargs):
            if "track complete synchronized projections" in args:
                COUNTS["preparation_commit"] += 1
            return _original(*args, **kwargs)
        module._cli, module.git = counted_cli, counted_git

@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    start = time.perf_counter()
    yield
    if fixturedef.argname in {"accepted_handoff_base", "handoff_repository_template"}:
        TIMES.setdefault(fixturedef.argname, []).append(time.perf_counter() - start)

def pytest_sessionfinish(session, exitstatus):
    worker = getattr(session.config, "workerinput", {}).get("workerid", "controller")
    record = {"counts": COUNTS, "fixture_seconds": TIMES, "cases": CASES, "exit_code": exitstatus}
    (Path(os.environ["FIXTURE_MEASURE_OUTPUT"]) / (worker + ".json")).write_text(json.dumps(record))
"""


def run(label: str, source: Path, parallel: bool, temporary: Path) -> dict:
    output = temporary / label
    output.mkdir()
    env = dict(os.environ, FIXTURE_MEASURE_OUTPUT=str(output))
    env["PYTHONPATH"] = str(temporary) + os.pathsep + env.get("PYTHONPATH", "")
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        str(ROOT / "pyproject.toml"),
        "-p",
        "fixture_measure",
        "-p",
        "no:cacheprovider",
        "-q",
        str(source),
    ]
    command += ["-n", "auto", "--maxprocesses", "8", "--dist", "worksteal"] if parallel else ["-n0"]
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    summary = re.search(r"\b(\d+) passed(?:, \d+ deselected)? in ([^\n]+)", completed.stdout)
    if completed.returncode or not summary or int(summary[1]) != 12:
        raise RuntimeError(f"{label}: invalid test outcome\n{completed.stdout}\n{completed.stderr}")
    workers = [json.loads(path.read_text()) for path in sorted(output.glob("*.json"))]
    active = [worker for worker in workers if worker["cases"]]
    assert active and all(worker["exit_code"] == 0 for worker in workers)
    cases = active[0]["cases"]
    assert len(cases) == 12 and all(worker["cases"] == cases for worker in active)
    result = {
        "label": label,
        "wall_seconds": elapsed,
        "passed": 12,
        "cases": cases,
        "active_workers": len(active),
        "sync_calls": sum(worker["counts"]["sync"] for worker in active),
        "preparation_commits": sum(worker["counts"]["preparation_commit"] for worker in active),
        "fixture_seconds": {
            name: [value for worker in active for value in worker["fixture_seconds"].get(name, [])]
            for name in ("accepted_handoff_base", "handoff_repository_template")
        },
    }
    print(f"[MEASUREMENT: label={label} seconds={elapsed:.3f} sync={result['sync_calls']} passed=12]", flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("measurements.json"))
    args = parser.parse_args()
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check_test_environment.py"),
            "--",
            sys.executable,
            str(Path(__file__).relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )
    baseline = subprocess.run(
        ["git", "show", f"{args.baseline}:{SOURCE}"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    result = {
        "baseline_revision": args.baseline,
        "baseline_source_sha256": hashlib.sha256(baseline.encode()).hexdigest(),
        "current_source_sha256": hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
        "checkout_head": head,
        "python": sys.version.split()[0],
        "scope": "same twelve original handoff consumers; current may include uncommitted changes",
        "samples": [],
    }
    with tempfile.TemporaryDirectory(prefix="handoff-initialization-") as directory:
        temporary = Path(directory)
        old = temporary / "test_integration.py"
        old.write_text(baseline)
        (temporary / "fixture_measure.py").write_text(PLUGIN)
        order = [
            ("serial-baseline", old, False),
            ("serial-current", ROOT / SOURCE, False),
            ("parallel-baseline-1", old, True),
            ("parallel-current-1", ROOT / SOURCE, True),
            ("parallel-current-2", ROOT / SOURCE, True),
            ("parallel-baseline-2", old, True),
        ]
        for label, source, parallel in order:
            result["samples"].append(run(label, source, parallel, temporary))
            assert all(sample["cases"] == result["samples"][0]["cases"] for sample in result["samples"])
            args.output.write_text(json.dumps(result, indent=2) + "\n")
    for mode in ("serial", "parallel"):
        result[mode + "_medians"] = {
            algorithm: statistics.median(
                sample["wall_seconds"]
                for sample in result["samples"]
                if sample["label"].startswith(mode + "-" + algorithm)
            )
            for algorithm in ("baseline", "current")
        }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
