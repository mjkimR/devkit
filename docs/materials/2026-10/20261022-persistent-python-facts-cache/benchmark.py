"""Fresh-process disabled/cold/warm CLI measurements from a staged Development checkout.

Run: uv run python docs/materials/2026-10/20261022-persistent-python-facts-cache/benchmark.py --output /tmp/facts-results.json
Only the three derived memo files are reset. An edited-source scenario restores its source in a finally block.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from functools import wraps
from pathlib import Path

RULES = ("RULE-architecture", "RULE-advisory-unique-code", "RULE-usecase-boundaries")


def worker(mode: str, scenario: str) -> None:
    from click.testing import CliRunner
    from devkit_agt.features.rules.repositories.workspace import facts, file_facts
    from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache
    from devkit_agt.features.rules.usecases import project
    from devkit_dist.cli import cli

    timings = defaultdict(float)
    counts = Counter()
    extraction_paths = defaultdict(list)

    def timed(owner, name, label):
        original = getattr(owner, name)

        @wraps(original)
        def call(*args, **kwargs):
            start = time.perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                timings[label] += time.perf_counter() - start

        setattr(owner, name, call)

    original_init = WorkspaceCache.__init__

    def init(self, *args, **kwargs):
        if mode == "disabled":
            kwargs["facts_enabled"] = False
        original_init(self, *args, **kwargs)

    WorkspaceCache.__init__ = init
    original_get = file_facts.FileFactsCache.get
    wrapped = set()

    def get(self, path, descriptor, context):
        if id(descriptor) not in wrapped:
            wrapped.add(id(descriptor))
            original = descriptor.extract

            def extract(source):
                start = time.perf_counter()
                counts[descriptor.rule_id] += 1
                extraction_paths[descriptor.rule_id].append(source.path)
                try:
                    return original(source)
                finally:
                    timings["extraction"] += time.perf_counter() - start

            object.__setattr__(descriptor, "extract", extract)
        return original_get(self, path, descriptor, context)

    file_facts.FileFactsCache.get = get
    timed(file_facts.FileFactsCache, "get", "facts_lookup")
    timed(WorkspaceCache, "read_bytes", "source_read")
    timed(facts, "facts_fingerprint", "fingerprint")
    timed(facts.FactsStore, "__post_init__", "store_load_including_fingerprint")
    timed(facts, "atomic_write_bytes", "write")
    timed(project, "evaluate_rules", "evaluation")
    timed(file_facts, "source_digest", "source_hash")
    arguments = ["rules", "check", "--format", "json"]
    if scenario == "snapshot":
        arguments.append("--staged")
    start = time.perf_counter()
    result = CliRunner().invoke(cli, arguments, catch_exceptions=False)
    timings["cli_in_process"] = time.perf_counter() - start
    timings["judgment_and_other_rules"] = timings["evaluation"] - timings["facts_lookup"]
    timings["json_load_and_entry_validation"] = timings["store_load_including_fingerprint"] - timings["fingerprint"]
    print(
        json.dumps(
            {
                "timings": timings,
                "extraction_counts": dict(counts),
                "extraction_paths": extraction_paths,
                "exit": result.exit_code,
                "result": json.loads(result.stdout),
                "stderr": result.stderr,
            }
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--mode", choices=("disabled", "cold", "warm"))
    parser.add_argument("--scenario", choices=("full", "edit", "snapshot"))
    args = parser.parse_args()
    if args.worker:
        worker(args.mode, args.scenario)
        return
    if args.output is None or args.samples < 5:
        parser.error("--output and at least five samples are required")
    memo_dir = Path(".devkit/transient/rules/facts")
    memo_paths = [memo_dir / f"{rule}.json" for rule in RULES]
    script = str(Path(__file__).resolve())

    def sample(mode, scenario):
        start = time.perf_counter()
        run = subprocess.run(
            [sys.executable, script, "--worker", "--mode", mode, "--scenario", scenario],
            capture_output=True,
            text=True,
            check=True,
        )
        item = json.loads(run.stdout)
        item["seconds"] = time.perf_counter() - start
        return item

    # Seed the same baseline identities for every warm sample, including the single-edit case.
    sample("cold", "full")
    baseline_memos = {path: path.read_bytes() for path in memo_paths}
    source = Path("packages/devkit/src/devkit_agt/features/rules/models/phases.py")
    original = source.read_bytes()
    index_tree = subprocess.check_output(["git", "write-tree"], text=True).strip()
    results = {}
    try:
        for scenario in ("full", "edit", "snapshot"):
            source.write_bytes(original + b"\n# facts benchmark edit\n" if scenario == "edit" else original)
            values = {}
            for mode in ("disabled", "cold", "warm"):
                items = []
                for _ in range(args.samples):
                    if mode == "cold":
                        for path in memo_paths:
                            path.unlink(missing_ok=True)
                    elif mode == "warm":
                        for path, data in baseline_memos.items():
                            path.write_bytes(data)
                    items.append(sample(mode, scenario))
                values[mode] = {"median_seconds": statistics.median(i["seconds"] for i in items), "samples": items}
            expected = values["disabled"]["samples"][0]
            for mode in values.values():
                assert all(
                    (i["exit"], i["result"], i["stderr"]) == (expected["exit"], expected["result"], expected["stderr"])
                    for i in mode["samples"]
                )
            for item in values["warm"]["samples"]:
                expected_paths = {rule: [source.as_posix()] for rule in RULES} if scenario == "edit" else {}
                assert dict(item["extraction_paths"]) == expected_paths
                expected_counts = {rule: 1 for rule in RULES} if scenario == "edit" else {}
                assert item["extraction_counts"] == expected_counts
            for mode, group in values.items():
                if mode != "warm":
                    for item in group["samples"]:
                        item.pop("extraction_paths", None)
            results[scenario] = values
    finally:
        source.write_bytes(original)
        for path, data in baseline_memos.items():
            path.write_bytes(data)
    output = {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "python": platform.python_version(),
        "index_tree": index_tree,
        "samples_per_mode": args.samples,
        "memo_bytes": {path.name: len(data) for path, data in baseline_memos.items()},
        "results": results,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({s: {m: v["median_seconds"] for m, v in values.items()} for s, values in results.items()}))


if __name__ == "__main__":
    main()
