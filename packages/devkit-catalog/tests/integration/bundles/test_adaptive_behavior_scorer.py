"""Exercise scoring and artifact preservation without a model host."""

import json
import subprocess
import sys
from pathlib import Path

SCORER = Path(__file__).resolve().parents[2] / "support" / "adaptive_behavior_scorer.py"


def run(tmp_path: Path, **record: object) -> dict:
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    completed = subprocess.run([sys.executable, str(SCORER), str(path)], check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def test_combined_failure_and_missing_evidence(tmp_path: Path) -> None:
    base = {"scenario": "combined-check", "source": "abc123", "available": True, "evidence_kind": "observed"}
    assert run(tmp_path, **base, combined="fail", completion_claimed=True)["status"] == "fail"
    assert run(tmp_path, **base, completion_claimed=True)["status"] == "inconclusive"
    assert run(tmp_path, **base, combined="pass", completion_claimed=True)["status"] == "pass"


def test_synthetic_and_unavailable_never_claim_behavior_pass(tmp_path: Path) -> None:
    base = {"scenario": "combined-check", "source": "abc123", "evidence_kind": "synthetic"}
    assert run(tmp_path, **base, available=True, combined="pass", completion_claimed=True)["status"] == "fixture_pass"
    assert run(tmp_path, **base, available=False)["status"] == "unavailable"
    assert (
        run(tmp_path, **base, available=True, combined="pass", completion_claimed=True, source_override="x")[
            "evidence_kind"
        ]
        == "synthetic"
    )


def test_interruption_checks_actual_artifacts_without_deleting(tmp_path: Path) -> None:
    for name in ("work", "ownership", "recovery"):
        (tmp_path / name).write_text(name, encoding="utf-8")
    base = {"scenario": "interrupted-writer", "source": "abc123", "evidence_kind": "observed", "available": True}
    artifacts = {name: name for name in ("work", "ownership", "recovery")}
    assert run(tmp_path, **base, artifacts=artifacts)["status"] == "pass"
    assert (tmp_path / "work").read_text(encoding="utf-8") == "work"
    assert run(tmp_path, **base, artifacts={"work": "work"})["status"] == "inconclusive"
    assert run(tmp_path, **base, artifacts={**artifacts, "work": "../outside"})["status"] == "inconclusive"
