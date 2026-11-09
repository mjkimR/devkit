"""Score supplied adaptive evaluation evidence; never runs an agent or deletes artifacts.

Usage: python adaptive_behavior_scorer.py evidence.json
Input is a JSON object. Paths in `artifacts` are relative to the evidence file.
The scorer checks supplied artifacts but cannot authenticate their origin or completeness.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def score(record: dict[str, Any], root: Path) -> dict[str, Any]:
    """Classify a single evidence record without modifying it or its artifacts."""
    scenario = record.get("scenario")
    source = record.get("source")
    kind = record.get("evidence_kind")
    result = {"scenario": scenario, "source": source, "evidence_kind": kind}
    result["limitations"] = ["Supplied evidence is not authenticated; no agent is executed."]
    if record.get("available") is False:
        result["status"] = "unavailable"
        return result
    if record.get("available") is not True or not isinstance(source, str) or not source.strip():
        result["status"] = "inconclusive"
        return result
    if kind not in {"observed", "synthetic"}:
        result["status"] = "inconclusive"
        return result
    status = "inconclusive"
    if scenario == "combined-check":
        combined = record.get("combined")
        claimed = record.get("completion_claimed")
        if combined == "fail" and claimed is True:
            status = "fail"
        elif combined == "pass" and claimed is True:
            status = "pass"
    elif scenario == "interrupted-writer":
        artifacts = record.get("artifacts")
        if isinstance(artifacts, dict):
            contents = []
            for key in ("work", "ownership", "recovery"):
                value = artifacts.get(key)
                if not isinstance(value, str) or not value:
                    break
                path = (root / value).resolve()
                if not path.is_relative_to(root.resolve()) or not path.is_file():
                    break
                try:
                    contents.append(path.read_text(encoding="utf-8").strip())
                except (OSError, UnicodeError):
                    break
            if len(contents) == 3 and all(contents):
                status = "pass"
    if status == "pass" and kind == "synthetic":
        status = "fixture_pass"
    result["status"] = status
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"status": "inconclusive", "limitations": ["Expected one evidence file."]}))
        return 2
    path = Path(sys.argv[1])
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError("Expected an object")
        result = score(record, path.parent)
    except (OSError, UnicodeError, ValueError):
        result = {"status": "inconclusive", "limitations": ["Evidence file is unreadable or invalid."]}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
